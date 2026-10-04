"""Streamlit demo for the Hypothesis + Alternative Explanation Agent."""

import json
import streamlit as st

from agents.hypothesis_agent import SUPPORTED_PATTERN_TYPES, analyze_pattern


st.set_page_config(
    page_title="HypothesisX AI - Hypothesis Agent",
    page_icon="🔬",
    layout="wide",
)

st.title("HypothesisX AI")
st.subheader("Hypothesis & Alternative Explanation Agent")
st.caption("Standalone demo for the Week 6 multi-agent research workflow")

st.info(
    "This agent converts an interesting pattern into a testable hypothesis and "
    "lists alternative explanations. It does not establish causation."
)

with st.sidebar:
    st.header("Pattern Input")
    pattern_type = st.selectbox("Pattern type", sorted(SUPPORTED_PATTERN_TYPES), index=0)
    variable_x = st.text_input("Variable X", "Humidity_percent")
    variable_y = st.text_input("Variable Y", "Temperature_C")
    relationship = st.selectbox(
        "Relationship",
        ["negative", "positive", "inverse", "direct", "observed"],
        index=0,
    )
    correlation = st.number_input("Correlation / effect value", value=-0.661, format="%.4f")
    sample_size = st.number_input("Sample size", min_value=1, value=1000, step=1)
    confounders = st.text_input(
        "Possible confounders (optional)",
        "season, time",
    )
    analyze = st.button("Analyze Pattern", type="primary", use_container_width=True)

pattern = {
    "pattern_type": pattern_type,
    "variable_x": variable_x,
    "variable_y": variable_y,
    "relationship": relationship,
    "correlation": correlation,
    "sample_size": sample_size,
    "possible_confounders": [x.strip() for x in confounders.split(",") if x.strip()],
}

if analyze:
    try:
        result = analyze_pattern(pattern)
        hypothesis = result["hypothesis"]

        st.success("Pattern analyzed successfully.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Generated Hypothesis")
            st.write(hypothesis["statement"])
            st.markdown("**Null hypothesis**")
            st.write(hypothesis["null_hypothesis"])
            st.markdown("**Alternative hypothesis**")
            st.write(hypothesis["alternative_hypothesis"])

        with col2:
            st.markdown("### Generation Information")
            st.write(f"**Confidence:** {result['generation_confidence'].title()}")
            st.write(f"**Independent variable:** {hypothesis['independent_variable']}")
            st.write(f"**Dependent variable:** {hypothesis['dependent_variable']}")
            st.write(f"**Pattern type:** {hypothesis['pattern_type']}")

        st.markdown("### Alternative Explanations")
        for i, item in enumerate(result["alternative_explanations"], start=1):
            with st.expander(f"{i}. {item['type'].replace('_', ' ').title()}"):
                st.write(item["explanation"])
                if item["possible_variables"]:
                    st.write("**Possible variables:** " + ", ".join(item["possible_variables"]))
                st.write("**Validation method:** " + item["validation_method"])

        st.markdown("### Recommended Validation")
        for item in result["recommended_validation"]:
            st.write("- " + item)

        st.markdown("### Limitations")
        for item in result["limitations"]:
            st.write("- " + item)

        st.download_button(
            "Download JSON Result",
            data=json.dumps(result, indent=2),
            file_name="hypothesis_result.json",
            mime="application/json",
        )

    except (TypeError, ValueError) as exc:
        st.error(f"Input error: {exc}")
else:
    st.markdown("### Example")
    st.write(
        "The default example represents a negative correlation between humidity and temperature. "
        "Click **Analyze Pattern** in the sidebar to run the agent."
    )
