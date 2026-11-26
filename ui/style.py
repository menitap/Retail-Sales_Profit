"""
UI Styling and Design Module - Retail Sales and Profitability Analysis.
Green / Brown / Beige earthy professional theme.
Supports Dark (default) and Light mode toggling.
Zero-scroll viewport enforced. Full dropdown visibility fix applied globally.
"""

import streamlit as st

# ─── Earthy Color Palette (used in Python-side chart calls) ───────────────────
PRIMARY_COLOR   = "#3D7A5A"   # Forest green
SECONDARY_COLOR = "#5C8C6E"   # Sage green
ACCENT_COLOR    = "#8B6914"   # Warm golden-brown
WARNING_COLOR   = "#A0522D"   # Sienna / muted terracotta
DANGER_COLOR    = "#8B3A3A"   # Muted crimson-brown
DARK_BG         = "#1A2318"   # Very dark forest green
CARD_BG         = "#243020"   # Dark green-brown card
BORDER_COLOR    = "#3A4A36"   # Muted green border
TEXT_MUTED      = "#A8B89E"   # Sage muted text
TEXT_LIGHT      = "#F0EBD8"   # Warm cream/beige

__all__ = [
    "PRIMARY_COLOR", "SECONDARY_COLOR", "ACCENT_COLOR",
    "WARNING_COLOR", "DANGER_COLOR", "DARK_BG", "CARD_BG",
    "BORDER_COLOR", "TEXT_MUTED", "TEXT_LIGHT",
    "apply_custom_css", "render_page_header", "render_kpi_card",
    "render_insight_box", "render_section_title", "get_plotly_layout",
    "is_light_mode",
]


def is_light_mode():
    """Returns True if the user has toggled light mode."""
    return st.session_state.get("theme_mode", "dark") == "light"


def apply_custom_css():
    """
    Inject earthy Green/Brown/Beige theme CSS.
    Fixes dropdown/popover visibility globally.
    Enforces zero-scroll viewport.
    """
    light = is_light_mode()

    # ── Token maps ────────────────────────────────────────────────────────────
    if light:
        # Light: warm beige / cream background, dark-brown text, forest-green accents
        bg_main            = "#F5F0E8"   # warm linen
        bg_secondary       = "#EDE8DC"   # slightly darker linen
        bg_card_1          = "#FDFAF4"   # near-white cream
        bg_card_2          = "#F5F0E8"   # linen
        border_col         = "#C8BFA8"   # warm tan border
        text_primary       = "#2C1A0E"   # very dark brown
        text_secondary     = "#4A3728"   # dark brown
        text_muted         = "#7A6B58"   # medium brown-gray
        text_kpi_value     = "#1A0F05"   # richest brown
        text_kpi_title     = "#5C4033"   # medium-dark brown
        nav_bg             = "#E8E0CF"   # tan nav bar
        nav_pill_active    = "linear-gradient(135deg, #3D7A5A, #2D5E42)"
        nav_pill_text      = "#4A3728"
        nav_pill_act_text  = "#FDFAF4"
        nav_hover_bg       = "rgba(61,122,90,0.12)"
        nav_hover_text     = "#2D5E42"
        insight_bg         = "linear-gradient(90deg, rgba(253,250,244,0.98), rgba(237,232,220,0.98))"
        insight_border_def = "#8B6914"
        code_bg            = "#E8E0CF"
        code_color         = "#2D5E42"
        sidebar_bg         = "#EDE8DC"
        sidebar_border     = "#C8BFA8"
        # Dropdown / popover
        input_bg           = "#FDFAF4"
        input_border       = "#A89880"
        input_text         = "#2C1A0E"
        select_arrow       = "#4A3728"
        popover_bg         = "#FDFAF4"
        popover_border     = "#C8BFA8"
        popover_text       = "#2C1A0E"
        popover_hover_bg   = "#DCF0E5"   # light sage green
        popover_hover_text = "#1A4A32"
        popover_sel_bg     = "#3D7A5A"
        popover_sel_text   = "#FDFAF4"
        tab_text           = "#5C4033"
        tab_active         = "#3D7A5A"
        caption_color      = "#7A6B58"
        grid_color         = "#DCE0D4"
        shadow_alpha       = "0.08"
        btn_bg             = "#EDE8DC"
        btn_text           = "#2C1A0E"
        section_border     = "rgba(200,191,168,0.6)"
        title_banner_brd   = "rgba(200,191,168,0.5)"
    else:
        # Dark: deep forest green background, cream text, sage/brown accents
        bg_main            = "#141C12"   # deepest forest
        bg_secondary       = "#1A2318"   # dark forest green
        bg_card_1          = "#1F2B1C"   # dark card
        bg_card_2          = "#192116"   # slightly darker card
        border_col         = "#354A30"   # dark sage border
        text_primary       = "#F0EBD8"   # warm cream
        text_secondary     = "#D8D0BA"   # lighter cream
        text_muted         = "#8A9E82"   # sage muted
        text_kpi_value     = "#F8F4EC"   # brightest cream
        text_kpi_title     = "#B8C8A8"   # sage label
        nav_bg             = "#0F1710"   # very dark nav
        nav_pill_active    = "linear-gradient(135deg, #3D7A5A, #2D5E42)"
        nav_pill_text      = "#A8B89E"
        nav_pill_act_text  = "#F0EBD8"
        nav_hover_bg       = "rgba(61,122,90,0.2)"
        nav_hover_text     = "#90C8A0"
        insight_bg         = "linear-gradient(90deg, rgba(31,43,28,0.98), rgba(25,33,22,0.98))"
        insight_border_def = "#8B6914"
        code_bg            = "#1F2B1C"
        code_color         = "#78C8A0"
        sidebar_bg         = "#141C12"
        sidebar_border     = "#1F2B1C"
        # Dropdown / popover
        input_bg           = "#1F2B1C"
        input_border       = "#4A6040"
        input_text         = "#F0EBD8"
        select_arrow       = "#8A9E82"
        popover_bg         = "#243020"   # dark green surface — key fix
        popover_border     = "#3A4A36"
        popover_text       = "#F0EBD8"
        popover_hover_bg   = "#2D4228"
        popover_hover_text = "#C8E8B8"
        popover_sel_bg     = "#3D7A5A"
        popover_sel_text   = "#F0EBD8"
        tab_text           = "#8A9E82"
        tab_active         = "#78C8A0"
        caption_color      = "#8A9E82"
        grid_color         = "#243020"
        shadow_alpha       = "0.4"
        btn_bg             = "#1F2B1C"
        btn_text           = "#D8D0BA"
        section_border     = "rgba(53,74,48,0.7)"
        title_banner_brd   = "rgba(53,74,48,0.6)"

    css = f"""
<style>
/* ═══════════════════════════════════════════════════════════
   FONTS
═══════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ═══════════════════════════════════════════════════════════
   CLEAN VIEWPORT STYLING (NO OVERFLOW HIDDEN LOCKDOWN)
   Allows normal rendering while layout compactness ensures
   the entire page fits cleanly in the viewport without scrolling.
═══════════════════════════════════════════════════════════ */
html, body {{
    margin: 0 !important;
    padding: 0 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    background-color: {bg_main} !important;
    color: {text_primary} !important;
}}

[data-testid="stAppViewContainer"] {{
    background-color: {bg_main} !important;
    color: {text_primary} !important;
}}

.main {{
    background-color: {bg_main} !important;
    color: {text_primary} !important;
}}

/* ═══════════════════════════════════════════════════════════
   GLOBAL TEXT — earthy defaults, not transparent
═══════════════════════════════════════════════════════════ */
p, h1, h2, h3, h4, h5, h6 {{
    color: {text_primary};
}}
.stMarkdown, .stText, [data-testid="stMarkdownContainer"] p {{
    color: {text_secondary} !important;
}}
[data-testid="stCaptionContainer"] p,
.stCaption p {{
    color: {caption_color} !important;
}}

/* ═══════════════════════════════════════════════════════════
   MAIN CONTAINER PADDING — tight to prevent page overflow
═══════════════════════════════════════════════════════════ */
.block-container {{
    padding-top: 0.15rem !important;
    padding-bottom: 0.2rem !important;
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
    max-width: 100% !important;
}}

/* ═══════════════════════════════════════════════════════════
   STREAMLIT HEADER & SIDEBAR TOGGLE
   Keep the header minimal and transparent; keep sidebar toggle
   visible and functional.
═══════════════════════════════════════════════════════════ */
header[data-testid="stHeader"] {{
    background: transparent !important;
    height: 1.8rem !important;
    min-height: 1.8rem !important;
    padding: 0 0.5rem !important;
    z-index: 99 !important;
}}
[data-testid="stToolbar"] {{
    display: none !important;
}}
[data-testid="collapsedControl"] {{
    display: block !important;
    visibility: visible !important;
    color: {text_primary} !important;
}}

/* ═══════════════════════════════════════════════════════════
   VERTICAL / HORIZONTAL BLOCK SPACING — compact gaps
═══════════════════════════════════════════════════════════ */
div[data-testid="stVerticalBlock"] {{
    gap: 0.22rem !important;
}}
div[data-testid="stVerticalBlock"] > div {{
    margin-bottom: 0.04rem !important;
}}
div[data-testid="stHorizontalBlock"] {{
    gap: 0.35rem !important;
    align-items: stretch !important;
}}
div[data-testid="stElementContainer"] {{
    margin-bottom: 0 !important;
}}

/* ═══════════════════════════════════════════════════════════
   HORIZONTAL NAV — pill style
═══════════════════════════════════════════════════════════ */
div[data-testid="stRadio"] > div[role="radiogroup"] {{
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 0.12rem !important;
    background: {nav_bg} !important;
    border: 1px solid {border_col} !important;
    border-radius: 6px !important;
    padding: 0.1rem 0.15rem !important;
    align-items: center !important;
    overflow-x: auto !important;
}}
div[data-testid="stRadio"] > div[role="radiogroup"] label {{
    background: transparent !important;
    border-radius: 5px !important;
    padding: 0.16rem 0.5rem !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    color: {nav_pill_text} !important;
    font-size: 0.73rem !important;
    font-weight: 600 !important;
    border: none !important;
    white-space: nowrap !important;
}}
div[data-testid="stRadio"] > div[role="radiogroup"] label:hover {{
    color: {nav_hover_text} !important;
    background: {nav_hover_bg} !important;
}}
div[data-testid="stRadio"] > div[role="radiogroup"] label[data-checked="true"],
div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) {{
    background: {nav_pill_active} !important;
    color: {nav_pill_act_text} !important;
    box-shadow: 0 2px 6px rgba(45,94,66,0.4) !important;
}}
div[data-testid="stRadio"] > div[role="radiogroup"] label[data-checked="true"] p,
div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) p {{
    color: {nav_pill_act_text} !important;
    font-weight: 700 !important;
}}
/* Hide radio dots */
div[data-testid="stRadio"] > div[role="radiogroup"] label div:first-child {{
    display: none !important;
}}

/* ═══════════════════════════════════════════════════════════
   PAGE TITLE BANNER
═══════════════════════════════════════════════════════════ */
.page-title-banner {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 0.18rem;
    padding-bottom: 0.1rem;
    border-bottom: 1px solid {title_banner_brd};
}}
.page-title-text {{
    font-size: 0.92rem;
    font-weight: 800;
    color: {text_primary};
    letter-spacing: -0.01em;
}}
.page-subtitle-text {{
    font-size: 0.68rem;
    color: {text_muted};
    margin-left: 0.4rem;
}}

/* ═══════════════════════════════════════════════════════════
   SECTION HEADERS
═══════════════════════════════════════════════════════════ */
.section-header {{
    font-size: 0.76rem;
    font-weight: 700;
    color: {text_primary};
    margin-top: 0.15rem;
    margin-bottom: 0.12rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    border-bottom: 1px solid {section_border};
    padding-bottom: 0.08rem;
}}

/* ═══════════════════════════════════════════════════════════
   KPI CARDS
═══════════════════════════════════════════════════════════ */
.kpi-card {{
    background: linear-gradient(145deg, {bg_card_1}, {bg_card_2});
    border: 1px solid {border_col};
    border-radius: 7px;
    padding: 0.32rem 0.55rem;
    box-shadow: 0 1px 6px rgba(0,0,0,{shadow_alpha});
    position: relative;
    overflow: hidden;
}}
.kpi-card-glow-green  {{ border-left: 3px solid #3D7A5A; }}
.kpi-card-glow-sage   {{ border-left: 3px solid #5C8C6E; }}
.kpi-card-glow-brown  {{ border-left: 3px solid #8B6914; }}
.kpi-card-glow-terra  {{ border-left: 3px solid #A0522D; }}
.kpi-card-glow-muted  {{ border-left: 3px solid #8B3A3A; }}
/* Keep legacy color names working */
.kpi-card-glow-blue   {{ border-left: 3px solid #4A8A7A; }}
.kpi-card-glow-purple {{ border-left: 3px solid #8B6914; }}
.kpi-card-glow-amber  {{ border-left: 3px solid #A0522D; }}
.kpi-card-glow-rose   {{ border-left: 3px solid #8B3A3A; }}

.kpi-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.06rem;
}}
.kpi-title {{
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: {text_kpi_title};
    font-weight: 700;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.kpi-icon {{
    font-size: 0.8rem;
    opacity: 0.9;
}}
.kpi-value {{
    font-size: 1.05rem;
    font-weight: 800;
    color: {text_kpi_value};
    line-height: 1.1;
    margin-bottom: 0.04rem;
    white-space: nowrap;
}}
.kpi-subtext {{
    font-size: 0.6rem;
    color: {text_muted};
    display: flex;
    align-items: center;
    gap: 0.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* ═══════════════════════════════════════════════════════════
   INSIGHT / STRATEGY BOX
═══════════════════════════════════════════════════════════ */
.insight-card {{
    background: {insight_bg};
    border: 1px solid {border_col};
    border-left: 3px solid {insight_border_def};
    border-radius: 6px;
    padding: 0.25rem 0.55rem;
    margin-top: 0.12rem;
    margin-bottom: 0.06rem;
}}
.insight-title {{
    font-size: 0.7rem;
    font-weight: 800;
    color: {text_primary};
    margin-bottom: 0.04rem;
    display: flex;
    align-items: center;
    gap: 0.2rem;
}}
.insight-desc {{
    font-size: 0.66rem;
    color: {text_secondary};
    line-height: 1.3;
    margin: 0;
}}

/* ═══════════════════════════════════════════════════════════
   FORM LABELS
═══════════════════════════════════════════════════════════ */
.stSelectbox label, .stSlider label, .stMultiSelect label {{
    font-size: 0.68rem !important;
    margin-bottom: 0.02rem !important;
    font-weight: 700 !important;
    color: {text_secondary} !important;
}}

/* ═══════════════════════════════════════════════════════════
   GLOBAL DROPDOWN / SELECTBOX FIX
   Root cause: Streamlit uses BaseWeb components rendered in
   a <div data-baseweb="popover"> that floats OUTSIDE the main
   container. Without explicit background/color rules on the
   popover tree and listbox items, they inherit the page
   background (dark/light) and text becomes invisible.
   Solution: Explicitly set bg + text on EVERY level of the
   popover/menu/listbox subtree so options are always readable.
═══════════════════════════════════════════════════════════ */

/* ── Selected-value trigger box ── */
div[data-baseweb="select"] {{
    font-size: 0.78rem !important;
}}
div[data-baseweb="select"] > div:first-child {{
    background-color: {input_bg} !important;
    border-color: {input_border} !important;
    border-radius: 6px !important;
    color: {input_text} !important;
}}
div[data-baseweb="select"] > div:first-child > div,
div[data-baseweb="select"] > div:first-child span,
div[data-baseweb="select"] > div:first-child p {{
    color: {input_text} !important;
    background-color: transparent !important;
}}
div[data-baseweb="select"] svg {{
    fill: {select_arrow} !important;
    color: {select_arrow} !important;
}}

/* ── Popover wrapper (floats at root, outside main DOM) ── */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] > div > div {{
    background-color: {popover_bg} !important;
    border: 1px solid {popover_border} !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,{shadow_alpha}) !important;
}}

/* ── Menu container ── */
div[data-baseweb="menu"] {{
    background-color: {popover_bg} !important;
    border-radius: 8px !important;
    padding: 0.2rem 0 !important;
}}
div[data-baseweb="menu"] > ul,
ul[role="listbox"] {{
    background-color: {popover_bg} !important;
    padding: 0 !important;
    margin: 0 !important;
}}

/* ── Every list item (option) ── */
div[data-baseweb="menu"] li,
ul[role="listbox"] > li,
li[role="option"] {{
    background-color: {popover_bg} !important;
    color: {popover_text} !important;
    font-size: 0.78rem !important;
    padding: 0.42rem 0.75rem !important;
    cursor: pointer !important;
}}
/* Make all child spans/divs inside an option inherit the right color */
li[role="option"] *,
div[data-baseweb="menu"] li * {{
    color: {popover_text} !important;
    background-color: transparent !important;
}}

/* ── Hover state ── */
div[data-baseweb="menu"] li:hover,
ul[role="listbox"] > li:hover,
li[role="option"]:hover {{
    background-color: {popover_hover_bg} !important;
    color: {popover_hover_text} !important;
}}
li[role="option"]:hover * {{
    color: {popover_hover_text} !important;
}}

/* ── Selected/active option ── */
li[role="option"][aria-selected="true"],
div[data-baseweb="menu"] li[aria-selected="true"] {{
    background-color: {popover_sel_bg} !important;
    color: {popover_sel_text} !important;
    font-weight: 700 !important;
}}
li[role="option"][aria-selected="true"] *,
div[data-baseweb="menu"] li[aria-selected="true"] * {{
    color: {popover_sel_text} !important;
    background-color: transparent !important;
}}

/* ── Highlighted/focused option (keyboard nav) ── */
li[role="option"][data-highlighted="true"] {{
    background-color: {popover_hover_bg} !important;
    color: {popover_hover_text} !important;
}}

/* ── Selectbox element spacing ── */
div[data-testid="stSelectbox"],
div[data-testid="stMultiSelect"] {{
    margin-bottom: 0.18rem !important;
}}
div[data-testid="stSlider"] {{
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    margin-bottom: 0.18rem !important;
}}

/* ═══════════════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════════════ */
button[data-baseweb="tab"] {{
    padding: 0.2rem 0.6rem !important;
    font-size: 0.74rem !important;
    color: {tab_text} !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {tab_active} !important;
    font-weight: 700 !important;
    border-bottom-color: {tab_active} !important;
}}
div[data-baseweb="tab-highlight"] {{
    background-color: {tab_active} !important;
}}

/* ═══════════════════════════════════════════════════════════
   DATAFRAMES / TABLES
═══════════════════════════════════════════════════════════ */
div[data-testid="stDataFrame"] {{
    margin-bottom: 0.08rem !important;
}}

/* ═══════════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background-color: {sidebar_bg} !important;
    border-right: 1px solid {sidebar_border} !important;
}}

/* ═══════════════════════════════════════════════════════════
   CODE BLOCKS
═══════════════════════════════════════════════════════════ */
code {{
    font-family: 'JetBrains Mono', monospace !important;
    background-color: {code_bg} !important;
    padding: 0.1rem 0.25rem !important;
    border-radius: 4px !important;
    font-size: 0.7rem !important;
    color: {code_color} !important;
}}

/* ═══════════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════════ */
div[data-testid="stDownloadButton"] button,
button[kind="secondary"] {{
    background-color: {btn_bg} !important;
    color: {btn_text} !important;
    border: 1px solid {border_col} !important;
    border-radius: 6px !important;
}}
button[kind="primary"] {{
    background-color: #3D7A5A !important;
    color: #F0EBD8 !important;
    border: 1px solid #2D5E42 !important;
    border-radius: 6px !important;
}}

/* ═══════════════════════════════════════════════════════════
   ALERTS
═══════════════════════════════════════════════════════════ */
div[data-testid="stAlert"] {{
    background-color: {bg_card_1} !important;
    color: {text_primary} !important;
    border-color: {border_col} !important;
}}

/* ═══════════════════════════════════════════════════════════
   SLIDER THUMB COLOR
═══════════════════════════════════════════════════════════ */
div[data-testid="stSlider"] > div > div > div {{
    color: {text_primary} !important;
}}

/* ═══════════════════════════════════════════════════════════
   SPINNER OVERRIDE
═══════════════════════════════════════════════════════════ */
div[data-testid="stSpinner"] p {{
    color: {text_muted} !important;
}}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


def render_page_header(title, subtitle=None):
    """Renders a unified top page title with optional subtitle."""
    sub_html = f"<span class='page-subtitle-text'>— {subtitle}</span>" if subtitle else ""
    st.markdown(
        f"""<div class="page-title-banner"><div>
<span class="page-title-text">{title}</span>{sub_html}
</div></div>""",
        unsafe_allow_html=True,
    )


def render_kpi_card(title, value, subtitle=None, icon="📊", glow_color="green"):
    """Renders a styled KPI card using earthy theme classes."""
    valid = ["green", "sage", "brown", "terra", "muted", "blue", "purple", "amber", "rose"]
    glow_class = f"kpi-card-glow-{glow_color if glow_color in valid else 'green'}"
    sub_html = f"<div class='kpi-subtext'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""<div class="kpi-card {glow_class}">
<div class="kpi-header"><span class="kpi-title">{title}</span><span class="kpi-icon">{icon}</span></div>
<div class="kpi-value">{value}</div>{sub_html}
</div>""",
        unsafe_allow_html=True,
    )


def render_insight_box(title, message, icon="💡", border_color=None):
    """Renders a strategy/insight callout card."""
    if border_color is None:
        border_color = "#8B6914"
    st.markdown(
        f"""<div class="insight-card" style="border-left-color:{border_color};">
<div class="insight-title">{icon} {title}</div>
<div class="insight-desc">{message}</div>
</div>""",
        unsafe_allow_html=True,
    )


def render_section_title(title, icon="▸"):
    """Renders a compact section header."""
    st.markdown(
        f"""<div class="section-header"><span>{icon}</span><span>{title}</span></div>""",
        unsafe_allow_html=True,
    )


def get_plotly_layout(height=215, title="", showlegend=True):
    """
    Returns a Plotly layout dict using earthy Green/Brown/Beige palette.
    Adapts to light/dark theme.
    """
    light = is_light_mode()

    if light:
        paper_bg       = "rgba(0,0,0,0)"
        plot_bg        = "rgba(0,0,0,0)"
        font_color     = "#7A6B58"
        title_color    = "#2C1A0E"
        tick_color     = "#7A6B58"
        legend_color   = "#4A3728"
        grid_col       = "#DCE0D4"
        zeroline_col   = "#C8BFA8"
        hover_bg       = "#FDFAF4"
        hover_border   = "#C8BFA8"
        hover_fc       = "#2C1A0E"
    else:
        paper_bg       = "rgba(0,0,0,0)"
        plot_bg        = "rgba(0,0,0,0)"
        font_color     = "#8A9E82"
        title_color    = "#F0EBD8"
        tick_color     = "#8A9E82"
        legend_color   = "#B8C8A8"
        grid_col       = "#1F2B1C"
        zeroline_col   = "#354A30"
        hover_bg       = "#1F2B1C"
        hover_border   = "#4A6040"
        hover_fc       = "#F0EBD8"

    return {
        "title": {
            "text": title,
            "font": {"size": 10, "color": title_color, "family": "Inter", "weight": "bold"},
            "x": 0.02,
            "y": 0.98,
        },
        "height": height,
        "margin": dict(l=28, r=14, t=22, b=18),
        "paper_bgcolor": paper_bg,
        "plot_bgcolor": plot_bg,
        "font": {"family": "Inter", "color": font_color, "size": 8.5},
        "showlegend": showlegend,
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 8, "color": legend_color},
        },
        "xaxis": {
            "gridcolor": grid_col,
            "zerolinecolor": zeroline_col,
            "showgrid": True,
            "tickfont": {"color": tick_color, "size": 8},
        },
        "yaxis": {
            "gridcolor": grid_col,
            "zerolinecolor": zeroline_col,
            "showgrid": True,
            "tickfont": {"color": tick_color, "size": 8},
        },
        "hoverlabel": {
            "bgcolor": hover_bg,
            "bordercolor": hover_border,
            "font": {"family": "Inter", "size": 10.5, "color": hover_fc},
        },
        "colorway": [
            "#3D7A5A", "#8B6914", "#5C8C6E", "#A0522D",
            "#78A898", "#C8A878", "#8B3A3A", "#6B8C6B",
        ],
    }
