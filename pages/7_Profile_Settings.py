from datetime import datetime

import pandas as pd
import streamlit as st

from src.constants import *
from src.core.runtime import bootstrap_state
from src.ui.components import get_profile, render_sidebar, save_profile

st.set_page_config(page_title="Profile & Settings", layout="wide")
bootstrap_state()
render_sidebar()


def _option_index(options, value):
    return options.index(value) if value in options else 0


def _integration_rows(profile):
    integrations = profile["integrations"]
    rows = []
    for item in INTEGRATION_CATALOG:
        account = (
            profile["email"]
            if item["key"] in ["gmail", "outlook", "zoom"]
            else item["account"]
        )
        rows.append(
            {
                "Category": item["category"],
                "Integration": item["name"],
                "Status": (
                    "Connected" if integrations.get(item["key"]) else "Disconnected"
                ),
                "Account / workspace": account,
                "Use": item["use"],
            }
        )
    return pd.DataFrame(rows)


if st.session_state.get("profile_settings_saved"):
    st.success("Profile and settings saved for this session.")
    st.session_state.profile_settings_saved = False

profile = get_profile()

st.title("Profile & Settings")
st.caption(
    "Manage analyst identity, connected channels, permissions, and account preferences."
)

profile_rows = pd.DataFrame(
    [
        {"Field": "ID", "Value": profile["user_id"]},
        {"Field": "Name", "Value": profile["name"]},
        {"Field": "Email", "Value": profile["email"]},
        {"Field": "Bank", "Value": profile["bank"]},
        {"Field": "Role", "Value": profile["role"]},
        {"Field": "Team", "Value": profile["team"]},
        {"Field": "User type", "Value": profile["user_type"]},
        {"Field": "Permission", "Value": profile["permission"]},
        {"Field": "Team manager", "Value": profile["team_manager"]},
        {"Field": "Preferred email app", "Value": profile["preferred_email_app"]},
    ]
)
integration_rows = _integration_rows(profile)

profile_tab, apps_tab, admin_tab = st.tabs(
    ["Profile", "Personal Apps", "Admin Controls"]
)

with profile_tab:
    st.subheader("Profile")
    st.dataframe(profile_rows, width="stretch", hide_index=True)

with apps_tab:
    st.subheader("Personal Connected Apps")
    st.dataframe(integration_rows, width="stretch", hide_index=True)

with admin_tab:
    st.subheader("Admin Controls")
    st.caption(
        "Update session preferences and controlled profile fields for the current demo workspace."
    )
    admin_controls_enabled = st.checkbox(
        "Enable controlled profile fields", value=False
    )
    with st.form("profile_settings_form"):
        identity_left, identity_right = st.columns(2)
        with identity_left:
            user_id = st.text_input("ID", value=profile["user_id"], disabled=True)
            name = st.text_input("Name", value=profile["name"])
            email = st.text_input("Email", value=profile["email"], disabled=True)
            role = st.text_input("Role", value=profile["role"])
            team = st.text_input("Team", value=profile["team"])
        with identity_right:
            user_type = st.selectbox(
                "User type",
                PROFILE_TYPES,
                index=_option_index(PROFILE_TYPES, profile["user_type"]),
                disabled=not admin_controls_enabled,
            )
            permission = st.selectbox(
                "Permission",
                PERMISSIONS,
                index=_option_index(PERMISSIONS, profile["permission"]),
                disabled=not admin_controls_enabled,
            )
            team_manager = st.selectbox(
                "Team manager",
                MANAGERS,
                index=_option_index(MANAGERS, profile["team_manager"]),
                disabled=not admin_controls_enabled,
            )
            preferred_channel = st.radio(
                "Preferred channel",
                CHANNELS,
                index=_option_index(CHANNELS, profile["preferred_channel"]),
                horizontal=True,
            )
            preferred_email_app = st.radio(
                "Preferred email app",
                EMAIL_APPS,
                index=_option_index(EMAIL_APPS, profile["preferred_email_app"]),
                horizontal=True,
            )

        st.markdown("**Personal app access**")
        integration_values = {}
        integration_cols = st.columns(2)
        for index, item in enumerate(INTEGRATION_CATALOG):
            with integration_cols[index % 2]:
                integration_values[item["key"]] = st.checkbox(
                    item["name"],
                    value=bool(profile["integrations"].get(item["key"], False)),
                    key=f"integration_{item['key']}",
                )

        notification_cols = st.columns(2)
        with notification_cols[0]:
            review_alerts = st.checkbox(
                "Review alerts", value=bool(profile["review_alerts"])
            )
        with notification_cols[1]:
            daily_digest = st.checkbox(
                "Daily digest", value=bool(profile["daily_digest"])
            )
        dark_mode = st.checkbox("Dark mode", value=bool(profile["dark_mode"]))

        saved = st.form_submit_button("Save Admin Controls", width="stretch")

    if saved:
        channel_key = preferred_channel.lower()
        if channel_key in ["slack", "teams"] and not integration_values.get(
            channel_key, False
        ):
            st.error(
                f"Connect {preferred_channel} before setting it as the preferred channel."
            )
        else:
            save_profile(
                {
                    "id": user_id,
                    "user_id": user_id,
                    "name": name.strip() or profile["name"],
                    "display_name": name.strip() or profile["display_name"],
                    "email": profile["email"],
                    "role": role.strip() or profile["role"],
                    "team": team.strip() or profile["team"],
                    "user_type": user_type,
                    "permission": permission,
                    "team_manager": team_manager,
                    "integrations": integration_values,
                    "preferred_channel": preferred_channel,
                    "preferred_email_app": preferred_email_app,
                    "review_alerts": review_alerts,
                    "daily_digest": daily_digest,
                    "dark_mode": dark_mode,
                    "settings_last_saved": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            )
            st.session_state.profile_settings_saved = True
            rerun = getattr(st, "rerun", None) or getattr(
                st, "experimental_rerun", None
            )
            if rerun:
                rerun()

last_saved = profile.get("settings_last_saved")
if last_saved:
    st.caption(f"Last saved: {last_saved}")
