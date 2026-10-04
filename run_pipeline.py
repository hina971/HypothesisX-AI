"""Command-line run (no UI): python run_pipeline.py data/simulated_weather.xlsx"""
import sys, json
from agents.hypothesisx_agent import HypothesisXAgent, load_excel
from reports.evidence_report import to_markdown
from utils.helpers import to_json

path = sys.argv[1] if len(sys.argv) > 1 else "data/simulated_weather.xlsx"
out = HypothesisXAgent().run_all(load_excel(path))
print(f"Rows: {out['quality']['n_rows']}  date column: {out['date_col']}")
print("Findings by type:", out["discovery"]["counts"])
if out["discovery"]["errors"]:
    print("Detector errors:", out["discovery"]["errors"])
for r in out["records"]:
    print(f"\n{r.id}: {r.statement}\n   -> {r.evidence_report['final_assessment']['label']}")
with open("evidence_reports.json", "w") as fh:
    fh.write(to_json([r.to_dict() for r in out["records"]]))
if out["records"]:
    open("example_report.md", "w").write(to_markdown(out["records"][0].evidence_report))
print("\nSaved evidence_reports.json and example_report.md")
