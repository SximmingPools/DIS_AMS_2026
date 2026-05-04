import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def load_env_file() -> None:
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
            continue

        name, value = clean_line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip())


def database_url() -> str:
    load_env_file()
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is missing. Copy .env.example to .env and edit it.")
    return url
