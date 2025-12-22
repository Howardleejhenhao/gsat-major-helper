import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm

MAIN_URL = "https://www.cac.edu.tw/apply114/system/ColQry_114applyXForStu_Fd87eO2q/gsd_search_php.php?part=part_1"
BASE = "https://www.cac.edu.tw/apply114/system/ColQry_114applyXForStu_Fd87eO2q/"
POST_URL = BASE + "ShowGsd.php"

CODE_RE = re.compile(r"\((\d{6})\)")

def build_session():
    s = requests.Session()

    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods={"GET", "POST"},
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)

    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.5",
        "Referer": MAIN_URL,
        "Origin": "https://www.cac.edu.tw",
        "Connection": "keep-alive",
    })

    return s

def parse_result_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    tds = soup.find_all("td", attrs={"title": re.compile("校系名稱及代碼")})
    for td in tds:
        raw_text = td.get_text("\n", strip=True)
        m = CODE_RE.search(raw_text)
        if not m:
            continue

        dept_id = m.group(1)
        univ_id = dept_id[:3]

        cleaned = CODE_RE.sub("", raw_text).strip()
        parts = [p.strip() for p in cleaned.split("\n") if p.strip()]
        department = parts[-1] if parts else ""

        rows.append({
            "dept_id": dept_id,
            "univ_id": univ_id,
            "department": department,
        })

    dedup = {}
    for r in rows:
        dedup[r["dept_id"]] = r
    return list(dedup.values())

def fetch_by_univ_id(s: requests.Session, univ_id: str):
    s.get(MAIN_URL, timeout=20)

    data = {
        "TxtGsdCode": univ_id,
        "SubTxtGsdCode": "依校系代碼查詢",
        "action": "SubTxtGsdCode",
    }

    resp = s.post(POST_URL, data=data, timeout=30)
    resp.raise_for_status()
    return parse_result_html(resp.text)

def main():
    schools = pd.read_csv("../csv/University.csv", dtype={"univ_id": str})
    schools["univ_id"] = schools["univ_id"].str.zfill(3)

    s = build_session()
    all_rows = []

    univ_list = schools["univ_id"].tolist()

    for univ_id in tqdm(univ_list, desc="Fetching departments", unit="univ"):
        try:
            rows = fetch_by_univ_id(s, univ_id)
            rows = [r for r in rows if r["univ_id"] == univ_id]
            all_rows.extend(rows)

            time.sleep(0.4)

        except requests.exceptions.RequestException as e:
            tqdm.write(f"[WARN] {univ_id} failed: {e}")
            time.sleep(1.0)

    df = pd.DataFrame(all_rows).drop_duplicates(subset=["dept_id"])
    df = df.sort_values(["univ_id", "dept_id"]).reset_index(drop=True)

    df.to_csv("../csv/Department.csv", index=False, encoding="utf-8-sig")
    print(f"departments_114.csv（{len(df)} rows）")

if __name__ == "__main__":
    main()
