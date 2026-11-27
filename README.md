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

## The web desk (main interface)

A small Flask site, built for comprehension rather than features: one page
explains the mechanism in five steps, and **every result is a URL** that can be
replayed, cited, or challenged.

```bash
python -m desk.webapp          # http://localhost:5000
```

| Step | Question it answers | Side |
| :--- | :--- | :--- |
| 1. The shock | What does the currency move do to the debt? | Market |
| 2. The hedge | How much is covered, at what cost? | Market |
| 3. Can the project pay? | Minimum DSCR, year by year, against your threshold | Market |
| 4. Every combination | Shock × coverage grid, green above threshold, red below | Market |
| 5. Read in carbon terms | Debt service and shock cost **per tCO2e avoided** | Green |

Three dated scenarios ship with the site, each carrying its own exchange-rate
regime so a shock is never displayed without its label:

- `xaf-peg-infra` — CEMAC infrastructure loan, hard peg (XAF/EUR). A shock is a
  **hypothetical parity break**.
- `ghs-managed-solar` — West African solar IPP, managed float (GHS/USD).
- `brl-float-transport` — Latin American transport project, free float (BRL/USD).

Routes: `GET /` (desk), `GET /scenario/<key>` (switch scenario),
`GET /export.csv` (annual table). No API, no database, no session: all state is
in the query string. All user-facing text is in English, per repository rule.

The Streamlit prototype `app.py` is kept as the original quick-look interface; it
is not maintained in parallel.

---

## Repository Structure

```text
Making-Change/
├── app.py                          # Legacy Streamlit interface (kept for reference)
├── model.py                        # Pure calculation engine (Inputs, simulate)
├── desk/                           # Flask web desk — the main interface
│   ├── webapp.py                   # routes, URL state, CSV export
│   ├── engine.py                   # orchestration over model.py (no formulas)
│   ├── scenarios.py                # dated scenarios + exchange-rate regimes
│   ├── templates/desk.html         # one page, five steps
│   └── static/                     # style.css (market + green), app.js
├── requirements.txt                # Python dependencies
├── UTILISATION-IA.md               # AI transparency log & SKEMA anti-plagiarism compliance
├── tests/
│   ├── test_model.py               # Engine unit tests
│   └── test_webapp.py              # Routes, URL reproducibility, clamping
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
