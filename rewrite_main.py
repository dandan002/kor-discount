import re

with open("simple_paper/main.tex", "r") as f:
    content = f.read()

# Abstract
content = content.replace(
    r"Cross-sectional regressions find governance insignificant once growth is controlled \citep{yang2025korea}, while natural experiments consistently identify the self-dealing channel as a direct value destroyer \citep{black2015governance}.",
    r"Cross-sectional regressions found governance insignificant once growth was controlled \citep{yang2025korea}, while natural experiments consistently identified the self-dealing channel as a direct value destroyer \citep{black2015governance}."
)

# Section 2
content = content.replace(
    r"\citet{kim2026korean} provide the most comprehensive international evidence, documenting persistently lower P/B and P/E multiples for Korean firms across 48 countries from 1990 to 2023, even after controlling for firm size, profitability, growth, GDP per capita, financial market development, and geopolitical risk. The finding holds across all sub-periods (1990s, 2000s, 2010s onward), demonstrating that the discount is structural, not cyclical.",
    r"The most comprehensive international evidence documented persistently lower P/B and P/E multiples for Korean firms across 48 countries from 1990 to 2023, even after controlling for firm size, profitability, growth, GDP per capita, financial market development, and geopolitical risk \citep{kim2026korean}. The finding held across all sub-periods (1990s, 2000s, 2010s onward), demonstrating that the discount was structural, not cyclical."
)

content = content.replace(
    r"\citet{choi2012equity} find that Korean firms' cost of equity is significantly higher than 31-country peers after controlling for firm characteristics. However, they note the discount has eased in recent years---suggesting partial convergence.",
    r"Korean firms' cost of equity was significantly higher than 31-country peers after controlling for firm characteristics, compounding the P/B discount \citep{choi2012equity}. However, the discount eased in recent years, suggesting partial convergence."
)

content = content.replace(
    r"\citet{jung2022korea} show that Korean firms with book-to-market ratios above one consistently outperform lower-BTM firms, but further demonstrate that high BTM is associated with a higher probability of positive extreme returns and a lower probability of negative extremes---indicating mispricing rather than risk compensation. A governance factor is the strongest cross-sectional predictor.",
    r"Korean firms with book-to-market (BTM) ratios above one consistently outperformed lower-BTM firms. Furthermore, high BTM was associated with a higher probability of positive extreme returns and a lower probability of negative extremes, indicating mispricing rather than risk compensation \citep{jung2022korea}. A governance factor was the strongest cross-sectional predictor."
)

# Section 3.1
content = content.replace(
    r"\citet{almeida2011chaebol} map chaebol formation, showing that controlling families use ``central firms'' to acquire low-profitability entities through pyramidal structures, with central firms trading at a discount reflecting shareholders' anticipation of value-destroying acquisitions.",
    r"Mapping chaebol formation revealed that controlling families used ``central firms'' to acquire low-profitability entities through pyramidal structures. These central firms traded at a discount, reflecting shareholders' anticipation of value-destroying acquisitions \citep{almeida2011chaebol}."
)

content = content.replace(
    r"\citet{kim2004chaebol} document that the cash flow rights disparity between voting and economic ownership is substantially larger than previously reported, because studies using only public firms miss the amplifying role of non-public affiliates.",
    r"The cash flow rights disparity between voting and economic ownership was substantially larger than previously reported, because studies using only public firms missed the amplifying role of non-public affiliates \citep{kim2004chaebol}."
)

content = content.replace(
    r"The economic scale of tunneling is documented by \citet{bae2002tunneling}: when a chaebol-affiliated firm makes an acquisition, its stock price falls on average while the controlling shareholder benefits through value transfer to other group firms.",
    r"The economic scale of tunneling was substantial: when a chaebol-affiliated firm made an acquisition, its stock price fell on average while the controlling shareholder benefited through value transfers to other group firms \citep{bae2002tunneling}."
)

content = content.replace(
    r"\citet{kim2019tunneling} show that business group-affiliated firms make systematically larger charitable donations---coordinated to tunnel resources from public affiliates (lower family cash flow rights) to private ones (higher family stakes).",
    r"Business group-affiliated firms made systematically larger charitable donations. These donations were coordinated to tunnel resources from public affiliates (where families held lower cash flow rights) to private ones (where they held higher stakes) \citep{kim2019tunneling}."
)

# Section 3.2
content = content.replace(
    r"The most causally credible evidence comes from \citet{black2015governance}, who exploit Korea's 1999 reform imposing stricter board requirements on large firms (assets above 2 trillion won). Event studies show that large firms whose controllers had incentives to tunnel earned strong positive abnormal returns; panel regressions confirm that better governance moderates the negative effect of related-party transactions on firm value and increases the sensitivity of firm profitability to industry profitability---consistent with reduced tunneling.",
    r"Exploiting Korea's 1999 reform that imposed stricter board requirements on large firms provided strong causal evidence. Event studies showed that large firms whose controllers had incentives to tunnel earned strong positive abnormal returns. Furthermore, panel regressions confirmed that better governance moderated the negative effect of related-party transactions on firm value and increased the sensitivity of firm profitability to industry profitability, consistent with reduced tunneling \citep{black2015governance}."
)

content = content.replace(
    r"\citet{njoku2026governance} find that among chaebol-affiliated firms, only shareholder rights protection retains explanatory power for dividend payouts; board effectiveness, audit competency, and disclosure transparency lose independent influence once ownership structure is controlled.",
    r"Among chaebol-affiliated firms, only shareholder rights protection retained explanatory power for dividend payouts; board effectiveness, audit competency, and disclosure transparency lost independent influence once ownership structure was controlled \citep{njoku2026governance}."
)

# Section 3.3
content = content.replace(
    r"\citet{park2019holding} document that legally designated holding companies trade at significant P/B discounts relative to both operating companies and their fundamental values---a phenomenon unique to Korea and absent from Japan and the US.",
    r"Legally designated holding companies traded at significant P/B discounts relative to both operating companies and their fundamental values---a phenomenon unique to Korea and absent from Japan and the US \citep{park2019holding}."
)

content = content.replace(
    r"\citet{park2025cross} argue that cross-shareholding voting restrictions can positively influence capital markets by exposing holding companies to boardroom coups, inducing upward revaluation---though this remains a defensive tactic rather than a governance improvement.",
    r"Cross-shareholding voting restrictions could positively influence capital markets by exposing holding companies to boardroom coups, inducing upward revaluation \citep{park2025cross}. However, this remained a defensive tactic rather than a fundamental governance improvement."
)

content = content.replace(
    r"\citet{kim2022supermajority} exploit court rulings weakening supermajority anti-takeover provisions, finding that firms with such provisions outperform, supporting their value-enhancing role when not abused for entrenchment.",
    r"Exploiting court rulings that weakened supermajority anti-takeover provisions showed that firms with such provisions outperformed, supporting their value-enhancing role when not abused for entrenchment \citep{kim2022supermajority}."
)

# Section 4
content = content.replace(
    r"\citet{yang2025korea} directly test governance, shareholder payout, and growth potential hypotheses, finding that corporate governance has \emph{no} significant relationship with PBR, while stagnant growth variables---low R\&D, high tangible-asset intensity, and firm maturity---exhibit strong positive correlations with low PBR. Higher shareholder payout is paradoxically associated with \emph{lower} PBR.",
    r"Direct tests of governance, shareholder payout, and growth potential hypotheses found that corporate governance had \emph{no} significant relationship with PBR. Instead, stagnant growth variables---such as low R\&D, high tangible-asset intensity, and firm maturity---exhibited strong positive correlations with low PBR, and higher shareholder payouts were paradoxically associated with \emph{lower} PBR \citep{yang2025korea}."
)

content = content.replace(
    r"\citet{lee2025korea_pbr} corroborate this for large manufacturers: dividend expansion has weak or negative effects on PBR, while R\&D investment is more significant.",
    r"This was corroborated for large manufacturers: dividend expansion had weak or negative effects on PBR, while R\&D investment remained more significant \citep{lee2025korea_pbr}."
)

content = content.replace(
    r"\citet{kim2025causes} broaden the challenge: across 58 markets (2001--2018), Korea's formal shareholder rights scores are not distinctively lower than peers, and markets with the largest shareholder return increases actually saw declines in average firm value. What distinguishes Korea is low value relevance: profitability and growth are incorporated into prices to a far lesser degree (51st of 58 countries), suggesting a short-term investment culture that prevents long-term expectations from being capitalized.",
    r"A broader challenge emerged across 58 markets from 2001 to 2018: Korea's formal shareholder rights scores were not distinctively lower than its peers. In fact, markets with the largest shareholder return increases actually saw declines in average firm value. What distinguished Korea was low value relevance: profitability and growth were incorporated into prices to a far lesser degree (ranking 51st out of 58 countries), suggesting a short-term investment culture that prevented long-term expectations from being capitalized \citep{kim2025causes}."
)

# Section 5.1
content = content.replace(
    r"\citet{kim2014nps} find that markets do not react to NPS ``Vote No'' announcements---inconsistent with developed-market activism---though firms improving internal governance afterward show higher valuation.",
    r"However, markets did not react to NPS ``Vote No'' announcements, a result inconsistent with developed-market activism, though firms that subsequently improved internal governance showed higher valuations \citep{kim2014nps}."
)

content = content.replace(
    r"\citet{kim2022nps_esg} document that NPS shareholding improves ESG performance and financial outcomes, with ESG as the transmission channel.",
    r"NPS shareholding improved ESG performance and financial outcomes, with ESG serving as the primary transmission channel \citep{kim2022nps_esg}."
)

content = content.replace(
    r"\citet{lee2026esg} confirm that NPS ESG engagement disclosures are associated with significant firm value gains, with effects strongest for firms with weakest internal governance---institutional activism substitutes for rather than complements internal governance.",
    r"Furthermore, NPS ESG engagement disclosures were associated with significant firm value gains. These effects were strongest for firms with the weakest internal governance, indicating that institutional activism substituted for, rather than complemented, internal governance \citep{lee2026esg}."
)

# Section 5.2
content = content.replace(
    r"\citet{park2021stewardship} find a positive correlation between Stewardship Code adoption and earnings quality, but multivariate regressions fail to establish significance. The broader challenge \citep{kim2025causes} is that Korea's formal governance scores are not distinctively lower than peers; the problem lies in enforcement credibility, not norms.",
    r"While a positive correlation was found between Stewardship Code adoption and earnings quality, multivariate regressions failed to establish statistical significance \citep{park2021stewardship}. The broader challenge was that Korea's formal governance scores were not distinctively lower than those of its peers; the problem lay in enforcement credibility rather than established norms \citep{kim2025causes}."
)

content = content.replace(
    r"\citet{kim2015foreign} show that foreign investors facilitate firm-specific information incorporation into stock prices more effectively than domestic institutions.",
    r"Foreign investors facilitated the incorporation of firm-specific information into stock prices more effectively than domestic institutions \citep{kim2015foreign}."
)

content = content.replace(
    r"\citet{joo2026foreign} demonstrate that foreign ownership reduces growth disparity through asymmetric discipline---correcting over-investment in over-growing firms and encouraging profitable management in under-growing ones---implying that governance reforms improving market accessibility would amplify foreign investor discipline.",
    r"Foreign ownership also reduced growth disparities through asymmetric discipline---correcting over-investment in over-growing firms and encouraging profitable management in under-growing ones. This implied that governance reforms that improved market accessibility could significantly amplify foreign investor discipline \citep{joo2026foreign}."
)

# Section 6.2
content = content.replace(
    r"\citet{lee2025valueup} evaluates the program and finds low participation and weak market response.",
    r"Evaluations of the program found low participation and weak market responses \citep{lee2025valueup}."
)

content = content.replace(
    r"\citet{kang2026commercial} provide direct market evidence that \emph{legislative} reform shifts expectations: the 2025 Commercial Act amendment (expanding directors' fiduciary duties to shareholders broadly) produced significantly positive abnormal returns for high-book-to-market firms, with no significant reaction among high controlling-shareholder-ownership firms---markets expect reform to be most effective where expropriation risk is highest.",
    r"Conversely, direct market evidence showed that \emph{legislative} reform shifted expectations: the 2025 Commercial Act amendment (which expanded directors' fiduciary duties to shareholders) produced significantly positive abnormal returns for high-book-to-market firms. There was no significant reaction among firms with high controlling-shareholder ownership, indicating that markets expected the reform to be most effective where expropriation risk was highest \citep{kang2026commercial}."
)

# Section 7
content = content.replace(
    r"\citet{kim2025causes} show that Korea's economic policy uncertainty index, not military threat, explains cross-country discount differentials. The GPR falsification in Section~\ref{sec:reform} confirms the null: the coefficient is indistinguishable from zero.",
    r"Korea's economic policy uncertainty index, rather than military threat, explained cross-country discount differentials \citep{kim2025causes}. Our GPR falsification in Section~\ref{sec:reform} confirmed this null result: the coefficient was indistinguishable from zero."
)

content = content.replace(
    r"\citet{yun2022sentiment} find that initial audit fees are significantly lower during high-sentiment periods in Korea's low-litigation environment, suggesting that optimistic bias reduces monitoring quality---complementing the governance channel.",
    r"Initial audit fees were significantly lower during high-sentiment periods in Korea's low-litigation environment, suggesting that optimistic bias reduced monitoring quality, thereby complementing the governance channel \citep{yun2022sentiment}."
)

content = content.replace(
    r"\citet{the_economist_2012} attributes the Korea Discount primarily to poor corporate governance at chaebols, describing ``tunnelling'' and ``propping'' as mechanisms through which insiders benefit at minority shareholders' expense.",
    r"Financial media have also attributed the Korea Discount primarily to poor corporate governance at chaebols, describing ``tunneling'' and ``propping'' as mechanisms through which insiders benefited at minority shareholders' expense \citep{the_economist_2012}."
)

with open("simple_paper/main.tex", "w") as f:
    f.write(content)

