import csv

# ====== 路徑設定 ======
INPUT_CSV = "../csv/Category.csv"
OUTPUT_CSV = "split_category.csv"

with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))

# 用 dict 依 category_id 去重
category_map = {}

for row in rows[1:]:
    if len(row) < 6:
        continue

    category_id = row[5].strip()
    group = row[3].strip()
    category = row[4].strip()

    # 同一 category_id 只保留第一筆
    if category_id not in category_map:
        category_map[category_id] = [category_id, group, category]

# ====== 依 category_id 由小到大排序 ======
sorted_categories = sorted(
    category_map.values(),
    key=lambda x: int(x[0])  # x[0] 是 category_id
)

# ====== 寫出 CSV ======
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["category_id", "學群", "學類"])
    writer.writerows(sorted_categories)

print("✅ category.csv 產生完成（已去重＋排序）")
print(f"📤 輸出路徑：{OUTPUT_CSV}")
