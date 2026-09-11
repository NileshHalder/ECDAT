"""ECDAT design system — restrained enterprise security workspace."""

# ─── Color Palette ────────────────────────────────────────────────
THEME = {
    "bg_void":      "#0B1220",
    "bg_app":       "#111827",
    "bg_sidebar":   "#0F172A",
    "bg_card":      "#172033",
    "bg_card_hover":"#1E293B",
    "bg_glass":     "rgba(23, 32, 51, 0.94)",
    
    "border_dim":   "#334155",
    "border_glow":  "rgba(96, 165, 250, 0.35)",
    "border_active":"#3B82F6",
    
    "text_hero":    "#FFFFFF",
    "text_main":    "#E2E8F0",
    # Secondary copy must remain readable on the dark command-center surface.
    "text_muted":   "#94A3B8",
    "text_dim":     "#64748B",
    
    "neon_blue":    "#60A5FA",
    "neon_purple":  "#818CF8",
    "neon_pink":    "#C084FC",
    "neon_orange":  "#FBBF24",
    "neon_green":   "#4ADE80",
    "neon_red":     "#F87171",
    
    "critical":     "#F87171",
    "high":         "#FB923C",
    "medium":       "#FBBF24",
    "low":          "#4ADE80",
    "info":         "#60A5FA",

    "font_ui":        "Inter, ui-sans-serif, system-ui, sans-serif",
    "font_fam":       "ui-monospace, SFMono-Regular, Consolas, monospace",
}

RISK_COLORS = {
    "safe":       "#00FF66",
    "partial":    "#FFD600",
    "vulnerable": "#FF8A00",
    "critical":   "#FF3D00",
}

def inject_css():
    """Inject Global CSS - The 'Nova' Command Center Theme."""
    import streamlit as st

    st.markdown(f"""
<style>
/* GLOBAL RESETS */
:root {{
    --bg-void: {THEME['bg_void']};
    --bg-app: {THEME['bg_app']};
    --bg-card: {THEME['bg_card']};
    --border: {THEME['border_dim']};
    --neon-blue: {THEME['neon_blue']};
    --neon-purple: {THEME['neon_purple']};
}}

html, body, [data-testid="stApp"] {{
    background-color: var(--bg-void) !important;
    color: {THEME['text_main']} !important;
    font-family: {THEME['font_ui']} !important;
}}

.stApp {{
    background: var(--bg-void) !important;
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background-color: {THEME['bg_sidebar']} !important;
    border-right: 1px solid var(--border) !important;
}}

/* CARDS & CONTAINERS */
div.stVerticalBlockBorderWrapper {{
    border: 1px solid var(--border) !important;
    background: {THEME['bg_glass']} !important;
    border-radius: 16px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}}

div.stVerticalBlockBorderWrapper:hover {{
    border-color: {THEME['border_glow']} !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}}

/* BUTTONS */
.stButton > button {{
    background: #2563EB !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.1rem !important;
    font-weight: 700 !important;
    box-shadow: none !important;
    transition: background 0.15s ease !important;
}}

.stButton > button:hover {{
    transform: none !important;
    background: #1D4ED8 !important;
}}

/* ANIMATIONS */
@keyframes status-pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(0, 255, 102, 0.4); }}
    70% {{ box-shadow: 0 0 0 10px rgba(0, 255, 102, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(0, 255, 102, 0); }}
}}

@keyframes nova-glow {{
    0% {{ opacity: 0.8; filter: brightness(1); }}
    50% {{ opacity: 1; filter: brightness(1.3); }}
    100% {{ opacity: 0.8; filter: brightness(1); }}
}}

@keyframes scanner-line {{
    0% {{ top: 0%; }}
    100% {{ top: 100%; }}
}}

.nova-status-online {{
    animation: none;
}}

.nova-glow-text {{
    animation: none;
}}

.nova-card-glow {{
    position: relative;
}}
.nova-card-glow::after {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    border-radius: 16px;
    box-shadow: none;
    pointer-events: none;
}}

/* CUSTOM BADGES */
.vg-badge {{
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.65rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.vg-badge-safe {{ background: rgba(0,255,102,0.1); color: #00FF66; border: 1px solid rgba(0,255,102,0.2); }}
.vg-badge-critical {{ background: rgba(255,61,0,0.1); color: #FF3D00; border: 1px solid rgba(255,61,0,0.2); }}

/* TREE BOX */
.tree-box {{
    background: #0F172A;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-muted);
    font-size: 0.8rem;
    overflow-x: auto;
}}
</style>
""", unsafe_allow_html=True)

def ec_badge(text: str, type: str = "safe"):
    """Render a themed badge."""
    import streamlit as st
    badge_class = "vg-badge-safe" if type == "safe" else "vg-badge-critical"
    st.markdown(f'<span class="vg-badge {badge_class}">{text}</span>', unsafe_allow_html=True)

def raw_html(html: str):
    """Render a multi-line HTML snippet as a single markdown HTML block.

    A blank line inside the composed string closes the markdown HTML block and
    turns the following indented lines into a literal code block, so blank and
    whitespace-only lines are dropped here.
    """
    import streamlit as st
    st.markdown("\n".join(line for line in html.splitlines() if line.strip()), unsafe_allow_html=True)

def nova_kpi(label: str, value: str, icon: str = "", color: str = "#60A5FA"):
    """Render a compact enterprise KPI card."""
    import streamlit as st
    st.markdown(f"""
    <div style="background: {THEME['bg_card']}; border: 1px solid {THEME['border_dim']}; border-radius: 16px; padding: 20px; margin-bottom: 10px; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: {color};"></div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="color: {THEME['text_muted']}; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">{label}</div>
                <div style="color: #fff; font-size: 2rem; font-weight: 800; margin-top: 5px;">{value}</div>
            </div>
            <div style="width: 8px; height: 8px; margin-top: 5px; border-radius: 50%; background: {color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_semi_gauge_svg(score: float, max_score: float = 100.0) -> str:
    """SVG Gauge for risk scoring."""
    pct = max(0.0, min(100.0, (score / max_score) * 100.0))
    half_circ = 251.327
    offset = half_circ * (1.0 - (pct / 100.0))
    arc_color = THEME["neon_green"] if pct >= 75 else (THEME["neon_blue"] if pct >= 50 else THEME["neon_red"])

    return f'''
    <svg viewBox="0 0 220 120" style="width:100%; max-width:200px; height:auto; display: block; margin: auto;">
        <path d="M 30 100 A 80 80 0 0 1 190 100" fill="none" stroke="#161D2E" stroke-width="14" stroke-linecap="round" />
        <path d="M 30 100 A 80 80 0 0 1 190 100" fill="none" stroke="{arc_color}" stroke-width="14" stroke-linecap="round"
              stroke-dasharray="{half_circ}" stroke-dashoffset="{offset}" />
        <text x="110" y="85" text-anchor="middle" font-family="Plus Jakarta Sans" font-size="32" font-weight="800" fill="#FFFFFF">{score:.0f}%</text>
        <text x="110" y="105" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="10" font-weight="400" fill="#FFFFFF">QUANTUM READINESS</text>
    </svg>
    '''
