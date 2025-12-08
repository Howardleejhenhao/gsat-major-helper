import pandas as pd

dept_path = "../csv/department_category/Department_category_chinese_v1.csv" # TODO
map_path = "../csv/department_category/Category.csv" # TODO
output_path = "../csv/department_category/Department.csv" # TODO

df = pd.read_csv(dept_path)
cat_map = pd.read_csv(map_path)

name_to_id = dict(zip(
    cat_map["category_name"].astype(str),
    cat_map["category_id"]
))

def category_names_to_ids(cell):
    if pd.isna(cell):
        return ""
    tags = [t.strip() for t in str(cell).split(";") if t.strip()]
    ids = []
    missing = []

    for t in tags:
        if t in name_to_id:
            ids.append(str(name_to_id[t]))
        else:
            missing.append(t)

    # 如果你想遇到缺 mapping 就直接報錯，把下面兩行取消註解
    # if missing:
    #     raise ValueError(f"Missing tags in mapping: {missing}")

    return ",".join(ids)

# 轉換 category 欄位
df["category"] = df["category"].apply(category_names_to_ids)

# 輸出
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("Done!")
