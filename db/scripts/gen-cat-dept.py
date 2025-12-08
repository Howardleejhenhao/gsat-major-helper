import pandas as pd

# ======TODO=====
input_path = "Department_category_chinese_v1.csv"
map_path = "Category.csv"
output_path = "Department.csv"
# ===============

df = pd.read_csv(input_path)

tags = set()

for cell in df.get("category", pd.Series(dtype=object)).dropna().astype(str):
    for tag in cell.split(";"):
        tag = tag.strip()
        if tag:
            tags.add(tag)

unique_tags = sorted(tags)

category_map = pd.DataFrame({
    "category_id": range(1, len(unique_tags) + 1),
    "category_name": unique_tags
})

category_map.to_csv(map_path, index=False, encoding="utf-8-sig")
print(f"Category map done! total tags: {len(category_map)} -> {map_path}")

name_to_id = dict(zip(
    category_map["category_name"].astype(str),
    category_map["category_id"]
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
    return ",".join(ids)

if "category" in df.columns:
    df["category"] = df["category"].apply(category_names_to_ids)
else:
    print("Warning: input file has no 'category' column.")

df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"Department file done! -> {output_path}")
