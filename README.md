# Making Change — FX Risk Simulation Platform

Research project linked to the **SKEMA Business School** thesis:
*Making Change: How FX Risk Management Enables Sustainable Infrastructure Financing in Africa and Latin America.*

> **Repository status**: public research and working repository, maintained up to the closure of the thesis (6-month horizon), in an academic framework at **SKEMA Business School** (institutional reference only).
>
> **Contributors and reviewers**: this repository is produced by the **Making Change project contributors** and is shared, over the same period and up to the closure of the thesis, with the **industry professionals associated with the review**.
>
> **No individual is named**: no person is identified in this repository — neither in the code, the documentation, nor the working documents — until their explicit consent has been obtained.

---

## Objective and Positioning

**Making Change** explores how foreign exchange (FX) risk affects infrastructure financing and how different hedging scenarios can alter debt service and the Debt Service Coverage Ratio (DSCR).

The current prototype is an **exploratory and educational simulation tool**. It does **not** constitute **a market forecast, a live market quote, or financial/investment advice**.

---

## Getting Started

Python 3.10 or higher. From a terminal opened at the repository root:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Unit tests (engine and web layer):

```bash
python -m unittest discover -s tests -v
```

---

## Start here: the one-file dashboard

`simple/index.html` is the entry point. One file, no dependency, no server, no
install, no Internet: open it in a browser and it works.

```bash
xdg-open simple/index.html      # macOS: open / Windows: double-click
```

It contains, in this order: the case, five sliders (shock, hedged share, cost of
cover, covenant, avoided CO2e), four KPI cards, a DSCR chart year by year, the
annual table, and the carbon reading. About 500 lines of HTML, CSS and vanilla
JavaScript, with the model in **20 readable lines** at the top of the script.

Two guarantees:

- **The numbers are tested.** `tests/test_simple.py` extracts the page's own
  JavaScript, runs it under node, and compares every row against `model.py`; it
  also executes `render()` against a DOM stub so a typo cannot ship silently.
- **The origin is visible.** Served from a static host it is a live page; opened
  from disk it is the same page. Nothing is fetched, so nothing can fail quietly.

The Flask desk described below is the fuller version (managers, live FX feed,
JSON API). Keep it for later: the single file is what a jury, a classmate, or a
treasurer can actually open.

---

## The web desk (main interface)

A Flask site whose design follows **ShockDesk**: dark surface, mint accent,
monospace URL bar, underlined tabs, dense KPI cards. One page explains the
mechanism, and **every result is a URL** that can be replayed, cited, or argued
with in a footnote.

```bash
python -m desk.webapp          # http://localhost:5000
```

| Tab | Question | Side |
| :--- | :--- | :--- |
| Desk | Headline KPIs: shock P&L, minimum DSCR, cost of cover, break-even cover | Market |
| Exposure | The two dials: simulated shock, hedged share, hedged rate, cost, covenant | Market |
| Scenarios | DSCR year by year, hedged vs unhedged, with the covenant line | Market |
| Grid | Shock x coverage matrix, green above covenant, red below 1.00x | Market |
| Green | Debt service and shock cost **per tCO2e avoided** by the asset | Green |
| Market & doc | Live FX panel with provider status, and what the feed may not be used for | Market |
| Code | Every hedge manager as source, ShockDesk style | Both |

### Hedge managers

A manager is a Python file, not a black box: it receives a `HedgeView` (years,
capacity, shock, spot **with its provenance**, hedged rate, cost, covenant, and a
`dscr_with(coverage)` callable) and returns a coverage share plus the reasoning.
It never does the loan arithmetic, so it cannot disagree with the tested engine.

| Key | Manager | Family |
| :--- | :--- | :--- |
| `none` | No hedge (reference) | reference |
| `threshold` | Covenant threshold seeker | optimiser |
| `slice` | Equal slices ladder | ladder |
| `carry` | Carry-aware manager | tactical |
| `full` | Full hedge | static |

Add one by subclassing `Manager` in `desk/managers.py` and registering it in
`MANAGERS`. No build step, no plugin API.

### Market data

`desk/market.py` is an offline-first client with an explicit fallback chain:

```
open.er-api.com  ->  api.frankfurter.dev  ->  on-disk cache  ->  scenario assumption
```

- Cache TTL 12 h (`MC_CACHE_TTL`), cross through EUR when a provider does not
  quote the pair directly.
- `MC_LIVE_DEFAULT=1` tries a live rate on first load; `MC_OFFLINE=1` never
  touches the network.
- These are **daily reference rates**: not a dealer quote, not bid/offer, not
  executable, no forward points. The hedged rate and its cost stay user inputs.
- When no provider answers, the page says *assumption* and shows the scenario
  value with its date. Degradation is visible, never silent.

### Routes

```
GET /                     desk (all state in the query string)
GET /scenarios/<key>      switch scenario        GET /managers/<key>  switch manager
GET /market               FX panel + provider status
GET /code                 managers as source
GET /api/simulate         same numbers as JSON      GET /api/managers   manager list
GET /export.csv           annual table              GET /healthz        liveness
```

### Deploy on Render

`render.yaml` (blueprint) and `Procfile` are included: one free web service,
gunicorn, no database, no secrets. Push the branch, then *New > Blueprint* in
Render and point it at the repository. Set `MC_LIVE_DEFAULT=1` to try the live
feed; leave it at `0` for a fully offline, reproducible demo.

All user-facing text is in English, per repository rule. The Streamlit prototype
`app.py` is kept as the original quick-look interface and is not maintained in
parallel.

---

## Repository Structure

```text
Making-Change/
├── app.py                          # Legacy Streamlit interface (kept for reference)
├── model.py                        # Pure calculation engine (Inputs, simulate)
├── simple/index.html               # ← one-file dashboard, start here
├── desk/                           # Flask desk — fuller version
│   ├── webapp.py                   # routes, URL state, CSV + JSON export
│   ├── engine.py                   # orchestration over model.py (no formulas)
│   ├── scenarios.py                # dated scenarios + exchange-rate regimes
│   ├── managers.py                 # hedge managers (one class = one file)
│   ├── market.py                   # offline-first FX client, explicit fallback
│   ├── templates/                  # base, desk, market, code
│   └── static/                     # ShockDesk-style CSS, vanilla JS
├── render.yaml / Procfile          # one-service deploy, no database
├── .python-version
├── requirements.txt                # Python dependencies
├── UTILISATION-IA.md               # AI transparency log & SKEMA anti-plagiarism compliance
├── tests/
│   ├── test_model.py               # Engine unit tests
│   ├── test_webapp.py              # Routes, managers, market fallback, green
│   └── test_simple.py              # HTML/JS parity with model.py
├── docs/
│   ├── METHODOLOGIE.md             # Formulas, FX conventions, and model limitations
│   ├── SOURCES-ACADEMIQUES.md      # Prototype academic framing notes
│   ├── REFERENCES-ACADEMIQUES.md   # Structured academic bibliography with DOI links
│   └── ressources-externes/        # External documents / reports found online
├── data/
│   └── interviews-anonymisees/     # Anonymized field data and banking interviews
└── these/                          # Thesis working documents (drafts, bibliography)
```

---

## Scope, Limitations, and Confidentiality

- **Exchange rate regimes**: For pegged currencies (e.g., `XAF/EUR`), any simulated depreciation is a **hypothetical parity-break scenario**, not an ordinary market fluctuation. The regime is an attribute of each scenario, not a note added afterwards.
- **Green figures**: the avoided-CO2e input is supplied by the user and shown with its basis. It is never presented as measured, and no causal link between hedging and climate outcomes is claimed.
- **No person is named**: not in the code, the documentation, the interface, or the working documents, pending explicit consent.
- **AI transparency**: In accordance with SKEMA Business School anti-plagiarism requirements, all generative AI assistance (prompts, queries, edits) is logged in [`UTILISATION-IA.md`](UTILISATION-IA.md).
- **Confidentiality**: No personal data, banking secrets, or non-anonymized interviews may be published in this repository.
