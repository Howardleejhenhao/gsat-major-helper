import csv

# ====== 設定檔案路徑 ======
INPUT_CSV_PATH = "../csv/Category.csv"     # 原始資料
OUTPUT_CSV_PATH = "output.csv"   # 修正後輸出

# ====== 讀取 CSV ======
with open(INPUT_CSV_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))

# ====== 處理資料 ======
new_rows = []

# 保留表頭
header = rows[0]
new_rows.append(header)

for row in rows[1:]:
    # 防呆：如果欄位數不足，直接跳過
    if len(row) < 5:
        continue

    # 第 4 欄（index 3）是「學群」
    field = row[3].strip()

    # 如果沒有 '-'，代表本來就是正常資料
    if '-' not in field:
        new_rows.append(row)
        continue

    # 統一破折號（避免全形符號）
    field = field.replace('—', '-')

    # 拆成 學群 / 學類
    group, category = field.split('-', 1)

    # 組成正確 6 欄格式
    fixed_row = [
        row[0],            # dept_id
        row[1],            # univ_id
        row[2],            # department
        group.strip(),     # 學群
        category.strip(),  # 學類
        row[4].strip()     # category_id
    ]

    new_rows.append(fixed_row)

# ====== 寫回 CSV ======
with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(new_rows)

print("✅ CSV 修正完成")
print(f"📥 輸入檔案：{INPUT_CSV_PATH}")
print(f"📤 輸出檔案：{OUTPUT_CSV_PATH}")
