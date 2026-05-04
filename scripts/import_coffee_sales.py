import argparse
import csv
import sys
from pathlib import Path

import psycopg

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import database_url


def clean_name(name: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in name).strip("_")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()

    with args.csv_file.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = [clean_name(column) for column in (reader.fieldnames or [])]
        rows = list(reader)

    if not columns:
        raise RuntimeError("CSV file has no header row.")

    with psycopg.connect(database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("drop table if exists coffee_sales")
            column_sql = ", ".join(f"{column} text" for column in columns)
            cur.execute(f"create table coffee_sales (id bigserial primary key, {column_sql})")

            placeholders = ", ".join(["%s"] * len(columns))
            insert_sql = f"insert into coffee_sales ({', '.join(columns)}) values ({placeholders})"
            for row in rows:
                cur.execute(insert_sql, [row[value] for value in reader.fieldnames or []])

            cur.execute("select count(*) from coffee_sales")
            count = cur.fetchone()[0]

    print(f"Imported {count} rows into coffee_sales")
    print("Next: inspect columns, choose better data types, then add constraints.")


if __name__ == "__main__":
    main()

