import pandas as pd
import streamlit as st

from src.core.runtime import bootstrap_state
from src.ui.components import get_profile, is_sme_profile, render_sidebar, safe_page_link
from src.utils.acronym_guide import acronym_rows, metric_rows


st.set_page_config(page_title="Acronym Guide", layout="wide")
bootstrap_state()
render_sidebar()

profile = get_profile()
sme_mode = is_sme_profile(profile)


def _filter_rows(rows, query):
    query = str(query or "").strip().lower()
    if not query:
        return rows
    filtered = []
    for row in rows:
        haystack = " ".join(str(value) for value in row.values()).lower()
        if query in haystack:
            filtered.append(row)
    return filtered


st.title("Acronym & Metric Guide")
if sme_mode:
    st.caption(
        "Applicant-facing glossary for company portal terms, document evidence, simulated connections, and published-rating language."
    )
else:
    st.caption(
        "Analyst glossary for Personal Workspace, evidence review, scoring, monitoring, and model-governance terms."
    )

st.info(
    "Tip: the app uses **DSCR** for Debt Service Coverage Ratio. If you see **DCSR** in rough notes, read it as DSCR.",
    icon=":material/menu_book:",
)

search = st.text_input(
    "Search acronyms and metrics",
    placeholder="Try DSCR, FCF, PSD2, KYB, document completeness...",
)

acronym_tab, metric_tab = st.tabs(["Acronyms", "How to read metrics"])

with acronym_tab:
    rows = _filter_rows(acronym_rows(sme_mode), search)
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.warning("No acronym matches found. Try a shorter search term.")

with metric_tab:
    rows = _filter_rows(metric_rows(sme_mode), search)
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.warning("No metric matches found. Try a shorter search term.")

st.subheader("Where to use this")
if sme_mode:
    st.write(
        "Use this guide while preparing company data, uploading documents, reading a published rating, or planning future improvements."
    )
    link_cols = st.columns(3)
    with link_cols[0]:
        safe_page_link("pages/6_SME_Credit_Health.py", "Open Company Portal", ":material/domain:")
    with link_cols[1]:
        safe_page_link("pages/9_Support.py", "Connect with a Consultant", ":material/support_agent:")
    with link_cols[2]:
        safe_page_link("pages/10_Tutorials.py", "Open Tutorials", ":material/school:")
else:
    st.write(
        "Use this guide while interpreting score output, evidence readiness, document validation, risk drivers, and governance rows."
    )
    link_cols = st.columns(3)
    with link_cols[0]:
        safe_page_link("pages/1_Personal_Workspace.py", "Open Personal Workspace", ":material/person_search:")
    with link_cols[1]:
        safe_page_link("pages/9_Support.py", "Open Support", ":material/support_agent:")
    with link_cols[2]:
        safe_page_link("pages/8_About.py", "Open About", ":material/info:")
