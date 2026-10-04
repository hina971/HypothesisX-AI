import os
from dotenv import load_dotenv
from openai import OpenAI


class LLMReasoningAgent:
    """
    LLM-based reasoning layer for HypothesisX AI.

    This agent takes patterns/findings from the analysis
    and generates:
    - Testable hypotheses
    - Alternative explanations
    - Possible confounding factors
    - Interpretation of findings
    """

    def __init__(self):
        # Load environment variables from .env
        load_dotenv()

        # Get OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY was not found. "
                "Please add OPENAI_API_KEY to your Streamlit Secrets "
                "or .env file."
            )

        self.client = OpenAI(api_key=api_key)

        # Model
        self.model = os.getenv(
            "OPENAI_MODEL",
            "gpt-4o-mini"
        )

    def generate_reasoning(self, pattern):
        """
        Generate hypotheses and alternative explanations
        from a discovered pattern.
        """

        prompt = f"""
You are the Hypothesis Generation and Alternative Explanation Agent
for HypothesisX AI.

Analyze the following discovered pattern:

{pattern}

Provide:

1. Main Hypothesis
- Write one clear, testable hypothesis.

2. Null Hypothesis
- Write the corresponding null hypothesis.

3. Alternative Explanations
- Give 2-4 possible alternative explanations.

4. Confounding Factors
- Identify variables that could influence the observed relationship.

5. Interpretation
- Explain what the pattern could mean in simple language.

Important:
Do not claim that the hypothesis is proven.
Statistical validation will be performed separately.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI research reasoning assistant. "
                        "Generate scientifically careful, testable hypotheses "
                        "and alternative explanations."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content

    def run(self, pattern):
        """
        Compatibility method for the main application.
        """
        return self.generate_reasoning(pattern)
