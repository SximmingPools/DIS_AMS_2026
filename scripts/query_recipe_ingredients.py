import sys
from pathlib import Path

from pymongo import MongoClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import mongodb_url
from sync_recipes_to_mongodb import MONGO_COLLECTION, MONGO_DATABASE, main as sync_recipes


TARGET_RECIPE = "Americano with Milk"


def main() -> None:
    sync_recipes()

    client = MongoClient(mongodb_url(), serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        database = client[MONGO_DATABASE]
        collection = database[MONGO_COLLECTION]

        recipe = collection.find_one({"name": TARGET_RECIPE}, {"_id": 0})
        if not recipe:
            raise RuntimeError(f"Recipe not found: {TARGET_RECIPE}")

        print(f"MongoDB connection: {mongodb_url()}")
        print(f"Database: {MONGO_DATABASE}")
        print(f"Collection: {MONGO_COLLECTION}")
        print(f"Recipe: {recipe['name']}")
        print("Ingredients:")
        for ingredient in recipe["ingredients"]:
            print(f"- {ingredient['item']}: {ingredient['amount']} {ingredient['unit']}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
