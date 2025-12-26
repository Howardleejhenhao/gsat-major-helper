import csv

INPUT_FILE = "unews_general_university_sorted2.csv"
OUTPUT_FILE = "unews_general_university_sorted.csv"

with open(INPUT_FILE, newline="", encoding="utf-8-sig") as fin:
    reader = csv.DictReader(fin)
    rows = list(reader)
    fieldnames = reader.fieldnames

# 排序：先 univ_id，再 dept_id（都用字串即可，因為已補零）
rows.sort(key=lambda r: (r["univ_id"], r["dept_id"]))

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as fout:
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("排序完成")
print(f"輸入檔案：{INPUT_FILE}")
print(f"輸出檔案：{OUTPUT_FILE}")
print(f"總筆數：{len(rows)}")
