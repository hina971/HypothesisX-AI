```python
import os
from dotenv import load_dotenv
from openai import OpenAI


class LLMReasoningAgent:
    """
    LLM-based reasoning layer for HypothesisX AI.

    Generates:
    - Main hypothesis
    - Null hypothesis
    - Alternative explanations
    - Confounding factors
    - Interpretation
    """

    def __init__(self):
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY was not found. "
                "Please add it to Streamlit Secrets or .env file."
            )

        self.client = OpenAI(api_key=api_key)

        self.model = os.getenv(
            "OPENAI_MODEL",
            "gpt-4o-mini"
        )

    def generate_reasoning(
        self,
        variable_1=None,
        variable_2=None,
        relationship=None,
        pattern=None,
        strength=None,
        p_value=None,
        correlation=None,
        sample_size=None,
        **kwargs
    ):
        """
        Generate hypotheses and alternative explanations.

        Accepts the named arguments sent by app.py.
        """

        # If the application sends a complete pattern instead,
        # use that as the main information.
        if pattern is not None:
            pattern_text = str(pattern)
        else:
            pattern_text = f"""
Variable 1: {variable_1}
Variable 2: {variable_2}
Relationship: {relationship}
Pattern strength: {strength}
P-value: {p_value}
Correlation: {correlation}
Sample size: {sample_size}
"""

        prompt = f"""
You are the Hypothesis Generation and Alternative Explanation
Agent for HypothesisX AI.

Analyze the following discovered pattern:

{pattern_text}

Your task is to generate scientifically careful reasoning.

Provide the following sections:

1. Main Hypothesis
Write one clear and testable hypothesis.

2. Null Hypothesis
Write the corresponding null hypothesis.

3. Alternative Explanations
Provide 2-4 possible explanations for the observed pattern.

4. Confounding Factors
Identify variables that could influence the observed relationship.

5. Interpretation
Explain what the observed pattern could mean in simple language.

6. Recommended Next Step
Suggest what statistical or experimental validation should be
performed next.

IMPORTANT:
- Do not claim that the hypothesis is proven.
- Correlation does not automatically imply causation.
- Statistical validation is performed separately.
- Clearly distinguish observations from hypotheses.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a scientific reasoning assistant "
                        "for hypothesis generation. Be careful, "
                        "objective, and avoid unsupported causal claims."
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
        return self.generate_reasoning(pattern=pattern)
```
