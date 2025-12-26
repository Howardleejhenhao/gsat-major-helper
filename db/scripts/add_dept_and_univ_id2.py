import csv

# ===== 檔案名稱 =====
INPUT_FILE = "unews_general_university_sorted.csv"
OUTPUT_FILE = "unews_general_university_sorted2.csv"
UNIV_FILE = "University_copy.csv"
DEPT_FILE = "Department_copy.csv"

# ===== 讀取 University_copy.csv：univ_name -> univ_id =====
univ_map = {}
with open(UNIV_FILE, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        univ_map[row["univ_name"].strip()] = row["univ_id"].strip()

# ===== 讀取 Department_copy.csv：
# 1) 精確比對：(univ_id, department) -> dept_id
# 2) 前綴展開用：univ_id -> list of (dept_id, department_full)
dept_exact_map = {}
dept_by_univ = {}
with open(DEPT_FILE, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        univ_id = row["univ_id"].strip()
        dept_name = row["department"].strip()
        dept_id = row["dept_id"].strip()

        dept_exact_map[(univ_id, dept_name)] = dept_id
        dept_by_univ.setdefault(univ_id, []).append((dept_id, dept_name))

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
    expanded_count = 0

    for row in reader:
        univ_name = row["univ_name"].strip()
        department = row["department"].strip()

        univ_id = univ_map.get(univ_name, "")
        if not univ_id:
            missing_univ.add(univ_name)

        # 1) 先走精確比對
        dept_id = dept_exact_map.get((univ_id, department), "") if univ_id else ""

        if dept_id:
            writer.writerow({
                "dept_id": dept_id,
                "univ_id": univ_id,
                "univ_name": univ_name,
                "department": department,
                "academic_cluster": row["academic_cluster"],
                "category": row["category"],
                "category_id": row["category_id"],
            })
            continue

        # 2) 精確找不到 dept_id，嘗試「前綴展開」
        #    條件：同 univ_id，且 Department_copy 的 department 以輸入 department 作為前綴
        expanded = []
        if univ_id:
            for did, dname_full in dept_by_univ.get(univ_id, []):
                if dname_full.startswith(department):
                    expanded.append((did, dname_full))

        if expanded:
            # 依 dept_id 升冪輸出（可讀性好）
            expanded.sort(key=lambda x: x[0])
            for did, dname_full in expanded:
                writer.writerow({
                    "dept_id": did,
                    "univ_id": univ_id,
                    "univ_name": univ_name,
                    "department": dname_full,  # 用更細的系名
                    "academic_cluster": row["academic_cluster"],
                    "category": row["category"],
                    "category_id": row["category_id"],
                })
                expanded_count += 1
            continue

        # 3) 仍找不到：保留原列（dept_id 空），並列入 missing_dept
        if univ_id and not dept_id:
            missing_dept.add((univ_name, department))

        writer.writerow({
            "dept_id": "",
            "univ_id": univ_id,
            "univ_name": univ_name,
            "department": department,
            "academic_cluster": row["academic_cluster"],
            "category": row["category"],
            "category_id": row["category_id"],
        })

print("完成：已補上 dept_id 與 univ_id（含前綴展開）")
print(f"輸出檔案：{OUTPUT_FILE}")
print(f"前綴展開新增列數：{expanded_count}")

if missing_univ:
    print("\n⚠️ 找不到 univ_id 的學校：")
    for u in sorted(missing_univ):
        print("  -", u)

if missing_dept:
    print("\n⚠️ 找不到 dept_id 的系所（可能是名稱不完全一致，且無法用前綴展開補齊）：")
    for u, d in sorted(missing_dept):
        print(f"  - {u} / {d}")
