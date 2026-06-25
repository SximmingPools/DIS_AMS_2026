import sys
from collections import defaultdict
from pathlib import Path

import psycopg
from pymongo import MongoClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import database_url, mongodb_url


MONGO_DATABASE = "dis_ams_nosql"
MONGO_COLLECTION = "coffee_recipes"


def normalize_ingredient(item: str, unit: str) -> tuple[str, str, float]:
    if item == "Milk or water":
        return "Milk", "ml", 1.0

    if item == "Espresso":
        return "Espresso", "shots", 1.0

    return item, unit, 1.0


def load_recipes_from_mongodb() -> dict[str, list[dict]]:
    client = MongoClient(mongodb_url(), serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        collection = client[MONGO_DATABASE][MONGO_COLLECTION]
        recipes = list(collection.find({}, {"_id": 0, "name": 1, "ingredients": 1}))
    finally:
        client.close()

    if not recipes:
        raise RuntimeError(
            "No recipes found in MongoDB. Run scripts/sync_recipes_to_mongodb.py first."
        )

    return {recipe["name"]: recipe["ingredients"] for recipe in recipes}


def fetch_daily_sales() -> list[tuple]:
    with psycopg.connect(database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select sale_date, coffee_name, count(*) as sales_count
                from coffee_sales
                group by sale_date, coffee_name
                order by sale_date, coffee_name
                """
            )
            return cur.fetchall()


def build_daily_usage() -> dict[tuple, float]:
    recipes = load_recipes_from_mongodb()
    sales = fetch_daily_sales()
    usage = defaultdict(float)

    for sale_date, coffee_name, sales_count in sales:
        if coffee_name not in recipes:
            raise RuntimeError(f"Missing recipe for {coffee_name}")

        for ingredient in recipes[coffee_name]:
            item, unit, factor = normalize_ingredient(
                ingredient["item"],
                ingredient["unit"],
            )
            amount = float(ingredient["amount"]) * factor
            key = (sale_date, item, unit)
            usage[key] += sales_count * amount

    return usage


def save_daily_usage_to_postgres(usage: dict[tuple, float]) -> None:
    with psycopg.connect(database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("drop table if exists daily_ingredient_usage")
            cur.execute(
                """
                create table daily_ingredient_usage (
                    sale_date date not null,
                    ingredient text not null,
                    unit text not null,
                    daily_usage numeric(12, 2) not null check (daily_usage >= 0),
                    primary key (sale_date, ingredient, unit)
                )
                """
            )

            for (sale_date, ingredient, unit), daily_usage in sorted(usage.items()):
                cur.execute(
                    """
                    insert into daily_ingredient_usage (
                        sale_date,
                        ingredient,
                        unit,
                        daily_usage
                    )
                    values (%s, %s, %s, %s)
                    """,
                    (sale_date, ingredient, unit, daily_usage),
                )


def main() -> None:
    usage = build_daily_usage()
    save_daily_usage_to_postgres(usage)

    print(f"Loaded recipes from MongoDB database {MONGO_DATABASE}, collection {MONGO_COLLECTION}.")
    print("Created PostgreSQL table: daily_ingredient_usage")
    print()
    print("sale_date,ingredient,unit,daily_usage")

    for (sale_date, ingredient, unit), daily_usage in sorted(usage.items()):
        print(f"{sale_date},{ingredient},{unit},{daily_usage:.2f}")


if __name__ == "__main__":
    main()
