"""Render an evidence report (dict from EvidenceAgent) as Markdown or standalone HTML."""
from __future__ import annotations

import html
from typing import Dict, List, Tuple

SECTIONS: List[Tuple[str, str]] = [
    ("statistical_evidence", "Statistical evidence"), ("ml_evidence", "ML / DL evidence"),
    ("robustness_evidence", "Robustness evidence"), ("alternative_explanations", "Alternative explanations"),
    ("data_limitations", "Data limitations and assumptions"), ("uncertainty", "Uncertainty"),
]


def _blocks(rep: Dict):
    h = rep["hypothesis"]
    yield "title", f"Evidence report: {h['id']}"
    yield "h2", "Hypothesis"
    yield "p", h["statement"]
    if h.get("why_discovered"):
        yield "p", "Why it was discovered: " + h["why_discovered"]
    for key, title in SECTIONS:
        yield "h2", title
        yield "ul", rep[key]["summary"]
    fa = rep["final_assessment"]
    yield "h2", "Final evidence assessment"
    yield "p", fa["label"]
    yield "ul", fa["reasons"]
    yield "p", rep["causality_statement"]
    yield "h2", "Recommended next investigation"
    yield "ul", rep["recommended_next_investigation"]


def to_markdown(rep: Dict) -> str:
    out = []
    for kind, val in _blocks(rep):
        out.append({"title": f"# {val}", "h2": f"\n## {val}", "p": val}[kind] if kind != "ul"
                   else "\n".join(f"- {v}" for v in val))
    return "\n\n".join(out)


def to_html(rep: Dict) -> str:
    body = []
    for kind, val in _blocks(rep):
        if kind == "ul":
            body.append("<ul>" + "".join(f"<li>{html.escape(str(v))}</li>" for v in val) + "</ul>")
        else:
            tag = {"title": "h1", "h2": "h2", "p": "p"}[kind]
            body.append(f"<{tag}>{html.escape(val)}</{tag}>")
    return ("<!doctype html><html><head><meta charset='utf-8'><title>Evidence report</title>"
            "<style>body{font-family:sans-serif;max-width:820px;margin:2rem auto;line-height:1.5}"
            "h2{border-bottom:1px solid #ddd;padding-bottom:4px}</style></head><body>"
            + "".join(body) + "</body></html>")
