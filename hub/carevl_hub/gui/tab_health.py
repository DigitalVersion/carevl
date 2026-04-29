"""
Tab 3: Health check — version, CWD, session info.
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from carevl_hub import __version__
from carevl_hub.gui.session import mask_secret


def render() -> None:
    """Tab 3: Health check."""
    st.subheader("🏥 Health")

    st.metric("Version", __version__)
    st.text(f"CWD: {os.getcwd()}")

    out = Path(st.session_state.get("hub_output_dir") or "./hub_data")
    st.text(f"Output dir: {out.resolve()}")
    st.text(f"Exists: {out.resolve().is_dir()}")

    st.divider()
    st.markdown("**Session**")
    st.code(
        f"Org: {st.session_state.get('hub_org') or '(trống)'}\n"
        f"PAT: {mask_secret(st.session_state.get('hub_pat', ''))}\n"
        f"Key: {mask_secret(st.session_state.get('hub_encryption_key', ''))}\n"
        f"GitHub token: {mask_secret(str(st.session_state.get('github_token') or ''))}"
    )
