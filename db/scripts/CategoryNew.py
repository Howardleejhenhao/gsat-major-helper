import requests
from bs4 import BeautifulSoup
import csv
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_departments(group_internal_id):
    url = f"https://www.unews.com.tw/Search/Group?type=1&group={group_internal_id}&limit=100"
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = []
    for tr in soup.select("table tbody tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        school = tds[0].get_text(strip=True)
        dept = tds[1].get_text(strip=True)
        rows.append((school, dept))
    return rows


def main():
    results = []

    with open("category_internal_map.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row["category_id"]
            group = row["academic_cluster"]
            cname = row["category_name"]
            gid = row["group_internal_id"]

            print(f"爬取：{group} / {cname} (group={gid})")

            for school, dept in fetch_departments(gid):
                results.append([school, dept, group, cname, cid])

            time.sleep(0.3)

    with open("unews_general_university.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["school", "department", "academic_cluster", "category", "category_id"])
        w.writerows(results)

    print(f"\n完成，共 {len(results)} 筆資料")


if __name__ == "__main__":
    main()
