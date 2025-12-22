import pandas as pd

INPUT_CSV = "../csv/ExamRequirement.csv"

df = pd.read_csv(INPUT_CSV)
df.insert(0, "req_id", range(len(df)))
df.to_csv(INPUT_CSV, index=False, encoding="utf-8-sig")

print(f"[DONE] overwritten {INPUT_CSV} rows={len(df)}")
