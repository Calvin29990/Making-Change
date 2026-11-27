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
| 2026-11-26 | Initial audit | "Start by reading the repository and auditing the existing prototype: explain what works, potential errors or risks, and open questions to resolve. Do not build a full platform before this discussion." | Inventoried `making-change-projet.zip` (12 files), ran the 3 unit tests (`unittest`), verified FX/DSCR formulas, and identified financial risks (free-hedge illusion, cost base ambiguity, XAF/EUR regime, causal over-interpretation) and academic gaps. | Authors' review of limitations and validation of modeling choices prior to any development. |
| 2026-11-26 | Repository structuring | "Everything written in the repo including prompts and my queries must be explained in a dedicated 'AI usage' file, sources must be academic with links in a references doc, sign the README for Edwin, Mr. Ayundy and the jury, create subfolders for anonymized data/interviews and docs found online, and write the GitHub docs in English." | Extracted the archive cleanly at the root, created `UTILISATION-IA.md`, `docs/REFERENCES-ACADEMIQUES.md`, `data/interviews-anonymisees/`, `docs/ressources-externes/`, and updated `README.md` in English. | Authors' verification of names, SKEMA compliance, and public repository scope. |

---

## 3. Update Rule

Any new AI-assisted work session (code additions, documentation drafting, bibliographic research) must add a row to the table above before pushing to the main branch.
