"""
robustness_alt_control.py - ROBUST-03: Alternative EM control group robustness.

Two variants:
  (a) MSCI EM Asia as EM ex-Korea proxy (replaces MSCI_EM in panel).
  (b) MSCI EM ex-China proxy (constructed via weighted residual from MSCI_EM and MSCI_China).

Each variant runs the Phase 3 panel OLS with two-way FE and saves a LaTeX regression table
to output/robustness/ to confirm results are not driven by the specific EM benchmark choice.

Decisions: D-12 (both variants), D-13 (each variant to own LaTeX file), D-18 (output naming).
"""
import logging
import sys
import warnings
from pathlib import Path

import pandas as pd
from linearmodels import PanelOLS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)

ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"

# [ASSUMED] CHINA_WEIGHT_APPROX = 0.30 - approximate China weight in MSCI EM
# (~30-35% circa 2023). See RESEARCH.md Pattern 6 for derivation.
CHINA_WEIGHT_APPROX = 0.30
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

TERM_LABELS = {
    "post_stewardship": "Post Stewardship Code",
    "post_cgc": "Post Corporate Governance Code",
    "post_tse_pb_reform": "Post TSE P/B Reform",
    "stewardship_x_japan": "Stewardship x Japan",
    "cgc_x_japan": "Corporate Governance Code x Japan",
    "tse_pb_reform_x_japan": "TSE P/B Reform x Japan",
}


def _month_end_dates(series: pd.Series) -> pd.Series:
    """Normalize Bloomberg monthly observation dates to canonical month-end dates."""
    return pd.to_datetime(series) + pd.offsets.MonthEnd(0)


def _read_raw_pb(filename: str) -> pd.DataFrame:
    """Read and validate one raw P/B CSV used by the alt-control variants."""
    path = config.RAW_DIR / filename
    df = pd.read_csv(path)
    assert "pb" in df.columns, f"{path} must contain a 'pb' column"
    assert df["pb"].notna().all(), f"{path} contains missing pb values"
    assert "date" in df.columns, f"{path} must contain a 'date' column"
    df = df.copy()
    df["date"] = _month_end_dates(df["date"])
    df["pb"] = df["pb"].astype("float64")
    return df


def load_base_panel() -> pd.DataFrame:
    """Load the canonical panel and keep non-EM rows for benchmark substitution."""
    panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    required_columns = {"date", "country", "pb"}
    missing_columns = required_columns - set(panel.columns)
    if missing_columns:
        raise ValueError(f"panel.parquet is missing required columns: {sorted(missing_columns)}")

    base = panel[panel["country"].isin(["KOSPI", "TOPIX", "SP500"])].copy()
    base["date"] = pd.to_datetime(base["date"])
    return base[["date", "country", "pb"]]


def build_em_asia_panel(base: pd.DataFrame) -> pd.DataFrame:
    """Replace MSCI_EM with MSCI EM Asia and return the long regression panel."""
    em_asia = _read_raw_pb("msci_em_asia_pb_2004_2026.csv")
    # MSCI EM Asia is the closest available proxy for EM ex-Korea (D-12a).
    em_asia["country"] = "MSCI_EM_ASIA"
    alt_rows = em_asia[["date", "country", "pb"]].copy()
    return pd.concat([base[["date", "country", "pb"]], alt_rows], ignore_index=True)


def build_em_exchina_panel(base: pd.DataFrame) -> pd.DataFrame:
    """Construct an EM ex-China proxy and return the long regression panel."""
    # Mathematical derivation:
    # MSCI_EM = china_wt * China_PB + (1 - china_wt) * EM_ex_China_PB
    # => EM_ex_China_PB = (MSCI_EM_PB - china_wt * China_PB) / (1 - china_wt)
    # [ASSUMED] china_wt ~ 0.30; this is an approximation, not an official MSCI series.
    em = _read_raw_pb("msci_em_pb_2004_2026.csv")
    china = _read_raw_pb("msci_china_pb_2004_2026.csv")
    merged = em.merge(china, on="date", suffixes=("_em", "_china"))
    if merged.empty:
        raise ValueError("MSCI EM and MSCI China files have no overlapping dates")

    merged["pb"] = (
        (merged["pb_em"] - CHINA_WEIGHT_APPROX * merged["pb_china"])
        / (1 - CHINA_WEIGHT_APPROX)
    )
    if (merged["pb"] <= 0).any():
        raise ValueError("Constructed EM ex-China proxy contains non-positive P/B values")

    merged["country"] = "MSCI_EM_EX_CHINA"
    alt_rows = merged[["date", "country", "pb"]].copy()
    return pd.concat([base[["date", "country", "pb"]], alt_rows], ignore_index=True)


def construct_regression_panel(panel_long: pd.DataFrame) -> pd.DataFrame:
    """Construct reform indicators and return a country-date indexed panel."""
    required_columns = {"date", "country", "pb"}
    missing_columns = required_columns - set(panel_long.columns)
    if missing_columns:
        raise ValueError(f"panel is missing required columns: {sorted(missing_columns)}")

    reg_panel = panel_long.copy()
    reg_panel["date"] = pd.to_datetime(reg_panel["date"])
    reg_panel = reg_panel[reg_panel["date"] <= STUDY_END].copy()

    reg_panel["is_japan"] = (reg_panel["country"] == "TOPIX").astype(int)
    reg_panel["post_stewardship"] = (
        reg_panel["date"] >= pd.Timestamp(config.STEWARDSHIP_CODE_DATE)
    ).astype(int)
    reg_panel["post_cgc"] = (reg_panel["date"] >= pd.Timestamp(config.CGC_DATE)).astype(int)
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

    duplicated = reg_panel.duplicated(subset=["country", "date"])
    if duplicated.any():
        raise ValueError("panel contains duplicate country-date rows")

    return reg_panel.sort_values(["country", "date"]).set_index(["country", "date"])


def _fit_panel_ols(reg_panel: pd.DataFrame, terms: list[str]):
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
    """Append normalized result rows for all reported panel OLS terms."""
    for term in TABLE_TERMS:
        if term in POST_TERMS and specification in {DUMMIES_SPEC, INTERACTIONS_SPEC}:
            rows.append(
                {
                    "specification": specification,
                    "term": term,
                    "coef": pd.NA,
                    "std_error": pd.NA,
                    "p_value": pd.NA,
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
                    "note": "",
                }
            )
            continue

        rows.append(
            {
                "specification": specification,
                "term": term,
                "coef": pd.NA,
                "std_error": pd.NA,
                "p_value": pd.NA,
                "note": "not included",
            }
        )


def _format_table_cell(row: pd.Series) -> str:
    """Format one coefficient cell for the LaTeX regression table."""
    note = row.get("note")
    if note == "absorbed by time FE":
        return "absorbed by time FE"
    if note == "not included" or pd.isna(row.get("coef")):
        return ""
    return f"{float(row['coef']):.2f} ({float(row['std_error']):.2f})"


def _build_results_table(results_df: pd.DataFrame) -> pd.DataFrame:
    """Pivot normalized result rows into a regression table layout."""
    table = pd.DataFrame(
        "",
        index=TABLE_TERMS,
        columns=[BASELINE_SPEC, DUMMIES_SPEC, INTERACTIONS_SPEC],
    )
    table.index = [TERM_LABELS[term] for term in TABLE_TERMS]
    table.index.name = "term"

    for _, row in results_df.iterrows():
        term = TERM_LABELS[row["term"]]
        specification = row["specification"]
        if term in table.index and specification in table.columns:
            table.loc[term, specification] = _format_table_cell(row)
    return table


def run_alt_ols(reg_panel: pd.DataFrame, variant_name: str) -> pd.DataFrame:
    """Run all alt-control PanelOLS specifications and save one LaTeX table."""
    rows: list[dict[str, object]] = []
    specs = [
        (BASELINE_SPEC, []),
        (DUMMIES_SPEC, POST_TERMS),
        (INTERACTIONS_SPEC, POST_TERMS + INTERACTION_TERMS),
    ]
    for specification, terms in specs:
        result = _fit_panel_ols(reg_panel, terms)
        _append_term_rows(rows, specification, result, terms)

    results_df = pd.DataFrame(rows)
    table = _build_results_table(results_df)
    caption_variant = variant_name.replace("_", " ").upper()
    latex_str = table.style.to_latex(
        hrules=True,
        caption=f"Panel OLS Robustness - {caption_variant} Control Group",
        label=f"tab:robust_alt_{variant_name}",
    )
    note = (
        "\\multicolumn{4}{l}{\\footnotesize Note: Coefficients from two-way FE "
        "PanelOLS using robust standard errors in parentheses. Post reform "
        "dummies are absorbed by time fixed effects where noted.} \\\\\n"
    )
    latex_str = latex_str.replace("\\bottomrule\n", note + "\\bottomrule\n")

    output_path = ROBUSTNESS_DIR / f"robustness_alt_control_{variant_name}.tex"
    output_path.write_text(latex_str, encoding="utf-8")
    logging.info("Saved %s", output_path)
    logging.info(
        "%s interaction estimates:\n%s",
        variant_name,
        results_df[
            (results_df["specification"] == INTERACTIONS_SPEC)
            & (results_df["term"].isin(INTERACTION_TERMS))
        ][["term", "coef", "std_error", "p_value"]].to_string(index=False),
    )
    return results_df


def main() -> None:
    """Run both ROBUST-03 alt-control variants and write LaTeX outputs."""
    ROBUSTNESS_DIR.mkdir(parents=True, exist_ok=True)
    base = load_base_panel()

    panel_em_asia = build_em_asia_panel(base)
    reg_panel_a = construct_regression_panel(panel_em_asia)
    run_alt_ols(reg_panel_a, "em_asia")

    panel_em_exchina = build_em_exchina_panel(base)
    reg_panel_b = construct_regression_panel(panel_em_exchina)
    run_alt_ols(reg_panel_b, "em_exchina")

    logging.info("robustness_alt_control.py complete")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
