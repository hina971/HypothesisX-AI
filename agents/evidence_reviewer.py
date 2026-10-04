class EvidenceReviewerAgent:

    def run(
        self,
        hypotheses,
        statistical_results,
        ml_results,
        robustness_results
    ):

        reviews = []

        for hypothesis in hypotheses:

            h_id = hypothesis["id"]

            stats = next(
                (
                    result
                    for result in statistical_results
                    if result["variable_x"] ==
                    hypothesis["variable_x"]
                    and
                    result["variable_y"] ==
                    hypothesis["variable_y"]
                ),
                None
            )

            robustness = next(
                (
                    result
                    for result in robustness_results
                    if result["variable_x"] ==
                    hypothesis["variable_x"]
                    and
                    result["variable_y"] ==
                    hypothesis["variable_y"]
                ),
                None
            )

            score = 0

            if stats:

                if stats["p_value"] < 0.05:
                    score += 1

                if abs(stats["correlation"]) >= 0.5:
                    score += 1

                if stats["r_squared"] >= 0.25:
                    score += 1

            if robustness:
                if robustness["stability"] == "Stable":
                    score += 1
                elif robustness["stability"] == "Moderately Stable":
                    score += 0.5

            if score >= 3:
                evidence = "Strong Evidence"
            elif score >= 2:
                evidence = "Moderate Evidence"
            elif score >= 1:
                evidence = "Weak Evidence"
            else:
                evidence = "Insufficient Evidence"

            reviews.append({
                "id": h_id,
                "hypothesis": hypothesis["hypothesis"],
                "evidence_level": evidence,
                "evidence_score": score,
                "statistical_result": stats,
                "robustness_result": robustness,
                "interpretation": (
                    "This is an evidence-supported association, "
                    "not proof of causation."
                )
            })

        return reviews