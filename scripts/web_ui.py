import html
import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote


HOST = "127.0.0.1"
PORT = 8000
ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT_DIR / ".env"
VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
PROJECT_PYTHON = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)
OUTPUT_DIR = ROOT_DIR / "output"
ASSETS_DIR = ROOT_DIR / "assets"


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DIS AMS</title>
  <style>
    :root {
      font-family: "Segoe UI", Arial, sans-serif;
      background: #eef3f7;
      color: #17212b;
      --panel: #ffffff;
      --panel-2: #f7fafc;
      --border: #d7e0e8;
      --accent: #1e5eff;
      --accent-soft: #e8f0ff;
      --text-soft: #5f6f82;
      --good: #0d8a54;
      --good-soft: #e8f8ef;
      --warn: #8a5a0d;
      --warn-soft: #fff5e8;
      --log: #111827;
      --disabled: #a8b5c6;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(30, 94, 255, 0.10), transparent 28%),
        linear-gradient(180deg, #f5f8fb 0%, #edf2f7 100%);
    }
    main {
      max-width: 1240px;
      margin: 0 auto;
      padding: 28px 18px 36px;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 18px;
      margin-bottom: 18px;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--border);
    }
    h1 {
      margin: 0 0 6px;
      font-size: 30px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .brand-logo {
      width: 56px;
      height: 56px;
      flex: 0 0 auto;
      display: block;
    }
    .brand-copy {
      min-width: 0;
    }
    p {
      margin: 0;
      color: var(--text-soft);
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 12px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: #1847c7;
      font-size: 13px;
      font-weight: 600;
      white-space: nowrap;
    }
    .layout {
      display: grid;
      gap: 18px;
    }
    .status-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 10px 26px rgba(20, 33, 55, 0.06);
    }
    .panel h2, .panel h3 {
      margin: 0 0 8px;
      font-size: 16px;
    }
    .panel h2 {
      font-size: 18px;
    }
    .status-card {
      display: grid;
      gap: 10px;
    }
    .status-line {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      font-size: 14px;
    }
    .status-line span:first-child {
      color: var(--text-soft);
    }
    .state-pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 92px;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
    }
    .state-ok {
      background: var(--good-soft);
      color: var(--good);
    }
    .state-warn {
      background: var(--warn-soft);
      color: var(--warn);
    }
    .section-grid {
      display: grid;
      grid-template-columns: 0.8fr 1.2fr;
      gap: 18px;
      align-items: start;
    }
    .stack {
      display: grid;
      gap: 18px;
    }
    .actions-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      margin-top: 12px;
    }
    button {
      border: 1px solid transparent;
      background: var(--accent);
      color: white;
      border-radius: 10px;
      padding: 10px 14px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      text-align: left;
    }
    button.secondary {
      background: var(--panel-2);
      color: #223246;
      border-color: var(--border);
    }
    button:disabled {
      background: #dbe4ee;
      color: #708197;
      border-color: #c8d3df;
      cursor: not-allowed;
    }
    .button-card {
      display: grid;
      gap: 6px;
    }
    .button-help {
      font-size: 12px;
      color: var(--text-soft);
      min-height: 32px;
    }
    button.danger {
      background: #c73b3b;
      color: white;
    }
    button.danger:disabled {
      background: #e6c6c6;
      color: #8a5b5b;
      border-color: #ddc2c2;
    }
    form {
      display: grid;
      gap: 10px;
    }
    label {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-soft);
    }
    input, select {
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 14px;
      width: 100%;
      background: #fff;
      color: #17212b;
    }
    input[type="range"] {
      padding: 0;
      border: 0;
      background: transparent;
      accent-color: var(--accent);
    }
    .range-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      font-size: 13px;
      color: var(--text-soft);
      margin-top: -2px;
    }
    .range-value {
      font-weight: 700;
      color: #203145;
      min-width: 54px;
      text-align: right;
    }
    .log-panel pre {
      margin: 0;
      min-height: 280px;
      max-height: 560px;
      overflow: auto;
      white-space: pre-wrap;
      background: var(--log);
      color: #edf2f7;
      border-radius: 10px;
      padding: 14px;
      line-height: 1.45;
      font-size: 13px;
    }
    .tiny {
      font-size: 12px;
      color: var(--text-soft);
    }
    .list {
      margin: 0;
      padding-left: 18px;
      color: var(--text-soft);
      font-size: 13px;
    }
    .log-layout {
      display: grid;
      grid-template-columns: 260px 1fr;
      gap: 14px;
      align-items: start;
    }
    .history-list {
      display: grid;
      gap: 8px;
      max-height: 560px;
      overflow: auto;
      padding-right: 4px;
    }
    .history-item {
      border: 1px solid var(--border);
      background: var(--panel-2);
      border-radius: 10px;
      padding: 10px 12px;
      cursor: pointer;
      text-align: left;
    }
    .history-item.active {
      border-color: #9db8ff;
      background: #edf3ff;
    }
    .history-title {
      font-size: 13px;
      font-weight: 700;
      color: #203145;
      margin-bottom: 4px;
    }
    .history-meta {
      font-size: 12px;
      color: var(--text-soft);
    }
    .history-empty {
      font-size: 13px;
      color: var(--text-soft);
      padding: 8px 2px;
    }
    .plot-controls {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: end;
      margin-bottom: 12px;
    }
    .toggle-group {
      display: inline-flex;
      border: 1px solid var(--border);
      background: var(--panel-2);
      border-radius: 10px;
      overflow: hidden;
    }
    .toggle-group button {
      border-radius: 0;
      border: 0;
      background: transparent;
      color: #223246;
      min-width: 112px;
    }
    .toggle-group button.active {
      background: var(--accent);
      color: white;
    }
    .plot-frame {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 10px;
      background: var(--panel-2);
      min-height: 320px;
      display: grid;
      place-items: center;
    }
    .plot-frame img {
      width: 100%;
      height: auto;
      border-radius: 8px;
      display: block;
    }
    .plot-empty {
      color: var(--text-soft);
      font-size: 14px;
      text-align: center;
      padding: 28px;
    }
    .flow-note {
      margin-top: 12px;
      padding: 12px 14px;
      border-radius: 10px;
      background: var(--panel-2);
      border: 1px dashed var(--border);
      font-size: 13px;
      color: var(--text-soft);
    }
    .loading-overlay {
      position: fixed;
      inset: 0;
      background: rgba(245, 248, 251, 0.92);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      transition: opacity 0.2s ease;
    }
    .loading-overlay.hidden {
      opacity: 0;
      pointer-events: none;
    }
    .loading-card {
      display: grid;
      gap: 14px;
      justify-items: center;
      padding: 24px 28px;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.96);
      border: 1px solid var(--border);
      box-shadow: 0 16px 36px rgba(20, 33, 55, 0.10);
      min-width: 180px;
    }
    .loading-logo {
      width: 88px;
      height: 88px;
      display: block;
    }
    .spinner {
      width: 34px;
      height: 34px;
      border-radius: 999px;
      border: 3px solid #d6e3ff;
      border-top-color: var(--accent);
      animation: spin 0.8s linear infinite;
    }
    .loading-text {
      font-size: 14px;
      font-weight: 600;
      color: #26407a;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    @media (max-width: 980px) {
      .section-grid {
        grid-template-columns: 1fr;
      }
      header {
        align-items: start;
        flex-direction: column;
      }
      .log-layout {
        grid-template-columns: 1fr;
      }
      .plot-controls {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div id="loading-overlay" class="loading-overlay">
    <div class="loading-card">
      <img class="loading-logo" src="/assets/DBIS_Logo.png" alt="DBIS logo">
      <div class="spinner" aria-hidden="true"></div>
      <div class="loading-text">Loading</div>
    </div>
  </div>
  <main>
    <header>
      <div class="brand">
        <img class="brand-logo" src="/assets/DBIS_Logo.png" alt="DBIS logo">
        <div class="brand-copy">
          <h1>DIS AMS</h1>
          <p>Database exercises dashboard with status, actions, and forecasting controls.</p>
        </div>
      </div>
      <div class="badge">Status snapshot: <span id="checked-at">not checked yet</span></div>
    </header>

    <section class="status-grid">
      <article class="panel status-card">
        <h3>PostgreSQL</h3>
        <div class="status-line"><span>Connection</span><strong id="pg-state" class="state-pill state-warn">Unknown</strong></div>
        <div class="status-line"><span>Sales rows</span><strong id="pg-sales-rows">-</strong></div>
        <div class="status-line"><span>Sales range</span><strong id="pg-sales-range">-</strong></div>
        <div class="status-line"><span>Ingredient usage rows</span><strong id="pg-ingredient-rows">-</strong></div>
        <div class="status-line"><span>Ingredient usage range</span><strong id="pg-ingredient-range">-</strong></div>
      </article>

      <article class="panel status-card">
        <h3>MongoDB</h3>
        <div class="status-line"><span>Connection</span><strong id="mongo-state" class="state-pill state-warn">Unknown</strong></div>
        <div class="status-line"><span>Recipes</span><strong id="mongo-recipe-count">-</strong></div>
        <div class="tiny">Current recipe names</div>
        <div id="mongo-recipe-names" class="tiny">-</div>
      </article>

      <article class="panel status-card">
        <h3>Generated Outputs</h3>
        <div class="status-line"><span>PNG plots</span><strong id="output-plot-count">-</strong></div>
        <div class="tiny">Current files</div>
        <div id="output-plot-names" class="tiny">-</div>
      </article>
    </section>

    <section class="section-grid">
      <div class="stack">
        <article class="panel">
          <h2>Connections And Setup</h2>
          <p>Use these first to verify the databases and inspect the current repo state.</p>
          <div class="actions-grid">
            <div class="button-card">
              <button data-action="/run/check-postgres" data-key="check-postgres">Check PostgreSQL</button>
              <div class="button-help" id="help-check-postgres">Always available.</div>
            </div>
            <div class="button-card">
              <button data-action="/run/check-mongo" data-key="check-mongo">Check MongoDB</button>
              <div class="button-help" id="help-check-mongo">Always available.</div>
            </div>
            <div class="button-card">
              <button class="secondary" data-action="/run/status" data-key="show-status">Show File Status</button>
              <div class="button-help" id="help-show-status">Always available.</div>
            </div>
            <div class="button-card">
              <button class="danger" data-action="/run/reset" data-key="reset-demo">RESET</button>
              <div class="button-help" id="help-reset-demo">Clears database tables, Mongo recipes, plots, and local UI history.</div>
            </div>
          </div>
        </article>

        <article class="panel">
          <h2>Exercise Sheet 1</h2>
          <p>Relational setup, transaction demo, and CSV import.</p>
          <div class="actions-grid">
            <div class="button-card">
              <button data-action="/run/operations-1-b" data-key="exercise-1b">Exercise 1b (Transactions)</button>
              <div class="button-help" id="help-exercise-1b">Runs the full concurrent transaction exercise.</div>
            </div>
            <div class="button-card">
              <button data-action="/run/exercise-1-c" data-key="exercise-1c">Exercise 1c (Import Coffee Sales)</button>
              <div class="button-help" id="help-exercise-1c">Creates and fills the coffee_sales tables from the CSV.</div>
            </div>
          </div>
        </article>

        <article class="panel">
          <h2>Exercise Sheet 2</h2>
          <p>NoSQL recipes and cross-database aggregation.</p>
          <div class="actions-grid">
            <div class="button-card">
              <button data-action="/run/sync-recipes" data-key="sync-recipes">Sync Recipes to MongoDB</button>
              <div class="button-help" id="help-sync-recipes">Requires MongoDB connection.</div>
            </div>
            <div class="button-card">
              <button data-action="/run/query-recipe" data-key="query-recipe">Find Americano with Milk Ingredients</button>
              <div class="button-help" id="help-query-recipe">Requires synced MongoDB recipes.</div>
            </div>
            <div class="button-card">
              <button data-action="/run/aggregate-daily-prep" data-key="aggregate-daily-prep">Aggregate Daily Prep Time</button>
              <div class="button-help" id="help-aggregate-daily-prep">Requires PostgreSQL and synced MongoDB recipes.</div>
            </div>
          </div>
        </article>

        <article class="panel">
          <h2>Exercise Sheet 3</h2>
          <p>Ingredient usage aggregation plus moving average forecasting.</p>
          <div class="actions-grid">
            <div class="button-card">
              <button data-action="/run/aggregate-ingredients" data-key="aggregate-ingredients">Aggregate Ingredient Usage</button>
              <div class="button-help" id="help-aggregate-ingredients">Requires PostgreSQL and synced MongoDB recipes.</div>
            </div>
          </div>
          <form id="forecast-form" style="margin-top: 14px;">
            <label for="ingredient">Ingredient</label>
            <select id="ingredient" name="ingredient">
              <option value="Milk">🥛 Milk</option>
              <option value="Espresso">☕ Espresso</option>
              <option value="Coffee beans">🫘 Coffee beans</option>
              <option value="Cocoa powder">🍫 Cocoa powder</option>
              <option value="Sugar">🍬 Sugar</option>
              <option value="Hot water">💧 Hot water</option>
              <option value="Salt">🧂 Salt</option>
            </select>

            <label for="window">Moving Average Window</label>
            <input id="window" name="window" type="range" value="7" min="2" max="30" step="1">
            <div class="range-row">
              <span>A larger window smooths more days together. A smaller window reacts faster.</span>
              <strong id="window-value" class="range-value">7 days</strong>
            </div>

            <button type="submit" id="run-forecast-button">Run Forecast</button>
          </form>
          <div class="flow-note" id="flow-note">
            Main flow: Check both DBs -> Sync recipes -> Aggregate ingredient usage -> Run forecast.
          </div>
        </article>
      </div>

      <div class="stack">
        <article class="panel">
          <h2>Environment</h2>
          <form id="env-form">
            <label for="database-url">DATABASE_URL</label>
            <input id="database-url" name="database_url" placeholder="postgresql://user:password@host/db?sslmode=require" value="__DATABASE_URL__">
            <button type="submit">Save .env</button>
          </form>
        </article>

        <article class="panel log-panel">
          <h2>Run Log</h2>
          <p class="tiny">Actions stay in history. Click an entry to revisit its output.</p>
          <div class="log-layout">
            <div>
              <div class="tiny" style="margin-bottom: 8px;">Recent actions</div>
              <div id="history-list" class="history-list">
                <div class="history-empty">No actions yet.</div>
              </div>
            </div>
            <pre id="output">Ready.</pre>
          </div>
        </article>

        <article class="panel">
          <h2>Forecast Plots</h2>
          <p class="tiny">View the generated evaluation and future plots directly here.</p>
          <div class="plot-controls">
            <div>
              <label for="plot-select">Forecast set</label>
              <select id="plot-select"></select>
            </div>
            <div class="toggle-group">
              <button id="show-evaluation" type="button" class="active">Evaluation</button>
              <button id="show-future" type="button">Future</button>
            </div>
          </div>
          <div class="tiny" id="plot-meta">No plots loaded yet.</div>
          <div class="plot-frame" style="margin-top: 12px;">
            <div id="plot-empty" class="plot-empty">Run a forecast or load existing plots to preview them here.</div>
            <img id="plot-image" alt="Forecast plot" style="display: none;">
          </div>
        </article>
      </div>
    </section>
  </main>

  <script>
    const output = document.querySelector("#output");
    const historyList = document.querySelector("#history-list");
    const plotSelect = document.querySelector("#plot-select");
    const plotMeta = document.querySelector("#plot-meta");
    const plotImage = document.querySelector("#plot-image");
    const plotEmpty = document.querySelector("#plot-empty");
    const windowInput = document.querySelector("#window");
    const windowValue = document.querySelector("#window-value");
    const historyStorageKey = "dis_ams_action_history";
    let actionHistory = [];
    let selectedHistoryId = null;
    let plotMode = "evaluation";
    let latestStatus = null;
    let initialStatusLoaded = false;
    let preferredPlotGroupKey = null;

    const actionLabels = {
      "/run/check-postgres": "Check PostgreSQL",
      "/run/check-mongo": "Check MongoDB",
      "/run/sync-recipes": "Sync Recipes to MongoDB",
      "/run/status": "Show File Status",
      "/run/reset": "RESET",
      "/run/import": "Import Coffee Sales",
      "/run/concurrency": "Transaction Demo (Quick)",
      "/run/operations-1-b": "Exercise 1b (Transactions)",
      "/run/exercise-1-c": "Exercise 1c (Import Coffee Sales)",
      "/run/query-recipe": "Find Americano with Milk Ingredients",
      "/run/aggregate-daily-prep": "Aggregate Daily Prep Time",
      "/run/aggregate-ingredients": "Aggregate Ingredient Usage",
      "/run/forecast": "Run Forecast"
    };

    function setState(id, ok, text) {
      const element = document.querySelector(id);
      element.textContent = text;
      element.className = `state-pill ${ok ? "state-ok" : "state-warn"}`;
    }

    function setText(id, value) {
      document.querySelector(id).textContent = value;
    }

    function syncWindowLabel() {
      windowValue.textContent = `${windowInput.value} days`;
    }

    function forecastKeyFromInput(ingredient, window) {
      const ingredientKey = ingredient.trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
      return `${ingredientKey}|${window.trim()}`;
    }

    function setGlobalLoading(isLoading) {
      const overlay = document.querySelector("#loading-overlay");
      overlay.classList.toggle("hidden", !isLoading);
    }

    function loadHistory() {
      try {
        actionHistory = JSON.parse(localStorage.getItem(historyStorageKey) || "[]");
      } catch {
        actionHistory = [];
      }
    }

    function saveHistory() {
      localStorage.setItem(historyStorageKey, JSON.stringify(actionHistory.slice(0, 20)));
    }

    function renderHistory() {
      if (!actionHistory.length) {
        historyList.innerHTML = '<div class="history-empty">No actions yet.</div>';
        return;
      }

      historyList.innerHTML = "";
      actionHistory.forEach((entry) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = `history-item ${entry.id === selectedHistoryId ? "active" : ""}`;
        button.innerHTML = `
          <div class="history-title">${entry.label}</div>
          <div class="history-meta">${entry.time}</div>
        `;
        button.addEventListener("click", () => {
          selectedHistoryId = entry.id;
          output.textContent = entry.output;
          renderHistory();
        });
        historyList.appendChild(button);
      });
    }

    function addHistoryEntry(label, outputText) {
      const entry = {
        id: crypto.randomUUID(),
        label,
        time: new Date().toLocaleString(),
        output: outputText
      };
      actionHistory.unshift(entry);
      actionHistory = actionHistory.slice(0, 20);
      selectedHistoryId = entry.id;
      saveHistory();
      renderHistory();
      output.textContent = outputText;
    }

    function parsePlotName(name) {
      const match = name.match(/^(evaluation|future)_forecast_(.+)_window_(\\d+)\\.png$/);
      if (!match) {
        return null;
      }
      return {
        type: match[1],
        ingredientKey: match[2],
        window: match[3],
        groupKey: `${match[2]}|${match[3]}`,
        label: `${match[2].replace(/_/g, " ")} | window ${match[3]}`
      };
    }

    function refreshPlotViewer(status) {
      const parsed = status.output.plot_names
        .map(parsePlotName)
        .filter(Boolean);

      const grouped = new Map();
      parsed.forEach((plot) => {
        if (!grouped.has(plot.groupKey)) {
          grouped.set(plot.groupKey, { label: plot.label });
        }
        grouped.get(plot.groupKey)[plot.type] = plot;
      });

      const groups = Array.from(grouped.entries()).map(([key, value]) => ({ key, ...value }));
      const previous = preferredPlotGroupKey || plotSelect.value;
      plotSelect.innerHTML = "";

      groups.forEach((group) => {
        const option = document.createElement("option");
        option.value = group.key;
        option.textContent = group.label;
        plotSelect.appendChild(option);
      });

      if (!groups.length) {
        plotMeta.textContent = "No plot files found yet.";
        plotImage.style.display = "none";
        plotEmpty.style.display = "block";
        plotSelect.innerHTML = "";
        preferredPlotGroupKey = null;
        return;
      }

      plotSelect.value = groups.some((group) => group.key === previous) ? previous : groups[0].key;
      const selected = groups.find((group) => group.key === plotSelect.value) || groups[0];
      preferredPlotGroupKey = null;
      const chosen = selected[plotMode] || selected.evaluation || selected.future;

      if (!chosen) {
        plotMeta.textContent = "Selected forecast set does not have a plot for this mode yet.";
        plotImage.style.display = "none";
        plotEmpty.style.display = "block";
        return;
      }

      plotMeta.textContent = `Showing ${plotMode} plot for ${selected.label}.`;
      plotImage.src = `/plots/${encodeURIComponent(`${chosen.type}_forecast_${chosen.ingredientKey}_window_${chosen.window}.png`)}?t=${Date.now()}`;
      plotImage.style.display = "block";
      plotEmpty.style.display = "none";
    }

    function updateActionAvailability(status) {
      latestStatus = status;
      const pgReady = status.postgres.connected;
      const mongoReady = status.mongodb.connected;
      const salesReady = pgReady && !!status.postgres.sales_table_ready;
      const recipesReady = mongoReady && (status.mongodb.recipe_count || 0) > 0;
      const ingredientsReady = pgReady && (status.postgres.ingredient_rows || 0) > 0;

      const rules = {
        "check-postgres": { enabled: true, help: "Always available." },
        "check-mongo": { enabled: true, help: "Always available." },
        "sync-recipes": { enabled: mongoReady, help: mongoReady ? "MongoDB is reachable." : "Blocked until MongoDB is connected." },
        "show-status": { enabled: true, help: "Always available." },
        "reset-demo": { enabled: pgReady && mongoReady, help: pgReady && mongoReady ? "Clears the current demo state from both databases and the output folder." : "Blocked until both PostgreSQL and MongoDB are connected." },
        "import-sales": { enabled: pgReady, help: pgReady ? (salesReady ? "PostgreSQL is reachable. Re-import will refresh the sales table." : "PostgreSQL is reachable. Import the coffee sales table now.") : "Blocked until PostgreSQL is connected." },
        "transaction-demo": { enabled: pgReady, help: pgReady ? "PostgreSQL is reachable." : "Blocked until PostgreSQL is connected." },
        "exercise-1b": { enabled: pgReady, help: pgReady ? "PostgreSQL is reachable. Runs the official transaction steps." : "Blocked until PostgreSQL is connected." },
        "exercise-1c": { enabled: pgReady, help: pgReady ? (salesReady ? "PostgreSQL is reachable. Re-running refreshes the imported sales tables." : "PostgreSQL is reachable. This is the import step for the coffee sales dataset.") : "Blocked until PostgreSQL is connected." },
        "query-recipe": { enabled: recipesReady, help: recipesReady ? "Recipes are present in MongoDB." : "Blocked until recipes are synced to MongoDB." },
        "aggregate-daily-prep": { enabled: salesReady && recipesReady, help: salesReady && recipesReady ? "Both databases are ready." : "Blocked until sales are imported into PostgreSQL and recipes are synced." },
        "aggregate-ingredients": { enabled: salesReady && recipesReady, help: salesReady && recipesReady ? "Both databases are ready." : "Blocked until sales are imported into PostgreSQL and recipes are synced." }
      };

      document.querySelectorAll("button[data-key]").forEach((button) => {
        const key = button.dataset.key;
        const rule = rules[key];
        if (!rule) {
          return;
        }
        button.disabled = !rule.enabled;
        const help = document.querySelector(`#help-${key}`);
        if (help) {
          help.textContent = rule.help;
        }
      });

      const forecastButton = document.querySelector("#run-forecast-button");
      forecastButton.disabled = !ingredientsReady;
      document.querySelector("#flow-note").textContent = ingredientsReady
        ? "Forecasting is ready. You can safely run forecasts and compare generated plots."
        : salesReady && recipesReady
          ? "Next step: Aggregate Ingredient Usage before running forecasts."
        : recipesReady
          ? "Next step: Run Exercise 1c to import Coffee Sales into PostgreSQL."
          : "Main flow: Check both DBs -> Exercise 1c -> Sync recipes -> Aggregate ingredient usage -> Run forecast.";
    }

    async function refreshStatus() {
      try {
        const response = await fetch("/status-data");
        const status = await response.json();
        latestStatus = status;

        setText("#checked-at", status.checked_at);
        setState("#pg-state", status.postgres.connected, status.postgres.message);
        setText("#pg-sales-rows", status.postgres.sales_rows ?? "-");
        setText("#pg-sales-range", status.postgres.sales_range ?? "-");
        setText("#pg-ingredient-rows", status.postgres.ingredient_rows ?? "-");
        setText("#pg-ingredient-range", status.postgres.ingredient_range ?? "-");

        setState("#mongo-state", status.mongodb.connected, status.mongodb.message);
        setText("#mongo-recipe-count", status.mongodb.recipe_count ?? "-");
        setText(
          "#mongo-recipe-names",
          status.mongodb.recipe_names.length ? status.mongodb.recipe_names.join(", ") : "-"
        );

        setText("#output-plot-count", status.output.plot_count);
        setText(
          "#output-plot-names",
          status.output.plot_names.length ? status.output.plot_names.join(", ") : "-"
        );
        updateActionAvailability(status);
        refreshPlotViewer(status);
        if (!initialStatusLoaded) {
          initialStatusLoaded = true;
          setGlobalLoading(false);
        }
      } catch (error) {
        setText("#checked-at", "status refresh failed");
        if (!initialStatusLoaded) {
          initialStatusLoaded = true;
          setGlobalLoading(false);
        }
      }
    }

    async function post(url, body) {
      output.textContent = "Running...";
      const response = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body
      });
      const responseText = await response.text();
      if (url === "/run/reset") {
        actionHistory = [];
        saveHistory();
        selectedHistoryId = null;
        renderHistory();
        output.textContent = responseText;
      } else {
        addHistoryEntry(actionLabels[url] || "Run Action", responseText);
      }
      await refreshStatus();
    }

    document.querySelectorAll("button[data-action]").forEach((button) => {
      button.addEventListener("click", () => {
        if (button.dataset.action === "/run/reset") {
          const confirmed = window.confirm("Reset all demo data? This clears PostgreSQL tables, MongoDB recipes, generated plots, and the local run history.");
          if (!confirmed) {
            return;
          }
        }
        post(button.dataset.action, "");
      });
    });

    document.querySelector("#env-form").addEventListener("submit", (event) => {
      event.preventDefault();
      const body = new URLSearchParams(new FormData(event.currentTarget)).toString();
      post("/save-env", body);
    });

    document.querySelector("#forecast-form").addEventListener("submit", (event) => {
      event.preventDefault();
      const formData = new FormData(event.currentTarget);
      preferredPlotGroupKey = forecastKeyFromInput(
        String(formData.get("ingredient") || "Milk"),
        String(formData.get("window") || "7"),
      );
      const body = new URLSearchParams(formData).toString();
      post("/run/forecast", body);
    });

    plotSelect.addEventListener("change", () => {
      if (latestStatus) {
        refreshPlotViewer(latestStatus);
      }
    });

    windowInput.addEventListener("input", syncWindowLabel);

    document.querySelector("#show-evaluation").addEventListener("click", () => {
      plotMode = "evaluation";
      document.querySelector("#show-evaluation").classList.add("active");
      document.querySelector("#show-future").classList.remove("active");
      if (latestStatus) {
        refreshPlotViewer(latestStatus);
      }
    });

    document.querySelector("#show-future").addEventListener("click", () => {
      plotMode = "future";
      document.querySelector("#show-future").classList.add("active");
      document.querySelector("#show-evaluation").classList.remove("active");
      if (latestStatus) {
        refreshPlotViewer(latestStatus);
      }
    });

    loadHistory();
    renderHistory();
    syncWindowLabel();
    setGlobalLoading(true);
    refreshStatus();
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
        if self.path == "/":
            body = PAGE.replace("__DATABASE_URL__", html.escape(current_database_url(), quote=True))
            self.respond(200, body, "text/html; charset=utf-8")
            return

        if self.path == "/status-data":
            self.respond_text(run_script("app_status.py"), content_type="application/json; charset=utf-8")
            return

        if self.path.startswith("/plots/"):
            requested = unquote(self.path.removeprefix("/plots/")).split("?", 1)[0]
            file_path = (OUTPUT_DIR / requested).resolve()
            if not str(file_path).startswith(str(OUTPUT_DIR.resolve())) or not file_path.exists():
                self.send_error(404)
                return
            self.respond_bytes(200, file_path.read_bytes(), "image/png")
            return

        if self.path.startswith("/assets/"):
            requested = unquote(self.path.removeprefix("/assets/")).split("?", 1)[0]
            file_path = (ASSETS_DIR / requested).resolve()
            if not str(file_path).startswith(str(ASSETS_DIR.resolve())) or not file_path.exists():
                self.send_error(404)
                return
            suffix = file_path.suffix.lower()
            if suffix == ".svg":
                content_type = "image/svg+xml"
            elif suffix == ".png":
                content_type = "image/png"
            else:
                content_type = "application/octet-stream"
            self.respond_bytes(200, file_path.read_bytes(), content_type)
            return

        self.send_error(404)

    def do_POST(self) -> None:
        try:
            if self.path == "/save-env":
                self.handle_save_env()
            elif self.path == "/run/check-postgres":
                self.respond_text(run_script("check_connection.py"))
            elif self.path == "/run/check-mongo":
                self.respond_text(run_script("check_mongodb.py"))
            elif self.path == "/run/import":
                self.respond_text(run_script("import_coffee_sales.py"))
            elif self.path == "/run/concurrency":
                self.respond_text(run_script("concurrency_demo.py"))
            elif self.path == "/run/operations-1-b":
                self.respond_text(run_script_path(ROOT_DIR / "src" / "db_exercise" / "operations-1-b.py"))
            elif self.path == "/run/exercise-1-c":
                self.respond_text(run_script_path(ROOT_DIR / "src" / "db_exercise" / "operations-1-c.py"))
            elif self.path == "/run/sync-recipes":
                self.respond_text(run_script("sync_recipes_to_mongodb.py"))
            elif self.path == "/run/query-recipe":
                self.respond_text(run_script("query_recipe_ingredients.py"))
            elif self.path == "/run/aggregate-daily-prep":
                self.respond_text(run_script("aggregate_daily_prep_time.py"))
            elif self.path == "/run/status":
                self.respond_text(status_text())
            elif self.path == "/run/reset":
                self.respond_text(run_script("reset_demo_state.py"))
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

    def respond_text(
        self,
        body: str,
        status: int = 200,
        content_type: str = "text/plain; charset=utf-8",
    ) -> None:
        self.respond(status, body, content_type)

    def respond(self, status: int, body: str, content_type: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def respond_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

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
    output = friendly_output(result.stdout, result.stderr)
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
    output = friendly_output(result.stdout, result.stderr)
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
    output = friendly_output(result.stdout, result.stderr)
    if result.returncode != 0:
        return output or f"{script_name} failed with exit code {result.returncode}"
    return output or f"{script_name} finished successfully"


def friendly_output(stdout: str, stderr: str) -> str:
    combined = (stdout + stderr).strip()
    if not combined:
        return ""

    if "Traceback (most recent call last):" not in combined:
        return combined

    for line in reversed(combined.splitlines()):
        clean = line.strip()
        if not clean:
            continue
        if clean.startswith("RuntimeError:"):
            return clean.replace("RuntimeError:", "Error:", 1).strip()
        if ":" in clean:
            head, tail = clean.split(":", 1)
            if head.endswith("Error") or head.endswith("Exception"):
                return f"Error: {tail.strip()}"

    return "Error: Action failed. Check that the required database service is running."


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Open http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
