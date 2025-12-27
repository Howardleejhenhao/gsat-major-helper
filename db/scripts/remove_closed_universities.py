import csv

INPUT_FILE = "unews_general_university_with_id.csv"
OUTPUT_FILE = "unews_general_university_clean.csv"

# 要刪除的學校（完全比對）
REMOVED_UNIVS = {
    "中華大學",
    "明道大學(112學年度起停招、113年停辦)(專案輔導至112/5/31)",
    "法鼓文理學院",
    "臺灣首府大學(111學年度起停招、112年停辦)(專案輔導至113/5/31)",
}

removed_count = 0
total = 0

with open(INPUT_FILE, newline="", encoding="utf-8-sig") as fin, \
     open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as fout:

    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        total += 1
        if row["univ_name"] in REMOVED_UNIVS:
            removed_count += 1
            continue
        writer.writerow(row)

print("完成刪除停辦學校資料")
print(f"原始筆數：{total}")
print(f"刪除筆數：{removed_count}")
print(f"輸出檔案：{OUTPUT_FILE}")
