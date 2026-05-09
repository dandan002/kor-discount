"""
robustness_pe.py - ROBUST-02: Full Phase 3 replication using P/E instead of P/B.

Re-runs event study, panel OLS (with wild-bootstrap inference), and GPR sub-analysis
with P/E as the dependent variable. Uses same estimation windows, fixed effects, and
standard error methods as Phase 3 (carry-forward from 03-CONTEXT.md D-01 through D-15).
All outputs written to output/robustness/ with _pe suffix on filenames.

Decisions: D-10 (full replication), D-11 (carry-forward methodology), D-18 (output naming).
"""
import logging
import math
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from linearmodels import PanelOLS
from linearmodels.panel.data import PanelData
from wildboottest.wildboottest import wildboottest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)

ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"

STACK_WINDOW_MIN = -36
STACK_WINDOW_MAX = 24
EVENT_WINDOW_MIN = -12
EVENT_WINDOW_MAX = 24
BASE_PERIOD = -1
ESTIMATION_WINDOW_MONTHS = 36
REQUIRE_COMPLETE_EVENT_WINDOWS = True
EVENT_OUTPUT_COLUMNS = [
    "cohort",
    "event_label",
    "event_rel_time",
    "coefficient",
    "car",
]

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

GPR_ESCALATION_QUANTILE = 0.75
STUDY_START = pd.Timestamp("2004-01-01")
GPR_FILENAME = "data_gpr_export.xls"
GPR_COLUMN = "GPRC_KOR"


def load_panel_pe() -> pd.DataFrame:
    """Load the canonical panel and drop rows without P/E before any analysis."""
    panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    panel_pe = panel.dropna(subset=["pe"]).copy()
    logging.info(
        "Panel PE: %d rows after dropping %d PE nulls",
        len(panel_pe),
        len(panel) - len(panel_pe),
    )
    return panel_pe


def _month_distance(dates: pd.Series | pd.DatetimeIndex, event_date: pd.Timestamp) -> pd.Series:
    """Return whole calendar-month distance from event_date to each date."""
    date_index = pd.DatetimeIndex(dates)
    rel_time = (date_index.year - event_date.year) * 12 + (
        date_index.month - event_date.month
    )
    return pd.Series(rel_time, index=date_index)


def _event_label(event_date: pd.Timestamp) -> str:
    """Look up the locked event label for a pandas timestamp."""
    return config.EVENT_LABELS[event_date.date()]


def _event_cohort(event_date: pd.Timestamp) -> str:
    """Stable cohort identifier derived from the locked config event date."""
    return event_date.date().isoformat()


def build_stacked_dataset(panel: pd.DataFrame) -> pd.DataFrame:
    """Create three full event-window cohorts with abnormal KOSPI-TOPIX P/E spread."""
    required_columns = {"date", "country", "pe"}
    missing_columns = required_columns - set(panel.columns)
    if missing_columns:
        raise ValueError(f"Panel is missing required columns: {sorted(missing_columns)}")

    df = panel.loc[:, ["date", "country", "pe"]].copy()
    df["date"] = pd.to_datetime(df["date"])

    event_dates = [pd.Timestamp(event_date) for event_date in config.EVENT_DATES]
    required_periods: set[pd.Period] = set()
    for event_date in event_dates:
        event_period = event_date.to_period("M")
        required_periods.update(
            event_period + offset
            for offset in range(STACK_WINDOW_MIN, STACK_WINDOW_MAX + 1)
        )

    pivot = (
        df.pivot(index="date", columns="country", values="pe")
        .sort_index()
        .loc[lambda frame: frame.index.to_period("M").isin(required_periods)]
    )
    for country in ("KOSPI", "TOPIX"):
        if country not in pivot.columns:
            raise ValueError(f"Panel is missing required country: {country}")

    spread = (pivot["KOSPI"] - pivot["TOPIX"]).rename("pe_spread").dropna().to_frame()
    cohorts: list[pd.DataFrame] = []
    expected_rel_times = set(range(STACK_WINDOW_MIN, STACK_WINDOW_MAX + 1))
    expected_pre_times = set(range(STACK_WINDOW_MIN, BASE_PERIOD + 1))

    for event_date in event_dates:
        cohort = spread.copy()
        cohort["event_rel_time"] = _month_distance(cohort.index, event_date).astype(int)
        cohort = cohort[
            cohort["event_rel_time"].between(STACK_WINDOW_MIN, STACK_WINDOW_MAX)
        ].copy()

        observed_rel_times = set(cohort["event_rel_time"])
        if REQUIRE_COMPLETE_EVENT_WINDOWS and observed_rel_times != expected_rel_times:
            missing = sorted(expected_rel_times - observed_rel_times)
            extra = sorted(observed_rel_times - expected_rel_times)
            raise ValueError(
                "Panel cannot supply complete event window "
                f"{STACK_WINDOW_MIN}..{STACK_WINDOW_MAX} for {_event_label(event_date)}; "
                f"missing={missing}, extra={extra}"
            )

        overlap_labels: list[str] = []
        for row_date in cohort.index:
            labels = []
            for other_date in event_dates:
                if other_date == event_date:
                    continue
                other_rel_time = _month_distance(pd.DatetimeIndex([row_date]), other_date).iloc[0]
                if STACK_WINDOW_MIN <= other_rel_time <= STACK_WINDOW_MAX:
                    labels.append(_event_label(other_date))
            overlap_labels.append("; ".join(labels))

        cohort["overlap_event_labels"] = overlap_labels
        cohort["overlaps_other_event_window"] = cohort["overlap_event_labels"].ne("")

        pre = cohort[cohort["event_rel_time"].between(STACK_WINDOW_MIN, BASE_PERIOD)].copy()
        observed_pre_times = set(pre["event_rel_time"])
        if observed_pre_times != expected_pre_times or len(pre) != ESTIMATION_WINDOW_MONTHS:
            missing = sorted(expected_pre_times - observed_pre_times)
            raise ValueError(
                "Panel cannot supply all 36 pre-event months "
                f"{STACK_WINDOW_MIN}..{BASE_PERIOD} for {_event_label(event_date)}; "
                f"missing={missing}"
            )

        trend_x = sm.add_constant(pre["event_rel_time"].astype(float), has_constant="add")
        trend_model = sm.OLS(pre["pe_spread"].astype(float), trend_x).fit()
        predict_x = sm.add_constant(
            cohort["event_rel_time"].astype(float),
            has_constant="add",
        )
        cohort["expected_spread"] = trend_model.predict(predict_x)
        cohort["abnormal_spread"] = cohort["pe_spread"] - cohort["expected_spread"]
        cohort["cohort"] = _event_cohort(event_date)
        cohort["event_label"] = _event_label(event_date)
        cohort = cohort.reset_index(names="date")

        cohorts.append(
            cohort[
                [
                    "date",
                    "cohort",
                    "event_label",
                    "event_rel_time",
                    "pe_spread",
                    "expected_spread",
                    "abnormal_spread",
                    "overlaps_other_event_window",
                    "overlap_event_labels",
                ]
            ]
        )

    return pd.concat(cohorts, ignore_index=True)


def estimate_event_study(stacked: pd.DataFrame) -> pd.DataFrame:
    """Estimate cohort x relative-time effects as descriptive P/E estimates."""
    windowed = stacked[
        stacked["event_rel_time"].between(EVENT_WINDOW_MIN, EVENT_WINDOW_MAX)
    ].copy()
    expected_times = list(range(EVENT_WINDOW_MIN, EVENT_WINDOW_MAX + 1))

    labels_by_cohort = (
        windowed[["cohort", "event_label"]]
        .drop_duplicates()
        .set_index("cohort")["event_label"]
        .to_dict()
    )

    design_names = []
    design_data: dict[str, list[float]] = {}
    cohort_values = windowed["cohort"].to_numpy()
    rel_values = windowed["event_rel_time"].to_numpy()
    for cohort in [_event_cohort(pd.Timestamp(event_date)) for event_date in config.EVENT_DATES]:
        for rel_time in expected_times:
            if rel_time == BASE_PERIOD:
                continue
            column = f"cohort_{cohort}__rel_{rel_time}"
            design_data[column] = [
                float(is_match)
                for is_match in (cohort_values == cohort) & (rel_values == rel_time)
            ]
            design_names.append(column)

    y = windowed["abnormal_spread"].astype(float)
    x = pd.DataFrame(design_data, index=windowed.index, columns=design_names)
    ols_result = sm.OLS(y, x).fit()
    params = pd.Series(ols_result.params.astype(float), index=design_names)

    rows = []
    for event_date in [pd.Timestamp(event_date) for event_date in config.EVENT_DATES]:
        cohort = _event_cohort(event_date)
        event_label = labels_by_cohort.get(cohort, _event_label(event_date))
        for rel_time in expected_times:
            if rel_time == BASE_PERIOD:
                row = {
                    "cohort": cohort,
                    "event_label": event_label,
                    "event_rel_time": rel_time,
                    "coefficient": 0.0,
                }
            else:
                column = f"cohort_{cohort}__rel_{rel_time}"
                row = {
                    "cohort": cohort,
                    "event_label": event_label,
                    "event_rel_time": rel_time,
                    "coefficient": float(params[column]),
                }
            rows.append(row)

    car = pd.DataFrame(rows)
    car["car"] = car.groupby("cohort", sort=False)["coefficient"].cumsum()
    return car.loc[:, EVENT_OUTPUT_COLUMNS]


def _write_event_latex_table(car_df: pd.DataFrame, path: Path) -> None:
    """Write the P/E event-study coefficient table as descriptive CARs."""
    table = car_df.copy()
    table = table.rename(
        columns={
            "event_label": "Event",
            "event_rel_time": "Month",
            "coefficient": "Coefficient",
            "car": "CAR",
        }
    )
    table = table.drop(columns=["cohort"])
    latex = table.to_latex(
        index=False,
        escape=False,
        float_format="%.2f",
        na_rep="--",
        caption="P/E stacked event-study descriptive CAR estimates (no inference reported).",
        label="tab:robustness_pe_event_study_coefs",
    )
    path.write_text(
        "% P/E robustness descriptive CARs: coefficients and cumulative abnormal KOSPI-TOPIX P/E spread.\n"
        "% Standard errors are not reported: the saturated cohort x relative-time design\n"
        "% makes sandwich robust inference undefined. See paper text for robustness discussion.\n"
        + latex,
        encoding="utf-8",
    )


def run_pe_event_study(panel_pe: pd.DataFrame) -> pd.DataFrame:
    """Run the Phase 3 event-study design with P/E as the valuation metric."""
    stacked = build_stacked_dataset(panel_pe)
    car = estimate_event_study(stacked)
    tex_path = ROBUSTNESS_DIR / "robustness_pe_event_coefs.tex"
    _write_event_latex_table(car, tex_path)
    logging.info("Saved %s", tex_path)
    final_cars = (
        car[car["event_rel_time"] == EVENT_WINDOW_MAX]
        .loc[:, ["event_label", "car"]]
        .to_string(index=False)
    )
    logging.info("P/E event-study CARs at +%d months:\n%s", EVENT_WINDOW_MAX, final_cars)
    return car


def construct_regression_panel(panel: pd.DataFrame) -> pd.DataFrame:
    """Construct reform indicators and return a country-date indexed P/E panel."""
    required_columns = {"date", "country", "pe"}
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
            reg_panel["pe"],
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
    """Append normalized result rows for all P/E robustness table terms."""
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

        rows.append(
            {
                "specification": specification,
                "term": term,
                "coef": math.nan,
                "std_error": math.nan,
                "p_value": math.nan,
                "wild_p_value": math.nan,
                "note": "not included",
            }
        )


def _wild_bootstrap_pvalues(reg_panel: pd.DataFrame) -> pd.Series:
    """Compute FWL wild-bootstrap p-values for the Japan interaction terms."""
    y_dm = (
        PanelData(reg_panel[["pe"]])
        .demean(group="both", return_panel=False)
        .dataframe["pe"]
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


def _format_table_cell(row: pd.Series) -> str:
    """Format one coefficient cell for the P/E regression table."""
    note = row.get("note")
    if note == "absorbed by time FE":
        return "absorbed by time FE"
    if note == "not included" or pd.isna(row.get("coef")):
        return ""

    coef = float(row["coef"])
    std_error = float(row["std_error"])
    wild_p = row.get("wild_p_value")

    if (
        row.get("term") in INTERACTION_TERMS
        and row.get("specification") == INTERACTIONS_SPEC
        and wild_p is not None
        and not pd.isna(wild_p)
    ):
        return f"{coef:.2f} [{float(wild_p):.3f}]"

    return f"{coef:.2f} ({std_error:.2f})"


def write_latex_table(results_df: pd.DataFrame) -> None:
    """Write the booktabs PanelOLS P/E robustness LaTeX artifact."""
    table = pd.DataFrame(
        "",
        index=TABLE_TERMS,
        columns=[BASELINE_SPEC, DUMMIES_SPEC, INTERACTIONS_SPEC],
    )
    table.index.name = "term"

    for _, row in results_df.iterrows():
        term = row["term"]
        specification = row["specification"]
        if term in table.index and specification in table.columns:
            table.loc[term, specification] = _format_table_cell(row)

    latex_str = table.style.to_latex(
        hrules=True,
        caption=(
            "P/E robustness: two-way fixed effects PanelOLS estimates of "
            "Japan reform valuation responses."
        ),
        label="tab:robustness_pe_panel_ols",
    )
    note = (
        "\\multicolumn{4}{l}{\\footnotesize Note: Coefficients use P/E "
        "(price-to-earnings) as the dependent variable in two-way FE PanelOLS. "
        "For \\textit{+ reform x Japan} specification, bracketed values are "
        "wild-bootstrap p-values (999 Rademacher draws, clustered by country). "
        "Standard errors shown for all other estimable cells.} \\\\\n"
    )
    latex_str = latex_str.replace("\\bottomrule\n", note + "\\bottomrule\n")

    output_path = ROBUSTNESS_DIR / "robustness_pe_ols.tex"
    output_path.write_text(latex_str, encoding="utf-8")
    logging.info("Saved %s", output_path)


def run_pe_panel_ols(panel_pe: pd.DataFrame) -> pd.DataFrame:
    """Run Phase 3 panel OLS specifications with P/E as the dependent variable."""
    reg_panel = construct_regression_panel(panel_pe)
    results_df, model_stats = fit_panel_specs(reg_panel)
    logging.info("P/E PanelOLS model stats:\n%s", model_stats.to_string(index=False))
    interactions = results_df[
        (results_df["specification"] == INTERACTIONS_SPEC)
        & (results_df["term"].isin(INTERACTION_TERMS))
    ].loc[:, ["term", "coef", "wild_p_value"]]
    logging.info("P/E PanelOLS Japan interactions:\n%s", interactions.to_string(index=False))
    write_latex_table(results_df)
    return results_df


def load_gpr_korea() -> tuple[pd.DataFrame, float]:
    """Load Korea country-level GPR and construct the escalation dummy."""
    gpr_path = config.RAW_DIR / GPR_FILENAME
    gpr = pd.read_excel(
        gpr_path,
        usecols=["month", GPR_COLUMN],
        engine="xlrd",
    )
    gpr = gpr.rename(columns={"month": "date"})
    gpr["date"] = pd.to_datetime(gpr["date"])
    gpr = gpr.dropna(subset=[GPR_COLUMN])

    study = gpr[
        (gpr["date"] >= STUDY_START) & (gpr["date"] <= STUDY_END)
    ].copy()
    threshold = study[GPR_COLUMN].quantile(GPR_ESCALATION_QUANTILE)
    study["gpr_escalation_dummy"] = (study[GPR_COLUMN] > threshold).astype(int)

    return study, float(threshold)


def build_geo_regression_data(panel: pd.DataFrame, gpr: pd.DataFrame) -> pd.DataFrame:
    """Merge monthly KOSPI/TOPIX P/E values with Korea GPR escalation data."""
    panel_study = panel[panel["date"] <= STUDY_END].copy()
    pe = (
        panel_study.pivot(index="date", columns="country", values="pe")
        .reset_index()
        .rename(columns={"KOSPI": "kospi_pe", "TOPIX": "topix_pe"})
    )
    pe["month_period"] = pe["date"].dt.to_period("M")

    gpr_study = gpr.copy()
    gpr_study["date"] = pd.to_datetime(gpr_study["date"])
    gpr_study["month_period"] = gpr_study["date"].dt.to_period("M")

    merged = pe.merge(
        gpr_study[[GPR_COLUMN, "gpr_escalation_dummy", "month_period"]],
        on="month_period",
        how="inner",
    )
    merged["year"] = merged["date"].dt.year.astype("category")
    merged = merged.sort_values("date")

    required = ["kospi_pe", "topix_pe", "gpr_escalation_dummy"]
    return merged.dropna(subset=required).reset_index(drop=True)


def estimate_geo_model(reg_df: pd.DataFrame):
    """Estimate KOSPI P/E on GPR escalation, TOPIX P/E, and year FE."""
    model = smf.ols(
        "kospi_pe ~ gpr_escalation_dummy + topix_pe + C(year)",
        data=reg_df,
    ).fit()
    return model.get_robustcov_results(cov_type="HC3")


def run_pe_geo_risk(panel_pe: pd.DataFrame) -> None:
    """Run the Phase 3 GPR sub-analysis with P/E and log the key coefficient."""
    gpr, threshold = load_gpr_korea()
    reg_df = build_geo_regression_data(panel_pe, gpr)
    result = estimate_geo_model(reg_df)
    names = result.model.exog_names
    gpr_idx = names.index("gpr_escalation_dummy")
    topix_idx = names.index("topix_pe")
    logging.info(
        "P/E GPR threshold %.4f; escalation share %.3f; N=%d",
        threshold,
        reg_df["gpr_escalation_dummy"].mean(),
        len(reg_df),
    )
    logging.info(
        "P/E GPR coefficient %.4f (HC3 p=%.4f); TOPIX P/E coefficient %.4f (HC3 p=%.4f)",
        float(result.params[gpr_idx]),
        float(result.pvalues[gpr_idx]),
        float(result.params[topix_idx]),
        float(result.pvalues[topix_idx]),
    )


def main() -> None:
    ROBUSTNESS_DIR.mkdir(parents=True, exist_ok=True)
    panel_pe = load_panel_pe()
    run_pe_event_study(panel_pe)
    run_pe_panel_ols(panel_pe)
    run_pe_geo_risk(panel_pe)
    logging.info("robustness_pe.py complete")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
