import re
import csv
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

url = "https://www.cac.edu.tw/cacportal/apply_his_report/114/114_sieve_standard/collegeList.htm"

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
})

retries = Retry(
    total=5,
    backoff_factor=0.6,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)

resp = session.get(url, timeout=20)
resp.encoding = resp.apparent_encoding

soup = BeautifulSoup(resp.text, "html.parser")

pattern = re.compile(r"^\((\d{3})\)(.+)$")

rows = []
for a in soup.find_all("a"):
    text = a.get_text(strip=True)
    m = pattern.match(text)
    if m:
        code = m.group(1)
        name = m.group(2).strip()
        rows.append((code, name))

rows = sorted(set(rows), key=lambda x: x[0])

out_path = "../csv/University.csv"
with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["univ_id", "univ_name"])
    w.writerows(rows)

print(f"{len(rows)}, {out_path}")
