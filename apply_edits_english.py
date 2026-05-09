import re

with open("simple_paper/main.tex", "r", encoding="utf-8") as f:
    content = f.read()

# Edit 3: Terminology in Abstract
content = content.replace(
    r"The evidence supports hard legislative reform over soft governance codes.",
    r"The evidence supports enforceable reform over voluntary governance codes."
)
content = content.replace(
    r"while mandatory exchange-level enforcement with binding improvement plans and market-demotion consequences, as embodied in Japan's 2023 TSE P/B reform request, does.",
    r"while exchange-level enforcement backed by credible sanctions---as embodied in Japan's 2023 TSE P/B reform request with its comply-or-explain mandate and monthly scorecards---does."
)
content = content.replace(
    r"The literature and empirical evidence suggest mitigating the Korea Discount requires hard legislative reform, not soft-law guidelines.",
    r"The literature and empirical evidence suggest mitigating the Korea Discount requires enforceable reform with credible sanctions, not voluntary guidelines."
)

# Edit 5: GPR in Abstract
content = content.replace(
    r"A geopolitical risk falsification rejects the North Korean threat explanation ($t=-0.84$, $p=0.40$).",
    r"A geopolitical risk falsification rejects acute geopolitical shocks as the driver of the discount ($t=-0.84$, $p=0.40$); a structural level premium cannot be ruled out."
)

# Edit 6: Index Composition in Sec 2
content = content.replace(
    r"The sub-period decomposition shows structural deterioration: the KOSPI--TOPIX gap widens from $0.05$ P/B points in 2004--2013 to $0.43$ points in 2023--2024.",
    r"The sub-period decomposition shows structural deterioration: the KOSPI--TOPIX gap widens from $0.05$ P/B points in 2004--2013 to $0.43$ points in 2023--2024. A sector-composition caveat applies: KOSPI is concentrated in cyclical hardware manufacturing (Samsung Electronics and SK Hynix alone account for roughly 30\% of index weight), while TOPIX and S\&P~500 carry larger shares of software, services, and consumer sectors that structurally command higher P/B multiples. \citet{kim2026korean} controls for firm-level characteristics across 48 countries and finds the discount survives, but the index-level spreads reported here do not adjust for sector weighting."
)

# Edit 1: Inheritance Tax in Sec 3.1
content = content.replace(
    r"private ones (where they held higher stakes) \citep{kim2019tunneling}.",
    r"private ones (where they held higher stakes) \citep{kim2019tunneling}." + "\n\n" + r"The tunneling incentive is amplified by Korea's tax regime. South Korea imposes one of the highest statutory inheritance tax rates in the OECD---up to 60\% for controlling stakes in large firms---alongside dividends taxed as ordinary income at marginal rates up to 45\%. For controlling families whose wealth is concentrated in group equity, a higher share price directly increases succession-tax liability, creating a rational incentive to suppress valuations through low payouts, inter-affiliate transfers, and share-price discouragement. This tax structure makes tunneling not merely opportunistic but privately optimal: by keeping public-firm valuations depressed, controlling shareholders minimize both the fiscal cost of generational succession and the risk of losing control to hostile acquirers."
)

# Edit 4: Growth-Governance Causal Link in Sec 4
content = content.replace(
    r"The two channels also reinforce one another: concentrated control depresses R\&D investment (registering as a growth deficit) because controlling shareholders prefer low-risk, tunnelable cash flows over long-horizon innovation spending; low value relevance then weakens the market penalty for value-destroying acquisitions, further entrenching the cycle. Hard reform that raises the cost of non-compliance disrupts this feedback at its root---the mechanism Section~\ref{sec:reform} tests empirically.",
    r"The two channels plausibly reinforce one another. Controlling shareholders may prefer low-risk, tunnelable cash flows over long-horizon R\&D spending, causing governance-driven expropriation to register empirically as a growth deficit; low value relevance then weakens the market penalty for value-destroying acquisitions, further entrenching the cycle. While direct causal estimation of this feedback loop remains limited by endogeneity, the event-study evidence in Section~\ref{sec:reform}---showing that enforceable reform produces re-rating while growth fundamentals remain unchanged---supports the governance channel as the deeper cause."
)

# Edit 2: Event Study Confounders in Sec 6.3
content = content.replace(
    r"the largest spread movement in the sample.",
    r"the largest spread movement in the sample." + "\n\n" + r"Two confounders warrant acknowledgment. First, the yen depreciated sharply in 2023---from roughly 130 to 150 against the dollar---boosting export-heavy TOPIX constituents' earnings. Second, foreign capital inflows into Japanese equities accelerated after April 2023, partly driven by Warren Buffett's high-profile investment in Japanese trading houses. The MSCI EM Asia--TOPIX specification partially insulates the result from Japan-specific appreciation, but the exact magnitude of the $-6.48$ P/B point CAR likely overstates the governance channel; the direction of the effect---enforceable mandates produce re-rating, voluntary codes do not---is robust."
)

# Edit 5: GPR Shocks vs Levels in Sec 7
content = content.replace(
    r"North Korean geopolitical risk is the most frequently invoked lay explanation for the Korea Discount, but the empirical record does not support it.",
    r"North Korean geopolitical risk is the most frequently invoked lay explanation for the Korea Discount, but the empirical record provides limited support for it."
)
content = content.replace(
    r"bias toward finding an effect, since GPRC\_KOR may also capture global risk-off episodes that depress Korean valuations for non-geopolitical reasons; it still finds none.",
    r"bias toward finding an effect, since GPRC\_KOR may also capture global risk-off episodes that depress Korean valuations for non-geopolitical reasons; it still finds none. This null result speaks to the pricing of geopolitical \emph{shocks}; it does not rule out a structural level premium that would be constant across the sample and thus absorbed by the intercept."
)

with open("simple_paper/main.tex", "w", encoding="utf-8") as f:
    f.write(content)

print("English edits applied")
