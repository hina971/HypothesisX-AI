import itertools
import numpy as np
import pandas as pd
from scipy.stats import pearsonr


class PatternMiningAgent:

    def run(self, df):

        numeric_columns = df.select_dtypes(
            include=np.number
        ).columns.tolist()

        patterns = []

        for col1, col2 in itertools.combinations(
            numeric_columns, 2
        ):

            pair = df[[col1, col2]].dropna()

            if len(pair) < 5:
                continue

            if pair[col1].nunique() < 2 or pair[col2].nunique() < 2:
                continue

            try:
                correlation, p_value = pearsonr(
                    pair[col1],
                    pair[col2]
                )

                patterns.append({
                    "variable_1": col1,
                    "variable_2": col2,
                    "correlation": round(float(correlation), 4),
                    "absolute_correlation": round(
                        abs(float(correlation)), 4
                    ),
                    "p_value": round(float(p_value), 6),
                    "sample_size": len(pair)
                })

            except Exception:
                continue

        patterns.sort(
            key=lambda x: x["absolute_correlation"],
            reverse=True
        )

        return patterns