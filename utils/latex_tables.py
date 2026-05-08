"""
DataFrame to LaTeX table exporter for Korea Discount study.

All analysis scripts call df_to_latex() to drop .tex fragments into
outputs/tables/. The paper inputs them directly.

Table format: booktabs (\\toprule, \\midrule, \\bottomrule), centered,
with caption, label, and optional footnote in \\footnotesize.
"""

import pandas as pd


def df_to_latex(df, caption, label, footnote=None, float_format="%.3f"):
    """
    Convert a pandas DataFrame to a standalone booktabs LaTeX table fragment.

    Args:
        df: pd.DataFrame to export
        caption: table caption (e.g. "Summary Statistics by Compliance Group")
        label: LaTeX label key (e.g. "tab:summary")
        footnote: optional note in footnotesize below the table
        float_format: printf-style format for float columns (default "%.3f")

    Returns:
        Complete standalone .tex table fragment as a string.

    Example:
        tex = df_to_latex(
            summary_df,
            caption="Summary Statistics by Compliance Group",
            label="tab:summary",
            footnote="* p<0.10, ** p<0.05, *** p<0.01. HC3 robust standard errors.",
        )
        with open("outputs/tables/table1_summary.tex", "w") as f:
            f.write(tex)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    col_format = "l" + "r" * len(df.columns)
    body = df.to_latex(
        float_format=float_format,
        escape=False,
        column_format=col_format,
        index=True,
    )
    lines = [
        r"\begin{table}[htbp]",
        r"  \centering",
        rf"  \caption{{{caption}}}",
        rf"  \label{{{label}}}",
        body.strip(),
    ]
    if footnote:
        lines.append(
            r"  \begin{tablenotes}"
            "\n"
            r"    \footnotesize\item \textit{Note:} "
            + footnote
            + "\n"
            r"  \end{tablenotes}"
        )
    lines.append(r"\end{table}")
    return "\n".join(lines)
