# Academic audit — static dashboard

Date: 2026-11-27. Scope: `docs/index.html`, `docs/dashboard.js`, `docs/dashboard.css` and the synchronized standalone version `simple/index.html`. The Flask desk is not revised by this audit.

## Findings and corrections

- The CEMAC loan was not an empirical company case. It is now explicitly a fictional infrastructure SPV: a classical contractual currency-mismatch teaching example, not a case reproduced from an academic publication.
- Principal, tenor, interest, CFADS and threshold are illustrative assumptions, not observations extracted from the cited papers. The page now provides a parameter register.
- XAF/EUR stress represents a hypothetical parity break, not ordinary market volatility. Depreciation d implies S/(1-d); a 20% loss in external currency value implies a 25% increase in XAF/EUR.
- The hedge rate equals initial spot for all maturities. The annual charge is a proportion of covered debt service converted at that rate, not a premium on outstanding principal. This is not a market-priced forward or evidence that a 15-year hedge is available.
- The DSCR calculation includes the illustrative charge in hedged debt service. CFADS is constant, annual principal repayments are equal and the stress applies immediately to every year. No discounting or endogenous investment behaviour is represented.
- The carbon panel has been removed: no verified emissions baseline, counterfactual or additionality evidence supported its environmental interpretation.
- Selected existing academic references now appear beside their limits. Association between derivative use and firm value must not be described as causal proof for this SPV.
- The interface is white with restrained colours, visible keyboard focus and printable panels.

## Source and case policy

The existing reference register supplies the bibliography for this pass. Publisher pages and full papers have **not been independently re-verified in this session**. This audit establishes transparent scope and internal consistency, not strict replication of a published academic model.

A real company or published teaching case may be added only with an accessible, precisely identified source (author, title, year, page/table), source-supported cash flows and debt characteristics, and a clear separation of observed and assumed inputs. Do not invent company figures or imply permission to reproduce proprietary teaching materials.

Allayannis & Weston (2001) concerns US non-financial firms; Froot et al. (1993) provides a theory of financing frictions; Adler & Dumas (1984) defines broader economic exposure; Kleimeier & Megginson (2000) frames project finance. None calibrates this constructed SPV or validates the simplified hedge pricing.

## Remaining research work

Select and verify an empirical or published teaching case before claiming case replication. Independently verify the bibliography, document the institutional peg with an authoritative source, and calibrate hedge term structure, CFADS responses and transaction constraints if moving beyond pedagogy. The existing full reference register remains a research bibliography, not a list of validated model inputs.
