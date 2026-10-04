import numpy as np
from scipy.stats import pearsonr, linregress


class StatisticalTestingAgent:

    def run(self, df, patterns):

        results = []

        for pattern in patterns[:10]:

            x_col = pattern["variable_1"]
            y_col = pattern["variable_2"]

            data = df[[x_col, y_col]].dropna()

            if len(data) < 5:
                continue

            x = data[x_col].values
            y = data[y_col].values

            try:
                correlation, p_value = pearsonr(x, y)

                regression = linregress(x, y)

                results.append({
                    "variable_x": x_col,
                    "variable_y": y_col,
                    "correlation": round(
                        float(correlation), 4
                    ),
                    "p_value": round(
                        float(p_value), 6
                    ),
                    "slope": round(
                        float(regression.slope), 4
                    ),
                    "intercept": round(
                        float(regression.intercept), 4
                    ),
                    "r_squared": round(
                        float(regression.rvalue ** 2), 4
                    ),
                    "statistically_significant":
                        bool(p_value < 0.05),
                    "sample_size": len(data)
                })

            except Exception:
                continue

        return results