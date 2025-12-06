import pandas as pd

subjects = [
    {"subject_id": 0, "subject_name": "國文"},
    {"subject_id": 1, "subject_name": "英文"},
    {"subject_id": 2, "subject_name": "數學A"},
    {"subject_id": 3, "subject_name": "數學B"},
    {"subject_id": 4, "subject_name": "社會"},
    {"subject_id": 5, "subject_name": "自然"},
]

df = pd.DataFrame(subjects)
df.to_csv("../csv/Subject.csv", index=False, encoding="utf-8-sig")
print(df)
