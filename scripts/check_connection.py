import sys
from pathlib import Path

import psycopg

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import database_url


def main() -> None:
    with psycopg.connect(database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("select version(), current_setting('transaction_isolation')")
            version, isolation_level = cur.fetchone()

    print("Connected to PostgreSQL")
    print(f"Isolation level: {isolation_level}")
    print(version)


if __name__ == "__main__":
    main()

