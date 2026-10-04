import numpy as np
import pandas as pd


def get_numeric_columns(df):
    return df.select_dtypes(include=np.number).columns.tolist()


def get_categorical_columns(df):
    return df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()


def detect_outliers(df, column):
    """
    Detect outliers using the IQR method.
    """

    series = pd.to_numeric(df[column], errors="coerce").dropna()

    if len(series) < 4:
        return 0

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    iqr = q3 - q1

    if iqr == 0:
        return 0

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return int(((series < lower) | (series > upper)).sum())


def safe_round(value, digits=4):
    try:
        return round(float(value), digits)
    except Exception:
        return value