"""
tests/test_phase3.py - Nyquist tests for Phase 3 primary empirics.

Run: pytest tests/test_phase3.py --collect-only -q
"""
import ast
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

OUTPUT_FIGURES = config.OUTPUT_DIR / "figures"
OUTPUT_TABLES = config.OUTPUT_DIR / "tables"
PANEL_PATH = config.PROCESSED_DIR / "panel.parquet"
GPR_PATH = config.RAW_DIR / "data_gpr_export.xls"


def _read_text(path: Path) -> str:
    assert path.exists(), f"Missing expected output: {path}"
    return path.read_text()


def _cohort_column(df: pd.DataFrame) -> str:
    for column in ("cohort", "event_label", "event"):
        if column in df.columns:
            return column
    raise AssertionError("Expected cohort or event label column in event-study output")


def test_three_cohorts():
    from src.analysis import event_study

    panel_df = pd.read_parquet(PANEL_PATH)
    stacked = event_study.build_stacked_dataset(panel_df)

    assert stacked["cohort"].nunique() == 3
    assert set(stacked.groupby("cohort")["event_rel_time"].min()) == {-36}
    assert set(stacked.groupby("cohort")["event_rel_time"].max()) == {24}
    pre_counts = (
        stacked[stacked["event_rel_time"].between(-36, -1)]
        .groupby("cohort")["event_rel_time"]
        .nunique()
    )
    assert (pre_counts == 36).all()
    assert {"overlaps_other_event_window", "overlap_event_labels"}.issubset(stacked.columns)
    assert stacked["overlaps_other_event_window"].any()


def test_figure2_exists():
    path = OUTPUT_FIGURES / "figure2_event_study.pdf"
    assert path.exists()
    assert path.stat().st_size > 0


def test_figure2_panels():
    car = pd.read_csv(OUTPUT_TABLES / "event_study_car.csv")
    cohort_col = _cohort_column(car)

    assert car[cohort_col].nunique() == 3
    expected_window = set(range(-12, 25))
    for cohort, group in car.groupby(cohort_col):
        assert set(group["event_rel_time"]) == expected_window, cohort


def test_event_study_coefs():
    """Event-study table presents descriptive CARs without HC3 inference claim."""
    content = _read_text(OUTPUT_TABLES / "table_event_study_coefs.tex")
    # HC3 claim must be absent — design is saturated and HC3 is undefined
    assert "HC3" not in content, (
        "table_event_study_coefs.tex must not claim HC3 robust standard errors; "
        "the saturated cohort x time design makes HC3 undefined."
    )
    assert "CAR" in content
    assert "Descriptive" in content or "descriptive" in content


def test_event_study_coefs_no_inference_columns():
    """event_study_car.csv must not contain blank HC3 inference columns."""
    import pandas as pd
    df = pd.read_csv(OUTPUT_TABLES / "event_study_car.csv")
    for col in ("hc3_se", "t_stat", "p_value"):
        assert col not in df.columns, (
            f"event_study_car.csv contains hollow inference column '{col}'. "
            "Remove HC3/inference columns from the saturated-design event-study output."
        )
    assert "coefficient" in df.columns
    assert "car" in df.columns


def test_table2_exists():
    path = OUTPUT_TABLES / "table2_ols.tex"
    assert path.exists()
    assert path.stat().st_size > 0


def test_panel_ols_results_csv_contract():
    source = PROJECT_ROOT / "src" / "analysis" / "panel_ols.py"
    content = _read_text(source)
    assert "from linearmodels import PanelOLS" in content
    assert "entity_effects=True" in content
    assert "time_effects=True" in content
    assert "BOOTSTRAP_ITERATIONS = 999" in content
    assert "weights_type=WILD_BOOTSTRAP_WEIGHTS" in content

    csv_path = OUTPUT_TABLES / "panel_ols_results.csv"
    df = pd.read_csv(csv_path)
    expected_columns = {
        "specification",
        "term",
        "coef",
        "std_error",
        "p_value",
        "wild_p_value",
        "note",
    }
    assert expected_columns.issubset(df.columns)
    expected_terms = {
        "post_stewardship",
        "post_cgc",
        "post_tse_pb_reform",
        "stewardship_x_japan",
        "cgc_x_japan",
        "tse_pb_reform_x_japan",
    }
    assert expected_terms.issubset(set(df["term"]))
    # OLS-03: wild-bootstrap p-values must be populated for interaction terms
    ix_rows = df[
        (df["specification"] == "+ reform x Japan")
        & (df["term"].isin(["stewardship_x_japan", "cgc_x_japan", "tse_pb_reform_x_japan"]))
    ]
    assert ix_rows["wild_p_value"].notna().all(), (
        "Wild-bootstrap p-values must be non-null for all three reform x Japan "
        f"interaction rows:\n{ix_rows[['term','wild_p_value']].to_string()}"
    )


def test_table2_reform_dummies():
    content = _read_text(OUTPUT_TABLES / "table2_ols.tex").lower()
    expected_reforms = (
        ("stewardship", "2014"),
        ("corporate governance", "cgc", "2015"),
        ("tse", "p/b", "2023"),
    )
    for reform_tokens in expected_reforms:
        assert any(token in content for token in reform_tokens), reform_tokens
    assert "japan" in content


def test_table2_booktabs():
    content = _read_text(OUTPUT_TABLES / "table2_ols.tex")
    assert "\\toprule" in content
    assert "\\midrule" in content
    assert "\\bottomrule" in content


def test_table2_wild_bootstrap_displayed():
    """Table 2 must display wild-bootstrap p-values in brackets for interaction terms."""
    import re
    content = _read_text(OUTPUT_TABLES / "table2_ols.tex")
    # Pattern: coefficient followed by bracketed wild-p, e.g. "-0.15 [0.032]"
    wild_p_cells = re.findall(r"-?\d+\.\d{2} \[\d+\.\d{3}\]", content)
    assert len(wild_p_cells) >= 3, (
        f"Expected at least 3 wild-bootstrap p-value cells in table2_ols.tex, "
        f"found {len(wild_p_cells)}: {wild_p_cells}"
    )
    # The old misleading note must be absent
    assert "Wild-bootstrap p-values use 999 Rademacher draws clustered by country." not in content, (
        "Old note referencing undisplayed wild-bootstrap p-values must be removed from Table 2."
    )
    # The new accurate note must be present
    assert "bracketed values are" in content, (
        "Table 2 note must describe that bracketed values are wild-bootstrap p-values."
    )


def test_gpr_threshold():
    from src.analysis import geo_risk

    loaded = geo_risk.load_gpr_korea()
    gpr = loaded[0] if isinstance(loaded, tuple) else loaded

    escalation_cols = [
        column for column in gpr.columns if "escalation" in column.lower()
    ]
    assert escalation_cols, "Expected an escalation indicator column"
    escalation_share = gpr[escalation_cols[0]].mean()
    assert 0.20 <= escalation_share <= 0.30


def test_figure3_exists():
    path = OUTPUT_FIGURES / "figure3_geo_risk.pdf"
    assert path.exists()
    assert path.stat().st_size > 0


def test_geo_caveats():
    content = _read_text(OUTPUT_TABLES / "table3_geo_risk.tex").lower()
    assert "partial identification" in content or "caveat" in content


def test_analysis_modules_do_not_import_each_other():
    analysis_modules = {"event_study", "panel_ols", "geo_risk"}

    for module_name in analysis_modules:
        path = PROJECT_ROOT / "src" / "analysis" / f"{module_name}.py"
        if not path.exists():
            continue

        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.module is None:
                continue

            module = node.module
            if module.startswith(("src.analysis.", "analysis.")):
                imported_module = module.rsplit(".", maxsplit=1)[-1]
                assert imported_module not in analysis_modules - {module_name}, (
                    f"{path} imports another Phase 3 analysis module: {module}"
                )

            if module in {"src.analysis", "analysis"}:
                imported_names = {alias.name for alias in node.names}
                forbidden = imported_names & (analysis_modules - {module_name})
                assert not forbidden, (
                    f"{path} imports another Phase 3 analysis module: {forbidden}"
                )
