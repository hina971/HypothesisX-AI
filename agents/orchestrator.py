from agents.data_explorer import DataExplorerAgent
from agents.pattern_mining import PatternMiningAgent
from agents.hypothesis_generator import HypothesisGeneratorAgent
from agents.alternative_explanation import (
    AlternativeExplanationAgent
)
from agents.statistical_testing import (
    StatisticalTestingAgent
)
from agents.ml_validation import MLValidationAgent
from agents.robustness import RobustnessAgent
from agents.evidence_reviewer import EvidenceReviewerAgent


class OrchestratorAgent:

    def __init__(self):

        self.data_explorer = DataExplorerAgent()
        self.pattern_mining = PatternMiningAgent()
        self.hypothesis_generator = (
            HypothesisGeneratorAgent()
        )
        self.alternative_explanation = (
            AlternativeExplanationAgent()
        )
        self.statistical_testing = (
            StatisticalTestingAgent()
        )
        self.ml_validation = MLValidationAgent()
        self.robustness = RobustnessAgent()
        self.evidence_reviewer = (
            EvidenceReviewerAgent()
        )

    def run(self, df):

        # 1. Data Exploration
        exploration = self.data_explorer.run(df)

        # 2. Pattern Mining
        patterns = self.pattern_mining.run(df)

        # 3. Hypothesis Generation
        hypotheses = self.hypothesis_generator.run(
            patterns
        )

        # 4. Alternative Explanations
        alternatives = (
            self.alternative_explanation.run(
                hypotheses
            )
        )

        # 5. Statistical Testing
        statistical_results = (
            self.statistical_testing.run(
                df,
                patterns
            )
        )

        # 6. ML Validation
        ml_results = self.ml_validation.run(
            df,
            patterns
        )

        # 7. Robustness
        robustness_results = self.robustness.run(
            df,
            patterns
        )

        # 8. Evidence Review
        evidence = self.evidence_reviewer.run(
            hypotheses,
            statistical_results,
            ml_results,
            robustness_results
        )

        # 9. Next Investigation
        next_investigation = self._next_investigation(
            evidence
        )

        return {
            "exploration": exploration,
            "patterns": patterns,
            "hypotheses": hypotheses,
            "alternatives": alternatives,
            "statistical_results": statistical_results,
            "ml_results": ml_results,
            "robustness": robustness_results,
            "evidence": evidence,
            "next_investigation": next_investigation
        }

    def _next_investigation(self, evidence):

        if not evidence:
            return (
                "No sufficiently strong relationship was "
                "identified. Explore additional variables "
                "or collect more data."
            )

        strong = [
            item
            for item in evidence
            if item["evidence_level"] ==
            "Strong Evidence"
        ]

        moderate = [
            item
            for item in evidence
            if item["evidence_level"] ==
            "Moderate Evidence"
        ]

        if strong:
            return (
                "Investigate the strongest relationship "
                "using additional confounder analysis, "
                "alternative datasets, and causal methods."
            )

        if moderate:
            return (
                "Perform additional robustness testing "
                "and investigate possible confounding variables."
            )

        return (
            "Collect additional data and investigate "
            "alternative explanations before drawing conclusions."
        )