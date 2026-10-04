import numpy as np
from scipy.stats import pearsonr


class RobustnessAgent:

    def run(self, df, patterns):

        results = []

        for pattern in patterns[:5]:

            x_col = pattern["variable_1"]
            y_col = pattern["variable_2"]

            data = df[[x_col, y_col]].dropna()

            if len(data) < 10:
                continue

            original_corr = pattern["correlation"]

            # Remove extreme values using quantiles
            x_low = data[x_col].quantile(0.05)
            x_high = data[x_col].quantile(0.95)

            y_low = data[y_col].quantile(0.05)
            y_high = data[y_col].quantile(0.95)

            filtered = data[
                (data[x_col] >= x_low) &
                (data[x_col] <= x_high) &
                (data[y_col] >= y_low) &
                (data[y_col] <= y_high)
            ]

            if len(filtered) >= 5:

                new_corr, _ = pearsonr(
                    filtered[x_col],
                    filtered[y_col]
                )

                change = abs(
                    abs(original_corr) - abs(new_corr)
                )

                if change < 0.10:
                    stability = "Stable"
                elif change < 0.20:
                    stability = "Moderately Stable"
                else:
                    stability = "Sensitive"

                results.append({
                    "variable_x": x_col,
                    "variable_y": y_col,
                    "original_correlation": round(
                        float(original_corr), 4
                    ),
                    "outlier_removed_correlation": round(
                        float(new_corr), 4
                    ),
                    "correlation_change": round(
                        float(change), 4
                    ),
                    "stability": stability
                })

        return results