import pandas as pd

input_path = "../csv/department_category/Department_category_chinese_v1.csv" # TODO
output_path = "../csv/department_category/Category.csv" # TODO


df = pd.read_csv(input_path)

tags = set()

for cell in df["category"].dropna().astype(str):
    for tag in cell.split(";"):
        tag = tag.strip()
        if tag:
            tags.add(tag)

unique_tags = sorted(tags)

category_map = pd.DataFrame({
    "category_id": range(1, len(unique_tags) + 1),
    "category_name": unique_tags
})

category_map.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"Done! total tags: {len(category_map)}")
