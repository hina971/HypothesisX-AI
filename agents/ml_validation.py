import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)
from sklearn.metrics import (
    r2_score,
    mean_squared_error
)


class MLValidationAgent:

    def run(self, df, patterns):

        if len(df) < 20:
            return {
                "status": "Insufficient data",
                "message": "At least 20 rows are recommended for ML validation.",
                "models": []
            }

        numeric_columns = df.select_dtypes(
            include=np.number
        ).columns.tolist()

        if len(numeric_columns) < 2:
            return {
                "status": "Insufficient numeric variables",
                "message": "At least two numeric variables are required.",
                "models": []
            }

        if patterns:
            target = patterns[0]["variable_2"]
        else:
            target = numeric_columns[-1]

        features = [
            column
            for column in numeric_columns
            if column != target
        ]

        if not features:
            return {
                "status": "No features available",
                "models": []
            }

        data = df[features + [target]].dropna()

        if len(data) < 20:
            return {
                "status": "Insufficient clean rows",
                "models": []
            }

        X = data[features]
        y = data[target]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        models = {
            "Random Forest": RandomForestRegressor(
                n_estimators=100,
                random_state=42
            ),
            "Gradient Boosting": GradientBoostingRegressor(
                random_state=42
            )
        }

        results = []

        for name, model in models.items():

            try:
                model.fit(X_train, y_train)

                predictions = model.predict(X_test)

                r2 = r2_score(y_test, predictions)

                rmse = np.sqrt(
                    mean_squared_error(
                        y_test,
                        predictions
                    )
                )

                feature_importance = {}

                if hasattr(model, "feature_importances_"):
                    for feature, importance in zip(
                        features,
                        model.feature_importances_
                    ):
                        feature_importance[feature] = round(
                            float(importance), 4
                        )

                results.append({
                    "model": name,
                    "target": target,
                    "features": features,
                    "r2": round(float(r2), 4),
                    "rmse": round(float(rmse), 4),
                    "feature_importance": feature_importance
                })

            except Exception as error:

                results.append({
                    "model": name,
                    "error": str(error)
                })

        return {
            "status": "Completed",
            "models": results
        }