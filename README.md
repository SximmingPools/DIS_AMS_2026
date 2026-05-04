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

Edit `.env` so `DATABASE_URL` points at your Neon PostgreSQL database.

For the shared team database, use a hosted Neon Postgres connection string.
Each teammate should keep the same value in their own local `.env` file.
Do not commit `.env`.

Quick Neon setup:

1. Create a Neon project.
2. Copy the direct PostgreSQL connection string from the Neon dashboard.
3. Paste it into `.env` as `DATABASE_URL=...`.
4. Share the connection string with teammates privately.

The database itself does not live inside GitHub. GitHub stores the code and CSV;
Neon hosts the shared database that everyone connects to.

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
