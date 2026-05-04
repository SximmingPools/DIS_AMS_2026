import csv
from pathlib import Path

import psycopg

from db_exercise.config import ROOT_DIR, database_url


DEFAULT_CSV = ROOT_DIR / "data" / "coffee_sales.csv"


def check_connection() -> str:
    with psycopg.connect(database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("select version(), current_setting('transaction_isolation')")
            version, isolation_level = cur.fetchone()

    return "\n".join(
        [
            "Connected to PostgreSQL",
            f"Isolation level: {isolation_level}",
            version,
        ]
    )


def clean_name(name: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in name).strip("_")


def import_coffee_sales(csv_path: Path = DEFAULT_CSV) -> str:
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        original_columns = reader.fieldnames or []
        columns = [clean_name(column) for column in original_columns]
        rows = list(reader)

    if not columns:
        raise RuntimeError("CSV file has no header row.")

    with psycopg.connect(database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("drop table if exists coffee_sales")
            cur.execute(
                """
                create table coffee_sales (
                    id bigserial primary key,
                    hour_of_day integer not null check (hour_of_day between 0 and 23),
                    cash_type text not null check (cash_type in ('card', 'cash')),
                    money numeric(10, 2) not null check (money >= 0),
                    coffee_name text not null,
                    time_of_day text not null,
                    weekday text not null,
                    month_name text not null,
                    weekdaysort integer not null check (weekdaysort between 1 and 7),
                    monthsort integer not null check (monthsort between 1 and 12),
                    sale_date date not null,
                    sale_time time not null
                )
                """
            )

            placeholders = ", ".join(["%s"] * len(columns))
            insert_sql = (
                "insert into coffee_sales ("
                "hour_of_day, cash_type, money, coffee_name, time_of_day, weekday, "
                "month_name, weekdaysort, monthsort, sale_date, sale_time"
                f") values ({placeholders})"
            )
            for row in rows:
                cur.execute(insert_sql, [row[column] for column in original_columns])

            cur.execute("select count(*) from coffee_sales")
            count = cur.fetchone()[0]

    return "\n".join(
        [
            f"Imported {count} rows into coffee_sales",
            "Next: inspect columns, choose better data types, then add constraints.",
        ]
    )


def show_rows(conn: psycopg.Connection) -> list[tuple[int, str]]:
    with conn.cursor() as cur:
        cur.execute("select id, note from concurrency_demo order by id")
        return cur.fetchall()


def concurrency_demo() -> str:
    output: list[str] = []
    url = database_url()

    conn_a = psycopg.connect(url, autocommit=True)
    conn_b = psycopg.connect(url, autocommit=True)

    try:
        with conn_a.cursor() as cur:
            cur.execute("drop table if exists concurrency_demo")
            cur.execute("create table concurrency_demo (id integer primary key, note text not null)")
            cur.execute("insert into concurrency_demo (id, note) values (1, 'original')")

        conn_a.autocommit = False
        conn_b.autocommit = False

        with conn_a.cursor() as cur:
            cur.execute("insert into concurrency_demo (id, note) values (2, 'inserted by A')")
        with conn_b.cursor() as cur:
            cur.execute("insert into concurrency_demo (id, note) values (3, 'inserted by B')")

        output.append(f"A sees before commit: {show_rows(conn_a)}")
        output.append(f"B sees before commit: {show_rows(conn_b)}")

        conn_a.commit()
        conn_b.commit()

        output.append(f"A sees after commit: {show_rows(conn_a)}")
        output.append(f"B sees after commit: {show_rows(conn_b)}")

        with psycopg.connect(url) as conn_c:
            output.append(f"C sees after both commits: {show_rows(conn_c)}")

        with conn_a.cursor() as cur:
            cur.execute("set lock_timeout = '1500ms'")
        with conn_b.cursor() as cur:
            cur.execute("set lock_timeout = '1500ms'")

        with conn_a.cursor() as cur:
            cur.execute("update concurrency_demo set note = 'updated by A' where id = 1")

        try:
            with conn_b.cursor() as cur:
                cur.execute("update concurrency_demo set note = 'updated by B' where id = 1")
        except psycopg.errors.LockNotAvailable as exc:
            output.append(f"B update failed while A holds the row lock: {exc.__class__.__name__}")
            conn_b.rollback()

        conn_a.commit()
        output.append(f"A sees after update commit: {show_rows(conn_a)}")

        with psycopg.connect(url) as conn_c:
            output.append(f"C sees final contents: {show_rows(conn_c)}")
    finally:
        conn_a.close()
        conn_b.close()

    return "\n".join(output)
