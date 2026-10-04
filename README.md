# HypothesisX AI — Hypothesis & Alternative Explanation Agent

Standalone contribution for the **HypothesisX AI** multi-agent research workflow.

## What this module does

The agent receives an interesting pattern from the Pattern Mining stage and produces:

- A clear, testable hypothesis
- Null and alternative hypotheses
- Independent and dependent variables
- Alternative explanations
- Possible confounders
- Recommended validation methods
- Limitations
- A generation-confidence level based on the available pattern evidence

**Important:** This module does not establish causation and does not replace the Statistical + ML/DL Validation or Robustness/Evidence stages.

## Project structure

```text
hypothesisx-ai-hypothesis-agent/
├── agents/
│   ├── __init__.py
│   └── hypothesis_agent.py
├── models/
│   ├── __init__.py
│   └── hypothesis_models.py
├── tests/
│   ├── __init__.py
│   └── test_hypothesis_agent.py
├── app.py
├── example_output.json
├── requirements.txt
├── .gitignore
└── README.md
```

## 1. Install dependencies

Use Python 3.10+.

```bash
pip install -r requirements.txt
```

## 2. Run automated tests

```bash
python -m unittest discover -s tests -v
```

## 3. Run the Streamlit demo

```bash
streamlit run app.py
```

The app lets you enter a pattern and displays the generated hypothesis, alternative explanations, validation recommendations, and limitations.

## 4. Orchestrator integration

The main function is:

```python
from agents.hypothesis_agent import analyze_pattern

result = analyze_pattern(pattern_from_pattern_mining)
```

Expected input example:

```python
pattern = {
    "pattern_type": "correlation",
    "variable_x": "Humidity_percent",
    "variable_y": "Temperature_C",
    "relationship": "negative",
    "correlation": -0.661,
    "sample_size": 1000
}
```

The result is a normal Python dictionary and can be serialized to JSON or passed to the next agent.

## Supported pattern types

`correlation`, `trend`, `association`, `cluster`, `anomaly`, `nonlinear`, `feature_interaction`

## Team workflow position

```text
Pattern Mining
      ↓
Interesting Pattern
      ↓
Hypothesis Generator  ← this module
      ↓
Alternative Explanation Agent  ← this module
      ↓
Statistical + ML/DL Validation
      ↓
Robustness + Evidence
```

## Handover note

This repository is designed to be handed to the HypothesisX AI team leader. The agent logic is independent of Streamlit so it can later be imported by the team's Orchestrator without rewriting the core module.
