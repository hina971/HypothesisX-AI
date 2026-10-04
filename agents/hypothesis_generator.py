class HypothesisGeneratorAgent:

    def run(self, patterns):

        hypotheses = []

        for index, pattern in enumerate(patterns[:10], start=1):

            x = pattern["variable_1"]
            y = pattern["variable_2"]
            correlation = pattern["correlation"]

            if correlation > 0:
                direction = "increase"
                relationship = "positive"
            else:
                direction = "decrease"
                relationship = "negative"

            hypothesis = (
                f"H{index}: {x} and {y} show a {relationship} "
                f"relationship. An {direction} in {x} may be "
                f"associated with an {direction} in {y}."
            )

            hypotheses.append({
                "id": f"H{index}",
                "hypothesis": hypothesis,
                "variable_x": x,
                "variable_y": y,
                "correlation": correlation,
                "relationship": relationship
            })

        return hypotheses