import re
import csv
import time
import random
import os
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin
from tqdm import tqdm  # ✅ 加這行

# 115 入口（需要按按鈕的那頁）
start_url = "https://www.cac.edu.tw/apply115/system/ColQry_115xappLyfOrStu_Azd5gP29/school_search.htm"
post_url = urljoin(start_url, "ShowSchool.php")

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": start_url,
    "Origin": "https://www.cac.edu.tw",
})

retries = Retry(
    total=5,
    backoff_factor=0.6,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)

# ===== Step 1: 抓 115 學校清單（依學校名稱查詢）=====
payload = {
    "option": "SCHNAME",
    "SubSchName": "依學校名稱查詢",
}
resp = session.post(post_url, data=payload, timeout=20)
resp.encoding = resp.apparent_encoding
soup = BeautifulSoup(resp.text, "html.parser")

univ_pattern = re.compile(r"^\((\d{3})\)(.+)$")

universities = []
for a in soup.find_all("a"):
    text = a.get_text(strip=True)
    m = univ_pattern.match(text)
    if not m:
        continue

    univ_id = m.group(1)
    univ_name = m.group(2).strip()
    href = a.get("href", "").strip()
    if not href:
        continue

    univ_url = urljoin(post_url, href)
    universities.append((univ_id, univ_name, univ_url))

# 去重
tmp = {}
for uid, uname, uurl in universities:
    tmp[uid] = (uid, uname, uurl)
universities = [tmp[k] for k in sorted(tmp.keys())]

print(f"universities: {len(universities)}")

# ===== Step 2: 逐校抓科系 =====
dept_code_pat = re.compile(r"\((\d{6})\)")

rows = []

# ✅ tqdm 包住 universities
for univ_id, univ_name, univ_url in tqdm(
    universities,
    desc="Fetching departments",
    unit="univ"
):
    time.sleep(random.uniform(0.2, 0.6))

    r = session.get(univ_url, timeout=20)
    r.encoding = r.apparent_encoding
    s = BeautifulSoup(r.text, "html.parser")

    table = s.find("table")
    if not table:
        continue

    trs = table.find_all("tr")
    if not trs:
        continue

    for tr in trs[1:]:
        tds = tr.find_all("td")
        if not tds:
            continue

        first_td = tds[0]
        cell_text = first_td.get_text(separator="\n", strip=True)

        m = dept_code_pat.search(cell_text)
        if not m:
            continue
        dept_id = m.group(1)

        lines = [ln.strip() for ln in cell_text.split("\n") if ln.strip()]
        clean = []
        for ln in lines:
            if dept_code_pat.search(ln):
                continue
            if univ_name in ln:
                continue
            clean.append(ln)

        department = clean[0] if clean else cell_text.replace(univ_name, "").strip()

        rows.append((dept_id, univ_id, department))

rows = sorted(set(rows), key=lambda x: x[0])

# ===== Step 3: 輸出 CSV =====
out_dir = "../csv"
os.makedirs(out_dir, exist_ok=True)  # ✅ 避免資料夾不存在

out_path = os.path.join(out_dir, "Department_ori_115.csv")
with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["dept_id", "univ_id", "department"])
    w.writerows(rows)

print(f"departments: {len(rows)}, {out_path}")
