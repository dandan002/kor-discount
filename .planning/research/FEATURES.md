# Feature Landscape: Korea Discount Academic Paper

**Domain:** Quantitative finance / corporate governance academic paper (equity valuation, emerging markets, natural experiment identification)
**Researched:** 2026-04-14
**Confidence:** HIGH for structural norms (based on JF/JFE/RFS empirical standards and governance literature); MEDIUM for Korea-specific differentiators (training data, no live search)

---

## Table Stakes

Features every reviewer expects. Missing any of these signals the paper is incomplete or unpublishable at a serious venue.

| Feature | Why Expected | Typical Length / Scope | Complexity | Notes |
|---------|--------------|------------------------|------------|-------|
| **Abstract** | Standard; must convey research question, method, and main finding | 150–200 words | Low | Reviewers decide to read based on this; must state the discount magnitude and the Japan finding |
| **Introduction** | Sets motivation, contribution, previews findings, signals positioning | 3–5 pages | Medium | Must include "contribution to literature" paragraph; previews key numbers (e.g., "KOSPI traded at X median P/B vs Y for TOPIX over 2003–2023") |
| **Institutional background / setting** | Especially required for emerging-market or single-country papers; reviewers unfamiliar with chaebol structure or TSE reforms need grounding | 3–5 pages | Medium | Cover: chaebol cross-shareholding mechanics, FSC/KRX regulatory history, Japan's three reform dates with brief description of each, North Korea risk history |
| **Literature review** | Situates the paper; demonstrates awareness of prior work | 3–6 pages | Medium | Must cover: Korea Discount prior empirics (Kim & Yi, Black et al.), Japan governance reform event studies (Miyajima, Oikawa), broader governance–valuation literature (Gompers et al., La Porta et al.), natural experiment / synthetic control methodology papers |
| **Data section** | Describes sources, coverage, cleaning decisions, variable construction | 2–4 pages + table | Medium | Must include: time period, source for each index, variable definitions (P/B, P/E construction), survivorship bias discussion, missing data treatment; Table 1 is typically a summary statistics table |
| **Summary statistics table (Table 1)** | Near-universal in empirical finance; reviewers check for red flags before reading methods | 1 table | Low | By country × year or period; show mean, median, SD, min/max for core valuation metrics; include correlation matrix |
| **Graphical documentation of the discount** | Visual evidence precedes all formal tests; makes the paper accessible | 1–2 figures | Low | Time-series of P/B or P/E for KOSPI vs TOPIX, S&P, MSCI EM; ideally shows the discount persisting across cycles |
| **Causal mechanism / theoretical framework** | Papers without a mechanism are descriptive; JF/JFE expect a coherent story | 2–4 pages | Medium | Spell out three channels (chaebol opacity, minority-shareholder recourse, geopolitical premium); does not need to be a formal model but must be structured |
| **Empirical strategy section** | Explains identification approach before presenting results | 1–2 pages | Medium | Walk through event study design, OLS spec, and synthetic control logic separately; state estimating equations with notation |
| **Event study results** | Primary empirical test; required given the Japan natural experiment framing | 2–4 pages + 1–2 figures/tables | High | Cumulative abnormal returns / valuation changes around each treatment date; statistical inference via heteroskedasticity-robust SEs; separate results for 2014, 2015, 2023 |
| **Panel OLS results** | Complementary to event study; provides long-run cross-sectional variation | 2–3 pages + 1–2 tables | High | Country + time FEs; interaction terms for reform dummies; clustered SEs (by country); coefficient interpretation in economic terms (e.g., bps of P/B) |
| **Robustness checks section** | Reviewers expect at least 2–3 alternative specifications | 2–4 pages + tables | High | Synthetic control is your primary robustness; should also include: placebo tests (non-reform years), alternative valuation metrics (P/E instead of P/B), alternative control groups |
| **Discussion of limitations** | Required for honest identification; especially important for single-country comparison | 1–2 pages | Low-Medium | Explicitly: single treated unit problem for synthetic control; confounders (Abenomics, yen depreciation), generalizability of Japan→Korea inference |
| **Policy recommendations** | Expected given the paper's explicit prescriptive goal; reviewers at policy-oriented journals require it | 2–3 pages | Medium | Should be specific to Korean institutional levers: FSC disclosure requirements, KRX listing rules, stewardship code design |
| **Conclusion** | Standard closing | 1–2 pages | Low | Summarizes findings, contributions, limitations, future work; do not introduce new findings |
| **References** | Required | As long as needed | Low | Must include canonical governance + EM valuation literature; use consistent citation format (APA or journal-specific) |
| **Appendix: variable definitions** | Increasingly standard in empirical finance | 1–2 pages | Low | Exact formula for each constructed variable, source, transformation |
| **Appendix: robustness tables** | Overflow tables that clutter main body | Variable | Low | Move alternative-spec tables here to keep main body clean |

---

## Differentiators

Features that would set this paper apart. Not expected by default, but valued by reviewers and increase acceptance probability at top venues.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Stacked event study with all three Japan reform dates** | Most governance event studies use a single treatment date; using 2014 + 2015 + 2023 as stacked identification is richer and more credible | High | Requires careful choice of event windows (avoid overlap between 2014 and 2015; 2023 is clean); cite Cengiz et al. 2019 / Baker et al. 2022 for stacked DiD methodology |
| **Synthetic control with pre-treatment fit statistics** | Synthetic control for single treated unit (Japan) is the methodological frontier for this design; stronger than panel OLS alone | High | Use Abadie et al. (2010) Synth method; report MSPE ratio, pre-treatment RMSPE, placebo inference; Python: `mlsynth` or manual implementation via `scipy.optimize` |
| **Decomposition of the discount by driver** | Separating chaebol opacity, regulatory recourse, and geopolitical premium quantitatively (even partially) would be novel | Very High | Partial: use North Korea escalation event indicators (missile tests, nuclear tests) as a sub-sample test; geopolitical premium can be estimated as valuation response to DEFCON-adjacent events |
| **Geopolitical risk sub-analysis** | North Korea event indicators as a natural experiment within the paper; few papers formally estimate this component of the Korea Discount | High | Use GDELT or news-based geopolitical risk index (Caldara & Iacoviello GPR) alongside NK-specific event dummies; shows the paper is thorough on all three claimed mechanisms |
| **Counterfactual projection for Korea** | "If Korea implemented Japan's 2023 P/B reform, the discount would close by X% within Y years" — gives the policy section quantitative grounding | High | Requires extrapolating the synthetic control treatment effect; clearly labeled as illustrative; adds significant value to policy audience |
| **Visualization: discount anatomy chart** | A stacked or decomposed time-series that visually attributes portions of the discount to each driver is memorable and highly citeable | Medium | Even if the decomposition is qualitative, a well-designed figure that shows reform-correlated inflection points for Japan alongside KOSPI discount persistence is differentiating |
| **Comparison to other "discounted" markets** | Briefly comparing Korea's structure to China A-share discount, Hong Kong H-share discount, or India discount places the Korea case in global EM context | Medium | 1–2 pages; not a full second case study; positions Korea Discount as a general EM governance phenomenon with Korea-specific depth |
| **Formal placebo / falsification tests** | Running the Japan reform event study on markets that did NOT reform (Taiwan, China, Indonesia) strengthens identification | Medium | Standard in DiD literature; shows effect is specific to reform treatment, not a global valuation trend |
| **Machine-readable replication package** | Many journals now require this, but a clean, documented Python repo with a one-command reproducer is still differentiating in the governance / EM finance literature where R and Stata dominate | Medium | Given the project's explicit reproducibility goal; include a `make all` or `dvc repro` style entry point |

---

## Anti-Features

Things to deliberately NOT build for v1. Each has a reason.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Formal theoretical model (game theory or asset pricing)** | Would require months of additional work; not needed to publish at policy-adjacent journals (EMEAP, JIMF, Pacific-Basin Finance Journal); empirical evidence is the core contribution | Cite existing theoretical frameworks (e.g., Stulz agency cost model, La Porta investor protection model) rather than deriving new ones |
| **Firm-level microstructure analysis (individual chaebol stocks)** | Dramatically increases data requirements, cleaning burden, and scope; would require a different identification strategy; already declared Out of Scope in PROJECT.md | Stay at index/market level; note firm-level analysis as future work |
| **Real-time or live data pipeline** | Out of scope per PROJECT.md; adds infrastructure complexity without contributing to the academic argument | Use static, versioned data snapshots; document vintage dates |
| **FX / macro confound neutralization as a primary section** | Currency effects on P/B comparisons are a legitimate concern but addressing them as a full section would bloat the paper | Address in a robustness check: show results hold on USD-denominated P/B ratios; 1–2 paragraphs in the robustness section |
| **Full DID parallel-trends pre-test section** | For index-level data with few units, formal parallel-trends testing (e.g., Sun & Abraham estimator) is less applicable and can distract; the synthetic control pre-fit is the appropriate substitute | Report synthetic control pre-treatment RMSPE as the primary pre-trend evidence; note OLS parallel-trends assumption in limitations |
| **Survey or qualitative interview data** | Adds a different methodological chapter; journals expect methodological coherence; mixing quant + survey in v1 overcomplicates | Cite analyst reports or qualitative literature to support mechanism claims; no primary data collection |
| **Non-equity asset class sections (bonds, FX, CDS)** | Out of scope per PROJECT.md; would require separate data pipelines and are tangential to the equity valuation argument | Note CDS spread correlation as a descriptive aside in the geopolitical risk subsection only if the data is already in hand |
| **Country-by-country breakdown beyond Korea and Japan** | A full comparative study of 10 EM markets is a different, longer paper | Use MSCI EM as a benchmark index; brief 1-paragraph mention of China/India/Taiwan discounts as context only |
| **Trading strategy or alpha generation framing** | Would reposition this as a finance practitioner paper rather than academic governance paper; reviewers at policy journals would penalize this framing | Keep framing on policy implications and governance reform; avoid "investable" language |

---

## Feature Dependencies

```
Data acquisition and cleaning
  → Summary statistics (Table 1)
  → Descriptive discount chart (Figure 1)
  → Event study
  → Panel OLS
  → Synthetic control

Institutional background section
  → Causal mechanism section (references the reform dates)
  → Event study design (reform dates are treatment events)

Literature review
  → Identification of which robustness checks are needed (mirrors reviewer expectations from cited papers)

Event study (primary result)
  → Robustness checks (placebo tests test the same event windows)
  → Policy recommendations (draws on event study magnitude to size reform impact)

Panel OLS
  → Robustness checks (alternative specs use same base regression)

Synthetic control
  → Counterfactual projection (optional differentiator; requires synthetic control to exist first)
  → Limitations section (discusses synthetic control assumptions)
```

---

## MVP Recommendation

**Prioritize (must have for submission-ready v1):**

1. Data pipeline (all other sections depend on this)
2. Descriptive discount documentation (Table 1 + Figure 1) — establishes the phenomenon before any causal claims
3. Institutional background — enables non-specialist reviewers to follow the Japan natural experiment
4. Event study (2014, 2015, 2023) — primary result
5. Panel OLS with country/time FEs — primary result, complementary to event study
6. Synthetic control for 2023 TSE reform — primary robustness
7. Placebo tests (non-reform years / non-reform markets) — minimum robustness requirement
8. Limitations section — non-negotiable for credible identification claims
9. Policy recommendations — core purpose of the paper

**Defer to v2:**
- Geopolitical risk sub-analysis (North Korea event indicators): valuable differentiator but adds a separate data pipeline (GDELT or GPR index); add after core results are solid
- Counterfactual projection for Korea: requires additional modeling assumptions; label v2
- Comparison to other EM discounts: positioning enhancement, not core argument
- Full replication package polish: ship after results are final

---

## Section Length Norms (Journal of Finance / JFE standard)

| Section | Typical Pages |
|---------|--------------|
| Abstract | 0.2 |
| Introduction | 3–5 |
| Institutional background | 3–5 |
| Literature review | 3–6 |
| Data | 2–4 |
| Empirical strategy | 1–2 |
| Event study results | 2–4 |
| Panel OLS results | 2–3 |
| Robustness | 2–4 |
| Discussion / limitations | 1–2 |
| Policy recommendations | 2–3 |
| Conclusion | 1–2 |
| References | 2–4 |
| Appendices | 2–6 |
| **Total** | **~30–50 pages** |

Note: Policy-adjacent journals (Pacific-Basin Finance Journal, Journal of International Money and Finance, Emerging Markets Review) tolerate longer papers (45–55 pages) with appendices. Top-4 finance journals (JF, JFE, RFS) target 40–50 pages including appendices.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Table stakes (structural norms) | HIGH | Standard for JF/JFE/RFS empirical finance; stable across years |
| Differentiators (Korea/Japan specific) | MEDIUM | Based on training knowledge of governance literature; would benefit from a live literature scan for 2024–2025 working papers that may have already done some of these |
| Anti-features | HIGH | Scope decisions grounded in PROJECT.md and standard empirical finance scoping |
| Section length norms | HIGH | Stable convention in the field |

---

## Sources

- Training knowledge: Journal of Finance, Journal of Financial Economics, Review of Financial Studies empirical paper conventions
- Governance literature: Black, Jang & Kim (2006) Korea corporate governance; Miyajima et al. Japan governance reform event studies; Gompers, Ishii & Metrick (2003) governance index; La Porta et al. (1998, 2000) investor protection
- Methodology: Abadie, Diamond & Hainmueller (2010) synthetic control; Baker, Larcker & Wang (2022) stacked DiD critique; Cengiz et al. (2019) stacked event study design
- Note: No live web search was performed. Differentiator confidence is MEDIUM as a result. A scan of 2024–2025 SSRN working papers on Korea Discount and Japan governance would increase confidence.
