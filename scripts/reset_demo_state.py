import sys
from pathlib import Path

import psycopg
from pymongo import MongoClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import ROOT_DIR, database_url, mongodb_url
from sync_recipes_to_mongodb import MONGO_COLLECTION, MONGO_DATABASE


OUTPUT_DIR = ROOT_DIR / "output"


def reset_postgres(output: list[str]) -> None:
    tables = [
        "daily_ingredient_usage",
        "coffee_sales_normalized",
        "calendar_days",
        "coffee_products",
        "coffee_sales",
        "exercise_1_b_demo",
        "concurrency_demo",
    ]

    with psycopg.connect(database_url(), connect_timeout=3) as conn:
        with conn.cursor() as cur:
            for table in tables:
                cur.execute(f"drop table if exists {table} cascade")
                output.append(f"PostgreSQL: dropped {table} (if present).")


def reset_mongodb(output: list[str]) -> None:
    client = MongoClient(mongodb_url(), serverSelectionTimeoutMS=2500, connectTimeoutMS=2500)
    try:
        collection = client[MONGO_DATABASE][MONGO_COLLECTION]
        result = collection.delete_many({})
        output.append(
            f"MongoDB: cleared {result.deleted_count} recipe document(s) from {MONGO_DATABASE}.{MONGO_COLLECTION}."
        )
    finally:
        client.close()


def reset_output_files(output: list[str]) -> None:
    deleted = 0
    for png_file in OUTPUT_DIR.glob("*.png"):
        png_file.unlink(missing_ok=True)
        deleted += 1
    output.append(f"Output: deleted {deleted} plot file(s).")


def main() -> None:
    output: list[str] = []
    reset_postgres(output)
    reset_mongodb(output)
    reset_output_files(output)
    output.append("Browser action history will be cleared by the UI after this reset.")
    print("\n".join(output))


if __name__ == "__main__":
    main()
