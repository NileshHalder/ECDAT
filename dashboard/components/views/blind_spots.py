"""
Blind Spots & Risk View.
"""
from typing import Any

import streamlit as st

from ..theme import THEME, nova_kpi, raw_html


def render_blind_spots_and_risk(results: dict[str, Any]):
    st.markdown(f"""
        <div style="margin-bottom: 30px;">
            <div style="color: {THEME['text_muted']}; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">Exposure Analysis</div>
            <div style="color: #fff; font-size: 2.2rem; font-weight: 800; letter-spacing: -1.5px; margin-top: 5px;">Blind Spots <span style="color: {THEME['neon_orange']}">& Risk</span></div>
        </div>
    """, unsafe_allow_html=True)

    # ─── TOP METRICS ───
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        nova_kpi("Blind Spots", "12", "👁️", THEME["neon_orange"])
    with k2:
        nova_kpi("Coverage Gap", "18%", "📉", THEME["neon_red"])
    with k3:
        nova_kpi("Shadow Crypto", "4", "👻", THEME["neon_purple"])
    with k4:
        nova_kpi("Risk Density", "High", "☣️", THEME["neon_red"])

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Hardware & Cloud Gaps</div>', unsafe_allow_html=True)
        with st.container(border=True):
            raw_html(f"""
            <div style="margin-bottom:20px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <span style="color:#fff; font-size:0.85rem; font-weight:600;">HSM (Thales/nShield)</span>
                    <span style="color:{THEME['neon_orange']}; font-size:0.85rem; font-weight:700;">41% Covered</span>
                </div>
                <div style="height:6px; background:rgba(255,255,255,0.05); border-radius:3px;">
                    <div style="width:41%; height:100%; background:{THEME['neon_orange']}; border-radius:3px; box-shadow:0 0 10px {THEME['neon_orange']}44;"></div>
                </div>
            </div>

            <div style="margin-bottom:20px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <span style="color:#fff; font-size:0.85rem; font-weight:600;">Embedded Firmware</span>
                    <span style="color:{THEME['neon_red']}; font-size:0.85rem; font-weight:700;">23% Covered</span>
                </div>
                <div style="height:6px; background:rgba(255,255,255,0.05); border-radius:3px;">
                    <div style="width:23%; height:100%; background:{THEME['neon_red']}; border-radius:3px; box-shadow:0 0 10px {THEME['neon_red']}44;"></div>
                </div>
            </div>

            <div style="margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <span style="color:#fff; font-size:0.85rem; font-weight:600;">AWS CloudHSM</span>
                    <span style="color:{THEME['neon_green']}; font-size:0.85rem; font-weight:700;">92% Covered</span>
                </div>
                <div style="height:6px; background:rgba(255,255,255,0.05); border-radius:3px;">
                    <div style="width:92%; height:100%; background:{THEME['neon_green']}; border-radius:3px; box-shadow:0 0 10px {THEME['neon_green']}44;"></div>
                </div>
            </div>
            """)

    with col2:
        st.markdown('<div style="color:#fff;font-weight:700;font-size:1rem;margin-bottom:15px;text-transform:uppercase;letter-spacing:1px;">Critical Risk Concentrations</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.error("Legacy TLS 1.0/1.1 detected in 4 network endpoints.")
            st.error("Hardcoded AES keys found in 3 source files.")
            st.warning("Expired certificates found in 'production/ingress' gateway.")
            st.info("Unsigned binaries detected in CI/CD pipeline artifact store.")
