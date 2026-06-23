import base64
from html import escape
from pathlib import Path
from string import Template
from time import sleep

import streamlit as st

from src.utils.demo_persistence import clear_demo_state, persist_demo_state


PROFILE = {
    "account_type": "lender",
    "bank": "Rabobank",
    "id": "01",
    "user_id": "USR-001",
    "name": "Alice Cooper",
    "display_name": "Ms. Cooper",
    "email": "alice.cooper@rabobank.nl",
    "role": "Credit Analyst",
    "team": "SME Credit Operations",
    "user_type": "Team Member",
    "permission": "Credit review and manual decision approval",
    "team_manager": "Ravi Meijer",
    "slack_connected": True,
    "teams_connected": False,
    "integrations": {
        "slack": True,
        "teams": False,
        "gmail": True,
        "outlook": True,
        "google_drive": False,
        "onedrive": True,
        "sharepoint": True,
        "zoom": False,
    },
    "preferred_channel": "Slack",
    "preferred_email_app": "Outlook",
    "review_alerts": True,
    "daily_digest": True,
    "dark_mode": False,
}

SME_PROFILE = {
    "account_type": "sme",
    "bank": "A2M Logistics",
    "id": "SME-001",
    "user_id": "SME-001",
    "name": "A2M Logistics",
    "display_name": "A2M Logistics",
    "email": "finance@a2mlogistics.eu",
    "role": "Finance Director",
    "team": "Company Finance",
    "user_type": "SME Applicant",
    "permission": "Manage company application",
    "team_manager": "Company administrator",
    "slack_connected": False,
    "teams_connected": False,
    "integrations": {
        "slack": False,
        "teams": False,
        "gmail": True,
        "outlook": False,
        "google_drive": True,
        "onedrive": False,
        "sharepoint": False,
        "zoom": False,
    },
    "preferred_channel": "Email",
    "preferred_email_app": "Gmail",
    "review_alerts": True,
    "daily_digest": False,
    "dark_mode": False,
}


NAV_SECTIONS = [
    (
        "Credit Work",
        [
            ("Home", "Home.py", ":material/home:"),
            ("Personal Workspace", "pages/1_Personal_Workspace.py", ":material/person_search:"),
            ("SME Credit Health", "pages/6_SME_Credit_Health.py", ":material/monitor_heart:"),
            ("LLM Integration", "pages/5_LLM_Integration.py", ":material/psychology:"),
        ],
    ),
    (
        "Operations & Risk",
        [
            ("Operations Desk", "pages/2_Operations_Desk.py", ":material/view_list:"),
            ("Risk Dashboard", "pages/3_Risk_Dashboard.py", ":material/monitoring:"),
            ("Model Insights", "pages/4_Model_Insights.py", ":material/analytics:"),
        ],
    ),
    (
        "Account & Help",
        [
            ("Profile & Settings", "pages/7_Profile_Settings.py", ":material/manage_accounts:"),
            ("Tutorials", "pages/10_Tutorials.py", ":material/school:"),
            ("Support", "pages/9_Support.py", ":material/support_agent:"),
            ("About", "pages/8_About.py", ":material/info:"),
        ],
    ),
]

SME_NAV_SECTIONS = [
    (
        "Company Portal",
        [
            ("Company Setup & Credit Health", "pages/6_SME_Credit_Health.py", ":material/domain:"),
        ],
    ),
    (
        "Help",
        [
            ("Tutorials", "pages/10_Tutorials.py", ":material/school:"),
            ("Support", "pages/9_Support.py", ":material/support_agent:"),
            ("About", "pages/8_About.py", ":material/info:"),
        ],
    ),
]

DARK_MODE_STATE_KEY = "dark_mode_preference"
DARK_MODE_WIDGET_KEY = "dark_mode_toggle"
DEMO_PROMPT_REMEMBERED_KEY = "demo_prompt_remembered"
DEMO_PROMPT_CHOICE_KEY = "demo_prompt_choice"
DEMO_PROMPT_HANDLED_KEY = "demo_prompt_handled_this_session"
DEMO_PROMPT_CHECKBOX_KEY = "demo_prompt_remember_checkbox"

# Enable this after the YouTube demo has been published.
# DEMO_VIDEO_URL = "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"


def _set_dark_mode_preference(value=False, profile=None):
    dark_mode = bool(value)
    st.session_state[DARK_MODE_STATE_KEY] = dark_mode
    st.session_state.dark_mode = dark_mode

    target_profile = profile
    if target_profile is None and "user_profile" in st.session_state:
        target_profile = {**st.session_state.user_profile}
        st.session_state.user_profile = target_profile
    if target_profile is not None:
        target_profile["dark_mode"] = dark_mode
    return dark_mode


def _is_dark_mode():
    if DARK_MODE_STATE_KEY not in st.session_state:
        saved_profile = st.session_state.get("user_profile", {})
        fallback = st.session_state.get("dark_mode", saved_profile.get("dark_mode", PROFILE["dark_mode"]))
        _set_dark_mode_preference(fallback)
    else:
        st.session_state.dark_mode = bool(st.session_state[DARK_MODE_STATE_KEY])
    return bool(st.session_state[DARK_MODE_STATE_KEY])


def _sync_dark_mode_from_widget():
    _set_dark_mode_preference(st.session_state.get(DARK_MODE_WIDGET_KEY, _is_dark_mode()))


def get_profile():
    saved_profile = st.session_state.get("user_profile", {})
    defaults = SME_PROFILE if saved_profile.get("account_type") == "sme" else PROFILE
    profile = {**defaults, **saved_profile}
    if profile.get("user_type") == "Internal analyst":
        profile["user_type"] = "Team Member"
    profile["dark_mode"] = _is_dark_mode()
    saved_integrations = profile.get("integrations", {})
    profile["integrations"] = {
        key: bool(saved_integrations.get(key, default))
        for key, default in PROFILE["integrations"].items()
    }
    profile["integrations"]["slack"] = bool(profile.get("slack_connected", profile["integrations"]["slack"]))
    profile["integrations"]["teams"] = bool(profile.get("teams_connected", profile["integrations"]["teams"]))
    profile["slack_connected"] = profile["integrations"]["slack"]
    profile["teams_connected"] = profile["integrations"]["teams"]
    profile["user_id"] = profile.get("user_id") or profile.get("id", PROFILE["id"])
    profile["id"] = profile.get("id") or profile["user_id"]
    st.session_state.user_profile = profile
    return profile


def save_profile(profile):
    defaults = SME_PROFILE if profile.get("account_type") == "sme" else PROFILE
    updated_profile = {**defaults, **profile}
    if updated_profile.get("user_type") == "Internal analyst":
        updated_profile["user_type"] = "Team Member"
    dark_mode = updated_profile["dark_mode"] if "dark_mode" in updated_profile else _is_dark_mode()
    updated_profile["dark_mode"] = _set_dark_mode_preference(dark_mode)
    saved_integrations = updated_profile.get("integrations", {})
    updated_profile["integrations"] = {
        key: bool(saved_integrations.get(key, default))
        for key, default in PROFILE["integrations"].items()
    }
    updated_profile["slack_connected"] = updated_profile["integrations"]["slack"]
    updated_profile["teams_connected"] = updated_profile["integrations"]["teams"]
    updated_profile["user_id"] = updated_profile.get("user_id") or updated_profile.get("id", PROFILE["id"])
    updated_profile["id"] = updated_profile.get("id") or updated_profile["user_id"]
    st.session_state.user_profile = updated_profile
    persist_demo_state()
    return updated_profile


def is_sme_profile(profile=None):
    active_profile = profile or get_profile()
    return active_profile.get("account_type") == "sme" or active_profile.get("user_type") == "SME Applicant"


def _page_link(page, label, icon=None):
    page_link = getattr(st, "page_link", None)
    if not page_link:
        st.caption(label)
        return
    try:
        page_link(page, label=label, icon=icon)
    except TypeError:
        try:
            page_link(page, label=label)
        except KeyError:
            st.caption(label)
    except KeyError:
        st.caption(label)


def safe_page_link(page, label, icon=None):
    _page_link(page, label, icon)


def _clear_scored_workspace_case():
    st.session_state.last_application = None
    st.session_state.last_prediction = None
    st.session_state.last_explanation = None
    st.session_state.last_review = None
    st.session_state.last_email_link = None
    st.session_state.show_review_dialog = False


def open_application_in_workspace(application, source="Workspace"):
    st.session_state.active_queue_application = dict(application)
    st.session_state.active_intake_source = source
    st.session_state.loan_example_scenario = "Custom application"
    _clear_scored_workspace_case()
    persist_demo_state()

    switch_page = getattr(st, "switch_page", None)
    if switch_page:
        switch_page("pages/1_Personal_Workspace.py")
    st.success("Case loaded into Personal Workspace.")
    _page_link("pages/1_Personal_Workspace.py", "Open Personal Workspace", ":material/person_search:")


def _rerun():
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun:
        rerun()


@st.cache_data(show_spinner=False)
def _asset_data_uri(relative_path):
    path = Path(__file__).resolve().parent.parent / relative_path
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _render_global_theme():
    dark = _is_dark_mode()
    tokens = {
        "bg": "#0b1220" if dark else "#f8fafc",
        "bg_soft": "#111827" if dark else "#ecfeff",
        "surface": "#111827" if dark else "#ffffff",
        "surface_soft": "#1e293b" if dark else "#f1f5f9",
        "border": "rgba(148, 163, 184, 0.18)" if dark else "rgba(15, 23, 42, 0.10)",
        "text": "#f8fafc" if dark else "#0f172a",
        "muted": "#cbd5e1" if dark else "#64748b",
        "input_bg": "#0f172a" if dark else "#ffffff",
        "input_text": "#f8fafc" if dark else "#0f172a",
        "header_bg": "rgba(11, 18, 32, 0.82)" if dark else "rgba(248, 250, 252, 0.78)",
        "page_bg": "linear-gradient(180deg, #0b1220 0%, #111827 52%, #0f172a 100%)"
        if dark
        else "linear-gradient(180deg, rgba(248, 250, 252, 0.98) 0%, rgba(236, 254, 255, 0.62) 42%, #f8fafc 100%)",
        "sidebar_bg": "linear-gradient(180deg, #020617 0%, #0f172a 55%, #083f46 100%)"
        if dark
        else "linear-gradient(180deg, #111827 0%, #0f172a 58%, #083f46 100%)",
        "shadow": "0 16px 34px rgba(0, 0, 0, 0.24)" if dark else "0 12px 28px rgba(15, 23, 42, 0.06)",
        "soft_shadow": "0 10px 24px rgba(0, 0, 0, 0.20)" if dark else "0 10px 24px rgba(15, 23, 42, 0.04)",
    }
    st.markdown(
        Template(
            """
        <style>
        :root {
            --cr-bg: $bg;
            --cr-bg-soft: $bg_soft;
            --cr-surface: $surface;
            --cr-surface-soft: $surface_soft;
            --cr-border: $border;
            --cr-border-strong: rgba(20, 184, 166, 0.30);
            --cr-text: $text;
            --cr-muted: $muted;
            --cr-input-bg: $input_bg;
            --cr-input-text: $input_text;
            --cr-teal: #14b8a6;
            --cr-cyan: #06b6d4;
            --cr-blue: #2563eb;
            --cr-green: #22c55e;
            --cr-amber: #f59e0b;
            --cr-red: #ef4444;
            --cr-sidebar: #111827;
        }
        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"] {
            background: $page_bg;
            color: var(--cr-text);
        }
        [data-testid="stHeader"] {
            background: $header_bg;
            backdrop-filter: blur(14px);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3 {
            color: var(--cr-text);
            letter-spacing: 0;
        }
        p,
        label,
        [data-testid="stCaptionContainer"] {
            color: var(--cr-muted);
        }
        [data-testid="stSidebar"] {
            background: $sidebar_bg;
            border-right: 1px solid rgba(20, 184, 166, 0.20);
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
            color: rgba(248, 250, 252, 0.92);
        }
        div[data-testid="stMetric"] {
            background: color-mix(in srgb, var(--cr-surface) 94%, transparent);
            border: 1px solid var(--cr-border);
            border-radius: 8px;
            box-shadow: $shadow;
            padding: 0.85rem 1rem;
        }
        div[data-testid="stMetric"] label {
            color: var(--cr-muted);
            font-weight: 700;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--cr-text);
        }
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            border: 1px solid var(--cr-border);
            border-radius: 8px;
            box-shadow: $soft_shadow;
            overflow: hidden;
        }
        div[data-testid="stExpander"] {
            background: color-mix(in srgb, var(--cr-surface) 90%, transparent);
            border: 1px solid var(--cr-border);
            border-radius: 8px;
            box-shadow: $soft_shadow;
        }
        div[data-testid="stForm"] {
            background: color-mix(in srgb, var(--cr-surface) 90%, transparent);
            border: 1px solid var(--cr-border);
            border-radius: 8px;
            box-shadow: $soft_shadow;
            padding: 1rem;
        }
        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        .stMultiSelect div[data-baseweb="select"] > div {
            border-color: rgba(20, 184, 166, 0.24);
            border-radius: 8px;
            box-shadow: none;
            background: var(--cr-input-bg);
            color: var(--cr-input-text);
        }
        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border-color: var(--cr-teal);
            box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.16);
        }
        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, var(--cr-teal), var(--cr-blue));
            border: 0;
            border-radius: 8px;
            color: #ffffff;
            font-weight: 800;
            box-shadow: 0 10px 22px rgba(20, 184, 166, 0.18);
            transition: transform 150ms ease, box-shadow 150ms ease, filter 150ms ease;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            color: #ffffff;
            filter: brightness(1.04);
            transform: translateY(-1px);
            box-shadow: 0 14px 28px rgba(37, 99, 235, 0.18);
        }
        .stButton > button p,
        .stDownloadButton > button p,
        div[data-testid="stFormSubmitButton"] button p {
            color: #ffffff;
        }
        a {
            color: var(--cr-blue);
            font-weight: 700;
        }
        .stAlert {
            border-radius: 8px;
        }
        </style>
        """
        ).substitute(**tokens),
        unsafe_allow_html=True,
    )


def _render_login_screen():
    login_stage = st.session_state.get("login_stage", "credentials")
    hero_image = _asset_data_uri("assets/login-risk-hero.png")
    hero_image_html = (
        f'<img class="login-hero-image" src="{hero_image}" alt="Risk assessment workspace">'
        if hero_image
        else '<div class="login-hero-image login-hero-fallback"></div>'
    )
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
        .block-container {
            max-width: 1120px;
            padding-top: 5vh;
        }
        .login-hero {
            border: 1px solid rgba(20, 184, 166, 0.26);
            border-radius: 8px;
            background: rgba(17, 24, 39, 0.92);
            box-shadow: 0 24px 58px rgba(15, 23, 42, 0.20);
            color: #f8fafc;
            min-height: 560px;
            overflow: hidden;
            animation: loginRise 540ms ease-out both;
        }
        .login-hero-image {
            display: block;
            height: 315px;
            object-fit: cover;
            width: 100%;
        }
        .login-hero-fallback {
            background:
                linear-gradient(135deg, rgba(20, 184, 166, 0.34), rgba(15, 23, 42, 0.92)),
                radial-gradient(circle at 78% 20%, rgba(34, 197, 94, 0.25), transparent 32%);
        }
        .login-hero-body {
            padding: 1.55rem 1.75rem 1.75rem;
        }
        .login-kicker {
            color: #5eead4;
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
        }
        .login-title {
            font-size: 2.35rem;
            font-weight: 850;
            line-height: 1.05;
            margin: 0.6rem 0 0.75rem;
        }
        .login-copy {
            color: rgba(226, 232, 240, 0.78);
            font-size: 0.98rem;
            line-height: 1.55;
            max-width: 34rem;
        }
        .login-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin-top: 1.35rem;
        }
        .login-stat {
            border: 1px solid rgba(20, 184, 166, 0.22);
            border-radius: 8px;
            padding: 0.8rem;
            background: rgba(15, 23, 42, 0.50);
        }
        .login-stat-value {
            font-size: 1.25rem;
            font-weight: 800;
        }
        .login-stat-label {
            color: rgba(226, 232, 240, 0.68);
            font-size: 0.76rem;
            margin-top: 0.2rem;
        }
        div[data-testid="stForm"] {
            border: 1px solid rgba(20, 184, 166, 0.28);
            border-radius: 8px;
            background: rgba(17, 24, 39, 0.94);
            box-shadow: 0 24px 58px rgba(15, 23, 42, 0.20);
            min-height: 560px;
            padding: 1.45rem 1.45rem 1.25rem;
            animation: loginRise 620ms ease-out both;
        }
        div[data-testid="stForm"] label,
        div[data-testid="stForm"] p {
            color: rgba(248, 250, 252, 0.9);
        }
        .login-form-title {
            color: #f8fafc;
            font-size: 1.7rem;
            font-weight: 850;
            line-height: 1.12;
            margin: 0.35rem 0 0.45rem;
        }
        .login-form-copy {
            color: rgba(226, 232, 240, 0.74);
            font-size: 0.9rem;
            line-height: 1.45;
            margin-bottom: 1.2rem;
        }
        .login-form-divider {
            border-top: 1px solid rgba(148, 163, 184, 0.18);
            margin: 1.1rem 0;
        }
        @keyframes loginRise {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @media (max-width: 820px) {
            .block-container {
                padding-top: 2rem;
            }
            .login-strip {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    hero_col, login_col = st.columns([1.15, 0.85], gap="large")
    with hero_col:
        st.markdown(
            f"""
            <section class="login-hero">
                {hero_image_html}
                <div class="login-hero-body">
                <div class="login-kicker">CredRisk.AI</div>
                <div class="login-title">The place to be for your risk assessment.</div>
                <div class="login-copy">
                    One focused workbench for SME credit review, human decisions,
                    model explanations, and operational confidence.
                </div>
                <div class="login-strip">
                    <div class="login-stat">
                        <div class="login-stat-value">A-F</div>
                        <div class="login-stat-label">Risk grading</div>
                    </div>
                    <div class="login-stat">
                        <div class="login-stat-value">LLM</div>
                        <div class="login-stat-label">Review assist</div>
                    </div>
                    <div class="login-stat">
                        <div class="login-stat-value">Audit</div>
                        <div class="login-stat-label">Decision trail</div>
                    </div>
                </div>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
    with login_col:
        if login_stage == "2fa":
            with st.form("login_2fa_form"):
                st.markdown(
                    """
                    <div class="login-kicker">Two-factor verification</div>
                    <div class="login-form-title">Enter your verification code</div>
                    <div class="login-form-copy">
                        Use the six-digit code from your authenticator app to continue.
                    </div>
                    <div class="login-form-divider"></div>
                    """,
                    unsafe_allow_html=True,
                )
                verification_code = st.text_input("Verification code", max_chars=6)
                submitted = st.form_submit_button("Verify", width="stretch")
            if st.button("Use Different Credentials", width="stretch"):
                st.session_state.login_stage = "credentials"
                _rerun()
            if submitted:
                if verification_code.isdigit() and len(verification_code) == 6:
                    _complete_login()
                else:
                    st.warning("Enter a 6-digit verification code.")
        else:
            with st.form("login_form"):
                st.markdown(
                    """
                    <div class="login-kicker">Secure workspace</div>
                    <div class="login-form-title">Sign in to continue</div>
                    <div class="login-form-copy">
                        Access your risk-assessment workspace and continue the review flow.
                    </div>
                    <div class="login-form-divider"></div>
                    """,
                    unsafe_allow_html=True,
                )
                account_type = st.selectbox(
                    "Demo account",
                    ["lender", "sme"],
                    format_func=lambda value: "Lender analyst" if value == "lender" else "SME company",
                )
                login_profile = SME_PROFILE if account_type == "sme" else PROFILE
                username = st.text_input("Email", value=login_profile["email"], disabled=True)
                password = st.text_input("Password", type="password")
                remember_me = st.checkbox("Remember me", value=bool(st.session_state.get("remember_me", False)))
                submitted = st.form_submit_button("Continue", width="stretch")
            if submitted:
                if username.strip() and password:
                    st.session_state.remember_me = remember_me
                    st.session_state.pending_login_account_type = account_type
                    st.session_state.login_stage = "2fa"
                    _rerun()
                else:
                    st.warning("Enter your email and password to continue.")


def _complete_login():
    account_type = st.session_state.get("pending_login_account_type", "lender")
    login_profile = SME_PROFILE if account_type == "sme" else PROFILE
    transition = st.empty()
    progress = st.progress(0, text="Verifying security code")
    steps = [
        "Verifying security code",
        "Loading profile",
        "Loading company portal" if account_type == "sme" else "Syncing personal apps",
        "Opening SME workspace" if account_type == "sme" else "Opening underwriter workbench",
    ]
    for index, step in enumerate(steps, start=1):
        transition.success(step)
        progress.progress(index / len(steps), text=step)
        sleep(0.16)
    st.session_state.user_profile = dict(login_profile)
    st.session_state.authenticated = True
    st.session_state.login_transition = True
    st.session_state.login_destination = "pages/6_SME_Credit_Health.py" if account_type == "sme" else None
    st.session_state.login_stage = "credentials"
    st.session_state[DEMO_PROMPT_HANDLED_KEY] = False
    st.session_state[DEMO_PROMPT_CHECKBOX_KEY] = False
    persist_demo_state()
    _rerun()


def _render_login_transition():
    if not st.session_state.get("login_transition"):
        return
    st.session_state.login_transition = False
    profile = get_profile()
    destination_copy = (
        "Company portal unlocked. Complete your company profile, connect evidence sources, and review your credit health."
        if is_sme_profile(profile)
        else "Workspace unlocked. Start at Home, continue to Personal Workspace, then open LLM Integration."
    )
    st.markdown(
        Template(
            """
        <style>
        .app-transition-banner {
            border: 1px solid rgba(34, 197, 94, 0.28);
            border-left: 5px solid #22c55e;
            border-radius: 8px;
            background: rgba(22, 101, 52, 0.12);
            color: var(--cr-text);
            margin: 0 0 1rem;
            padding: 0.85rem 1rem;
            animation: appFadeIn 620ms ease-out both;
        }
        .app-transition-title {
            font-size: 1rem;
            font-weight: 800;
        }
        .app-transition-copy {
            color: var(--cr-muted);
            font-size: 0.86rem;
            margin-top: 0.15rem;
        }
        @keyframes appFadeIn {
            from { opacity: 0; transform: translateY(-8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        <div class="app-transition-banner">
            <div class="app-transition-title">Welcome back.</div>
            <div class="app-transition-copy">$destination_copy</div>
        </div>
        """
        ).substitute(destination_copy=escape(destination_copy)),
        unsafe_allow_html=True,
    )


def _save_demo_prompt_choice(choice):
    remember_choice = bool(st.session_state.get(DEMO_PROMPT_CHECKBOX_KEY, False))
    st.session_state[DEMO_PROMPT_CHOICE_KEY] = choice
    st.session_state[DEMO_PROMPT_REMEMBERED_KEY] = remember_choice
    st.session_state[DEMO_PROMPT_HANDLED_KEY] = True
    persist_demo_state()


def _demo_prompt_body():
    st.markdown(
        """
        <div style="font-size:1.2rem;font-weight:850;color:var(--cr-text);margin-bottom:.35rem;">
            First time? Check out our demo for an in-depth dive into our app!
        </div>
        <div style="color:var(--cr-muted);line-height:1.5;margin-bottom:.75rem;">
            You can also explore the page-by-page tutorials inside the workspace.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("The YouTube demo link will be enabled after the video is published.")

    # Uncomment when DEMO_VIDEO_URL is available. st.link_button opens external links in a new tab.
    # st.link_button("Watch Demo on YouTube", DEMO_VIDEO_URL, width="stretch")

    st.checkbox(
        "Remember my choice for next time",
        key=DEMO_PROMPT_CHECKBOX_KEY,
        help="When selected, this welcome prompt will not appear on later logins for this saved demo session.",
    )
    tutorial_col, skip_col = st.columns(2)
    if tutorial_col.button("Browse Tutorials", width="stretch", key="demo_prompt_tutorials"):
        _save_demo_prompt_choice("tutorials")
        st.switch_page("pages/10_Tutorials.py")
    if skip_col.button("Skip this step", width="stretch", key="demo_prompt_skip"):
        _save_demo_prompt_choice("skip")
        _rerun()


if hasattr(st, "dialog"):

    @st.dialog("Welcome to CredRisk.AI", dismissible=False)
    def _demo_prompt_dialog():
        _demo_prompt_body()


def _render_demo_prompt():
    if DEMO_PROMPT_CHECKBOX_KEY not in st.session_state:
        st.session_state[DEMO_PROMPT_CHECKBOX_KEY] = False
    if st.session_state.get(DEMO_PROMPT_REMEMBERED_KEY, False):
        return
    if st.session_state.get(DEMO_PROMPT_HANDLED_KEY, False):
        return

    if hasattr(st, "dialog"):
        _demo_prompt_dialog()
        return

    with st.container(border=True):
        _demo_prompt_body()


def render_sidebar():
    _render_global_theme()
    if not st.session_state.get("authenticated"):
        _render_login_screen()
        st.stop()

    _render_login_transition()
    profile = get_profile()
    login_destination = st.session_state.get("login_destination")
    if login_destination:
        st.session_state.login_destination = None
        persist_demo_state()
        switch_page = getattr(st, "switch_page", None)
        if switch_page:
            switch_page(login_destination)
    if not is_sme_profile(profile):
        _render_demo_prompt()
    st.markdown(
        """
        <style>
        .sidebar-section-label {
            color: rgba(100, 116, 139, 0.94);
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0;
            line-height: 1;
            margin: 1rem 0 0.2rem;
            text-transform: uppercase;
        }
        .profile-sidebar-card {
            border-top: 1px solid rgba(148, 163, 184, 0.24);
            color: rgba(100, 116, 139, 0.96);
            margin-top: 0.75rem;
            padding-top: 0.65rem;
        }
        .profile-sidebar-card .profile-name {
            font-size: 0.84rem;
            font-weight: 750;
            line-height: 1.2;
            overflow-wrap: anywhere;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.sidebar:
        hdr_col, dm_col = st.columns([3, 1])
        hdr_col.header("Company Portal" if is_sme_profile(profile) else "Workspace")
        st.session_state[DARK_MODE_WIDGET_KEY] = _is_dark_mode()
        dm_col.toggle(
            "Dark mode",
            key=DARK_MODE_WIDGET_KEY,
            on_change=_sync_dark_mode_from_widget,
            label_visibility="collapsed",
            help="Toggle dark mode",
        )
        navigation = SME_NAV_SECTIONS if is_sme_profile(profile) else NAV_SECTIONS
        for section_label, links in navigation:
            st.markdown(
                f'<div class="sidebar-section-label">{escape(section_label)}</div>',
                unsafe_allow_html=True,
            )
            for label, page, icon in links:
                _page_link(page, label, icon)
        profile["dark_mode"] = _is_dark_mode()
        st.session_state.user_profile = profile
        st.divider()
        st.markdown(
            f"""
            <div class="profile-sidebar-card">
                <div class="profile-name">{escape(profile["name"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Sign Out", width="stretch"):
            st.session_state.authenticated = False
            st.session_state.login_transition = False
            st.session_state[DEMO_PROMPT_HANDLED_KEY] = False
            st.session_state[DEMO_PROMPT_CHECKBOX_KEY] = False
            persist_demo_state()
            _rerun()
