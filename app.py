import streamlit as st
import pandas as pd

from config import APP_NAME, APP_DESCRIPTION
from utils.data_loader import load_data, clean_data
from agents.orchestrator import OrchestratorAgent
from agents.llm_reasoning import LLMReasoningAgent


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🔬",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🔬 HypothesisX AI")

st.subheader(
    "Autonomous Data-Driven Hypothesis Discovery "
    "and Validation"
)

st.write(APP_DESCRIPTION)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("HypothesisX AI")

st.sidebar.info(
    """
Workflow:

Data
↓
Data Exploration
↓
Pattern Mining
↓
LLM Reasoning
↓
Hypothesis
↓
Alternative Explanations
↓
Statistical Testing
↓
ML Validation
↓
Robustness
↓
Evidence Review
↓
Next Investigation
"""
)

st.sidebar.success(
    "🤖 Generative AI reasoning is enabled."
)


# ============================================================
# FILE UPLOAD
# ============================================================

st.header("1️⃣ Upload Dataset")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx", "xls"]
)


# ============================================================
# LOAD DATA
# ============================================================

if uploaded_file is not None:

    try:

        df = load_data(uploaded_file)

        df = clean_data(df)

        st.success(
            f"Dataset loaded successfully: "
            f"{df.shape[0]} rows × {df.shape[1]} columns"
        )

        st.subheader("Dataset Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )


        # ====================================================
        # RUN ANALYSIS
        # ====================================================

        if st.button(
            "🚀 Start Hypothesis Discovery",
            type="primary"
        ):

            with st.spinner(
                "HypothesisX AI is analyzing your dataset..."
            ):

                orchestrator = OrchestratorAgent()

                results = orchestrator.run(df)

            st.session_state["results"] = results

            st.success(
                "Analysis completed successfully!"
            )

    except Exception as e:

        st.error(
            "An error occurred while processing the dataset."
        )

        st.exception(e)


# ============================================================
# RESULTS
# ============================================================

if "results" in st.session_state:

    results = st.session_state["results"]

    st.divider()

    st.header("📊 HypothesisX AI Results")


    # ========================================================
    # DATA EXPLORER
    # ========================================================

    st.subheader("2️⃣ Data Explorer")

    exploration = results["exploration"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Rows",
        exploration["rows"]
    )

    col2.metric(
        "Columns",
        exploration["columns"]
    )

    col3.metric(
        "Duplicates",
        exploration["duplicate_rows"]
    )

    col4.metric(
        "Numeric Variables",
        len(exploration["numeric_columns"])
    )


    st.write("### Variable Types")

    st.write(
        "Numeric:",
        exploration["numeric_columns"]
    )

    st.write(
        "Categorical:",
        exploration["categorical_columns"]
    )


    # ========================================================
    # MISSING VALUES
    # ========================================================

    if exploration["missing_values"]:

        st.write("### Missing Values")

        missing_df = pd.DataFrame(
            list(
                exploration["missing_values"].items()
            ),
            columns=[
                "Column",
                "Missing Values"
            ]
        )

        st.dataframe(
            missing_df,
            use_container_width=True
        )

    else:

        st.success(
            "No missing values detected."
        )


    # ========================================================
    # DESCRIPTIVE STATISTICS
    # ========================================================

    st.subheader(
        "Descriptive Statistics"
    )

    if not exploration["statistics"].empty:

        st.dataframe(
            exploration["statistics"],
            use_container_width=True
        )


    # ========================================================
    # PATTERN MINING
    # ========================================================

    st.subheader("3️⃣ Pattern Mining")

    patterns = results["patterns"]

    if patterns:

        pattern_df = pd.DataFrame(patterns)

        st.dataframe(
            pattern_df,
            use_container_width=True
        )

        st.write(
            "### Strongest Discovered Relationships"
        )

        for pattern in patterns[:5]:

            st.info(
                f"""
**{pattern['variable_1']} ↔ {pattern['variable_2']}**

Correlation: {pattern['correlation']}

P-value: {pattern['p_value']}
"""
            )

    else:

        st.warning(
            "No suitable numeric relationships found."
        )


    # ========================================================
    # LLM REASONING
    # ========================================================

    st.subheader(
        "4️⃣ 🤖 LLM Hypothesis Reasoning"
    )

    if patterns:

        try:

            llm_agent = LLMReasoningAgent()

            strongest_pattern = patterns[0]

            sample_size = exploration["rows"]

            with st.spinner(
                "🤖 LLM is interpreting the strongest discovered pattern..."
            ):

                llm_reasoning = (
                    llm_agent.generate_reasoning(
                        variable_1=strongest_pattern[
                            "variable_1"
                        ],
                        variable_2=strongest_pattern[
                            "variable_2"
                        ],
                        correlation=strongest_pattern[
                            "correlation"
                        ],
                        p_value=strongest_pattern[
                            "p_value"
                        ],
                        sample_size=sample_size
                    )
                )

            st.success(
                "LLM reasoning generated successfully!"
            )

            st.markdown(
                llm_reasoning
            )

            st.session_state[
                "llm_reasoning"
            ] = llm_reasoning

        except Exception as e:

            st.error(
                "LLM reasoning could not be completed."
            )

            st.exception(e)

    else:

        st.info(
            "LLM reasoning requires at least one discovered pattern."
        )


    # ========================================================
    # PROGRAMMATIC HYPOTHESES
    # ========================================================

    st.subheader(
        "5️⃣ Generated Hypotheses"
    )

    hypotheses = results["hypotheses"]

    if hypotheses:

        for item in hypotheses:

            st.markdown(
                f"### {item['id']}"
            )

            st.write(
                item["hypothesis"]
            )

            st.caption(
                f"Relationship: "
                f"{item['relationship']}"
            )

    else:

        st.warning(
            "No hypotheses could be generated."
        )


    # ========================================================
    # ALTERNATIVE EXPLANATIONS
    # ========================================================

    st.subheader(
        "6️⃣ Alternative Explanations"
    )

    alternatives = results["alternatives"]

    for item in alternatives:

        with st.expander(
            item["id"]
        ):

            st.write(
                item["hypothesis"]
            )

            for explanation in item[
                "alternative_explanations"
            ]:

                st.write(
                    "•",
                    explanation
                )


    # ========================================================
    # STATISTICAL TESTING
    # ========================================================

    st.subheader(
        "7️⃣ Statistical Validation"
    )

    statistical_results = results[
        "statistical_results"
    ]

    if statistical_results:

        stats_df = pd.DataFrame(
            statistical_results
        )

        st.dataframe(
            stats_df,
            use_container_width=True
        )


    # ========================================================
    # ML VALIDATION
    # ========================================================

    st.subheader(
        "8️⃣ ML Validation"
    )

    ml_results = results[
        "ml_results"
    ]

    st.write(
        "Status:",
        ml_results.get("status")
    )

    if ml_results.get("message"):

        st.info(
            ml_results["message"]
        )

    for model in ml_results.get(
        "models",
        []
    ):

        if "error" in model:

            st.error(
                f"{model['model']}: "
                f"{model['error']}"
            )

        else:

            st.write(
                f"### {model['model']}"
            )

            c1, c2 = st.columns(2)

            c1.metric(
                "R²",
                model["r2"]
            )

            c2.metric(
                "RMSE",
                model["rmse"]
            )

            st.write(
                "Feature Importance"
            )

            st.json(
                model["feature_importance"]
            )


    # ========================================================
    # ROBUSTNESS
    # ========================================================

    st.subheader(
        "9️⃣ Robustness Testing"
    )

    robustness = results[
        "robustness"
    ]

    if robustness:

        robustness_df = pd.DataFrame(
            robustness
        )

        st.dataframe(
            robustness_df,
            use_container_width=True
        )

    else:

        st.info(
            "Not enough data for robustness analysis."
        )


    # ========================================================
    # EVIDENCE REVIEW
    # ========================================================

    st.subheader(
        "🔟 Evidence Review"
    )

    evidence = results[
        "evidence"
    ]

    if evidence:

        for item in evidence:

            if item[
                "evidence_level"
            ] == "Strong Evidence":

                st.success(
                    f"{item['id']} — "
                    f"{item['evidence_level']}"
                )

            elif item[
                "evidence_level"
            ] == "Moderate Evidence":

                st.warning(
                    f"{item['id']} — "
                    f"{item['evidence_level']}"
                )

            else:

                st.info(
                    f"{item['id']} — "
                    f"{item['evidence_level']}"
                )

            st.write(
                item["hypothesis"]
            )

            st.write(
                f"Evidence Score: "
                f"{item['evidence_score']}"
            )

            st.caption(
                item["interpretation"]
            )


    # ========================================================
    # NEXT INVESTIGATION
    # ========================================================

    st.subheader(
        "1️⃣1️⃣ Recommended Next Investigation"
    )

    st.success(
        results["next_investigation"]
    )


    # ========================================================
    # DOWNLOAD REPORT
    # ========================================================

    st.subheader(
        "📥 Export Results"
    )

    report_lines = []

    report_lines.append(
        "HYPOTHESISX AI DISCOVERY REPORT"
    )

    report_lines.append(
        "=" * 50
    )

    report_lines.append(
        f"Rows: {exploration['rows']}"
    )

    report_lines.append(
        f"Columns: {exploration['columns']}"
    )

    report_lines.append("")

    report_lines.append(
        "DISCOVERED PATTERNS"
    )

    for pattern in patterns:

        report_lines.append(
            f"- {pattern['variable_1']} vs "
            f"{pattern['variable_2']}: "
            f"correlation="
            f"{pattern['correlation']}, "
            f"p={pattern['p_value']}"
        )

    report_lines.append("")

    report_lines.append(
        "PROGRAMMATIC HYPOTHESES"
    )

    for hypothesis in hypotheses:

        report_lines.append(
            f"- {hypothesis['id']}: "
            f"{hypothesis['hypothesis']}"
        )

    report_lines.append("")

    report_lines.append(
        "LLM REASONING"
    )

    report_lines.append(
        st.session_state.get(
            "llm_reasoning",
            "LLM reasoning not available."
        )
    )

    report_lines.append("")

    report_lines.append(
        "NEXT INVESTIGATION"
    )

    report_lines.append(
        results["next_investigation"]
    )

    report = "\n".join(
        report_lines
    )

    st.download_button(
        label="Download Discovery Report",
        data=report,
        file_name="hypothesisx_report.txt",
        mime="text/plain"
    )
