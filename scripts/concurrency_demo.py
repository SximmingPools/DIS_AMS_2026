import sys
from pathlib import Path

import psycopg

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import database_url


def show_rows(label: str, conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("select id, note from concurrency_demo order by id")
        print(label, cur.fetchall())


def main() -> None:
    url = database_url()

    conn_a = psycopg.connect(url, autocommit=True)
    conn_b = psycopg.connect(url, autocommit=True)

    try:
        with conn_a.cursor() as cur:
            cur.execute("drop table if exists concurrency_demo")
            cur.execute("create table concurrency_demo (id integer primary key, note text not null)")
            cur.execute("insert into concurrency_demo (id, note) values (1, 'original')")

        conn_a.autocommit = False
        conn_b.autocommit = False

        with conn_a.cursor() as cur:
            cur.execute("insert into concurrency_demo (id, note) values (2, 'inserted by A')")
        with conn_b.cursor() as cur:
            cur.execute("insert into concurrency_demo (id, note) values (3, 'inserted by B')")

        show_rows("A sees before commit:", conn_a)
        show_rows("B sees before commit:", conn_b)

        conn_a.commit()
        conn_b.commit()

        show_rows("A sees after commit:", conn_a)
        show_rows("B sees after commit:", conn_b)

        conn_c = psycopg.connect(url)
        try:
            show_rows("C sees after both commits:", conn_c)
        finally:
            conn_c.close()

        conn_a.autocommit = False
        conn_b.autocommit = False

        with conn_a.cursor() as cur:
            cur.execute("update concurrency_demo set note = 'updated by A' where id = 1")
        with conn_b.cursor() as cur:
            cur.execute("update concurrency_demo set note = 'updated by B' where id = 1")

        conn_a.commit()
        conn_b.commit()

        show_rows("A sees after updates:", conn_a)
        show_rows("B sees after updates:", conn_b)
    finally:
        conn_a.close()
        conn_b.close()


if __name__ == "__main__":
    main()

