import os

from dotenv import load_dotenv
from openai import OpenAI


class LLMReasoningAgent:
    """
    LLM-based reasoning layer for HypothesisX AI.

    This agent does NOT perform statistical calculations.
    It interprets the results produced by the Python analysis agents.
    """

    def __init__(self):
        # Load variables from .env
        load_dotenv()

        api_key = os.getenv("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")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY was not found. "
                "Please check your .env file."
            )

        self.client = OpenAI(api_key=api_key)

        # Low-cost model suitable for this reasoning task.
        self.model = "gpt-6-luna"

    def generate_reasoning(
        self,
        variable_1,
        variable_2,
        correlation,
        p_value,
        sample_size
    ):
        """
        Interpret one discovered statistical relationship
        and generate a researchable hypothesis.
        """

        prompt = f"""
You are the Generative AI reasoning agent of HypothesisX AI.

Your job is to interpret a statistical relationship discovered
by the programmatic Pattern Mining and Statistical Testing agents.

IMPORTANT RULES:
- Do not invent statistical values.
- Do not change the provided numbers.
- Do not claim that correlation proves causation.
- Clearly distinguish observation from hypothesis.
- Suggest plausible alternative explanations.
- Keep the output understandable for a student/researcher.

Observed relationship:

Variable 1: {variable_1}
Variable 2: {variable_2}
Pearson correlation: {correlation}
P-value: {p_value}
Sample size: {sample_size}

Provide the following sections:

1. Research Hypothesis
2. Interpretation of the Observed Relationship
3. Possible Confounding Variables
4. Alternative Explanations
5. Recommended Next Investigation
6. Important Limitation

The hypothesis must be testable.
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        return response.output_text 
