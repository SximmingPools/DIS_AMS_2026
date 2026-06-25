import sys
from pathlib import Path

from pymongo.errors import PyMongoError
from pymongo import MongoClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import mongodb_url


def main() -> None:
    client = MongoClient(mongodb_url(), serverSelectionTimeoutMS=2500, connectTimeoutMS=2500)
    try:
        client.admin.command("ping")
        print("Connected to MongoDB")
        print(f"Connection: {mongodb_url()}")
    except PyMongoError as exc:
        raise RuntimeError("MongoDB is not reachable. Start Docker and try again.") from exc
    finally:
        client.close()


if __name__ == "__main__":
    main()
