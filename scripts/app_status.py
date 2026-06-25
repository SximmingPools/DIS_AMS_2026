import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from pymongo import MongoClient
from pymongo.errors import PyMongoError

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import ROOT_DIR, database_url, mongodb_url
from sync_recipes_to_mongodb import MONGO_COLLECTION, MONGO_DATABASE


OUTPUT_DIR = ROOT_DIR / "output"


def short_error_message(exc: Exception) -> str:
    if isinstance(exc, (psycopg.OperationalError, PyMongoError)):
        return "Service unavailable"
    return exc.__class__.__name__


def postgres_status() -> dict:
    status = {
        "connected": False,
        "message": "",
        "sales_rows": None,
        "sales_range": None,
        "ingredient_rows": None,
        "ingredient_range": None,
        "sales_table_ready": False,
        "ingredients_table_ready": False,
    }

    try:
        with psycopg.connect(database_url(), connect_timeout=2) as conn:
            with conn.cursor() as cur:
                cur.execute("select to_regclass('public.coffee_sales')")
                if cur.fetchone()[0]:
                    status["sales_table_ready"] = True
                    cur.execute("select count(*), min(sale_date), max(sale_date) from coffee_sales")
                    sales_rows, sales_min, sales_max = cur.fetchone()
                    status["sales_rows"] = int(sales_rows)
                    status["sales_range"] = (
                        f"{sales_min} to {sales_max}" if sales_min and sales_max else "n/a"
                    )
                else:
                    status["sales_rows"] = 0
                    status["sales_range"] = "not imported yet"

                cur.execute("select to_regclass('public.daily_ingredient_usage')")
                if cur.fetchone()[0]:
                    status["ingredients_table_ready"] = True
                    cur.execute(
                        "select count(*), min(sale_date), max(sale_date) from daily_ingredient_usage"
                    )
                    ingredient_rows, ingredient_min, ingredient_max = cur.fetchone()
                    status["ingredient_rows"] = int(ingredient_rows)
                    status["ingredient_range"] = (
                        f"{ingredient_min} to {ingredient_max}"
                        if ingredient_min and ingredient_max
                        else "n/a"
                    )
                else:
                    status["ingredient_rows"] = 0
                    status["ingredient_range"] = "not aggregated yet"

        status["connected"] = True
        status["message"] = (
            "Connected"
            if status["sales_table_ready"]
            else "Connected (sales not imported yet)"
        )
    except Exception as exc:
        status["message"] = short_error_message(exc)

    return status


def mongodb_status() -> dict:
    status = {
        "connected": False,
        "message": "",
        "recipe_count": None,
        "recipe_names": [],
    }

    client = MongoClient(mongodb_url(), serverSelectionTimeoutMS=2500, connectTimeoutMS=2500)
    try:
        client.admin.command("ping")
        collection = client[MONGO_DATABASE][MONGO_COLLECTION]
        status["recipe_count"] = collection.count_documents({})
        status["recipe_names"] = sorted(
            recipe["name"] for recipe in collection.find({}, {"_id": 0, "name": 1})
        )
        status["connected"] = True
        status["message"] = "Connected"
    except Exception as exc:
        status["message"] = short_error_message(exc)
    finally:
        client.close()

    return status


def output_status() -> dict:
    png_files = sorted(OUTPUT_DIR.glob("*.png"))
    return {
        "plot_count": len(png_files),
        "plot_names": [file.name for file in png_files],
    }


def main() -> None:
    payload = {
        "checked_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "postgres": postgres_status(),
        "mongodb": mongodb_status(),
        "output": output_status(),
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
