import csv

# ====== 路徑設定 ======
INPUT_CSV = "../csv/Category.csv"
OUTPUT_CSV = "split_department.csv"

with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))

# 新表表頭
new_rows = [["dept_id", "univ_id", "department", "category_id"]]

for row in rows[1:]:
    if len(row) < 6:
        continue

    new_rows.append([
        row[0],  # dept_id
        row[1],  # univ_id
        row[2],  # department
        row[5]   # category_id
    ])

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(new_rows)

print("✅ department.csv 產生完成")
print(f"📤 輸出路徑：{OUTPUT_CSV}")
