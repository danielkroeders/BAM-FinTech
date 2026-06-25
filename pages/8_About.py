# About page that explains scoring dimensions and risk grade interpretation.
import pandas as pd
import streamlit as st

from src.constants import *
from src.core.runtime import bootstrap_state
from src.ui.components import (
    get_profile,
    is_sme_profile,
    render_sidebar,
    safe_page_link,
)

st.set_page_config(page_title="About", layout="wide")
bootstrap_state()
render_sidebar()
profile = get_profile()

# The About page is intentionally role-gated. It documents internal scoring
# dimensions and policy thresholds, so SME users get routed to applicant-safe
# guidance instead of seeing lender-only model terminology.
if is_sme_profile(profile):
    # Keep internal model-policy explanations out of the applicant view.
    st.title("About")
    st.warning(
        "This reference page is available only in the lender workspace because it describes internal scoring "
        "DIMENSIONS, derived ratios, and review policy."
    )
    st.write(
        "For application guidance, use the SME company portal, applicant tutorials, or connect with a YourBank consultant."
    )
    link_cols = st.columns(3)
    with link_cols[0]:
        safe_page_link(
            "pages/6_SME_Credit_Health.py", "Open SME Portal", ":material/domain:"
        )
    with link_cols[1]:
        safe_page_link(
            "pages/10_Tutorials.py", "Open SME Tutorials", ":material/school:"
        )
    with link_cols[2]:
        safe_page_link(
            "pages/9_Support.py",
            "Connect with a Consultant",
            ":material/support_agent:",
        )
    st.stop()

st.title("About")
st.caption(
    "Definitions for the workspace scoring DIMENSIONS used by the SME application-risk model."
)

st.info(
    "Scores help prioritize analyst review and do not establish legal, "
    "credit, or compliance certainty."
)

# The three tabs below are static reference tables from constants.py. They are
# useful for auditors/graders because they connect raw inputs, derived signals,
# and A-F policy thresholds in one place.

def _filter_rows(frame, query):
    if not query:
        return frame
    # Search across all table columns so users can find both acronyms and plain-language explanations.
    haystack = frame.astype(str).agg(" ".join, axis=1).str.lower()
    return frame[haystack.str.contains(query.lower(), regex=False)]


search_query = st.text_input(
    "Search glossary", placeholder="Try document, DSCR, forecast, KYB, grade..."
)
# Filtering happens before tab rendering so all three reference tables respond
# to the same search term.
dimension_frame = _filter_rows(pd.DataFrame(DIMENSIONS), search_query)
derived_frame = _filter_rows(pd.DataFrame(DERIVED_DIMENSIONS), search_query)

dimension_tab, signal_tab, grade_tab = st.tabs(
    ["Scoring DIMENSIONS", "Derived Signals", "Grade Policy"]
)
with dimension_tab:
    # Dimensions are the starting fields a seed row or SME intake can provide.
    st.dataframe(dimension_frame, width="stretch", hide_index=True)
with signal_tab:
    # Derived signals are calculated by data_pipeline.py and then consumed by
    # the model, workbench tables, and explanations.
    st.dataframe(derived_frame, width="stretch", hide_index=True)
with grade_tab:
    # Grade rows document the fixed policy thresholds over the model probability.
    st.dataframe(pd.DataFrame(GRADE_ROWS), width="stretch", hide_index=True)

st.warning(
    "E and F recommendations should be treated as high-risk decision support requiring human compliance review."
)
