import json
import sys
from pathlib import Path

from pymongo import MongoClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import mongodb_url


ROOT_DIR = Path(__file__).resolve().parents[1]
RECIPES_JSON = ROOT_DIR / "data" / "coffee_recipes.json"
MONGO_DATABASE = "dis_ams_nosql"
MONGO_COLLECTION = "coffee_recipes"


def main() -> None:
    with RECIPES_JSON.open(encoding="utf-8") as file:
        payload = json.load(file)

    recipes = payload.get("recipes", [])
    if not recipes:
        raise RuntimeError("No recipes found in coffee_recipes.json")

    client = MongoClient(mongodb_url(), serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        collection = client[MONGO_DATABASE][MONGO_COLLECTION]
        collection.delete_many({})
        collection.insert_many(recipes)
        print(f"MongoDB connection: {mongodb_url()}")
        print(f"Database: {MONGO_DATABASE}")
        print(f"Collection: {MONGO_COLLECTION}")
        print(f"Inserted recipes: {len(recipes)}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
