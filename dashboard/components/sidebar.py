"""
Nova Sidebar — High-fidelity navigation for ECDAT.
"""
from datetime import datetime, timezone

import requests
import streamlit as st
import streamlit.components.v1 as components

from .theme import THEME, inject_css

API_BASE = "http://localhost:8000"

NAV_OPTIONS = [
    "Overview",
    "Discovery",
    "Asset Intelligence",
    "Evidence Graph",
    "Blind Spots & Risk",
    "Migration & Simulator",
    "CBOM & Compliance",
]


def _render_browser_back_bridge() -> None:
    """Use browser Back as the dashboard-to-scan-intake navigation control."""
    components.html(
        """
        <script>
        (() => {
            const parentWindow = window.parent;
            parentWindow.__ecdatDashboardActive = true;
            const dashboardUrl = new URL(parentWindow.location.href);
            if (dashboardUrl.hash !== '#ecdat-dashboard') {
                dashboardUrl.hash = 'ecdat-dashboard';
                parentWindow.history.pushState({ ecdatDashboard: true }, '', dashboardUrl.toString());
            }
            if (parentWindow.__ecdatBackBridgeInstalled) {
                return;
            }
            parentWindow.__ecdatBackBridgeInstalled = true;
            parentWindow.addEventListener('popstate', () => {
                if (!parentWindow.__ecdatDashboardActive) return;
                parentWindow.__ecdatDashboardActive = false;
                const url = new URL(parentWindow.location.href);
                url.hash = '';
                url.searchParams.set('scan_home', '1');
                parentWindow.location.assign(url.toString());
            });
        })();
        </script>
        """,
        height=0,
        width=0,
    )

def render_sidebar() -> str:
    """Render the Nova glassmorphic sidebar."""
    inject_css()

    # Custom Sidebar Navigation Styling
    st.markdown(f"""
    <style>
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] > div {{
        gap: 6px !important;
        padding-top: 10px !important;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        padding: 12px 18px !important;
        border-radius: 14px !important;
        border: 1px solid transparent !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: transparent !important;
        color: {THEME['text_muted']} !important;
        font-weight: 600 !important;
        margin-bottom: 2px !important;
        font-family: {THEME['font_ui']} !important;
        display: flex !important;
        align-items: center !important;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        background: rgba(255, 255, 255, 0.04) !important;
        color: #fff !important;
        transform: translateX(4px);
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {{
        background: rgba(0, 209, 255, 0.1) !important;
        border: 1px solid rgba(0, 209, 255, 0.3) !important;
        color: {THEME['neon_blue']} !important;
        box-shadow: 0 4px 20px rgba(0, 209, 255, 0.1) !important;
    }}

    /* Streamlit's checked state is held by the nested input in some releases. */
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
        background: rgba(0, 209, 255, 0.14) !important;
        border-color: {THEME['neon_blue']} !important;
        color: {THEME['neon_blue']} !important;
        box-shadow: inset 4px 0 0 {THEME['neon_blue']}, 0 4px 20px rgba(0, 209, 255, 0.12) !important;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {{
        font-size: 0.9rem !important;
        letter-spacing: 0.5px !important;
        margin: 0 !important;
        color: inherit !important;
        opacity: 1 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label span {{
        color: inherit !important;
    }}

    /* Hide only the radio control.  Do not target the first div: in newer
       Streamlit versions that div wraps the label text as well. */
    [data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] {{
        display: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Nova Brand Header
        st.html(f"""
        <div style="padding: 10px 0 35px 0; text-align: center;">
            <div style="position: relative; display: inline-block;">
                <div style="position: absolute; inset: -8px; background: linear-gradient(45deg, {THEME['neon_blue']}, {THEME['neon_purple']}); filter: blur(15px); opacity: 0.2; border-radius: 20px;"></div>
                <div style="position: relative; background: rgba(10, 14, 23, 0.9); padding: 16px 24px; border-radius: 20px; border: 1px solid {THEME['border_dim']}; backdrop-filter: blur(12px); display: flex; align-items: center; gap: 16px; min-width: 220px;">
                    <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, {THEME['neon_blue']} 0%, {THEME['neon_purple']} 100%); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 1.5rem; box-shadow: 0 0 25px {THEME['neon_blue']}66;">
                        💠
                    </div>
                    <div style="text-align: left; line-height: 1.1;">
                        <div style="font-family: {THEME['font_ui']}; font-size: 1.6rem; font-weight: 800; color: #fff; letter-spacing: -1.5px;">ECDAT</div>
                        <div style="font-size: 0.6rem; color: {THEME['neon_blue']}; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 4px;">CRYPTOGRAPHIC RISK</div>
                    </div>
                </div>
            </div>
        </div>
        """)

        # Section: Operations Center
        st.html(f"""
        <div style="margin: 10px 0 5px 0; padding: 0 10px; display: flex; align-items: center; gap: 12px;">
            <span style="color: {THEME['text_muted']}; font-size: 0.6rem; font-weight: 900; text-transform: uppercase; letter-spacing: 2.5px;">Operations</span>
            <div style="height: 1px; flex-grow: 1; background: linear-gradient(90deg, {THEME['border_dim']}, transparent);"></div>
        </div>
        """)

        # Radio Navigation
        selected = st.radio(
            "Navigation",
            options=NAV_OPTIONS,
            index=0,
            label_visibility="collapsed",
            key="nav_radio",
        )

        _render_browser_back_bridge()

        st.html("<div style='height: 35px;'></div>")

        # Section: Audit Engine
        st.html(f"""
        <div style="margin: 0 0 15px 0; padding: 0 10px; display: flex; align-items: center; gap: 12px;">
            <span style="color: {THEME['text_muted']}; font-size: 0.6rem; font-weight: 900; text-transform: uppercase; letter-spacing: 2.5px;">Scan</span>
            <div style="height: 1px; flex-grow: 1; background: linear-gradient(90deg, {THEME['border_dim']}, transparent);"></div>
        </div>
        """)

        # Scan controls inside a themed expander
        with st.expander("⚡ TRIGGER NEW AUDIT", expanded=False):
            _render_nova_scan_controls()

        # Telemetry Footer
        st.html(f"""
        <div style="margin-top: auto; padding: 20px 10px 10px 10px;">
            <div style="padding: 20px; background: rgba(15, 21, 36, 0.4); border-radius: 20px; border: 1px solid {THEME['border_dim']}; backdrop-filter: blur(8px); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 1px; background: linear-gradient(90deg, transparent, {THEME['neon_blue']}44, transparent);"></div>

                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 8px; height: 8px; border-radius: 50%; background: {THEME['neon_green']}; box-shadow: 0 0 10px {THEME['neon_green']}; animation: status-pulse 2s infinite;"></div>
                        <span style="font-size: 0.65rem; color: {THEME['text_muted']}; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px;">Node Health</span>
                    </div>
                    <span style="color: {THEME['neon_green']}; font-size: 0.65rem; font-weight: 900;">ACTIVE</span>
                </div>

                <div style="font-family: {THEME['font_fam']}; font-size: 0.85rem; color: #fff; font-weight: 700; margin-bottom: 4px;">ECDAT v2.8.5</div>
                <div style="font-size: 0.6rem; color: {THEME['text_dim']}; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 800;">Enterprise workspace</div>
            </div>
        </div>
        """)

    return selected.upper()

def _render_nova_scan_controls():
    """Nova-styled scan inputs."""
    st.markdown(f'<div style="color: {THEME["text_muted"]}; font-size: 0.65rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 12px;">Mode Selection</div>', unsafe_allow_html=True)
    scan_mode = st.segmented_control(
        "Mode",
        options=["PATH", "UPLOAD", "GITHUB"],
        default="PATH",
        label_visibility="collapsed",
        key="side_scan_mode",
    )

    st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)

    if scan_mode == "PATH":
        path = st.text_input(
            "Source Path",
            placeholder="/path/to/repository",
            label_visibility="collapsed",
            key="side_scan_path",
        )
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        if st.button("INITIALIZE ENGINE", type="primary", width="stretch", key="side_run_scan"):
            if path:
                _execute_scan(path)
            else:
                st.error("Engine requires a valid source path.")
    elif scan_mode == "GITHUB":
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/org/repo",
            label_visibility="collapsed",
            key="side_scan_github",
        )
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        if st.button("CLONE & AUDIT", type="primary", width="stretch", key="side_run_github"):
            if repo_url:
                _execute_github_scan(repo_url)
            else:
                st.error("Engine requires a valid GitHub repository URL.")
    else:
        uploaded_files = st.file_uploader(
            "Artifacts",
            type=["zip", "py", "java", "js", "ts", "go", "c", "cpp", "h", "rs"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="side_uploader",
        )
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        if st.button("EXECUTE AUDIT", type="primary", width="stretch", disabled=not uploaded_files, key="side_run_upload"):
            _execute_upload_scan(uploaded_files)


def _execute_scan(path: str):
    """Execute scan via API."""
    try:
        resp = requests.post(f"{API_BASE}/scan", params={"path": path}, timeout=10)
        resp.raise_for_status()
        st.session_state["scan_id"] = resp.json()["scan_id"]
        st.session_state.pop("show_scan_intake", None)
        st.session_state["last_scan_time"] = datetime.now(timezone.utc)
        st.session_state.pop("results_cache", None)
        st.toast("Scan started")
        st.rerun()
    except Exception as exc:
        st.error(f"Engine Error: {exc!s}")

def _execute_upload_scan(uploaded_files):
    """Execute upload scan via API."""
    try:
        resp = requests.post(
            f"{API_BASE}/scan/upload",
            files=[("files", (f.name, f.getvalue(), f.type or "application/octet-stream")) for f in uploaded_files],
            timeout=30,
        )
        resp.raise_for_status()
        st.session_state["scan_id"] = resp.json()["scan_id"]
        st.session_state.pop("show_scan_intake", None)
        st.session_state["last_scan_time"] = datetime.now(timezone.utc)
        st.session_state.pop("results_cache", None)
        st.toast("Upload scan started")
        st.rerun()
    except Exception as exc:
        st.error(f"Upload Error: {exc!s}")


def _execute_github_scan(repo_url: str):
    """Start a scan for a public GitHub repository."""
    try:
        resp = requests.post(f"{API_BASE}/scan/github", params={"repo_url": repo_url}, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("error"):
            st.error(payload["error"])
            return
        st.session_state["scan_id"] = payload["scan_id"]
        st.session_state.pop("show_scan_intake", None)
        st.session_state["last_scan_time"] = datetime.now(timezone.utc)
        st.session_state.pop("results_cache", None)
        st.toast("GitHub repository scan started")
        st.rerun()
    except Exception as exc:
        st.error(f"GitHub scan error: {exc!s}")


def retry_scan(target_path: str):
    """Retry a failed local, upload, or public GitHub scan."""
    if target_path.startswith("https://github.com/"):
        _execute_github_scan(target_path)
    else:
        _execute_scan(target_path)

def render_scan_controls_main():
    """Enterprise scan intake screen."""
    # Keep the intake centred and the three workflow cards on one action row.
    # The previous per-card 125px spacers made the page appear uneven and
    # pushed two primary actions far below the upload action.
    st.html(f"""
    <div style="max-width: 1080px; margin: 25px auto 35px auto; padding: 12px 8px;">
        <div style="color: {THEME['neon_blue']}; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1.8px; margin-bottom: 10px;">New assessment</div>
        <div style="color: #fff; font-size: 2.6rem; font-weight: 750; letter-spacing: -1.5px; line-height: 1.15;">Scan a codebase</div>
        <div style="color: {THEME['text_muted']}; font-size: 1.05rem; line-height: 1.6; max-width: 720px; margin-top: 12px;">
            Select a local directory, upload source files, or scan a public GitHub repository. ECDAT identifies cryptographic assets and migration priorities.
        </div>
    </div>
    """)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.html(f"""
        <div style="background: {THEME['bg_card']}; border: 1px solid {THEME['border_dim']}; border-radius: 14px; padding: 28px; height: 260px; box-sizing: border-box; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: {THEME['neon_blue']};"></div>
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                <div style="background: rgba(96, 165, 250, 0.1); width: 52px; height: 52px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: {THEME['neon_blue']}; font-size: 0.75rem; font-weight: 800; border: 1px solid rgba(96, 165, 250, 0.3);">LOCAL</div>
                <div style="color: #fff; font-weight: 750; font-size: 1.45rem; letter-spacing: -0.5px;">Local directory</div>
            </div>
            <p style="color: {THEME['text_muted']}; font-size: 0.95rem; line-height: 1.6; margin: 0;">
                Scan a local codebase to identify cryptographic algorithms and related risk.
            </p>
        </div>
        """)
        st.caption("Paste the folder you want to scan. Example: `demo_repos/1_legacy_fintech_core`")
        path = st.text_input("Local path", key="main_path_st", label_visibility="collapsed", placeholder="C:/projects/payment-service")
        st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)
        if st.button("Scan local directory", type="primary", width="stretch", key="btn_audit_local"):
            if path:
                _execute_scan(path)
            else:
                st.warning("Path required.")

    with col2:
        st.html(f"""
        <div style="background: {THEME['bg_card']}; border: 1px solid {THEME['border_dim']}; border-radius: 14px; padding: 28px; height: 260px; box-sizing: border-box; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: {THEME['neon_purple']};"></div>
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                <div style="background: rgba(129, 140, 248, 0.1); width: 52px; height: 52px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: {THEME['neon_purple']}; font-size: 0.75rem; font-weight: 800; border: 1px solid rgba(129, 140, 248, 0.3);">UPLOAD</div>
                <div style="color: #fff; font-weight: 750; font-size: 1.45rem; letter-spacing: -0.5px;">File upload</div>
            </div>
            <p style="color: {THEME['text_muted']}; font-size: 0.95rem; line-height: 1.6; margin: 0;">
                Upload source files or an archive for secure, isolated analysis.
            </p>
        </div>
        """)
        st.caption("Upload a ZIP or source files for an isolated scan.")
        files = st.file_uploader("Upload artifacts", accept_multiple_files=True, label_visibility="collapsed", key="main_uploader_st")
        st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)
        if st.button("Scan uploaded files", type="primary", width="stretch", disabled=not files, key="btn_audit_upload"):
            _execute_upload_scan(files)

    with col3:
        st.html(f"""
        <div style="background: {THEME['bg_card']}; border: 1px solid {THEME['border_dim']}; border-radius: 14px; padding: 28px; height: 260px; box-sizing: border-box; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: {THEME['neon_blue']};"></div>
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                <div style="background: rgba(96, 165, 250, 0.1); width: 52px; height: 52px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: {THEME['neon_blue']}; font-size: 0.75rem; font-weight: 800; border: 1px solid rgba(96, 165, 250, 0.3);">GITHUB</div>
                <div style="color: #fff; font-weight: 750; font-size: 1.45rem; letter-spacing: -0.5px;">GitHub repository</div>
            </div>
            <p style="color: {THEME['text_muted']}; font-size: 0.95rem; line-height: 1.6; margin: 0;">
                Clone and scan a public repository over HTTPS.
            </p>
        </div>
        """)
        repo_url = st.text_input(
            "GitHub repository URL",
            key="main_github_url",
            label_visibility="collapsed",
            placeholder="https://github.com/owner/repository",
        )
        st.caption("Private repositories are not supported in this release.")
        st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)
        if st.button("Scan GitHub repository", type="primary", width="stretch", key="btn_audit_github"):
            if repo_url:
                _execute_github_scan(repo_url)
            else:
                st.warning("Enter a public GitHub repository URL to continue.")

    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Try a sample repository")
    demo_left, demo_right = st.columns(2)
    with demo_left:
        if st.button("Try vulnerable fintech demo", width="stretch", key="demo_legacy"):
            _execute_scan("demo_repos/1_legacy_fintech_core")
    with demo_right:
        if st.button("Try quantum-ready demo", width="stretch", key="demo_quantum"):
            _execute_scan("demo_repos/3_quantum_ready_defense_app")
