import pandas as pd

SUBJECT_MAP = {
    "國文": 0,
    "英文": 1,
    "數學A": 2,
    "數學B": 3,
    "社會": 4,
    "自然": 5,
}

STD_MAP = {
    "頂標": "top",
    "前標": "high",
    "均標": "avg",
    "後標": "low",
    "底標": "bottom",
}

STD_ORDER_FALLBACK = ["頂標", "前標", "均標", "後標", "底標"]


def parse_standard_table(path: str, out_csv: str):
    raw = pd.read_excel(path, sheet_name=0, header=None)

    subj_row_idx = 1
    subj_row = raw.iloc[subj_row_idx]
    subject_value_cols = []
    for col_idx, val in enumerate(subj_row.tolist()):
        s = str(val).strip() if pd.notna(val) else ""
        if s in SUBJECT_MAP:
            subject_value_cols.append((s, col_idx))

    subject_cols = []
    for subj_name, val_col in subject_value_cols:
        label_col = val_col - 1
        if label_col < 0:
            continue
        subject_cols.append({
            "subject": subj_name,
            "subject_id": SUBJECT_MAP[subj_name],
            "label_col": label_col,
            "value_col": val_col
        })

    year_starts = []
    for r in range(len(raw)):
        v = raw.iat[r, 0]  # A 欄
        try:
            y = int(str(v).strip())
        except Exception:
            continue
        if y in (111, 112, 113, 114):
            year_starts.append((r, y))


    records = []

    for start_r, year in year_starts:
        block = raw.iloc[start_r:start_r + 5].copy()

        std_labels = []
        first_label_col = subject_cols[0]["label_col"]
        for i in range(len(block)):
            lv = block.iat[i, first_label_col] if first_label_col < block.shape[1] else None
            lab = str(lv).strip() if pd.notna(lv) else ""
            std_labels.append(lab)

        if not all(l in STD_MAP for l in std_labels):
            std_labels = STD_ORDER_FALLBACK

        for sc in subject_cols:
            subj_id = sc["subject_id"]
            val_col = sc["value_col"]
            label_col = sc["label_col"]

            row_values = {}

            for i, std_zh in enumerate(std_labels):
                std_en = STD_MAP.get(std_zh)
                if not std_en:
                    continue

                value = block.iat[i, val_col] if val_col < block.shape[1] else None
                try:
                    value_num = float(value)
                    if value_num.is_integer():
                        value_num = int(value_num)
                except Exception:
                    value_num = None

                row_values[std_en] = value_num

            records.append({
                "exam_year": year,
                "subject_id": subj_id,
                "top": row_values.get("top"),
                "high": row_values.get("high"),
                "avg": row_values.get("avg"),
                "low": row_values.get("low"),
                "bottom": row_values.get("bottom"),
            })

    df = pd.DataFrame(records)

    df = df.drop_duplicates(subset=["exam_year", "subject_id"], keep="first")

    df["std_id"] = df["exam_year"].astype(int).astype(str) + "_" + df["subject_id"].astype(int).astype(str)

    df = df[["std_id", "exam_year", "subject_id", "top", "high", "avg", "low", "bottom"]]
    df = df.sort_values(["exam_year", "subject_id"]).reset_index(drop=True)

    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"{out_csv}, {len(df)} ")


if __name__ == "__main__":
    parse_standard_table(
        path="../source/各科成績標準一覽表114.xls",
        out_csv="../csv/StandardLevel.csv",
    )
