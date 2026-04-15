# Econometric Models for Analyzing the Korea Discount

Based on the literature review, the following econometric approaches are most effective for quantifying the discount and testing policy impacts.

## 1. Valuation Metrics (Dependent Variables)
*   **Tobin’s Q:** The standard proxy for firm value, calculated as (Market Value of Equity + Book Value of Liabilities) / Book Value of Total Assets.
*   **Price-to-Book (P/B) & Price-to-Earnings (P/E) Ratios:** Used for cross-country panel comparisons (KOSPI vs. S&P 500 vs. TOPIX).
*   **Implied Cost of Capital (ICC):** Used to measure the "risk premium" associated with the discount.

## 2. Regression Frameworks
### A. Panel Data Regression (Fixed Effects)
Used to analyze a 20-year panel of valuation data while controlling for firm-specific and time-invariant factors.
$$Valuation_{it} = \alpha + \beta_1(Chaebol_{it}) + \beta_2(Governance_{it}) + \beta_3(GPR_t) + \gamma X_{it} + \eta_i + \delta_t + \epsilon_{it}$$
*   $X_{it}$: Controls (Size, Leverage, R&D intensity, ROE).
*   $\eta_i, \delta_t$: Firm and year fixed effects.

### B. Natural Experiment: Difference-in-Differences (DiD)
To evaluate the impact of policy reforms (e.g., Japan's 2023 TSE reform as a treatment).
*   **Treatment Group:** Japanese firms (or Korean firms post-Value-Up).
*   **Control Group:** Similar firms in markets without equivalent reforms (e.g., MSCI EM peers).

### C. GMM (Generalized Method of Moments)
Used to handle **endogeneity**—specifically the reverse causality between ownership structure and firm valuation.

## 3. Geopolitical Risk Modeling
*   **GPRNK Index:** A textual analysis-based index (constructed by IMF researchers) that counts the frequency of North Korean provocation keywords in global media. 
*   **Event Study Methodology:** Used to measure the abnormal returns (AR) and cumulative abnormal returns (CAR) surrounding specific "brinkmanship" events.
