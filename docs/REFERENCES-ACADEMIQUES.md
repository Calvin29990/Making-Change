# Academic References — Making Change

This document centralizes the academic references used in the **Making Change** project, along with their official links (DOI / publisher), core contributions, and **methodological limitations**.

> **Rigor rule**: None of the sources cited here directly validate the simplified formulas of the prototype (`model.py`). These references ground the research question and frame the modeling hypotheses.

---

## 1. FX Exposure and Corporate Risk Management

1. **Adler, M., & Dumas, B. (1984).** *Exposure to Currency Risk: Definition and Measurement.* Financial Management, 13(2), 41–50.
   - **Link**: <https://doi.org/10.2307/3665446>
   - **Contribution**: Defines economic FX exposure as the sensitivity of firm value to exchange rate changes, beyond accounting or contractual cash flows.
   - **Limitations**: Static 1984 theoretical framework; does not provide an operational DSCR formula or hedging pricing model.

2. **Froot, K. A., Scharfstein, D. S., & Stein, J. C. (1993).** *Risk Management: Coordinating Corporate Investment and Financing Policies.* The Journal of Finance, 48(5), 1629–1658.
   - **Link**: <https://doi.org/10.1111/j.1540-6261.1993.tb05123.x>
   - **Contribution**: Shows that risk management can create value when capital market imperfections make external financing costlier than internal cash flows.
   - **Limitations**: General corporate finance theory; does not model emerging-market capital constraints or project finance structures.

3. **Allayannis, G., & Weston, J. P. (2001).** *The Use of Foreign Currency Derivatives and Firm Market Value.* The Review of Financial Studies, 14(1), 243–276.
   - **Link**: <https://doi.org/10.1093/rfs/14.1.243>
   - **Contribution**: Finds a positive association between FX derivative use and firm value (Tobin's Q) across 720 large US non-financial firms (1990–1995).
   - **Limitations**: **Empirical association, not universal causal proof** (endogeneity and omitted-variable concerns). US large-cap sample, not directly transferable to SMEs or infrastructure SPVs in Africa or Latin America.

4. **Guay, W., & Kothari, S. P. (2003).** *How Much Do Firms Hedge with Derivatives?* Journal of Financial Economics, 70(3), 423–461.
   - **Link**: <https://doi.org/10.1016/S0304-405X(03)00179-X>
   - **Contribution**: Qualifies Allayannis & Weston (2001) by showing that corporate derivative portfolios are modest relative to overall firm-level risk exposure.
   - **Limitations**: Sample of large US corporations; does not cover project finance.

---

## 2. Emerging Markets, "Original Sin", and Hedging

5. **Eichengreen, B., Hausmann, R., & Panizza, U. (2005).** *The Pain of Original Sin.* In *Other People's Money: Debt Denomination and Financial Instability in Emerging Market Economies*, University of Chicago Press.
   - **Link**: <https://press.uchicago.edu/ucp/books/book/chicago/O/bo3637402.html>
   - **Contribution**: Documents the structural inability of many emerging economies to borrow long-term in their domestic currency, creating currency mismatches.
   - **Limitations**: Macroeconomic and structural analysis (2005 context); does not address micro-level hedging instruments.

6. **Alfaro, L., Calani, M., & Varela, L. (2021).** *Currency Hedging in Emerging Markets: Managing Cash Flow Exposure.* Harvard Business School Working Paper 21-096.
   - **Link**: <https://www.hbs.edu/faculty/Pages/item.aspx?num=57728>
   - **Contribution**: Analyzes OTC FX transactions in Chile (2005–2018): financial hedging is concentrated among large firms, natural hedging is limited, and forward premia are higher at longer maturities.
   - **Limitations**: Working paper covering a single country (Chile); generalization to Africa and the rest of Latin America remains to be tested.

---

## 3. Project Finance, Infrastructure, and Exchange Rate Regimes

7. **Kleimeier, S., & Megginson, W. L. (2000).** *Are Project Finance Loans Different from Other Syndicated Credits?* Journal of Applied Corporate Finance, 13(1), 75–87.
   - **Link**: <https://doi.org/10.1111/j.1745-6622.2000.tb00043.x>
   - **Contribution**: Shows that project finance loans carry longer maturities and rely on specific risk-allocation mechanisms.
   - **Limitations**: Pre-2000 dataset; does not specifically isolate FX risk.

8. **Hainz, C., & Kleimeier, S. (2012).** *Political Risk, Project Finance, and the Participation of Development Banks in Syndicated Lending.* Journal of Financial Intermediation, 21(2), 287–314.
   - **Link**: <https://doi.org/10.1016/j.jfi.2011.10.002>
   - **Contribution**: Examines the role of Development Finance Institutions (DFIs) in mitigating political risk.
   - **Limitations**: Focuses on political risk rather than currency risk.

9. **de Castro, L., Frischtak, C., & Rodrigues, V. (2025).** *Exchange Rate Risk and Infrastructure Investment.* Journal of Public Economic Theory, 27(1), e70003.
   - **Link**: <https://doi.org/10.1111/jpet.70003>
   - **Contribution**: Models the impact of FX volatility on long-term infrastructure investment (25–35 years) and studies concession-length adjustment as a risk-absorption mechanism.
   - **Limitations**: Results based on theoretical simulations; not an empirical validation of real-world projects.

10. **CFA / EUR Exchange Rate Regime (Historical Reference)**:
    - **Link**: <https://doi.org/10.1007/s11079-018-09520-8> (*The Euro and the CFA Franc: Evidence of Sectoral Trade Effects*, Open Economies Review, 2019).
    - **Contribution**: Recalls the institutional fixed-peg framework (`1 EUR = 655.957 CFA` since 1999, following the 50% devaluation in 1994).
    - **Limitations**: Focuses on sectoral trade effects; used here solely to justify labeling any XAF/EUR shock in the simulator as a **hypothetical parity-break scenario**.
