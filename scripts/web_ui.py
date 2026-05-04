import html
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from db_exercise.config import ROOT_DIR
from db_exercise.operations import check_connection, concurrency_demo, import_coffee_sales


HOST = "127.0.0.1"
PORT = 8000
ENV_FILE = ROOT_DIR / ".env"


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
      <button class="secondary" data-action="/run/status">Show Status</button>
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
                self.respond_text(check_connection())
            elif self.path == "/run/import":
                self.respond_text(import_coffee_sales())
            elif self.path == "/run/concurrency":
                self.respond_text(concurrency_demo())
            elif self.path == "/run/status":
                self.respond_text(status_text())
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
    return "\n".join(
        [
            f"Repository: {ROOT_DIR}",
            f".env exists: {ENV_FILE.exists()}",
            f"Coffee CSV exists: {csv_path.exists()}",
            f"Coffee CSV path: {csv_path}",
        ]
    )


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Open http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
