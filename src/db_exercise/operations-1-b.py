import sys
import threading
import time
from pathlib import Path

import psycopg

sys.path.append(str(Path(__file__).resolve().parents[1]))

from db_exercise.config import database_url


def connect(url: str) -> psycopg.Connection:
    return psycopg.connect(url, autocommit=True, connect_timeout=5)


def fetch_rows(conn: psycopg.Connection) -> list[tuple[int, str]]:
    with conn.cursor() as cur:
        cur.execute("select id, note from exercise_1_b_demo order by id")
        return cur.fetchall()


def log(output: list[str], step: str, message: str) -> None:
    output.append(f"{step}: {message}")


def main() -> None:
    output: list[str] = []
    url = database_url()

    # i
    conn_a = connect(url)
    log(output, "i", "Opened connection A to the persistent PostgreSQL database from DATABASE_URL.")

    try:

        with conn_a.cursor() as cur:
            cur.execute("select current_setting('transaction_isolation')")
            isolation_level = cur.fetchone()[0]
            log(output, "setup", f"Transaction isolation level: {isolation_level}") 

        # ii
        with conn_a.cursor() as cur:
            cur.execute("drop table if exists exercise_1_b_demo")
            cur.execute(
                """
                create table exercise_1_b_demo (
                    id integer primary key,
                    note text not null
                )
                """
            )
            cur.execute("insert into exercise_1_b_demo (id, note) values (1, 'original')")
        log(output, "ii", f"Created table and inserted original tuple. A sees: {fetch_rows(conn_a)}")

        # iii
        conn_b = connect(url)
        log(output, "iii", "Opened connection B to the same database.")

        try:
            # iv
            with conn_a.cursor() as cur:
                cur.execute("begin")
            with conn_b.cursor() as cur:
                cur.execute("begin")
            log(output, "iv", "Started one transaction in connection A and one in connection B.")

            # v
            with conn_a.cursor() as cur:
                cur.execute("insert into exercise_1_b_demo (id, note) values (2, 'inserted by A')")
            log(output, "v", "Connection A inserted a new record with id 2.")

            # vi
            with conn_b.cursor() as cur:
                cur.execute("insert into exercise_1_b_demo (id, note) values (3, 'inserted by B')")
            log(output, "vi", "Connection B inserted a different new record with id 3.")

            # vii
            log(output, "vii", f"A sees before commit: {fetch_rows(conn_a)}")
            log(output, "vii", f"B sees before commit: {fetch_rows(conn_b)}")

            # viii
            with conn_a.cursor() as cur:
                cur.execute("commit")
            log(output, "viii", f"Committed A. A sees: {fetch_rows(conn_a)}")

            with conn_b.cursor() as cur:
                cur.execute("commit")
            log(output, "viii", f"Committed B. B sees: {fetch_rows(conn_b)}")
            log(output, "viii", f"A sees after both commits: {fetch_rows(conn_a)}")

            # ix
            with connect(url) as conn_c:
                log(output, "ix", f"Opened connection C after both commits. C sees: {fetch_rows(conn_c)}")

            # x
            with conn_a.cursor() as cur:
                cur.execute("begin")
            with conn_b.cursor() as cur:
                cur.execute("begin")
            log(output, "x", "Started a new transaction in connection A and a new transaction in connection B.")

            # xi
            with conn_a.cursor() as cur:
                cur.execute("update exercise_1_b_demo set note = 'updated by A' where id = 1")
            log(output, "xi", "Connection A updated the original record to 'updated by A'.")

            b_update_started = threading.Event()
            b_update_finished = threading.Event()
            b_update_error: list[BaseException] = []

            def update_with_connection_b() -> None:
                try:
                    b_update_started.set()
                    with conn_b.cursor() as cur:
                        cur.execute("update exercise_1_b_demo set note = 'updated by B' where id = 1")
                    b_update_finished.set()
                except BaseException as exc:
                    b_update_error.append(exc)
                    b_update_finished.set()

            b_thread = threading.Thread(target=update_with_connection_b, daemon=True)
            b_thread.start()
            b_update_started.wait(timeout=5)
            time.sleep(0.5)

            if b_update_finished.is_set():
                log(output, "xi", "Connection B updated the original record to 'updated by B' immediately.")
            else:
                log(
                    output,
                    "xi",
                    "Connection B tried to update the same original record and is waiting for A's row lock.",
                )

            # xii
            with conn_a.cursor() as cur:
                cur.execute("commit")
            log(output, "xii", f"Committed A. A sees: {fetch_rows(conn_a)}")

            b_thread.join(timeout=10)
            if b_thread.is_alive():
                raise RuntimeError("Connection B update did not finish after connection A committed.")
            if b_update_error:
                raise b_update_error[0]

            with conn_b.cursor() as cur:
                cur.execute("commit")
            log(output, "xii", f"Committed B. B sees: {fetch_rows(conn_b)}")

            # xiii
            with connect(url) as conn_c:
                log(output, "xiii", f"Opened connection C after both update commits. C sees: {fetch_rows(conn_c)}")

        finally:
            conn_b.close()
            log(output, "cleanup", "Closed connection B.")
    finally:
        conn_a.close()
        log(output, "cleanup", "Closed connection A.")

    print("\n".join(output))


if __name__ == "__main__":
    main()
