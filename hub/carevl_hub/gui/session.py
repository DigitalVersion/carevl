"""
Session state management and local file persistence for Hub GUI.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


SESSION_KEYS = ("hub_pat", "hub_org", "hub_output_dir", "hub_encryption_key", "github_client_id")


def local_state_path() -> Path:
    """Next to hub package root (`hub/`), gitignored — optional persistence."""
    return Path(__file__).resolve().parents[3] / ".carevl_operator_local.json"


def init_session_defaults() -> None:
    defaults = {
        "hub_pat": "",
        "hub_org": "",
        "hub_output_dir": "./hub_data",
        "hub_encryption_key": "",
        "github_client_id": "",       # OAuth App Client ID — nhập 1 lần, lưu file
        "github_token": None,
        "auth_in_progress": False,
        "device_code": None,
        "user_code": None,
        "verification_uri": None,
        "polling_interval": 5,
        "last_generated_code": None,
        "last_generated_station": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def try_load_local_state() -> None:
    p = local_state_path()
    if not p.is_file():
        return
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(data, dict):
        return
    for k in SESSION_KEYS:
        v = data.get(k)
        if isinstance(v, str) and v:
            st.session_state[k] = v


def save_local_state() -> None:
    p = local_state_path()
    payload = {k: str(st.session_state.get(k, "") or "") for k in SESSION_KEYS}
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def delete_local_state_file() -> None:
    p = local_state_path()
    if p.is_file():
        p.unlink()


def mask_secret(value: str, keep_start: int = 4, keep_end: int = 2) -> str:
    if not value or len(value) <= keep_start + keep_end:
        return "••••" if value else "(trống)"
    return f"{value[:keep_start]}…{value[-keep_end:]}"
