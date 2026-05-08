import csv
import sys
from pathlib import Path

import psycopg
from psycopg import sql

sys.path.append(str(Path(__file__).resolve().parents[1]))

from db_exercise.config import ROOT_DIR, database_url


DEFAULT_CSV = ROOT_DIR / "data" / "coffee_sales.csv"


def inspect_csv(csv_path: Path, sample_size: int = 3) -> tuple[list[str], list[dict[str, str]], int]:
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = reader.fieldnames or []
        sample_rows: list[dict[str, str]] = []
        row_count = 0

        for row in reader:
            row_count += 1
            if len(sample_rows) < sample_size:
                sample_rows.append(row)

    return columns, sample_rows, row_count


def log(output: list[str], step: str, message: str) -> None:
    output.append(f"{step}: {message}")


def normalized_schema_visualization() -> list[str]:
    return [
        "Normalized table structure",
        "",
        "+-------------------------+",
        "| coffee_products         |",
        "+-------------------------+",
        "| PK coffee_id            |",
        "| UQ coffee_name          |",
        "+-------------------------+",
        "            ^",
        "            | FK coffee_id",
        "            |",
        "+-------------------------+          +-------------------------+",
        "| coffee_sales_normalized |          | calendar_days           |",
        "+-------------------------+          +-------------------------+",
        "| PK sale_id              |          | PK sale_date            |",
        "| FK coffee_id            |          | weekday                 |",
        "| FK sale_date            |--------->| weekdaysort             |",
        "| sale_time               | FK date  | month_name              |",
        "| hour_of_day             |          | monthsort               |",
        "| time_of_day             |          +-------------------------+",
        "| cash_type               |",
        "| money                   |",
        "+-------------------------+",
        "",
        "Original CSV table kept for comparison",
        "",
        "+-------------------------+",
        "| coffee_sales            |",
        "+-------------------------+",
        "| PK sale_id              |",
        "| hour_of_day             |",
        "| cash_type               |",
        "| money                   |",
        "| coffee_name             |",
        "| time_of_day             |",
        "| weekday                 |",
        "| month_name              |",
        "| weekdaysort             |",
        "| monthsort               |",
        "| sale_date               |",
        "| sale_time               |",
        "+-------------------------+",
    ]


def main() -> None:
    output: list[str] = []
    csv_path = DEFAULT_CSV
    columns, sample_rows, csv_row_count = inspect_csv(csv_path)
    url = database_url()

    # i
    log(output, "i", f"Using Coffee Sales CSV file: {csv_path}")
    log(output, "i", f"CSV rows: {csv_row_count}")
    log(output, "i", f"CSV columns: {', '.join(columns)}")
    if sample_rows:
        sample = ", ".join(f"{name}={sample_rows[0][name]}" for name in columns)
        log(output, "i", f"First sample row: {sample}")

    # ii
    log(output, "ii", "Identified missing primary key: the CSV has no stable id column.")
    log(output, "ii", "Useful checks: hour_of_day 0..23, cash_type in card/cash, money >= 0.")
    log(output, "ii", "Useful checks: weekdaysort 1..7, monthsort 1..12, date/time typed and not null.")
    log(output, "ii", "Repeated coffee names and calendar fields should be normalized.")

    with psycopg.connect(url, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            # iii
            cur.execute("drop table if exists coffee_sales_normalized")
            cur.execute("drop table if exists coffee_sales")
            cur.execute("drop table if exists coffee_products")
            cur.execute("drop table if exists calendar_days")

            cur.execute(
                """
                create table coffee_sales (
                    sale_id bigserial primary key,
                    hour_of_day integer not null check (hour_of_day between 0 and 23),
                    cash_type text not null check (cash_type in ('card', 'cash')),
                    money numeric(10, 2) not null check (money >= 0),
                    coffee_name text not null check (length(coffee_name) > 0),
                    time_of_day text not null check (length(time_of_day) > 0),
                    weekday text not null check (length(weekday) > 0),
                    month_name text not null check (length(month_name) > 0),
                    weekdaysort integer not null check (weekdaysort between 1 and 7),
                    monthsort integer not null check (monthsort between 1 and 12),
                    sale_date date not null,
                    sale_time time not null
                )
                """
            )

            copy_columns = [
                "hour_of_day",
                "cash_type",
                "money",
                "coffee_name",
                "time_of_day",
                "weekday",
                "month_name",
                "weekdaysort",
                "monthsort",
                "sale_date",
                "sale_time",
            ]
            copy_sql = sql.SQL("copy coffee_sales ({}) from stdin with (format csv, header true)").format(
                sql.SQL(", ").join(sql.Identifier(column) for column in copy_columns)
            )
            with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
                with cur.copy(copy_sql) as copy:
                    for chunk in iter(lambda: csv_file.read(8192), ""):
                        copy.write(chunk)

            cur.execute("select count(*) from coffee_sales")
            inserted_count = cur.fetchone()[0]
            cur.execute(
                """
                select
                    min(sale_date),
                    max(sale_date),
                    count(distinct coffee_name),
                    count(distinct sale_date)
                from coffee_sales
                """
            )
            min_date, max_date, coffee_count, date_count = cur.fetchone()
            cur.execute(
                """
                select sale_id, sale_date, sale_time, coffee_name, cash_type, money
                from coffee_sales
                order by sale_id
                limit 3
                """
            )
            sample_inserted_rows = cur.fetchall()

            log(output, "iii", "Created coffee_sales with explicit PostgreSQL data types.")
            log(output, "iii", "Imported the CSV automatically through PostgreSQL COPY from Python.")
            log(output, "iii", f"Inserted rows: {inserted_count}")
            log(output, "iii", f"Date range: {min_date} to {max_date}")
            log(output, "iii", f"Distinct coffee names: {coffee_count}")
            log(output, "iii", f"Sample inserted rows: {sample_inserted_rows}")

            # iv
            log(output, "iv", "Primary key, NOT NULL, and CHECK constraints were created with coffee_sales.")
            log(output, "iv", "The generated sale_id column is the primary key added because the CSV has none.")

            # v
            cur.execute(
                """
                create table coffee_products (
                    coffee_id bigserial primary key,
                    coffee_name text not null unique check (length(coffee_name) > 0)
                )
                """
            )
            cur.execute(
                """
                insert into coffee_products (coffee_name)
                select distinct coffee_name
                from coffee_sales
                order by coffee_name
                """
            )

            cur.execute(
                """
                create table calendar_days (
                    sale_date date primary key,
                    weekday text not null check (length(weekday) > 0),
                    weekdaysort integer not null check (weekdaysort between 1 and 7),
                    month_name text not null check (length(month_name) > 0),
                    monthsort integer not null check (monthsort between 1 and 12)
                )
                """
            )
            cur.execute(
                """
                insert into calendar_days (sale_date, weekday, weekdaysort, month_name, monthsort)
                select sale_date, min(weekday), min(weekdaysort), min(month_name), min(monthsort)
                from coffee_sales
                group by sale_date
                order by sale_date
                """
            )

            cur.execute(
                """
                create table coffee_sales_normalized (
                    sale_id bigint primary key,
                    coffee_id bigint not null references coffee_products(coffee_id),
                    sale_date date not null references calendar_days(sale_date),
                    sale_time time not null,
                    hour_of_day integer not null check (hour_of_day between 0 and 23),
                    time_of_day text not null check (length(time_of_day) > 0),
                    cash_type text not null check (cash_type in ('card', 'cash')),
                    money numeric(10, 2) not null check (money >= 0)
                )
                """
            )
            cur.execute(
                """
                insert into coffee_sales_normalized (
                    sale_id,
                    coffee_id,
                    sale_date,
                    sale_time,
                    hour_of_day,
                    time_of_day,
                    cash_type,
                    money
                )
                select
                    s.sale_id,
                    p.coffee_id,
                    s.sale_date,
                    s.sale_time,
                    s.hour_of_day,
                    s.time_of_day,
                    s.cash_type,
                    s.money
                from coffee_sales s
                join coffee_products p on p.coffee_name = s.coffee_name
                """
            )

            cur.execute("select count(*) from coffee_products")
            product_count = cur.fetchone()[0]
            cur.execute("select count(*) from calendar_days")
            day_count = cur.fetchone()[0]
            cur.execute("select count(*) from coffee_sales_normalized")
            normalized_sale_count = cur.fetchone()[0]
            cur.execute(
                """
                select count(*)
                from coffee_sales_normalized s
                left join coffee_products p on p.coffee_id = s.coffee_id
                left join calendar_days d on d.sale_date = s.sale_date
                where p.coffee_id is null or d.sale_date is null
                """
            )
            orphan_count = cur.fetchone()[0]
            log(output, "v", f"Found redundancy: {inserted_count} sales contain {coffee_count} distinct coffee names.")
            log(output, "v", f"Found redundancy: {inserted_count} sales contain {date_count} distinct dates.")
            log(output, "v", "Moved coffee names to coffee_products and dates/week/month data to calendar_days.")
            log(output, "v", "Created coffee_sales_normalized with foreign keys to both normalized tables.")
            log(output, "v", f"coffee_products rows: {product_count}")
            log(output, "v", f"calendar_days rows: {day_count}")
            log(output, "v", f"coffee_sales_normalized rows: {normalized_sale_count}")
            log(output, "v", f"Foreign-key orphan check: {orphan_count}")
            output.extend(
                [
                    "",
                    *normalized_schema_visualization(),
                ]
            )

    print("\n".join(output))


if __name__ == "__main__":
    main()
