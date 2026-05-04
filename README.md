# DIS AMS

Small university project for DBIS Exercise Sheet 1.

Stack:

- Python
- PostgreSQL
- GitHub

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` only if you changed the Postgres username, password, database, or port.

## Local Postgres

This repo includes a Docker Postgres setup. It loads `data/coffee_sales.csv`
automatically the first time the database is created.

Start Postgres:

```powershell
docker compose up -d
```

Stop Postgres:

```powershell
docker compose down
```

Reset Postgres and reload the CSV from scratch:

```powershell
docker compose down -v
docker compose up -d
```

The database files themselves are not committed. GitHub has the reproducible
setup: Docker config, init SQL, source code, and the CSV.

## Local UI

Start the helper UI:

```powershell
python scripts/web_ui.py
```

Open:

```text
http://127.0.0.1:8000
```

The page can save `DATABASE_URL` to `.env`, check the connection, import the
Coffee Sales CSV, and run the transaction demo.

## Useful Commands

Check the database connection:

```powershell
.\.venv\Scripts\python.exe scripts/check_connection.py
```

Run the concurrency experiment scaffold:

```powershell
.\.venv\Scripts\python.exe scripts/concurrency_demo.py
```

Import the Coffee Sales CSV:

```powershell
.\.venv\Scripts\python.exe scripts/import_coffee_sales.py
```

The CSV is expected at `data/coffee_sales.csv`.
