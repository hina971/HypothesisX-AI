"""Hypothesis + Alternative Explanation Agent.

The module is intentionally independent of Streamlit and any specific LLM provider.
The Orchestrator can pass a pattern dictionary to analyze_pattern().
"""

from typing import Any, Dict, List

from models.hypothesis_models import AlternativeExplanation, HypothesisResult

SUPPORTED_PATTERN_TYPES = {
    "correlation", "trend", "association", "cluster", "anomaly", "nonlinear", "feature_interaction"
}


def _require_text(data: Dict[str, Any], key: str) -> str:
    value = data.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"Missing required field: {key}")
    return str(value).strip()


def validate_pattern(pattern: Dict[str, Any]) -> None:
    if not isinstance(pattern, dict):
        raise TypeError("pattern must be a dictionary")
    pattern_type = str(pattern.get("pattern_type", "")).strip().lower()
    if not pattern_type:
        raise ValueError("Missing required field: pattern_type")
    if pattern_type not in SUPPORTED_PATTERN_TYPES:
        raise ValueError(
            f"Unsupported pattern_type '{pattern_type}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_PATTERN_TYPES))}"
        )


def generate_hypothesis(pattern: Dict[str, Any]) -> Dict[str, Any]:
    validate_pattern(pattern)
    ptype = str(pattern["pattern_type"]).strip().lower()
    x = _require_text(pattern, "variable_x")
    y = _require_text(pattern, "variable_y")
    relationship = str(pattern.get("relationship", "")).strip().lower()

    if ptype in {"correlation", "association"}:
        if relationship in {"negative", "inverse"}:
            statement = f"Higher {x} is associated with lower {y}."
            alternative = f"{x} and {y} have a negative association."
        elif relationship in {"positive", "direct"}:
            statement = f"Higher {x} is associated with higher {y}."
            alternative = f"{x} and {y} have a positive association."
        else:
            statement = f"{x} is associated with variation in {y}."
            alternative = f"There is an association between {x} and {y}."
    elif ptype == "trend":
        direction = relationship or "observed"
        statement = f"{y} shows a {direction} trend with respect to {x}."
        alternative = f"The observed {y} trend with respect to {x} is not explained by random variation alone."
    elif ptype == "cluster":
        statement = f"Observations can be meaningfully differentiated into groups using {x} and {y}."
        alternative = f"The observed groups represent distinct patterns in the available {x} and {y} measurements."
    elif ptype == "anomaly":
        statement = f"The identified observations represent unusual {x}-{y} behavior relative to the main data distribution."
        alternative = f"The identified {x}-{y} observations are statistically or operationally unusual relative to typical observations."
    elif ptype == "nonlinear":
        statement = f"The relationship between {x} and {y} is nonlinear rather than adequately described by a simple linear relationship."
        alternative = f"A nonlinear association exists between {x} and {y}."
    else:  # feature_interaction
        statement = f"The relationship between {x} and {y} changes depending on another feature or condition."
        alternative = f"An interaction involving {x} and {y} contributes to the observed outcome pattern."

    null = f"There is no meaningful relationship between {x} and {y} in the analyzed population."

    return {
        "statement": statement,
        "null_hypothesis": null,
        "alternative_hypothesis": alternative,
        "independent_variable": x,
        "dependent_variable": y,
        "pattern_type": ptype,
    }


def generate_alternative_explanations(pattern: Dict[str, Any]) -> List[AlternativeExplanation]:
    x = _require_text(pattern, "variable_x")
    y = _require_text(pattern, "variable_y")
    possible = pattern.get("possible_confounders", [])
    if isinstance(possible, str):
        possible = [possible]
    if not isinstance(possible, list):
        possible = []

    explanations = [
        AlternativeExplanation(
            type="confounding",
            explanation=f"A third variable may influence both {x} and {y}, creating or changing the observed relationship.",
            possible_variables=[str(v) for v in possible],
            validation_method="Adjust for plausible confounders using stratification, regression, or another appropriate method."
        ),
        AlternativeExplanation(
            type="sampling_issue",
            explanation="The observed relationship may depend on which observations were included in the sample.",
            possible_variables=[],
            validation_method="Repeat the analysis on relevant subsets or resamples and compare the estimated relationship."
        ),
        AlternativeExplanation(
            type="temporal_effect",
            explanation="Time, seasonality, or another temporal process may affect both variables and create an apparent association.",
            possible_variables=["time", "season", "date"],
            validation_method="Analyze the relationship across time periods and include relevant temporal controls where appropriate."
        ),
        AlternativeExplanation(
            type="measurement_problem",
            explanation="Measurement error, sensor problems, inconsistent collection procedures, or recording artifacts may contribute to the pattern.",
            possible_variables=[],
            validation_method="Inspect data-quality indicators, measurement ranges, missingness, and collection procedures."
        ),
        AlternativeExplanation(
            type="spurious_correlation",
            explanation="The association may be statistical coincidence rather than a meaningful underlying relationship.",
            possible_variables=[],
            validation_method="Use an appropriate statistical test, effect size, confidence interval, and out-of-sample or resampling checks."
        ),
        AlternativeExplanation(
            type="data_quality_artifact",
            explanation="Duplicates, outliers, inconsistent units, missing values, or preprocessing choices may distort the observed relationship.",
            possible_variables=[],
            validation_method="Repeat the analysis after documented data-quality checks and sensitivity analyses."
        ),
    ]
    return explanations


def recommend_validation(pattern: Dict[str, Any]) -> List[str]:
    ptype = str(pattern.get("pattern_type", "")).lower()
    recommendations = [
        "Select a statistical test appropriate to the hypothesis and variable types.",
        "Report effect size and confidence intervals where applicable, not only statistical significance.",
        "Check relevant assumptions and inspect influential observations or outliers.",
        "Evaluate plausible confounders identified during alternative-explanation analysis.",
        "Use an appropriate ML model or nonlinear method when predictive or nonlinear validation is relevant.",
        "Compare results across reasonable samples, preprocessing choices, or model configurations to assess stability.",
    ]
    if ptype == "correlation":
        recommendations.insert(0, "Verify the observed association with an appropriate correlation test and inspect the scatter relationship.")
    elif ptype == "nonlinear":
        recommendations.insert(0, "Compare linear and nonlinear specifications and evaluate whether the nonlinear improvement is meaningful.")
    return recommendations


def analyze_pattern(pattern: Dict[str, Any]) -> Dict[str, Any]:
    """Generate the complete structured result expected by the Orchestrator."""
    validate_pattern(pattern)
    hypothesis = generate_hypothesis(pattern)
    explanations = generate_alternative_explanations(pattern)
    validation = recommend_validation(pattern)

    evidence_fields = ["correlation", "effect_size", "sample_size", "p_value"]
    available = sum(1 for key in evidence_fields if pattern.get(key) is not None)
    confidence = "high" if available >= 3 else "medium" if available >= 1 else "low"

    result = HypothesisResult(
        hypothesis=hypothesis,
        alternative_explanations=explanations,
        recommended_validation=validation,
        limitations=[
            "This module generates testable hypotheses; it does not establish causation.",
            "Alternative explanations depend on variables and metadata available in the dataset.",
            "Final evidence strength must be determined by statistical, ML/DL, robustness, and evidence-review stages."
        ],
        generation_confidence=confidence,
    )
    return result.to_dict()


if __name__ == "__main__":
    example = {
        "pattern_type": "correlation",
        "variable_x": "Humidity_percent",
        "variable_y": "Temperature_C",
        "relationship": "negative",
        "correlation": -0.661,
        "sample_size": 1000,
    }
    import json
    print(json.dumps(analyze_pattern(example), indent=2))
