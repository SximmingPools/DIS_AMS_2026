import html
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs


HOST = "127.0.0.1"
PORT = 8000
ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT_DIR / ".env"
VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
PROJECT_PYTHON = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DIS AMS</title>
  <style>
    :root {
      color-scheme: light dark;
      font-family: Arial, sans-serif;
      background: #f6f3ee;
      color: #1f2933;
    }
    body {
      margin: 0;
      min-height: 100vh;
    }
    main {
      max-width: 920px;
      margin: 0 auto;
      padding: 32px 18px;
    }
    header {
      border-bottom: 1px solid #d8d3ca;
      margin-bottom: 22px;
      padding-bottom: 14px;
    }
    h1 {
      margin: 0 0 6px;
      font-size: 28px;
    }
    p {
      margin: 0;
      color: #52606d;
    }
    section {
      margin-top: 20px;
    }
    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    button {
      border: 1px solid #1f2933;
      background: #1f2933;
      color: white;
      border-radius: 6px;
      padding: 10px 14px;
      cursor: pointer;
      font-size: 14px;
    }
    button.secondary {
      background: transparent;
      color: #1f2933;
    }
    form {
      display: grid;
      gap: 10px;
    }
    input {
      border: 1px solid #b8b2a8;
      border-radius: 6px;
      padding: 10px;
      font-size: 14px;
      width: min(100%, 760px);
      box-sizing: border-box;
    }
    pre {
      min-height: 260px;
      overflow: auto;
      white-space: pre-wrap;
      background: #15191f;
      color: #e8edf2;
      border-radius: 6px;
      padding: 14px;
      line-height: 1.45;
    }
    input,
    select {
        border: 1px solid #b8b2a8;
        border-radius: 6px;
        padding: 10px;
        font-size: 14px;
        width: min(100%, 760px);
        box-sizing: border-box;
        background: #0f172a;
        border-color: #4b5563;
        color: #e5e7eb;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        background: #111827;
        color: #e5e7eb;
      }
      header {
        border-bottom-color: #374151;
      }
      p {
        color: #a7b0bd;
      }
      button.secondary {
        border-color: #d1d5db;
        color: #e5e7eb;
      }
      input {
        background: #0f172a;
        border-color: #4b5563;
        color: #e5e7eb;
      }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>DIS AMS</h1>
      <p>Local helper UI for the DBIS Postgres exercise.</p>
    </header>

    <section>
      <form id="env-form">
        <label for="database-url">DATABASE_URL</label>
        <input id="database-url" name="database_url" placeholder="postgresql://user:password@host/db?sslmode=require" value="__DATABASE_URL__">
        <button type="submit">Save .env</button>
      </form>
    </section>

    <section class="actions">
      <button data-action="/run/check">Check Connection</button>
      <button data-action="/run/import">Import Coffee Sales</button>
      <button data-action="/run/concurrency">Run Transaction Demo</button>
      <button data-action="/run/operations-1-b">Run Exercise 1b</button>
      <button data-action="/run/exercise-1-c">Run Exercise 1c</button>
      <button data-action="/run/query-recipe">Find Americano with Milk Ingredients</button>
      <button data-action="/run/aggregate-daily-prep">Aggregate Daily Prep Time</button>
      <button class="secondary" data-action="/run/status">Show Status</button>
      <button data-action="/run/aggregate-ingredients">Aggregate Ingredient Usage</button>
    </section>

    <section>
      <form id="forecast-form">
        <label for="ingredient">Ingredient</label>
        <select id="ingredient" name="ingredient">
            <option value="Milk">Milk</option>
            <option value="Espresso">Espresso</option>
            <option value="Coffee beans">Coffee beans</option>
            <option value="Cocoa powder">Cocoa powder</option>
            <option value="Sugar">Sugar</option>
            <option value="Hot water">Hot water</option>
            <option value="Salt">Salt</option>
        </select>

        <label for="window">Moving Average Window</label>
        <input id="window" name="window" type="number" value="7" min="1">

        <button type="submit">Run Forecast</button>
      </form>
    </section>

    <section>
      <pre id="output">Ready.</pre>
    </section>
  </main>

  <script>
    const output = document.querySelector("#output");

    async function post(url, body) {
      output.textContent = "Running...";
      const response = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body
      });
      output.textContent = await response.text();
    }

    document.querySelectorAll("button[data-action]").forEach((button) => {
      button.addEventListener("click", () => post(button.dataset.action, ""));
    });

    document.querySelector("#env-form").addEventListener("submit", (event) => {
      event.preventDefault();
      const body = new URLSearchParams(new FormData(event.currentTarget)).toString();
      post("/save-env", body);
    });

    document.querySelector("#forecast-form").addEventListener("submit", (event) => {
      event.preventDefault();
      const body = new URLSearchParams(new FormData(event.currentTarget)).toString();
      post("/run/forecast", body);
    });
  </script>
</body>
</html>
"""


def current_database_url() -> str:
    if not ENV_FILE.exists():
        return ""

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1]
    return ""


def save_database_url(database_url: str) -> None:
    ENV_FILE.write_text(f"DATABASE_URL={database_url}\n", encoding="utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/":
            self.send_error(404)
            return

        body = PAGE.replace("__DATABASE_URL__", html.escape(current_database_url(), quote=True))
        self.respond(200, body, "text/html; charset=utf-8")

    def do_POST(self) -> None:
        try:
            if self.path == "/save-env":
                self.handle_save_env()
            elif self.path == "/run/check":
                self.respond_text(run_script("check_connection.py"))
            elif self.path == "/run/import":
                self.respond_text(run_script("import_coffee_sales.py"))
            elif self.path == "/run/concurrency":
                self.respond_text(run_script("concurrency_demo.py"))
            elif self.path == "/run/operations-1-b":
                self.respond_text(run_script_path(ROOT_DIR / "src" / "db_exercise" / "operations-1-b.py"))
            elif self.path == "/run/exercise-1-c":
                self.respond_text(run_script_path(ROOT_DIR / "src" / "db_exercise" / "operations-1-c.py"))
            elif self.path == "/run/query-recipe":
                self.respond_text(run_script("query_recipe_ingredients.py"))
            elif self.path == "/run/aggregate-daily-prep":
                self.respond_text(run_script("aggregate_daily_prep_time.py"))
            elif self.path == "/run/status":
                self.respond_text(status_text())
            elif self.path == "/run/aggregate-ingredients":
                self.respond_text(run_script("aggregate_daily_ingredient_usage.py"))
            elif self.path == "/run/forecast":
                self.handle_forecast()
            else:
                self.send_error(404)
        except Exception as exc:
            self.respond_text(f"{exc.__class__.__name__}: {exc}", status=500)

    def handle_save_env(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        database_url = parse_qs(body).get("database_url", [""])[0].strip()
        save_database_url(database_url)
        self.respond_text(".env saved")

    def handle_forecast(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        params = parse_qs(body)

        ingredient = params.get("ingredient", ["Milk"])[0].strip()
        window = params.get("window", ["7"])[0].strip()

        self.respond_text(
            run_script_with_args(
                "forecast_ingredient_usage.py",
                [
                    "--ingredient", ingredient,
                    "--window", window,
                    "--steps", "14",
                    "--test-size", "14",
                ],
            )
        )

    def respond_text(self, body: str, status: int = 200) -> None:
        self.respond(status, body, "text/plain; charset=utf-8")

    def respond(self, status: int, body: str, content_type: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        print(format % args)


def status_text() -> str:
    csv_path = ROOT_DIR / "data" / "coffee_sales.csv"
    recipes_path = ROOT_DIR / "data" / "coffee_recipes.json"
    notes_path = ROOT_DIR / "notes" / "exercise2_notes.md"
    return "\n".join(
        [
            f"Repository: {ROOT_DIR}",
            f"Python used for actions: {PROJECT_PYTHON}",
            f".env exists: {ENV_FILE.exists()}",
            f"Coffee CSV exists: {csv_path.exists()}",
            f"Coffee CSV path: {csv_path}",
            f"Recipes JSON exists: {recipes_path.exists()}",
            f"Recipes JSON path: {recipes_path}",
            f"Exercise 2 notes exist: {notes_path.exists()}",
            f"Exercise 2 notes path: {notes_path}",
        ]
    )


def run_script(script_name: str) -> str:
    script_path = ROOT_DIR / "scripts" / script_name
    result = subprocess.run(
        [str(PROJECT_PYTHON), str(script_path)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        return output or f"{script_name} failed with exit code {result.returncode}"
    return output or f"{script_name} finished successfully"

def run_script_path(script_path: Path) -> str:
    result = subprocess.run(
        [str(PROJECT_PYTHON), str(script_path)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        return output or f"{script_path.name} failed with exit code {result.returncode}"
    return output or f"{script_path.name} finished successfully"

def run_script_with_args(script_name: str, args: list[str]) -> str:
  script_path = ROOT_DIR / "scripts" / script_name
  result = subprocess.run(
      [str(PROJECT_PYTHON), str(script_path), *args],
      cwd=ROOT_DIR,
      capture_output=True,
      text=True,
      timeout=120,
  )
  output = (result.stdout + result.stderr).strip()
  if result.returncode != 0:
      return output or f"{script_name} failed with exit code {result.returncode}"
  return output or f"{script_name} finished successfully"


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Open http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
