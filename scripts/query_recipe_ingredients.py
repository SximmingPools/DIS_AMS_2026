import json
import sys
from pathlib import Path

from pymongo import MongoClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import mongodb_url


ROOT_DIR = Path(__file__).resolve().parents[1]
RECIPES_JSON = ROOT_DIR / "data" / "coffee_recipes.json"
DATABASE_NAME = "dis_ams_nosql"
COLLECTION_NAME = "coffee_recipes"
TARGET_RECIPE = "Americano with Milk"


def main() -> None:
    with RECIPES_JSON.open(encoding="utf-8") as file:
        payload = json.load(file)

    recipes = payload.get("recipes", [])
    if not recipes:
        raise RuntimeError("No recipes found in coffee_recipes.json")

    client = MongoClient(mongodb_url(), serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        database = client[DATABASE_NAME]
        collection = database[COLLECTION_NAME]

        collection.delete_many({})
        collection.insert_many(recipes)

        recipe = collection.find_one({"name": TARGET_RECIPE}, {"_id": 0})
        if not recipe:
            raise RuntimeError(f"Recipe not found: {TARGET_RECIPE}")

        print(f"MongoDB connection: {mongodb_url()}")
        print(f"Database: {DATABASE_NAME}")
        print(f"Collection: {COLLECTION_NAME}")
        print(f"Recipe: {recipe['name']}")
        print("Ingredients:")
        for ingredient in recipe["ingredients"]:
            print(f"- {ingredient['item']}: {ingredient['amount']} {ingredient['unit']}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
