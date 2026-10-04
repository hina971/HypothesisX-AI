import pandas as pd
from utils.analysis_utils import (
    get_numeric_columns,
    get_categorical_columns,
    detect_outliers
)


class DataExplorerAgent:

    def run(self, df):
        numeric_columns = get_numeric_columns(df)
        categorical_columns = get_categorical_columns(df)

        missing_values = df.isnull().sum()

        missing_values = missing_values[
            missing_values > 0
        ].sort_values(ascending=False)

        outliers = {}

        for column in numeric_columns:
            outliers[column] = detect_outliers(df, column)

        if numeric_columns:
            statistics = df[numeric_columns].describe().T
        else:
            statistics = pd.DataFrame()

        return {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "column_names": df.columns.tolist(),
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "missing_values": missing_values.to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
            "outliers": outliers,
            "statistics": statistics
        }