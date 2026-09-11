"""
ECDAT — Enterprise Cryptographic Discovery & Analysis Tool.
"""
import sys
import time
from pathlib import Path

# Streamlit places the script directory on sys.path; add the project root so
# dashboard components can import sibling packages such as scanner and api.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests
import streamlit as st
from components.data import get_last_scan_string, get_scan_data
from components.sidebar import render_scan_controls_main, render_sidebar
from components.theme import THEME, inject_css
from components.views import (
    render_asset_intelligence,
    render_blind_spots_and_risk,
    render_cbom_and_compliance,
    render_discovery,
    render_evidence_graph,
    render_migration_and_simulator,
    render_overview,
)

st.set_page_config(
    page_title="ECDAT — Cryptographic Risk Management",
    page_icon="E",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    inject_css()
    if st.query_params.get("scan_home") == "1":
        st.session_state["show_scan_intake"] = True
        st.session_state.pop("scan_id", None)
        st.session_state.pop("results_cache", None)
        st.session_state.pop("last_scan_time", None)
        st.query_params.pop("scan_home", None)
    elif not any(key in st.session_state for key in ("scan_id", "results_cache", "show_scan_intake")):
        st.session_state["show_scan_intake"] = True
    scan_data = get_scan_data()
    has_scan_started = scan_data is not None and "error" not in scan_data

    if has_scan_started:
        nav_selection = render_sidebar()
        _render_nova_top_bar(nav_selection)

        if scan_data.get("status") == "failed":
            _render_scan_failure(scan_data)
            return

        if scan_data.get("status") == "running":
            st.info("Scan in progress — results will appear automatically.", icon="🧠")
            st.progress(35, text="Analyzing source files and cryptographic evidence…")
            if st.button("Refresh status", key="re_btn"):
                st.cache_data.clear()
                st.rerun()
            time.sleep(2)
            st.cache_data.clear()
            st.rerun()

        if nav_selection == "OVERVIEW":
            render_overview(scan_data)
        elif nav_selection == "DISCOVERY":
            render_discovery(scan_data)
        elif nav_selection == "ASSET INTELLIGENCE":
            render_asset_intelligence(scan_data)
        elif nav_selection == "EVIDENCE GRAPH":
            render_evidence_graph(scan_data)
        elif nav_selection == "BLIND SPOTS & RISK":
            render_blind_spots_and_risk(scan_data)
        elif nav_selection == "MIGRATION & SIMULATOR":
            render_migration_and_simulator(scan_data)
        elif nav_selection == "CBOM & COMPLIANCE":
            scan_id = st.session_state.get("scan_id", "LIVE-DEMO-2026")
            render_cbom_and_compliance(scan_id)
    else:
        st.markdown("<style>[data-testid='stSidebar']{display:none!important;}</style>", unsafe_allow_html=True)
        render_scan_controls_main()

def _render_nova_top_bar(nav_selection: str):
    last_scan_str = get_last_scan_string()
    clean_title = nav_selection.replace("_", " ").upper()

    html = f"""
    <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 28px; background: {THEME['bg_glass']}; border: 1px solid {THEME['border_dim']}; border-radius: 18px; margin-bottom: 50px; backdrop-filter: blur(12px);">
        <div style="display:flex; align-items:center; gap:15px;">
            <div style="text-align: left; line-height: 1.1;">
                <div style="color: {THEME['text_muted']}; font-size: 0.55rem; font-weight: 900; text-transform: uppercase; letter-spacing: 1.5px;">Command</div>
                <div style="color: {THEME['text_muted']}; font-size: 0.55rem; font-weight: 900; text-transform: uppercase; letter-spacing: 1.5px;">Center</div>
            </div>
            <div style="color: {THEME['text_dim']}; font-size: 1.2rem; font-weight: 300;">/</div>
            <div style="color: {THEME['neon_blue']}; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">{clean_title}</div>
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between; flex-grow: 1; margin-left: 40px;">
            <!-- Informational status, not a non-functional search control. -->
            <div style="flex-grow: 1; max-width: 480px; margin: 0 40px 0 0;">
                <div style="background: rgba(7, 10, 17, 0.6); border: 1px solid {THEME['border_dim']}; border-radius: 12px; padding: 10px 18px; color: {THEME['text_dim']}; font-size: 0.95rem; display: flex; align-items: center; gap: 12px;">
                    <span style="color: {THEME['neon_blue']}; font-size: 1.1rem;">●</span> Current scan workspace
                </div>
            </div>
            <!-- Right side: sync + status -->
            <div style="display: flex; align-items: center; gap: 30px;">
                <div style="text-align: right;">
                    <div style="font-size: 0.6rem; color: {THEME['text_muted']}; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 800;">Last Sync</div>
                    <div style="font-size: 0.95rem; color: #fff; font-weight: 800; margin-top: 2px; letter-spacing: -0.5px;">{last_scan_str}</div>
                </div>
                <div style="background: rgba(0, 255, 102, 0.05); border: 1px solid {THEME['neon_green']}33; padding: 8px 18px; border-radius: 12px; display: flex; align-items: center; gap: 10px;">
                    <div style="width: 8px; height: 8px; border-radius: 50%; background: {THEME['neon_green']}; box-shadow: 0 0 12px {THEME['neon_green']}; animation: status-pulse 1.5s infinite;"></div>
                    <span style="font-size: 0.75rem; font-weight: 800; color: {THEME['neon_green']}; letter-spacing: 1px;">ONLINE</span>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def _render_nova_welcome():
    html = f"""
    <div style="text-align:center;padding:40px 20px;">
        <div style="width:80px;height:80px;border-radius:20px;background:linear-gradient(135deg,{THEME['neon_blue']} 0%,{THEME['neon_purple']} 100%);display:flex;align-items:center;justify-content:center;font-size:2.5rem;color:#fff;margin:0 auto 20px auto;box-shadow:0 0 30px {THEME['neon_blue']}44;">⚡</div>
        <h1 style="font-size:3.5rem;font-weight:800;color:#fff;margin:0;letter-spacing:-2px;">ECDAT</h1>
        <p style="font-size:1.1rem;color:{THEME['text_muted']};max-width:600px;margin:20px auto;">Cryptographic discovery, quantum-risk assessment, and migration planning for enterprise codebases.</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def _render_scan_failure(scan_data: dict):
    """Show a clear recovery path rather than an empty dashboard after a failed scan."""
    error = scan_data.get("summary", {}).get("error", "The scan could not be completed.")
    with st.container(border=True):
        st.error("Scan could not be completed")
        st.write(error)
        st.caption(f"Source: {scan_data.get('target_path', 'Unknown source')}")
        target_path = scan_data.get("target_path", "")
        if target_path.lower().endswith(".zip"):
            if st.button("Choose another archive", type="primary", key="replace_failed_archive"):
                _start_new_scan()
        elif st.button("Retry scan", type="primary", key="retry_failed_scan"):
            _retry_scan(target_path)
        if st.button("Start a different scan", key="new_scan_after_failure"):
            _start_new_scan()
        st.caption("Check that the local path is available, the archive is valid, or the GitHub repository is public, then try again.")


def _start_new_scan():
    st.session_state["show_scan_intake"] = True
    st.session_state.pop("scan_id", None)
    st.session_state.pop("results_cache", None)
    st.rerun()


def _retry_scan(target_path: str):
    """Retry a failed source using the same endpoint as the original scan."""
    try:
        endpoint = "/scan/github" if target_path.startswith("https://github.com/") else "/scan"
        parameter = "repo_url" if endpoint.endswith("github") else "path"
        response = requests.post(f"http://localhost:8000{endpoint}", params={parameter: target_path}, timeout=10)
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            st.error(payload["error"])
            return
        st.session_state["scan_id"] = payload["scan_id"]
        st.session_state.pop("results_cache", None)
        st.session_state.pop("show_scan_intake", None)
        st.rerun()
    except Exception as exc:
        st.error(f"Unable to retry scan: {exc!s}")

if __name__ == "__main__":
    main()
