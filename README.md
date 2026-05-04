# DIS AMS

## Intro

This is the repo for our DIS_EMS group. I made it so we don't need an exterior hosted service for the postgres but we create it with docker.
Basically, you run the docker container which creates the database, then open the UI that I created to test the functions.
TODO list shows what is still open, below is a step-by-step guide on how to get the environment running.

I used Windows + VS Code + Powershell for the setup, so the guide is mostly framed from that perspective.

## Stack

- Python
- PostgreSQL
- Docker
- GitHub

## Components

**Database**

- `docker-compose.yml`: starts PostgreSQL in Docker.
- `db/init/001_coffee_sales.sql`: creates and fills the `coffee_sales` table.
- `data/coffee_sales.csv`: Coffee Sales dataset.

**Python**

- `requirements.txt`: Python packages.
- `scripts/`: runnable helper scripts and local UI.
- `src/db_exercise/`: shared code used by the scripts.

**Project**

- `.env.example`: default local database connection.
- `TODO.md`: exercise checklist.

## Setup Tutorial

### Step 1: Check Python

Requirement: Python must be installed.

Run:

```powershell
python --version
```

Worked if: a Python version is printed.

### Step 2: Install Python Requirements

Requirement: Python works.

Run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
```

Worked if: the install finishes without errors and `.env` exists.

Default `.env`:

```env
DATABASE_URL=postgresql://dis_ams:dis_ams@localhost:5432/dis_ams
```

### Step 3: Install Docker

Requirement: Docker Desktop must be installed.

Download:

```text
https://www.docker.com/products/docker-desktop/
```

During setup:

- Use WSL 2.
- Do not enable Windows Containers.
- No need to login, but you need to restart.

Run:

```powershell
docker --version
```

Worked if: a Docker version is printed.

### Step 4: Start PostgreSQL

Requirement: Docker Desktop is running.

Run:

```powershell
docker compose up -d
```

Worked if: Docker starts the `dis_ams_postgres` container.

### Step 5: Start The UI

Requirement: Python requirements are installed and PostgreSQL is running.

Run:

```powershell
python scripts/web_ui.py
```

Open:

```text
http://127.0.0.1:8000
```

Worked if: the page opens and **Check Connection** says Python connected to PostgreSQL.

## Buttons Explained

- **Check Connection**: checks the current `DATABASE_URL` connection.
- **Import Coffee Sales**: imports `data/coffee_sales.csv` into PostgreSQL.
- **Run Transaction Demo**: runs a first version of the concurrent transaction experiment.
- **Show Status**: shows local paths and setup status.

The transaction demo button does not complete the entire exercise. The exact
exercise steps still need to be executed, observed, and documented.

## Useful Commands

Stop PostgreSQL:

```powershell
docker compose down
```

Reset PostgreSQL and reload the CSV from scratch:

```powershell
docker compose down -v
docker compose up -d
```

Run scripts without the UI:

```powershell
.\.venv\Scripts\python.exe scripts/check_connection.py
.\.venv\Scripts\python.exe scripts/import_coffee_sales.py
.\.venv\Scripts\python.exe scripts/concurrency_demo.py
```

