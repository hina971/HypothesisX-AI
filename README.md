# HypothesisX AI - Robustness + Evidence + UI agent

Upload an Excel file. The agent searches for correlations, associations, trends, clusters, anomalies,
non-linear relationships and feature interactions, turns promising patterns into hypotheses, tests them
(statistics + cross-validated ML), stress-tests them (robustness) and writes a cautious evidence report.
Findings are evidence-supported hypotheses, never proven causes.

## Quick start
    pip install -r requirements.txt
    python tests/test_core.py                       # checks the logic
    python run_pipeline.py data/simulated_weather.xlsx   # no UI
    streamlit run app.py                            # UI

## Layout
- `agents/hypothesisx_agent.py` the single agent (discover -> hypothesise -> test -> robustness -> evidence)
- `analysis/` discovery, statistical tests, ML validation, robustness tests, preprocessing
- `agents/evidence_agent.py` rule-based evidence assessment (no arbitrary scores)
- `ui/` Streamlit pages, `reports/` Markdown/HTML report export
- `crew_narrator.py` optional CrewAI plain-language narrator (needs an LLM key)
