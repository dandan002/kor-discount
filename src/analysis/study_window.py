"""
study_window.py - Shared helpers for clipping panels to a study horizon.
"""
import datetime

import pandas as pd


def clip_to_study_end(
    frame: pd.DataFrame, study_end: datetime.date | pd.Timestamp
) -> pd.DataFrame:
    if "date" not in frame.columns:
        raise ValueError("frame must contain a 'date' column")

    resolved_end = pd.Timestamp(study_end)
    return frame.loc[frame["date"] <= resolved_end].copy()
