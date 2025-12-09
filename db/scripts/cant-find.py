import re
import pandas as pd

LOG_PATH = "get-requirement-score.txt"   # 你的 log
DEPT_PATH = "../csv/Department_ori.csv"  # 你的科系表（含 dept_id, univ_id, department）
UNIV_PATH = "../csv/University.csv"       # 你的學校表（univ_id, univ_name）
OUT_PATH = "Dept_404_list.csv"

def normalize_dept_id(x):
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if s.isdigit():
        return s.zfill(6)
    return s

def normalize_univ_id(x):
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if s.isdigit():
        return s.zfill(3)
    return s

# 1) 讀 log，抓出 404 dept_id
with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

dept_ids = sorted(set(re.findall(r"HTTP 404:\s*(\d{6})", text)))

df_404 = pd.DataFrame({"dept_id": dept_ids})
df_404["dept_id"] = df_404["dept_id"].apply(normalize_dept_id)

# 2) 讀科系表
dept_df = pd.read_csv(DEPT_PATH)
dept_df["dept_id"] = dept_df["dept_id"].apply(normalize_dept_id)

if "univ_id" in dept_df.columns:
    dept_df["univ_id"] = dept_df["univ_id"].apply(normalize_univ_id)

# 3) 讀學校表
univ_df = pd.read_csv(UNIV_PATH)
univ_df["univ_id"] = univ_df["univ_id"].apply(normalize_univ_id)

# 4) 先把科系表補上 univ_name
dept_with_univ = dept_df.merge(
    univ_df[["univ_id", "univ_name"]],
    on="univ_id",
    how="left"
)

# 5) 用 404 dept_id 去對照科系 + 校名
merged = df_404.merge(
    dept_with_univ[["dept_id", "univ_id", "univ_name", "department"]],
    on="dept_id",
    how="left"
)

# 6) 組出「學校/科系名」
def make_school_dept(row):
    school = row.get("univ_name")
    dept = row.get("department")
    if pd.notna(school) and pd.notna(dept):
        return f"{school}/{dept}"
    if pd.notna(dept):
        return str(dept)
    if pd.notna(school):
        return str(school)
    return None

merged["學校/科系"] = merged.apply(make_school_dept, axis=1)

# 7) 輸出你要的欄位
out = merged[["dept_id", "學校/科系"]]

out.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print(f"[DONE] {OUT_PATH} rows={len(out)}")
print(out.head(20))
