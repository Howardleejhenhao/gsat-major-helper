import csv

# ===== 檔案名稱 =====
INPUT_FILE = "unews_general_university_fix.csv"
OUTPUT_FILE = "unews_general_university_with_id.csv"
UNIV_FILE = "University_copy.csv"
DEPT_FILE = "Department_copy.csv"

# ===== 讀取 University.csv：univ_name -> univ_id =====
univ_map = {}
with open(UNIV_FILE, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        univ_map[row["univ_name"].strip()] = row["univ_id"].strip()

# ===== 讀取 Department_ori.csv：(univ_id, department) -> dept_id =====
dept_map = {}
with open(DEPT_FILE, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row["univ_id"].strip(), row["department"].strip())
        dept_map[key] = row["dept_id"].strip()

# ===== 主處理 =====
with open(INPUT_FILE, newline="", encoding="utf-8-sig") as fin, \
     open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as fout:

    reader = csv.DictReader(fin)
    fieldnames = [
        "dept_id",
        "univ_id",
        "univ_name",
        "department",
        "academic_cluster",
        "category",
        "category_id",
    ]
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()

    missing_univ = set()
    missing_dept = set()

    for row in reader:
        univ_name = row["univ_name"].strip()
        department = row["department"].strip()

        univ_id = univ_map.get(univ_name, "")
        if not univ_id:
            missing_univ.add(univ_name)

        dept_id = dept_map.get((univ_id, department), "")
        if univ_id and not dept_id:
            missing_dept.add((univ_name, department))

        writer.writerow({
            "dept_id": dept_id,
            "univ_id": univ_id,
            "univ_name": univ_name,
            "department": department,
            "academic_cluster": row["academic_cluster"],
            "category": row["category"],
            "category_id": row["category_id"],
        })

# ===== 訊息輸出 =====
print("完成：已補上 dept_id 與 univ_id")
print(f"輸出檔案：{OUTPUT_FILE}")

if missing_univ:
    print("\n⚠️ 找不到 univ_id 的學校：")
    for u in sorted(missing_univ):
        print("  -", u)

if missing_dept:
    print("\n⚠️ 找不到 dept_id 的系所（可能是名稱不完全一致）：")
    for u, d in sorted(missing_dept):
        print(f"  - {u} / {d}")
