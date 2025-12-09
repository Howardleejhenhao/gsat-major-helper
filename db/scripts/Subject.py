import pandas as pd
from itertools import combinations

subjects = [
    {"subject_id": 0, "subject_name": "國文"},
    {"subject_id": 1, "subject_name": "英文"},
    {"subject_id": 2, "subject_name": "數學A"},
    {"subject_id": 3, "subject_name": "數學B"},
    {"subject_id": 4, "subject_name": "社會"},
    {"subject_id": 5, "subject_name": "自然"},
]

base_df = pd.DataFrame(subjects).sort_values("subject_id").reset_index(drop=True)
base_names = base_df["subject_name"].tolist()

combo_rows = []
next_id = int(base_df["subject_id"].max()) + 1

sep = "+"

for r in range(2, len(base_names) + 1):
    for idxs in combinations(range(len(base_names)), r):
        combo_name = sep.join(base_names[i] for i in idxs)
        combo_rows.append({
            "subject_id": next_id,
            "subject_name": combo_name
        })
        next_id += 1

combo_df = pd.DataFrame(combo_rows)
out_df = pd.concat([base_df, combo_df], ignore_index=True)
out_df.to_csv("../csv/Subject.csv", index=False, encoding="utf-8-sig")

print(out_df)
print(f"原始科目數: {len(base_df)}")
print(f"新增組合數(2科以上): {len(combo_df)}")
print(f"總筆數: {len(out_df)}")