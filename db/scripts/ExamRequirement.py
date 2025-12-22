import re
import os
import time
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

INPUT_CSV = "../csv/Department_ori_115.csv"
OUTPUT_CSV = "../csv/ExamRequirement_115.csv"

START_URL = "https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/SchoolSearch.php"

EXAM_YEAR = 115

REQUEST_TIMEOUT = 20
SLEEP_SEC = 0.05
ALWAYS_OUTPUT_6_SUBJECTS = True
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

CANONICAL_SUBJECT_ORDER = ["國文", "英文", "數A", "數B", "社會", "自然"]

def build_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Referer": START_URL,
    })

    retries = Retry(
        total=5,
        backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s

def normalize_dept_id(x: str) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if s.isdigit():
        if len(s) == 6:
            return s
        if len(s) in (4, 5):
            return s.zfill(6)
    return s

def fetch_university_list(session: requests.Session):
    post_url = urljoin(START_URL, "ShowSchool.php")

    payload = {
        "option": "SCHNAME",
        "SubSchName": "依學校名稱查詢",
    }

    r = session.post(post_url, data=payload, timeout=REQUEST_TIMEOUT)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")

    univ_pattern = re.compile(r"^\((\d{3})\)(.+)$")

    universities = []
    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        m = univ_pattern.match(text)
        if not m:
            continue

        univ_id = m.group(1)
        univ_name = m.group(2).strip()
        href = (a.get("href") or "").strip()
        if not href:
            continue

        univ_url = urljoin(post_url, href)
        universities.append((univ_id, univ_name, univ_url))

    # 去重 & sort
    tmp = {}
    for uid, uname, uurl in universities:
        tmp[uid] = (uid, uname, uurl)
    universities = [tmp[k] for k in sorted(tmp.keys())]
    return universities

def extract_dept_detail_links(school_html: str, base_url: str):
    soup = BeautifulSoup(school_html, "html.parser")

    dept_code_pat = re.compile(r"\((\d{6})\)")
    detail_href_pat = re.compile(r"115_\d{6}\.htm", re.IGNORECASE)

    mapping = {}

    for a in soup.find_all("a"):
        a_text = a.get_text(strip=True)
        href = (a.get("href") or "").strip()
        if not href:
            continue

        if a_text == "詳細資料" or detail_href_pat.search(href):
            abs_url = urljoin(base_url, href)

            m = re.search(r"115_(\d{6})\.htm", href)
            dept_id = m.group(1) if m else None

            if not dept_id:
                tr = a.find_parent("tr")
                if tr:
                    first_td = tr.find("td")
                    if first_td:
                        txt = first_td.get_text(" ", strip=True)
                        m2 = dept_code_pat.search(txt)
                        if m2:
                            dept_id = m2.group(1)

            if dept_id:
                mapping[dept_id] = abs_url

    return mapping

def parse_first_stage_requirements(html: str):
    soup = BeautifulSoup(html, "html.parser")

    anchor = soup.find(string=re.compile(r"校系代碼"))
    if not anchor:
        return {}

    tr = anchor.find_parent("tr")
    if not tr:
        return {}

    tds = tr.find_all("td")
    if not tds:
        return {}

    subject_idx = None
    subject_tokens_set = set(HEADERS_CANONICAL.keys())

    def split_lines(td):
        txt = td.get_text("\n", strip=True)
        return [x.strip() for x in txt.split("\n") if x.strip()]

    for i, td in enumerate(tds):
        lines = split_lines(td)
        hit = sum(1 for ln in lines if ln in subject_tokens_set)
        if hit >= 2:
            if "國文" in lines and "英文" in lines:
                subject_idx = i
                break

    if subject_idx is None:
        return {}

    if subject_idx + 1 >= len(tds):
        return {}

    subject_lines = split_lines(tds[subject_idx])
    level_lines = split_lines(tds[subject_idx + 1])

    pairs = list(zip(subject_lines, level_lines))

    header_to_value = {}
    for subj, lvl in pairs:
        canon = HEADERS_CANONICAL.get(subj, subj)
        if canon in SUBJECT_NAME_TO_ID:
            if lvl in ("--", "－", "-", ""):
                header_to_value[canon] = None
            else:
                header_to_value[canon] = lvl

    return header_to_value


def build_requirement_rows_for_dept(dept_id: str, header_to_value: dict):
    rows = []
    for canon in CANONICAL_SUBJECT_ORDER:
        sid = SUBJECT_NAME_TO_ID[canon]

        req = header_to_value.get(canon, None)

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


def main():
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    df = pd.read_csv(INPUT_CSV, dtype=str)
    if "dept_id" not in df.columns:
        raise ValueError("INPUT_CSV 找不到 dept_id 欄位")

    target_dept_ids = []
    for x in df["dept_id"].dropna().unique().tolist():
        did = normalize_dept_id(x)
        if did and did.isdigit() and len(did) == 6:
            target_dept_ids.append(did)

    target_dept_ids = sorted(set(target_dept_ids))
    target_set = set(target_dept_ids)

    session = build_session()
    universities = fetch_university_list(session)
    dept_to_detail = {}

    for univ_id, univ_name, univ_url in tqdm(
        universities,
        desc="Scanning universities",
        unit="univ"
    ):
        time.sleep(random.uniform(0.1, 0.4))
        try:
            r = session.get(univ_url, timeout=REQUEST_TIMEOUT)
            r.encoding = r.apparent_encoding
        except Exception as e:
            tqdm.write(f"[WARN] school page fetch fail {univ_id} {univ_name}: {e}")
            continue

        m = extract_dept_detail_links(r.text, univ_url)

        for did, durl in m.items():
            if did in target_set:
                dept_to_detail[did] = durl

    if dept_to_detail:
        sample_url = next(iter(dept_to_detail.values()))
        base_html_dir = sample_url.rsplit("/", 1)[0] + "/"
        for did in target_dept_ids:
            if did not in dept_to_detail:
                dept_to_detail[did] = urljoin(base_html_dir, f"115_{did}.htm?v=1.0")

    results = []

    for i, did in enumerate(
        tqdm(target_dept_ids, desc="Fetching detail pages", unit="dept"),
        1
    ):
        detail_url = dept_to_detail.get(did)
        if not detail_url:
            tqdm.write(f"[WARN] no detail url for dept_id={did}")
            continue

        try:
            r = session.get(detail_url, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                tqdm.write(f"[WARN] HTTP {r.status_code}: {did} -> {detail_url}")
                continue
            r.encoding = r.apparent_encoding
        except Exception as e:
            tqdm.write(f"[WARN] detail fetch error: {did} -> {e}")
            continue

        header_to_value = parse_first_stage_requirements(r.text)
        rows = build_requirement_rows_for_dept(did, header_to_value)
        results.extend(rows)

        if i % 50 == 0:
            tqdm.write(f"[INFO] processed {i}/{len(target_dept_ids)}")

        time.sleep(SLEEP_SEC)

    out_df = pd.DataFrame(results, columns=[
        "dept_id", "exam_year", "subject_id", "require_level"
    ])

    # 穩定排序
    if not out_df.empty:
        out_df = out_df.sort_values(by=["dept_id", "subject_id"]).reset_index(drop=True)
        out_df.insert(0, "req_id", range(len(out_df)))
    else:
        out_df = pd.DataFrame(columns=["req_id", "dept_id", "exam_year", "subject_id", "require_level"])

    out_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"[DONE] rows={len(out_df)} -> {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
