import json
import sys
from collections import defaultdict
from pathlib import Path

import psycopg
from pymongo import MongoClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import database_url, mongodb_url


ROOT_DIR = Path(__file__).resolve().parents[1]
RECIPES_JSON = ROOT_DIR / "data" / "coffee_recipes.json"
MONGO_DATABASE = "dis_ams_nosql"
MONGO_COLLECTION = "coffee_recipes"


def load_recipes() -> list[dict]:
    with RECIPES_JSON.open(encoding="utf-8") as file:
        payload = json.load(file)
    recipes = payload.get("recipes", [])
    if not recipes:
        raise RuntimeError("No recipes found in coffee_recipes.json")
    return recipes


def sync_recipes_to_mongo(recipes: list[dict]) -> dict[str, int]:
    client = MongoClient(mongodb_url(), serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        collection = client[MONGO_DATABASE][MONGO_COLLECTION]
        collection.delete_many({})
        collection.insert_many(recipes)
        return {recipe["name"]: recipe["time_minutes"] for recipe in collection.find({}, {"_id": 0, "name": 1, "time_minutes": 1})}
    finally:
        client.close()


def fetch_sales_counts() -> tuple[list[tuple], list[str]]:
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
            grouped_sales = cur.fetchall()

            cur.execute(
                """
                select distinct coffee_name
                from coffee_sales
                order by coffee_name
                """
            )
            sold_names = [row[0] for row in cur.fetchall()]

    return grouped_sales, sold_names


def main() -> None:
    recipes = load_recipes()
    recipe_minutes = sync_recipes_to_mongo(recipes)
    grouped_sales, sold_names = fetch_sales_counts()

    recipe_names = sorted(recipe_minutes)
    missing_recipes = [name for name in sold_names if name not in recipe_minutes]
    extra_recipes = [name for name in recipe_names if name not in sold_names]
    if missing_recipes:
        raise RuntimeError(f"Missing recipes after sync: {', '.join(missing_recipes)}")

    totals_by_day: dict[str, int] = defaultdict(int)
    sample_steps: list[str] = []

    for sale_date, coffee_name, sales_count in grouped_sales:
        recipe_time = recipe_minutes[coffee_name]
        subtotal = sales_count * recipe_time
        totals_by_day[str(sale_date)] += subtotal
        if len(sample_steps) < 8:
            sample_steps.append(
                f"- {sale_date}: {coffee_name} sold {sales_count} times x {recipe_time} min = {subtotal} min"
            )

    print("Step 1: Loaded recipes from data/coffee_recipes.json.")
    print(f"Step 2: Synced {len(recipe_names)} recipe documents into MongoDB collection {MONGO_COLLECTION}.")
    print(f"Step 3: Read sold coffee names and daily sales counts from PostgreSQL coffee_sales.")
    print(f"Sold coffee names: {', '.join(sold_names)}")
    print(f"Recipe names in MongoDB: {', '.join(recipe_names)}")
    print(f"Missing recipes: {', '.join(missing_recipes) if missing_recipes else 'none'}")
    print(f"Extra recipes not sold in sales data: {', '.join(extra_recipes) if extra_recipes else 'none'}")
    print("Step 4: Joined sales data with recipe time_minutes in Python and summed minutes per day.")
    print("Sample calculation rows:")
    print("\n".join(sample_steps))
    print("Aggregated preparation time per day:")
    for sale_date in sorted(totals_by_day):
        print(f"- {sale_date}: {totals_by_day[sale_date]} minutes")


if __name__ == "__main__":
    main()
