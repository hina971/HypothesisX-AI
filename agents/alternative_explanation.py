class AlternativeExplanationAgent:

    def run(self, hypotheses):

        results = []

        common_explanations = [
            "A confounding variable may influence both variables.",
            "Outliers may be contributing strongly to the observed relationship.",
            "Sampling effects may have produced the observed pattern.",
            "Measurement errors may affect one or both variables.",
            "The relationship may be non-causal and only represent association.",
            "Temporal or environmental effects may influence the relationship.",
            "The observed relationship may be a spurious correlation."
        ]

        for hypothesis in hypotheses:

            results.append({
                "id": hypothesis["id"],
                "hypothesis": hypothesis["hypothesis"],
                "alternative_explanations": common_explanations
            })

        return results