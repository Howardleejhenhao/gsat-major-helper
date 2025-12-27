import pandas as pd
from pathlib import Path

input_path = Path("../csv/Department.csv")
output_path = Path("../csv/Department_dedup.csv")

df = pd.read_csv(input_path, dtype=str, encoding="utf-8-sig")

df_dedup = df.drop_duplicates(subset=["dept_id"], keep="first")

df_dedup.to_csv(output_path, index=False, encoding="utf-8-sig")

print("原始筆數:", len(df), "dept_id 去重後筆數:", len(df_dedup))
print("輸出檔案:", output_path)
