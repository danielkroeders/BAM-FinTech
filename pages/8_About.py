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

if is_sme_profile(profile):
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


def _filter_rows(frame, query):
    if not query:
        return frame
    haystack = frame.astype(str).agg(" ".join, axis=1).str.lower()
    return frame[haystack.str.contains(query.lower(), regex=False)]


search_query = st.text_input(
    "Search glossary", placeholder="Try document, DSCR, forecast, KYB, grade..."
)
dimension_frame = _filter_rows(pd.DataFrame(DIMENSIONS), search_query)
derived_frame = _filter_rows(pd.DataFrame(DERIVED_DIMENSIONS), search_query)

dimension_tab, signal_tab, grade_tab = st.tabs(
    ["Scoring DIMENSIONS", "Derived Signals", "Grade Policy"]
)
with dimension_tab:
    st.dataframe(dimension_frame, width="stretch", hide_index=True)
with signal_tab:
    st.dataframe(derived_frame, width="stretch", hide_index=True)
with grade_tab:
    st.dataframe(pd.DataFrame(GRADE_ROWS), width="stretch", hide_index=True)

st.warning(
    "E and F recommendations should be treated as high-risk decision support requiring human compliance review."
)
