# AI Usage Log — Transparency & Anti-Plagiarism Compliance (SKEMA Business School)

This document transparently records the use of Artificial Intelligence (AI) tools within the **Making Change** project and the associated thesis:

*Making Change: How FX Risk Management Enables Sustainable Infrastructure Financing in Africa and Latin America.*

In accordance with **SKEMA Business School** academic integrity and anti-plagiarism standards, all generative AI assistance is declared, traced, and subject to strict human and bibliographic verification.

---

## 1. Guiding Principles

1. **No delegation of academic judgment**: AI is never used as a financial or academic source of truth. Every theoretical or empirical claim must be verified against the original peer-reviewed publication (DOI / publisher).
2. **Traceability**: User queries, prompts, and major interventions on code or documentation are logged below.
3. **Strict separation**: Code, modeling hypotheses, simplifications, and academic literature findings are explicitly separated.
4. **Confidentiality**: No personal data, banking secrets, or non-anonymized interviews are shared or published in the repository.

---

## 2. Log of Queries and AI Interventions

| Date | Stage | User Query / Prompt (faithful summary) | Action Performed with AI | Human Validation Required |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-26 | Initial audit | "Start by reading the repository and auditing the existing prototype: explain what works, potential errors or risks, and open questions to resolve. Do not build a full platform before this discussion." | Inventoried `making-change-projet.zip` (12 files), ran the 3 unit tests (`unittest`), verified FX/DSCR formulas, and identified financial risks (free-hedge illusion, cost base ambiguity, XAF/EUR regime, causal over-interpretation) and academic gaps. | Contributors' review of limitations and validation of modeling choices prior to any development. |
| 2026-11-26 | Repository structuring | "Everything written in the repo including prompts and my queries must be explained in a dedicated 'AI usage' file, sources must be academic with links in a references doc, sign the README for [names withheld], create subfolders for anonymized data/interviews and docs found online, and write the GitHub docs in English." | Extracted the archive cleanly at the root, created `UTILISATION-IA.md`, `docs/REFERENCES-ACADEMIQUES.md`, `data/interviews-anonymisees/`, `docs/ressources-externes/`, and updated `README.md` in English. | Contributors' verification, SKEMA compliance, and public repository scope. (The README signature requested at this stage was later removed — see the 2026-11-27 row.) |
| 2026-11-27 | Anonymization of the repository | "In `README.md` and in any other file where personal names appear (including `UTILISATION-IA.md` if needed), remove the mentions of personal names (pair and supervisor) and replace the status block with a generic English formulation, without any person's name without their consent. Mention only the project contributors and the industry professionals associated with the review, up to the closure of the thesis (6-month horizon)." | Replaced the status block in `README.md` with a generic, name-free formulation (contributors + industry professionals associated with the review, 6-month horizon). Redacted names in this log. Also sanitized the PDF working document `these/draft-one-page.pdf` (visible text and document metadata) and rebuilt `making-change-projet.zip` from the sanitized copy — a name-free PDF cannot be regenerated here because the source generator of the original file is not in the repository. | Contributors' verification that no individual is named and that the anonymous formulation is acceptable to all parties concerned. |
| 2026-11-27 | Web desk design | "Let's start simple so everyone can understand the tool, the goal is to explain the scenarios, have a market side and a green side." Three structure options were proposed (minimal desk / research desk / explainer-first); the minimal single-page desk was chosen, extended with a carbon reading. | Built `desk/` (Flask + Jinja + vanilla JS, no build step): `scenarios.py` (three dated scenarios, each carrying its exchange-rate regime), `engine.py` (orchestration only — every calculation delegated to the tested `model.simulate`), `webapp.py` (URL-only state, CSV export), one page in five steps with a market section (shock, hedge, DSCR, grid) and a green section (cost per tCO2e). Added `tests/test_webapp.py` (14 tests: engine parity, URL reproducibility, input clamping, regime labelling, absence of personal names). | Contributors' verification of the financial wording, of the CO2e assumptions, and of the "what this does not say" blocks before any external presentation. |
| 2026-11-27 | ShockDesk-style desk v2 | "Imitate the ShockDesk design and link it to a live site, notably to work on exposures; use every possible tool, code in Python." | Rewrote the interface on a ShockDesk design language (dark surface, mint accent, monospace URL bar, tabs, KPI cards). Added `desk/managers.py` (five named hedge managers as auditable Python files, receiving a `dscr_with()` callable so they never touch loan arithmetic), `desk/market.py` (offline-first FX client: er-api -> frankfurter -> cache -> assumption, with the provenance of every rate shown on the page), a market panel, a code view, a JSON API (`/api/simulate`, `/api/managers`), and Render deployment files (`render.yaml`, `Procfile`). Tests: 26. | Contributors' check of every figure, of the "what this does not say" blocks, and of the wording used for a live rate before any external presentation. |
| 2026-11-27 | One-file dashboard | "Maybe this is too complex for a first thing — I suggest something simple, an HTML page for example, or a simple interactive Streamlit dashboard." | Built `simple/index.html`: a single self-contained file (no dependency, no server, no network) with the model in 20 readable JavaScript lines mirroring `model.py`, five sliders, KPI cards, a hand-drawn SVG chart, the annual table and the carbon reading. Added `tests/test_simple.py`, which runs the page's JavaScript under node and asserts row-by-row parity with the Python engine, plus a DOM-stub execution of `render()`. | Contributors' check that the simplified wording and the single page are enough for a first presentation, and that the duplicated model stays aligned. |

| 2026-11-27 | Academic Pages audit | User requested strict academic framing, classical cases and a white interface. | Audited the published static dashboard against the existing reference register; labelled the SPV as fictional, disclosed numerical assumptions and hedge limitations, removed unsupported carbon metrics, added selected academic links and a white theme; synchronized the standalone page. No new external source verification performed. | Contributors must validate bibliographic metadata and any future empirical case before publication. |

---

## 3. Update Rule

Any new AI-assisted work session (code additions, documentation drafting, bibliographic research) must add a row to the table above before pushing to the main branch.
