"""
panel_ols.py - Estimate two-way fixed effects PanelOLS specifications.

Reads the canonical valuation panel and writes machine-readable regression
output for the Korea Discount study's primary panel OLS analysis.
"""
import logging
import math
import sys
import warnings
from pathlib import Path

import pandas as pd
import statsmodels.api as sm
from linearmodels import PanelOLS
from linearmodels.panel.data import PanelData
from wildboottest.wildboottest import wildboottest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)

BOOTSTRAP_ITERATIONS = 999
BOOTSTRAP_SEED = 42
WILD_BOOTSTRAP_WEIGHTS = "rademacher"
STUDY_END = pd.Timestamp("2024-12-31")

BASELINE_SPEC = "Baseline two-way FE"
DUMMIES_SPEC = "+ reform dummies"
INTERACTIONS_SPEC = "+ reform x Japan"

POST_TERMS = [
    "post_stewardship",
    "post_cgc",
    "post_tse_pb_reform",
]
INTERACTION_TERMS = [
    "stewardship_x_japan",
    "cgc_x_japan",
    "tse_pb_reform_x_japan",
]
TABLE_TERMS = POST_TERMS + INTERACTION_TERMS


def construct_regression_panel(panel: pd.DataFrame) -> pd.DataFrame:
    """Construct reform indicators and return a country-date indexed panel."""
    required_columns = {"date", "country", "pb"}
    missing_columns = required_columns - set(panel.columns)
    if missing_columns:
        raise ValueError(f"panel is missing required columns: {sorted(missing_columns)}")

    reg_panel = panel.copy()
    reg_panel["date"] = pd.to_datetime(reg_panel["date"])
    reg_panel = reg_panel[reg_panel["date"] <= STUDY_END].copy()

    reg_panel["is_japan"] = (reg_panel["country"] == "TOPIX").astype(int)
    reg_panel["post_stewardship"] = (
        reg_panel["date"] >= pd.Timestamp(config.STEWARDSHIP_CODE_DATE)
    ).astype(int)
    reg_panel["post_cgc"] = (
        reg_panel["date"] >= pd.Timestamp(config.CGC_DATE)
    ).astype(int)
    reg_panel["post_tse_pb_reform"] = (
        reg_panel["date"] >= pd.Timestamp(config.TSE_PB_REFORM_DATE)
    ).astype(int)

    reg_panel["stewardship_x_japan"] = (
        reg_panel["post_stewardship"] * reg_panel["is_japan"]
    )
    reg_panel["cgc_x_japan"] = reg_panel["post_cgc"] * reg_panel["is_japan"]
    reg_panel["tse_pb_reform_x_japan"] = (
        reg_panel["post_tse_pb_reform"] * reg_panel["is_japan"]
    )

    return reg_panel.sort_values(["country", "date"]).set_index(["country", "date"])


def _fit_panel_ols(
    reg_panel: pd.DataFrame,
    terms: list[str],
):
    """Fit one PanelOLS specification with two-way fixed effects."""
    exog = pd.DataFrame({"constant": 1.0}, index=reg_panel.index)
    for term in terms:
        exog[term] = reg_panel[term]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = PanelOLS(
            reg_panel["pb"],
            exog,
            entity_effects=True,
            time_effects=True,
            drop_absorbed=True,
            check_rank=False,
        )
        return model.fit(cov_type="robust")


def _append_term_rows(
    rows: list[dict[str, object]],
    specification: str,
    result,
    included_terms: list[str],
) -> None:
    """Append normalized result rows for all Table 2 terms."""
    for term in TABLE_TERMS:
        if term in POST_TERMS and specification in {DUMMIES_SPEC, INTERACTIONS_SPEC}:
            rows.append(
                {
                    "specification": specification,
                    "term": term,
                    "coef": math.nan,
                    "std_error": math.nan,
                    "p_value": math.nan,
                    "wild_p_value": math.nan,
                    "note": "absorbed by time FE",
                }
            )
            continue

        if term in result.params.index and term in included_terms:
            rows.append(
                {
                    "specification": specification,
                    "term": term,
                    "coef": float(result.params[term]),
                    "std_error": float(result.std_errors[term]),
                    "p_value": float(result.pvalues[term]),
                    "wild_p_value": math.nan,
                    "note": "",
                }
            )
            continue

        note = "not included"
        rows.append(
            {
                "specification": specification,
                "term": term,
                "coef": math.nan,
                "std_error": math.nan,
                "p_value": math.nan,
                "wild_p_value": math.nan,
                "note": note,
            }
        )


def _wild_bootstrap_pvalues(reg_panel: pd.DataFrame) -> pd.Series:
    """Compute FWL wild-bootstrap p-values for the Japan interaction terms."""
    y_dm = (
        PanelData(reg_panel[["pb"]])
        .demean(group="both", return_panel=False)
        .dataframe["pb"]
    )
    x_dm = (
        PanelData(reg_panel[INTERACTION_TERMS])
        .demean(group="both", return_panel=False)
        .dataframe
    )

    valid_rows = y_dm.notna() & x_dm.notna().all(axis=1)
    y_valid = y_dm.loc[valid_rows]
    x_valid = x_dm.loc[valid_rows]

    sm_model = sm.OLS(y_valid, x_valid)
    sm_model.fit()

    country_labels = pd.Series(
        x_valid.index.get_level_values("country"),
        index=x_valid.index,
        name="country",
    )
    country_cluster = pd.Series(
        pd.Categorical(country_labels).codes.astype("int64"),
        index=country_labels.index,
        name="country",
    )

    boot = wildboottest(
        sm_model,
        B=BOOTSTRAP_ITERATIONS,
        cluster=country_cluster,
        weights_type=WILD_BOOTSTRAP_WEIGHTS,
        bootstrap_type="11",
        seed=BOOTSTRAP_SEED,
        show=False,
    )
    return boot["p-value"].astype(float)


def fit_panel_specs(reg_panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Estimate PanelOLS specifications and return term rows plus model stats."""
    rows: list[dict[str, object]] = []
    model_rows: list[dict[str, object]] = []

    specs = [
        (BASELINE_SPEC, []),
        (DUMMIES_SPEC, POST_TERMS),
        (INTERACTIONS_SPEC, POST_TERMS + INTERACTION_TERMS),
    ]
    for specification, terms in specs:
        result = _fit_panel_ols(reg_panel, terms)
        _append_term_rows(rows, specification, result, terms)
        model_rows.append(
            {
                "specification": specification,
                "nobs": int(result.nobs),
                "rsquared_within": float(result.rsquared_within),
                "entity_effects": True,
                "time_effects": True,
            }
        )

    wild_pvalues = _wild_bootstrap_pvalues(reg_panel)
    for row in rows:
        if row["specification"] == INTERACTIONS_SPEC and row["term"] in wild_pvalues.index:
            row["wild_p_value"] = float(wild_pvalues.loc[row["term"]])

    return pd.DataFrame(rows), pd.DataFrame(model_rows)


def main() -> None:
    """Run the panel OLS analysis and write machine-readable results."""
    panel_path = config.PROCESSED_DIR / "panel.parquet"
    panel = pd.read_parquet(panel_path)
    reg_panel = construct_regression_panel(panel)
    results_df, model_stats = fit_panel_specs(reg_panel)

    output_path = config.OUTPUT_DIR / "tables" / "panel_ols_results.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)
    logging.info("Saved PanelOLS results to %s", output_path)
    logging.info("Estimated model stats:\n%s", model_stats.to_string(index=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
