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

Unit tests (no external dependencies required):

```bash
python -m unittest discover -s tests -v
```

---

## Repository Structure

```text
Making-Change/
├── app.py                          # Streamlit user interface
├── model.py                        # Pure calculation engine (Inputs, simulate)
├── requirements.txt                # Python dependencies
├── UTILISATION-IA.md               # AI transparency log & SKEMA anti-plagiarism compliance
├── tests/
│   └── test_model.py               # Reproducible unit tests
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

- **Exchange rate regimes**: For pegged currencies (e.g., `XAF/EUR`), any simulated depreciation is a **hypothetical parity-break scenario**, not an ordinary market fluctuation.
- **AI transparency**: In accordance with SKEMA Business School anti-plagiarism requirements, all generative AI assistance (prompts, queries, edits) is logged in [`UTILISATION-IA.md`](UTILISATION-IA.md).
- **Confidentiality**: No personal data, banking secrets, or non-anonymized interviews may be published in this repository.
