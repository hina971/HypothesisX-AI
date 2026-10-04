"""OPTIONAL: CrewAI layer that explains evidence reports in plain language.

The statistics never depend on an LLM; CrewAI only writes the narrative on top of the computed numbers.
Needs an LLM key (e.g. OPENAI_API_KEY) and:  pip install crewai
Usage:  from crew_narrator import narrate; print(narrate(record.evidence_report))
"""
import json
import os

from utils.helpers import to_json


def narrate(evidence_report: dict, model: str | None = None) -> str:
    from crewai import Agent, Crew, Task  # imported lazily so the core app works without CrewAI

    analyst = Agent(
        role="Careful research analyst",
        goal="Explain statistical evidence to a non-expert without overstating it",
        backstory=("You interpret evidence reports. You only use numbers present in the report, never claim "
                   "causation, and always mention the main limitations and the recommended next step."),
        llm=model or os.getenv("CREWAI_MODEL", "gpt-4o-mini"),
        verbose=False,
    )
    task = Task(
        description="Write a 150-word plain-language summary of this evidence report:\n" + to_json(evidence_report),
        expected_output="One short paragraph, then a one-line 'Next step:'.",
        agent=analyst,
    )
    return str(Crew(agents=[analyst], tasks=[task]).kickoff())
