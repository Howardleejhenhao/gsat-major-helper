import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

EXAM_YEAR = 114
BASE = "https://university-tw.ldkrsi.men/caac"

DEPT_SOURCE_CANDIDATES = [
    "../csv/Department_ori.csv",
    "ExamRequirement.csv",
]
DEPT_ID_COL_CANDIDATES = [
    "dept_id",
    "dep_id",
    "department_id",
]

OUT_ADMISSION = "../csv/AdmissionRecord.csv"
OUT_COMBO = "../csv/SubjectCombination.csv"
OUT_DETAIL = "../csv/CombinationDetail.csv"

INCLUDE_DEPT_ID_IN_ADMISSION = True

REQUEST_TIMEOUT = 15
SLEEP_SEC = 0.001

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; data-collector/1.0)"
}

SUBJECT_TABLE_TEXT = """
0,國文
1,英文
2,數學A
3,數學B
4,社會
5,自然
6,國文+英文
7,國文+數學A
8,國文+數學B
9,國文+社會
10,國文+自然
11,英文+數學A
12,英文+數學B
13,英文+社會
14,英文+自然
15,數學A+數學B
16,數學A+社會
17,數學A+自然
18,數學B+社會
19,數學B+自然
20,社會+自然
21,國文+英文+數學A
22,國文+英文+數學B
23,國文+英文+社會
24,國文+英文+自然
25,國文+數學A+數學B
26,國文+數學A+社會
27,國文+數學A+自然
28,國文+數學B+社會
29,國文+數學B+自然
30,國文+社會+自然
31,英文+數學A+數學B
32,英文+數學A+社會
33,英文+數學A+自然
34,英文+數學B+社會
35,英文+數學B+自然
36,英文+社會+自然
37,數學A+數學B+社會
38,數學A+數學B+自然
39,數學A+社會+自然
40,數學B+社會+自然
41,國文+英文+數學A+數學B
42,國文+英文+數學A+社會
43,國文+英文+數學A+自然
44,國文+英文+數學B+社會
45,國文+英文+數學B+自然
46,國文+英文+社會+自然
47,國文+數學A+數學B+社會
48,國文+數學A+數學B+自然
49,國文+數學A+社會+自然
50,國文+數學B+社會+自然
51,英文+數學A+數學B+社會
52,英文+數學A+數學B+自然
53,英文+數學A+社會+自然
54,英文+數學B+社會+自然
55,數學A+數學B+社會+自然
56,國文+英文+數學A+數學B+社會
57,國文+英文+數學A+數學B+自然
58,國文+英文+數學A+社會+自然
59,國文+英文+數學B+社會+自然
60,國文+數學A+數學B+社會+自然
61,英文+數學A+數學B+社會+自然
62,國文+英文+數學A+數學B+社會+自然
""".strip()

CANONICAL_ORDER = ["國文", "英文", "數學A", "數學B", "社會", "自然"]
ORDER_INDEX = {s: i for i, s in enumerate(CANONICAL_ORDER)}

ABBR_TO_FULL = {
    "國": "國文",
    "英": "英文",
    "數A": "數學A",
    "數學A": "數學A",
    "數B": "數學B",
    "數學B": "數學B",
    "社": "社會",
    "社會": "社會",
    "自": "自然",
    "自然": "自然",
    "國文": "國文",
    "英文": "英文",
}


def build_subject_map():
    """把 subject_name 正規化成 tuple key，建立對應 subject_id。"""
    raw = []
    for line in SUBJECT_TABLE_TEXT.splitlines():
        sid_str, name = line.split(",", 1)
        sid = int(sid_str.strip())
        name = name.strip()
        raw.append((sid, name))

    norm_map = {}
    for sid, name in raw:
        parts = [p.strip() for p in name.split("+")]
        # 依 canonical order 排序
        parts_sorted = sorted(parts, key=lambda x: ORDER_INDEX.get(x, 999))
        key = tuple(parts_sorted)
        norm_map[key] = sid

    return norm_map


SUBJECT_NORM_MAP = build_subject_map()

def find_dept_source_file():
    for fname in DEPT_SOURCE_CANDIDATES:
        if Path(fname).exists():
            return fname
    raise FileNotFoundError(
        f"找不到總表檔案，請確認以下其中一個存在：{DEPT_SOURCE_CANDIDATES}"
    )


def find_dept_id_col(df):
    for c in DEPT_ID_COL_CANDIDATES:
        if c in df.columns:
            return c
    raise ValueError(
        f"找不到 dept_id 欄位。已嘗試：{DEPT_ID_COL_CANDIDATES}，"
        f"你的欄位有：{list(df.columns)}"
    )


def normalize_dept_id(x):
    """把可能被 pandas 讀成數字/浮點的 dept_id 轉回字串，盡量整理成 6 碼。"""
    if pd.isna(x):
        return ""
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if s.isdigit():
        if len(s) == 6:
            return s
        if len(s) == 5:
            return s.zfill(6)
        if len(s) == 4:
            return s.zfill(6)
    return s


def build_url(dept_id):
    school_id = dept_id[:3]
    return f"{BASE}/{school_id}/{dept_id}"

def find_filter_result_table(soup):
    """依 dt/dd 結構找 '114年篩選結果' 的 table。"""
    for dt in soup.find_all("dt"):
        if dt.get_text(strip=True) == f"{EXAM_YEAR}年篩選結果":
            dd = dt.find_next_sibling("dd")
            if not dd:
                continue
            table = dd.find("table")
            if table:
                return table
    return None


def split_requirement_text(cell_text):
    """支援同一格有多個條件的情況。"""
    t = cell_text.strip()
    if not t or t in {"--", "－", "-"}:
        return []

    # 常見分隔符號
    seps = ["、", "；", ";", "／", "/", "\n"]
    for s in seps:
        t = t.replace(s, "|")

    parts = [p.strip() for p in t.split("|") if p.strip()]
    return parts


def parse_part(part):
    """
    解析像：
    - 國=15
    - 英+自=25
    回傳 (subjects_full_list, score_int, raw_part)
    """
    m = re.search(r"(.+?)\s*=\s*(\d+)", part)
    if not m:
        return None

    left = m.group(1).strip()
    score = int(m.group(2))

    tokens = [t.strip() for t in left.split("+") if t.strip()]
    fulls = []
    for tok in tokens:
        full = ABBR_TO_FULL.get(tok)

        if not full:
            if tok in {"數A", "數B"}:
                full = ABBR_TO_FULL.get(tok)
            else:
                full = tok

        fulls.append(full)

    return fulls, score, part


def subjects_to_subject_id(fulls):
    """把科目全名 list 轉成 subject_id。"""
    fulls_sorted = sorted(fulls, key=lambda x: ORDER_INDEX.get(x, 999))
    key = tuple(fulls_sorted)
    return SUBJECT_NORM_MAP.get(key)


def parse_filter_table(html):
    """
    回傳：
    - screenings: list of dict
        [
          {
            "combo_order": 1,
            "raw_cell": "英+自=25",
            "parts": [
                {"subject_id": 14, "require_score": 25, "remark": "英+自=25"}
            ]
          },
          ...
        ]
    - has_extra_screen: 0/1
    """
    soup = BeautifulSoup(html, "html.parser")
    table = find_filter_result_table(soup)
    if table is None:
        return [], 0

    thead = table.find("thead")
    tbody = table.find("tbody")
    if not thead or not tbody:
        return [], 0

    headers = [th.get_text(strip=True) for th in thead.find_all("th")]
    rows = tbody.find_all("tr")
    if not rows:
        return [], 0

    tds = rows[0].find_all(["td", "th"])
    cells = [c.get_text(strip=True) for c in tds]

    header_to_cell = {}
    for h, c in zip(headers, cells):
        header_to_cell[h] = c

    extra_text = header_to_cell.get("超額篩選", "")
    has_extra = 1 if extra_text == "有" else 0

    screening_headers = [h for h in headers if h.startswith("篩選")]

    screenings = []
    for idx, h in enumerate(screening_headers, start=1):
        cell_text = header_to_cell.get(h, "").strip()
        if not cell_text or cell_text in {"--", "－", "-"}:
            continue

        parts_raw = split_requirement_text(cell_text)
        parts_parsed = []

        for part in parts_raw:
            parsed = parse_part(part)
            if not parsed:
                # 解析不到也保留 remark
                parts_parsed.append({
                    "subject_id": None,
                    "require_score": None,
                    "remark": part
                })
                continue

            fulls, score, raw_part = parsed
            sid = subjects_to_subject_id(fulls)

            parts_parsed.append({
                "subject_id": sid,
                "require_score": score,
                "remark": raw_part
            })

        screenings.append({
            "combo_order": idx,
            "raw_cell": cell_text,
            "parts": parts_parsed
        })

    return screenings, has_extra


def compute_lowest_total_expr(screenings):
    """
    依你的例子，lowest_total 回傳「數字最大的那條原始表達式」。
    例如 國=13、英=14 -> 英=14
    """
    best = None
    best_score = None

    for sc in screenings:
        for p in sc["parts"]:
            score = p.get("require_score")
            remark = p.get("remark")
            if score is None or remark is None:
                continue
            if best_score is None or score > best_score:
                best_score = score
                best = remark

    return best


# =========================
# 主流程
# =========================
def main():
    src_file = find_dept_source_file()
    df = pd.read_csv(src_file)
    id_col = find_dept_id_col(df)

    raw_ids = df[id_col].dropna().unique().tolist()
    dept_ids = []
    for x in raw_ids:
        did = normalize_dept_id(x)
        if did and did.isdigit() and len(did) == 6:
            dept_ids.append(did)
        else:
            pass

    dept_ids = sorted(set(dept_ids))

    admission_rows = []
    combo_rows = []
    detail_rows = []

    record_id = 0
    combo_id = 0

    for i, dept_id in enumerate(tqdm(dept_ids, desc="Fetching 114篩選結果"), start=1):
        url = build_url(dept_id)
        try:
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                tqdm.write(f"[WARN] HTTP {r.status_code}: {dept_id}")
                continue

            screenings, has_extra = parse_filter_table(r.text)

            if not screenings and has_extra == 0:
                continue

            lowest_total = compute_lowest_total_expr(screenings)

            adm = {
                "record_id": record_id,
                "exam_year": EXAM_YEAR,
                "has_extra_screen": has_extra,
                "lowest_total": lowest_total
            }
            if INCLUDE_DEPT_ID_IN_ADMISSION:
                adm["dept_id"] = dept_id

            admission_rows.append(adm)

            for sc in screenings:
                cid = combo_id
                combo_rows.append({
                    "combo_id": cid,
                    "record_id": record_id,
                    "combo_order": sc["combo_order"]
                })

                for p in sc["parts"]:
                    detail_rows.append({
                        "combo_id": cid,
                        "subject_id": p.get("subject_id"),
                        "require_score": p.get("require_score"),
                        "remark": p.get("remark")
                    })

                combo_id += 1

            record_id += 1

            time.sleep(SLEEP_SEC)

        except Exception as e:
            tqdm.write(f"[WARN] error {dept_id}: {e}")
            continue

    if INCLUDE_DEPT_ID_IN_ADMISSION:
        admission_cols = ["record_id", "dept_id", "exam_year", "has_extra_screen", "lowest_total"]
    else:
        admission_cols = ["record_id", "exam_year", "has_extra_screen", "lowest_total"]

    adm_df = pd.DataFrame(admission_rows)
    if not adm_df.empty:
        adm_df = adm_df.reindex(columns=admission_cols)

    combo_df = pd.DataFrame(combo_rows, columns=["combo_id", "record_id", "combo_order"])
    detail_df = pd.DataFrame(detail_rows, columns=["combo_id", "subject_id", "require_score", "remark"])

    adm_df.to_csv(OUT_ADMISSION, index=False, encoding="utf-8-sig")
    combo_df.to_csv(OUT_COMBO, index=False, encoding="utf-8-sig")
    detail_df.to_csv(OUT_DETAIL, index=False, encoding="utf-8-sig")

    print(f"[DONE] {OUT_ADMISSION}: {len(adm_df)} rows")
    print(f"[DONE] {OUT_COMBO}: {len(combo_df)} rows")
    print(f"[DONE] {OUT_DETAIL}: {len(detail_df)} rows")
    print(f"[INFO] dept source: {src_file}, id_col: {id_col}")


if __name__ == "__main__":
    main()
