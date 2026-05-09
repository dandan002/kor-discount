# Domain Pitfalls

**Domain:** Quantitative finance academic paper — cross-country equity valuation panel, staggered event study, panel OLS, synthetic control
**Researched:** 2026-04-14
**Confidence:** HIGH for econometric methodology pitfalls (well-established literature); MEDIUM for data-sourcing specifics (depends on final source choice)

---

## Critical Pitfalls

Mistakes that cause paper rejection, major rewrites, or invalid causal claims.

---

### Pitfall 1: Staggered DiD with Heterogeneous Treatment Effects (Negative Weighting Problem)

**What goes wrong:**
Standard two-way fixed effects (TWFE) OLS with a single post-treatment dummy — `treated_country * post` — produces a weighted average of treatment effects where some weights are *negative* when treatment timing is staggered. With three Japan reform dates (2014, 2015, 2023), "already-treated" periods from earlier reforms contaminate the comparison group for later reforms. The OLS estimand is not the ATT — it can be sign-reversed even when every cohort-specific effect is positive.

**Why it happens:**
TWFE implicitly uses already-treated units as controls for later-treated units. Callaway & Sant'Anna (2021), Goodman-Bacon (2021), and Sun & Abraham (2021) formalize this. With only one treated country (Japan) and three events, the contamination is from the same unit across time, not across units — but the logic still applies: the 2023 regression residual is influenced by post-2014 and post-2015 regime changes baked into Japan's "baseline."

**Consequences:**
Referee will flag this immediately. If effects are heterogeneous across reforms (plausible — TSE 2023 was structural, 2014/2015 softer), the aggregate TWFE coefficient will be biased in unknown direction.

**Prevention:**
- Do not use a single stacked `reform_intensity * post` dummy across all three events in one TWFE regression.
- Run separate regressions for each reform event using a clean pre-period window with no overlap from prior reforms.
- Or use an "event-stacking" design (Cengiz et al. 2019): create one dataset per event with a symmetric window, exclude contaminated periods, stack datasets, and include event-by-cohort fixed effects.
- Explicitly acknowledge in paper that with one treated unit, standard heterogeneous-treatment corrections (Callaway-Sant'Anna) cannot be applied mechanically — present the separate-event approach as the honest alternative.

**Detection:**
- If your single pooled TWFE coefficient is small or wrongly signed but individual event windows look positive — negative weighting is likely the cause.
- Goodman-Bacon decomposition (if using Stata/R) can quantify the negative-weight share; Python equivalent requires manual calculation but the logic is auditable.

**Severity:** CRITICAL
**Phase to address:** Data pipeline and econometric specification (Phase: Panel OLS implementation)

---

### Pitfall 2: Event Study Pre-Trend Testing with Only One Country in the Treatment Group

**What goes wrong:**
Standard event study pre-trend tests (testing that pre-event coefficients are jointly zero) require cross-unit variation to identify differential trends. With Japan as the sole treated unit and Korea/S&P/MSCI EM as controls, you have N=4 countries, T~240 months. The parallel trends assumption is *untestable in the standard sense* — you cannot run a Hausman-style test when there is one treated observation per period.

**Why it happens:**
The "parallel trends" assumption is an identifying assumption, not a testable hypothesis, when treatment is binary and unit-invariant per period. Visual pre-trend inspection remains valid and expected by reviewers, but formal statistical tests have near-zero power and can create false confidence if they "pass."

**Consequences:**
Overclaiming causal identification. Reviewers of top finance journals will immediately note this limitation. If not disclosed, the paper looks naive; if disclosed properly, it is acceptable as a well-identified quasi-experiment with acknowledged limitations.

**Prevention:**
- Present pre-trend plots (event-time coefficients) with confidence intervals — visual inspection is the honest standard here.
- Explicitly state in the identification section: "Given that Japan is the sole treated unit, formal parallel trends tests lack power. We present pre-trend event-time coefficients as descriptive evidence and do not overstate causal identification."
- Lean on the synthetic control as the causal robustness check, not the TWFE as the primary causal claim.
- Use placebo tests: apply the same treatment dates to Korea (which did NOT reform) and show null effects.

**Detection:**
- If your event study shows pre-trend coefficients that are statistically insignificant but visually drifting — do not wave this away. Flag it.

**Severity:** CRITICAL
**Phase to address:** Event study implementation and paper framing (identification section)

---

### Pitfall 3: Synthetic Control Donor Pool Contamination

**What goes wrong:**
Including countries in the synthetic control donor pool that were themselves affected by Japan's reforms (via contagion, regional governance spillovers, or correlated macro shocks) violates the SUTVA assumption and inflates the apparent treatment effect. For the 2023 TSE reform specifically, any market that responded positively to Japanese governance activism (e.g., Taiwan, Hong Kong-listed China tech) contaminates the control.

**Why it happens:**
Researchers default to "all available MSCI constituents" or "all comparable markets" as the donor pool without checking for cross-market contamination. The synthetic control literature (Abadie, Diamond, Hainmueller 2010; Abadie 2021) requires donor units to be unaffected by treatment.

**Consequences:**
If contaminated donors are included, the synthetic Japan will itself be partially "treated," making the gap between actual and synthetic Japan smaller than the true effect. The treatment effect is understated — or worse, if contaminated donors drift in the opposite direction, it can be overstated.

**Prevention:**
- Explicitly justify each donor pool member in the paper. For the 2023 TSE reform, argue why, say, the MSCI Europe index is a valid donor but MSCI Asia ex-Japan may not be.
- Run robustness checks with restricted donor pools (e.g., OECD developed markets only; EM-only; exclude Asia-Pacific).
- Document what changes when you remove potentially contaminated donors.

**Detection:**
- If the synthetic control weight assigns >30% to a single donor that had a contemporaneous governance shock — investigate.
- Check if donor weights change substantially when you exclude Asia-Pacific comparators.

**Severity:** CRITICAL
**Phase to address:** Synthetic control implementation

---

### Pitfall 4: Survivorship Bias in Index Constituent Valuation Data

**What goes wrong:**
Using current-index P/B or P/E aggregates sourced from historical databases that reflect current (or recent) index constituents — not the constituents that existed in each historical period. KOSPI and TOPIX both had constituent changes, delistings, and additions. If the 2004 TOPIX P/B is calculated using 2024 constituents backcasted, the time series is survivorship-biased upward (failed companies are excluded).

**Why it happens:**
Free data sources (Yahoo Finance, Macrotrends, some FRED series) often report index-level valuation ratios without clarifying whether they reflect point-in-time constituent weights or current-day reconstituted constituents. Bloomberg/Refinitiv historical data generally uses point-in-time constituents, but export errors still occur.

**Consequences:**
Overestimates index P/B in early periods (only survivors remain, all of which look cheaper in hindsight than the full distribution including failed firms). Understates the Korea Discount's persistence if Korean survivorship bias is symmetric or greater.

**Prevention:**
- Document the exact data source for each valuation series, including whether it is point-in-time constituent-weighted.
- Prefer sources that explicitly state "total return index" or "point-in-time constituent" methodology — e.g., MSCI's own published factsheets, DataStream with point-in-time flags.
- For FRED/Yahoo Finance sourced series: state the limitation explicitly in a data section footnote and note the direction of bias.
- Cross-check with at least one academic or official secondary source (e.g., World Bank equity market indicators, IMF GFSR data) for multi-year plausibility.

**Detection:**
- If P/B for KOSPI pre-2010 looks suspiciously smooth or high relative to known crisis periods (2008 GFC: KOSPI P/B should have compressed sharply) — suspect survivorship contamination.
- Check that your 2008-2009 period shows a sharp dip and recovery, not a smooth trend through the crisis.

**Severity:** CRITICAL
**Phase to address:** Data pipeline and sourcing (Phase: Data collection and cleaning)

---

### Pitfall 5: Look-Ahead Bias via Reform Date Selection

**What goes wrong:**
Selecting the Japan reform event dates (2014, 2015, 2023) *after* eyeballing the valuation time series and noticing that those dates correspond to observed inflection points. This is a subtle form of specification search / p-hacking: the dates "work" in part because they were chosen to match observable movements.

**Why it happens:**
Researchers with subject-matter knowledge often "know" the important dates but have also seen the data. The Japan Stewardship Code (2014) and Corporate Governance Code (2015) are well-documented in the literature (Miyajima et al., Becht et al.), so using them is defensible — but only if the researcher can demonstrate the dates were fixed ex ante based on policy records, not post-hoc visual selection.

**Consequences:**
Even if unintentional, a reviewer who suspects date-mining can dismiss the findings. Significant coefficients around hand-picked dates are weaker evidence than pre-registered or literature-validated dates.

**Prevention:**
- Cite the specific policy implementation dates from official FSA/TSE announcements and the existing academic literature *before* running any regressions. Lock event dates in the data pipeline.
- State in the paper: "Event dates are fixed based on official FSA publication dates and established prior literature (cite Miyajima et al., Becht et al.) rather than identified from data patterns."
- Run robustness: shift each event date ±3 months and ±6 months and show the core result is not sensitive to exact date selection.

**Detection:**
- If your event study windows happen to align perfectly with visible market inflection points with no pre-specified justification — you may have look-ahead bias.

**Severity:** CRITICAL
**Phase to address:** Event study specification (before any regressions are run)

---

## Moderate Pitfalls

---

### Pitfall 6: Standard Error Clustering — Too Few Clusters

**What goes wrong:**
Panel OLS with country/time fixed effects requires clustering standard errors. The natural choice is clustering by country. But with N=4 countries, you have 4 clusters — far below the threshold (~30-50) where cluster-robust standard errors are reliable. Small-cluster clustering can produce standard errors that are too small (over-rejection of null) or unstable.

**Prevention:**
- Use the wild cluster bootstrap (Cameron, Gelbach & Miller 2008) as the primary inference method for the country-clustered errors. The `wildboottest` package exists for Python (or use the `wildclusterboot` implementation).
- Alternatively, cluster at the year level (20+ clusters) with country fixed effects absorbed — more clusters, at the cost of not accounting for country-level serial correlation.
- Report both clustering choices in a robustness table. Acknowledge the small-N problem explicitly.
- Consider heteroskedasticity-robust (HC3) standard errors as a secondary check.

**Detection:**
- If country-clustered SEs are dramatically smaller than HC-robust SEs for the same specification — small-cluster problem is active.

**Severity:** MODERATE
**Phase to address:** Panel OLS implementation

---

### Pitfall 7: Currency and Accounting Standard Differences in P/B Comparisons

**What goes wrong:**
Comparing P/B ratios across Japan (IFRS or J-GAAP), Korea (K-IFRS, converged 2011), and the US (US GAAP) treats accounting book values as equivalent when they are not. Key differences:
- Goodwill treatment (US GAAP requires impairment testing; J-GAAP historically allowed amortization; IFRS requires impairment)
- Pension liability recognition (US GAAP full recognition on-balance-sheet; J-GAAP historically off-balance or smoothed)
- Cross-shareholding book values vs. market values under each standard

Additionally, all values must be in a common currency or the analysis must explicitly account for currency effects, since yen depreciation (especially post-Abenomics 2013) affects yen-denominated P/B relative to USD-denominated comparators.

**Prevention:**
- Use P/B and P/E ratios as reported by a single data provider that normalizes for accounting differences (e.g., MSCI or Bloomberg's normalized ratios).
- If using raw index data, state in the paper which accounting standard is in effect for each country-period and note that accounting differences are a potential confound.
- For currency: state clearly whether you are comparing local-currency P/B (preferred for pure governance signal) or USD-translated P/B (preferred for global investor comparison). Do not mix the two.
- The 2013 yen depreciation creates a structural break in currency-translated metrics — this must be controlled for or explicitly acknowledged.

**Detection:**
- Check if Japan's apparent P/B "jump" in 2013 is real governance-driven or largely yen-depreciation-driven (book values fell in USD terms as yen weakened, which *raises* P/B if market cap adjusts less than book value in USD).

**Severity:** MODERATE
**Phase to address:** Data cleaning and variable construction

---

### Pitfall 8: Misspecifying the Synthetic Control Pre-Treatment Fit Period

**What goes wrong:**
The synthetic control's validity depends on the synthetic unit closely tracking the treated unit in the pre-treatment period. If the pre-treatment fit window is too short (e.g., only 2-3 years before 2023), the weights may fit noise rather than signal, and the synthetic control will not generalize to the counterfactual.

**Prevention:**
- Use the full available pre-treatment period (ideally 10+ years before 2023, i.e., 2004-2022 for the 2023 TSE reform).
- Report the RMSPE (root mean squared prediction error) for the pre-treatment period — a standard goodness-of-fit metric for synthetic control.
- If pre-treatment RMSPE is high relative to the post-treatment gap, the synthetic control result is unreliable — say so.
- Use predictor variables beyond just lagged P/B: include GDP growth, earnings growth, dividend yield, or corporate governance index scores as predictors, not just the outcome variable.

**Detection:**
- Pre-treatment fit plot: if synthetic TOPIX visually diverges from actual TOPIX in the pre-period by more than 0.1-0.2 P/B units on average, the fit is poor.

**Severity:** MODERATE
**Phase to address:** Synthetic control implementation

---

### Pitfall 9: Confounding Abenomics Macro Effects with Governance Reform Effects

**What goes wrong:**
Japan's Stewardship Code (2014) and Corporate Governance Code (2015) were implemented as explicit pillars of Abenomics' "Third Arrow" structural reform agenda. They occurred simultaneously with aggressive QQE monetary expansion (BOJ's 2013 QQE announcement, 2014 expansion) and fiscal stimulus. Any estimated governance effect is potentially confounded by the macro policy environment, which also boosted corporate earnings and equity valuations.

**Why it happens:**
Single-country natural experiments cannot partial out contemporaneous macro shocks without strong assumptions. The governance reforms were not randomly timed — they were part of a deliberate macro-policy package.

**Prevention:**
- Include macro control variables in the panel OLS: BOJ balance sheet size (as % GDP), 10-year JGB yield, Japan unemployment rate, Japan ROE or earnings growth — to partial out the macro channel.
- In the event study, compute abnormal valuation changes relative to an index that also benefited from Abenomics macro (e.g., subtract out a Japan equity return benchmark), isolating the *governance-specific* increment.
- In the paper, explicitly discuss the identification threat and argue why the governance mechanism is separate from the pure macro stimulus (e.g., governance effects should be persistent and sector-specific to firms with weak governance; macro effects are broad).

**Detection:**
- If your estimated treatment effect is largest in 2013 (QQE announcement) rather than 2014/2015 (governance codes) — confounding is active.

**Severity:** MODERATE
**Phase to address:** Panel OLS specification and identification section

---

### Pitfall 10: Treating MSCI EM as a Stable Benchmark

**What goes wrong:**
MSCI Emerging Markets index constituents and country weights change materially over a 20-year period. China went from ~5% to ~35% weight between 2004 and 2020 (due to A-share inclusion). The MSCI EM P/B in 2004 is largely a BRICs measure; by 2020 it is substantially a China growth measure. Using MSCI EM as a stable "EM average" comparison or donor pool constituent conflates these regime changes.

**Prevention:**
- Note the China weight change in the data section. Consider using MSCI EM ex-China as a robustness check for the post-2017 period.
- When using MSCI EM as a synthetic control donor or OLS control, include China weight or China GDP share as a time-varying control.
- Do not treat MSCI EM P/B as a "pure EM" counterfactual — it is heavily China-influenced.

**Detection:**
- If MSCI EM P/B trend changes sharply around 2018-2020 (China A-share inclusion phases), that is an index composition change, not a governance or economic signal.

**Severity:** MODERATE
**Phase to address:** Data pipeline and variable construction

---

### Pitfall 11: Serial Autocorrelation in Valuation Ratios Inflating Significance

**What goes wrong:**
P/B and P/E ratios are highly autocorrelated (AR(1) coefficients typically 0.90-0.97 at monthly frequency). Standard OLS standard errors — even with time fixed effects — do not account for this serial correlation. The result: t-statistics are inflated and p-values are spuriously small.

**Prevention:**
- After estimating the panel OLS, test residuals for serial correlation (Durbin-Watson, Breusch-Godfrey).
- Use Newey-West standard errors with bandwidth set to at least 12 months (monthly data) or use Driscoll-Kraay standard errors which correct for both cross-sectional and temporal dependence.
- `statsmodels` supports Newey-West via `cov_type='HAC'` with the `maxlags` parameter. Use `maxlags=12` for monthly data, `maxlags=4` for quarterly.
- First-differencing as a robustness check removes most serial correlation and tests whether *changes* in valuation ratios respond to reforms — a useful complement.

**Detection:**
- Durbin-Watson statistic far below 2 in OLS residuals.
- Coefficient on lagged residuals in AR(1) auxiliary regression is significant.

**Severity:** MODERATE
**Phase to address:** Panel OLS implementation

---

## Minor Pitfalls

---

### Pitfall 12: Reproducibility — Hard-Coded Dates and Paths

**What goes wrong:**
Event dates, sample start/end dates, and file paths scattered across multiple notebooks with no single source of truth. A reviewer requests "what if you extend the sample to 2025?" requires changes in 12 places, some of which get missed.

**Prevention:**
- Define all event dates, sample bounds, and key parameters in a single `config.py` or `params.yaml` file. All notebooks/scripts import from there.
- Use relative paths with a project root anchor, not absolute paths.
- Verify the repo is reproducible from scratch: delete all intermediate outputs, run the pipeline end-to-end, confirm all figures regenerate.

**Severity:** MINOR
**Phase to address:** Repository setup

---

### Pitfall 13: P/E Ratio Instability Near Zero Earnings

**What goes wrong:**
P/E ratios become undefined or meaningless when aggregate index earnings approach zero (e.g., during recessions). The 2008-2009 GFC caused negative or near-zero earnings for several indices. If your panel includes P/E as a valuation metric, the 2009 observations may be missing, infinite, or extreme outliers that distort regressions.

**Prevention:**
- Prefer P/B as the primary valuation metric for cross-country comparisons — it is more stable across cycles.
- If using P/E, winsorize at the 1st and 99th percentiles of the distribution and document this.
- Alternatively, use trailing 12-month EPS smoothed over a cycle (Shiller CAPE/CAPE-equivalent) which is more stable.
- Check how many observations are missing or flagged for P/E in 2008-2010 and note in the data section.

**Severity:** MINOR
**Phase to address:** Data cleaning

---

### Pitfall 14: Confusing Calendar-Year vs. Fiscal-Year Valuation Data

**What goes wrong:**
Japan and Korea corporations predominantly have March and December fiscal year-ends respectively. Index-level P/B reported as "2015" may reflect March 2016 book values for Japan (fiscal year ending March 2016) but December 2015 book values for Korea. This 0-3 month misalignment is usually acceptable for annual data but can create spurious lead-lag patterns if not noted.

**Prevention:**
- Document fiscal year conventions for each index in the data section.
- For monthly data (preferred), this issue is less severe — use month-end price and trailing book value.
- If using annual data, note the fiscal year mismatch as a limitation and check robustness by shifting Japan's annual observations by one quarter.

**Severity:** MINOR
**Phase to address:** Data cleaning

---

### Pitfall 15: Inference Inflation from Multiple Testing Across Three Reform Events

**What goes wrong:**
Running event studies for three reform dates (2014, 2015, 2023) without adjusting for multiple comparisons. If each test uses alpha=0.05, the family-wise error rate across three tests is ~14%. A result that is "significant at 5% for each event" may simply reflect the 14% chance of one false positive.

**Prevention:**
- Apply Bonferroni correction (alpha/3 = 0.017) or Benjamini-Hochberg correction for the three event tests.
- Frame the three events as a *stacked* argument: if all three show the same directional effect, the joint evidence is strong even if individual p-values are marginal.
- Use joint significance tests rather than three separate individual tests where possible.

**Severity:** MINOR
**Phase to address:** Event study implementation and reporting

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Data collection | Survivorship bias in historical index P/B | Verify point-in-time constituent methodology for each source |
| Data collection | MSCI EM composition drift (China weight) | Document and consider EM ex-China robustness |
| Data cleaning | P/E instability in 2008-2009 | Prefer P/B; winsorize or drop extreme P/E |
| Data cleaning | Currency/accounting standard differences | Use single normalized source or document standard per country-period |
| Event study specification | Look-ahead date selection | Lock event dates to policy records before running any regressions |
| Event study specification | Multiple testing inflation | Apply Bonferroni or BH correction across three reform events |
| Panel OLS implementation | Staggered TWFE negative weighting | Separate regressions per event or event-stacking design |
| Panel OLS implementation | Serial autocorrelation in valuation series | Newey-West or Driscoll-Kraay SEs; test residuals |
| Panel OLS implementation | Few clusters (N=4 countries) | Wild cluster bootstrap; also cluster by time |
| Panel OLS identification | Abenomics macro confound | Include BOJ balance sheet, JGB yield as controls; discuss in paper |
| Panel OLS identification | Parallel trends untestable | Visual pre-trends + placebo tests on untreated countries |
| Synthetic control | Donor pool contamination | Justify each donor; robustness with restricted pools |
| Synthetic control | Short pre-treatment fit window | Use full available pre-period (2004-2022 for 2023 reform) |
| Synthetic control | Poor predictor selection | Include earnings growth, governance scores, not just lagged P/B |
| Reproducibility | Hard-coded dates and paths | Single config file; end-to-end pipeline test |

---

## Sources and Confidence Notes

**HIGH confidence (well-established econometric literature, stable through 2025):**
- Staggered DiD / negative weighting: Goodman-Bacon (2021, QJE); Callaway & Sant'Anna (2021, JoE); Sun & Abraham (2021, JoE). These are foundational and widely cited. The practical implication for single-treated-unit designs is a direct application.
- Synthetic control methodology: Abadie, Diamond & Hainmueller (2010, JASA); Abadie (2021, JEL review). Donor pool SUTVA requirement is canonical.
- Small-cluster inference: Cameron, Gelbach & Miller (2008, REStat). Wild cluster bootstrap is the standard recommendation.
- Newey-West / HAC standard errors: Newey & West (1987, Econometrica). Routine in panel finance.

**MEDIUM confidence (domain-specific, based on training knowledge, no live verification):**
- MSCI EM China weight trajectory: approximately accurate but exact percentages should be verified against MSCI's published factsheets.
- Specific Python package availability (`wildboottest`): verify at time of implementation; alternatives may exist.
- J-GAAP vs. IFRS goodwill/pension accounting specifics: directionally correct, but accounting standard details should be verified against FSA/ASBJ publications for the exact transition year.

**Flags for validation (LOW confidence without live source verification):**
- Whether any single free public source provides point-in-time constituent P/B for KOSPI going back to 2004. This needs explicit verification during the data sourcing phase.
