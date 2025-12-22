import pandas as pd

years = [{"exam_year": y} for y in range(111, 116)]

df = pd.DataFrame(years)
df.to_csv("../csv/EaxmYear.csv", index=False, encoding="utf-8-sig")

print(df)
