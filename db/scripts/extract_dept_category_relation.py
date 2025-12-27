import csv

INPUT_FILE = "unews_general_university_sorted.csv"
OUTPUT_FILE = "dept_category_relation.csv"

with open(INPUT_FILE, newline="", encoding="utf-8-sig") as fin:
    reader = csv.DictReader(fin)

    rows = []
    for row in reader:
        rows.append({
            "dept_id": row["dept_id"].strip(),
            "univ_id": row["univ_id"].strip(),
            "dept_name": row["department"].strip(),
            "category_id": row["category_id"].strip(),
        })

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as fout:
    fieldnames = ["dept_id", "univ_id", "dept_name", "category_id"]
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("完成欄位精簡")
print(f"輸入檔案：{INPUT_FILE}")
print(f"輸出檔案：{OUTPUT_FILE}")
print(f"總筆數：{len(rows)}")
