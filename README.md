# DIS AMS

Small university project for DBIS Exercise Sheet 1.

Stack:

- Python
- PostgreSQL
- GitHub

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` so `DATABASE_URL` points at your local PostgreSQL database.

## Useful Commands

Check the database connection:

```powershell
python scripts/check_connection.py
```

Run the concurrency experiment scaffold:

```powershell
python scripts/concurrency_demo.py
```

Import the Coffee Sales CSV once it is downloaded from Moodle:

```powershell
python scripts/import_coffee_sales.py path\to\coffee_sales.csv
```

