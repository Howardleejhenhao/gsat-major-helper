import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import sys

INPUT_CSV = "../csv/Department_ori.csv"
OUTPUT_CSV = "../csv/ExamRequirement.csv"

ID_COL = "dept_id"
EXAM_YEAR = 114

SUBJECT_NAME_TO_ID = {
    "國文": 0,
    "英文": 1,
    "數學A": 2,
    "數A": 2,
    "數學B": 3,
    "數B": 3,
    "社會": 4,
    "自然": 5,
}

TARGET_SUBJECT_IDS = {0, 1, 2, 3, 4, 5}

HEADERS_CANONICAL = {
    "國文": "國文",
    "英文": "英文",
    "數A": "數A",
    "數學A": "數A",
    "數B": "數B",
    "數學B": "數B",
    "社會": "社會",
    "自然": "自然",
}

BASE = "https://university-tw.ldkrsi.men/caac"
ALWAYS_OUTPUT_6_SUBJECTS = True

REQUEST_TIMEOUT = 15
SLEEP_SEC = 0.2
# ==========================


def normalize_dept_id(x: str) -> str:
    """盡量把 dept_id 轉成網站可能用的 6 碼字串。
    - 若已是 6 碼數字字串：直接用
    - 若是 5 碼：左補 0
    - 其他長度：原樣回傳
    """
    if pd.isna(x):
        return ""
    s = str(x).strip()
    # pandas 可能把 013062 讀成 13062 或 13062.0
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


def build_url(dept_id: str) -> str:
    school_id = dept_id[:3]
    # print(f"{BASE}/{school_id}/{dept_id}")
    return f"{BASE}/{school_id}/{dept_id}"


def find_exam_standard_table(soup: BeautifulSoup):
    """從頁面中找出『學測檢定標準』對應的 table。"""
    # 方式 1：依 dt/dd 結構精準找
    for dt in soup.find_all("dt"):
        if dt.get_text(strip=True) == "學測檢定標準":
            dd = dt.find_next_sibling("dd")
            if dd:
                table = dd.find("table")
                if table:
                    return table

    # 方式 2：fallback - 找看起來像學測檢定標準的 standard 表
    candidates = soup.find_all("table", class_="standard")
    for t in candidates:
        thead = t.find("thead")
        if not thead:
            continue
        header_text = " ".join(th.get_text(strip=True) for th in thead.find_all(["th", "td"]))
        if "國文" in header_text and "英文" in header_text and "自然" in header_text:
            # 通常這張就是
            return t

    return None


def parse_requirements_from_html(html: str, dept_id: str):
    soup = BeautifulSoup(html, "html.parser")
    table = find_exam_standard_table(soup)
    if table is None:
        return []

    # 解析 header
    thead_tr = table.find("thead").find("tr") if table.find("thead") else None
    if not thead_tr:
        return []

    header_cells = thead_tr.find_all(["th", "td"])
    # 第一格通常是空白或年份欄
    header_names = [c.get_text(strip=True) for c in header_cells[1:]]

    # 正規化 header 名稱（數A/數B）
    norm_headers = []
    for h in header_names:
        norm_headers.append(HEADERS_CANONICAL.get(h, h))

    # 找 114 年那一列
    target_row = None
    for tr in table.find("tbody").find_all("tr"):
        th = tr.find("th")
        if not th:
            continue
        year_text = th.get_text(strip=True)
        if year_text == f"{EXAM_YEAR}年":
            target_row = tr
            break

    if target_row is None:
        return []

    tds = target_row.find_all("td")
    values = [td.get_text(strip=True) for td in tds]

    # 對齊 header - value
    header_to_value = {}
    for h, v in zip(norm_headers, values):
        header_to_value[h] = v

    rows = []

    # 依規格輸出 6 科
    # 我們用 canonical header 反推 subject_id
    canonical_subject_order = ["國文", "英文", "數A", "數B", "社會", "自然"]
    for canon in canonical_subject_order:
        sid = SUBJECT_NAME_TO_ID.get(canon)
        if sid not in TARGET_SUBJECT_IDS:
            continue

        v = header_to_value.get(canon, "--")
        if v in ("--", "－", "-", ""):
            req = None
        else:
            req = v

        if ALWAYS_OUTPUT_6_SUBJECTS:
            rows.append({
                "dept_id": dept_id,
                "exam_year": EXAM_YEAR,
                "subject_id": sid,
                "require_level": req
            })
        else:
            if req is not None:
                rows.append({
                    "dept_id": dept_id,
                    "exam_year": EXAM_YEAR,
                    "subject_id": sid,
                    "require_level": req
                })

    return rows


def fetch_and_parse(dept_id: str):
    url = build_url(dept_id)
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            print(f"[WARN] HTTP {r.status_code}: {dept_id} -> {url}")
            return []
        return parse_requirements_from_html(r.text, dept_id)
    except Exception as e:
        print(f"[WARN] Fetch error: {dept_id} -> {e}")
        return []


def main():
    df = pd.read_csv(INPUT_CSV)

    if ID_COL not in df.columns:
        raise ValueError(f"找不到欄位 {ID_COL}，請確認總表欄位名稱。")

    raw_ids = df[ID_COL].dropna().unique().tolist()

    dept_ids = []
    for x in raw_ids:
        did = normalize_dept_id(x)
        if not did:
            continue
        dept_ids.append(did)
    # print(dept_ids)
    results = []

    for i, did in enumerate(dept_ids, 1):
        # 這個網站看起來用 6 碼校系代碼（例：013062）
        # 若不是 6 碼數字字串，先跳過並警告
        if not (did.isdigit() and len(did) == 6):
            print(f"[SKIP] dept_id 格式可能不是網站校系代碼：{did}")
            continue

        rows = fetch_and_parse(did)
        results.extend(rows)

        if i % 50 == 0:
            print(f"[INFO] processed {i}/{len(dept_ids)}")

        time.sleep(SLEEP_SEC)

    out_df = pd.DataFrame(results, columns=["dept_id", "exam_year", "subject_id", "require_level"])
    out_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"[DONE] rows={len(out_df)} -> {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
