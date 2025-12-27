import csv

INPUT_FILE = "unews_general_university.csv"      # 你的原始輸出檔
OUTPUT_FILE = "unews_general_university_fix.csv" # 補零後的新檔

with open(INPUT_FILE, newline="", encoding="utf-8-sig") as fin, \
     open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as fout:

    reader = csv.reader(fin)
    writer = csv.writer(fout)

    header = next(reader)
    writer.writerow(header)

    for row in reader:
        # 假設 category_id 在最後一欄
        cid = row[-1].strip()

        # 補成 4 位數（101 -> 0101）
        if cid.isdigit():
            row[-1] = cid.zfill(4)

        writer.writerow(row)

print("完成：category_id 已補齊為四位數")
print(f"輸出檔案：{OUTPUT_FILE}")
