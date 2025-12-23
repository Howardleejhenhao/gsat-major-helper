import argparse
import csv
import os
from pathlib import Path
from typing import List, Optional

import psycopg2
from psycopg2 import sql

def read_csv_header(csv_path: Path) -> List[str]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            raise ValueError(f"csv no header: {csv_path}")
        header = [h.strip() for h in header if h is not None]
        if not all(header):
            raise ValueError(f"csv has none attribute: {csv_path} -> {header}")
        return header

def table_exists(conn, schema, table) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
              SELECT 1
              FROM information_schema.tables
              WHERE table_schema = %s AND table_name = %s
            );
            """,
            (schema, table),
        )
        return bool(cur.fetchone()[0])

def import_one_csv(
    conn,
    csv_path: Path,
    schema: str,
    table: str,
    truncate: bool,
    delimiter: str = ',',
    null_str: str = "",
) -> None:
    if not table_exists(conn, schema, table):
        print(f"[SKIP] table does not exist: {schema}.{table} ({csv_path.name})")
        return
    
    columns = read_csv_header(csv_path)

    with conn.cursor() as cur:
        if truncate:
            cur.execute(
                sql.SQL("TRUNCATE TABLE {}.{} RESTART IDENTITY CASCADE;").format(
                    sql.Identifier(schema),
                    sql.Identifier(table),
                )
            )
        copy_stmt = sql.SQL(
            "COPY {}.{} ({}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, DELIMITER {}, NULL {});"
        ).format(
            sql.Identifier(schema),
            sql.Identifier(table),
            sql.SQL(", ").join(sql.Identifier(c) for c in columns),
            sql.Literal(delimiter),
            sql.Literal(null_str),
        )

        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            cur.copy_expert(copy_stmt.as_string(conn), f)

    print(f"[OK] import success: {csv_path.name} -> {schema}.{table} (columns={len(columns)}) ")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv-dir", required=True)
    parser.add_argument("--host", default=os.getenv("PGHOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PGPORT", "5432")))
    parser.add_argument("--db", default=os.getenv("PGDATABASE", "appdb"))
    parser.add_argument("--user", default=os.getenv("PGUSER", "app"))
    parser.add_argument("--password", default=os.getenv("PGPASSWORD", "apppw"))
    parser.add_argument("--schema", default=os.getenv("PGSCHEMA", "public"))
    parser.add_argument("--truncate", action="store_true")
    parser.add_argument("--delimiter", default=",")
    
    args = parser.parse_args()

    csv_dir = Path(args.csv_dir).resolve()
    if not csv_dir.exists() or not csv_dir.is_dir():
        raise SystemError(f"not exist this folder: {csv_dir}")
    
    csv_files = list(csv_dir.glob("*.csv"))

    ORDER = [
        "university",
        "category",
        "subject",
        "examyear",
        "standardlevel",
        "subjectperformance",
        "department",
        "admissionrecord",
        "subjectcombination",
        "combinationdetail",
        "examrequirement",
    ]

    rank = {name: i for i, name in enumerate(ORDER)}

    csv_files.sort(key=lambda p: (rank.get(p.stem.lower(), 10_000), p.stem.lower()))


    conn = psycopg2.connect(
        host=args.host,
        port=args.port,
        dbname=args.db,
        user=args.user,
        password=args.password,
    )
    conn.autocommit = False

    try:
        for csv_path in csv_files:
            table = csv_path.stem.lower()
            import_one_csv(
                conn=conn,
                csv_path=csv_path,
                schema=args.schema,
                table=table,
                truncate=args.truncate,
                delimiter=args.delimiter,
            )
        conn.commit()
        print("[DONE] all the csv files has been import")
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()