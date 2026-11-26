"""
Home Landing Page — Retail Sales & Profitability Analysis.
Earthy Green / Brown / Beige theme.
Animated shopping cart hero (larger, slower).
Zero-scroll single-viewport layout.
"""

import streamlit as st
from ui.style import render_kpi_card


# ── Earthy theme palette helpers ──────────────────────────────────────────────
def _t(light, lv, dv):
    return lv if light else dv


def _hero_html(light, total_records, total_sales, total_profit):
    # Dark earthy
    if light:
        hero_bg       = "linear-gradient(135deg, rgba(245,240,232,0.97) 0%, rgba(237,232,220,0.90) 100%)"
        hero_brd      = "#C8BFA8"
        title_grad    = "linear-gradient(90deg, #2D5E42 0%, #8B6914 60%, #A0522D 100%)"
        badge_bg      = "rgba(61,122,90,0.12)"
        badge_col     = "#2D5E42"
        badge_brd     = "#3D7A5A"
        desc_col      = "#4A3728"
        stat_bg       = "rgba(253,250,244,0.9)"
        stat_brd      = "#C8BFA8"
        stat_lbl      = "#7A6B58"
        stat_ok_col   = "#3D7A5A"
        stat_data_col = "#8B6914"
        track_bg      = "linear-gradient(90deg,rgba(237,232,220,0.6) 0%,rgba(61,122,90,0.08) 50%,rgba(139,105,20,0.06) 100%)"
        track_brd     = "rgba(200,191,168,0.5)"
        dash_col      = "#3D7A5A"
        cart_body     = "#2D5E42"
        bar1          = "#3D7A5A"
        bar2          = "#8B6914"
        bar3          = "#A0522D"
        bar4          = "#5C8C6E"
        wheel_fill    = "#F5F0E8"
        wstroke1      = "#2D5E42"
        wstroke2      = "#8B6914"
        trail_grad    = "linear-gradient(270deg,rgba(61,122,90,0.7),rgba(139,105,20,0.3),transparent)"
        shadow        = "0.06"
    else:
        hero_bg       = "linear-gradient(135deg, rgba(20,28,18,0.97) 0%, rgba(31,43,28,0.90) 100%)"
        hero_brd      = "#354A30"
        title_grad    = "linear-gradient(90deg, #78C8A0 0%, #C8A050 55%, #E09070 100%)"
        badge_bg      = "rgba(61,122,90,0.18)"
        badge_col     = "#90C8A0"
        badge_brd     = "#3D7A5A"
        desc_col      = "#B8C8A8"
        stat_bg       = "rgba(15,22,12,0.75)"
        stat_brd      = "#354A30"
        stat_lbl      = "#8A9E82"
        stat_ok_col   = "#78C8A0"
        stat_data_col = "#C8A050"
        track_bg      = "linear-gradient(90deg,rgba(31,43,28,0.7) 0%,rgba(61,122,90,0.14) 50%,rgba(139,105,20,0.10) 100%)"
        track_brd     = "rgba(53,74,48,0.5)"
        dash_col      = "#3D7A5A"
        cart_body     = "#90C8A0"
        bar1          = "#78C8A0"
        bar2          = "#C8A050"
        bar3          = "#E09070"
        bar4          = "#8AB898"
        wheel_fill    = "#1F2B1C"
        wstroke1      = "#90C8A0"
        wstroke2      = "#C8A050"
        trail_grad    = "linear-gradient(270deg,rgba(78,180,120,0.9),rgba(200,160,80,0.4),transparent)"
        shadow        = "0.35"

    return f"""<div style="background:{hero_bg};border:1px solid {hero_brd};border-radius:10px;padding:0.45rem 0.85rem 0.3rem 0.85rem;margin-bottom:0.22rem;position:relative;overflow:hidden;box-shadow:0 3px 14px rgba(0,0,0,{shadow});">
<style>
@keyframes cartDrive {{
  0%   {{ transform:translateX(-130px); opacity:0.15; }}
  6%   {{ opacity:1; }}
  91%  {{ opacity:1; }}
  100% {{ transform:translateX(calc(100vw - 150px)); opacity:0.1; }}
}}
@keyframes wheelSpin {{
  0%   {{ transform:rotate(0deg); }}
  100% {{ transform:rotate(360deg); }}
}}
@keyframes trailPulse {{
  0%,100% {{ opacity:0.35; transform:scaleY(0.75); }}
  50%     {{ opacity:0.95; transform:scaleY(1.4); }}
}}
.cart-track {{
  position:relative; width:100%; height:74px;
  background:{track_bg};
  border-radius:6px; border:1px solid {track_brd};
  overflow:hidden; margin-top:0.25rem;
  display:flex; align-items:center;
}}
.track-line {{
  position:absolute; left:0; right:0; top:50%; height:2px;
  background:repeating-linear-gradient(90deg,{dash_col} 0px,{dash_col} 14px,transparent 14px,transparent 24px);
  opacity:0.45;
}}
.cart-vehicle {{
  position:absolute; display:flex; align-items:center;
  animation:cartDrive 20s cubic-bezier(0.35,0,0.25,1) infinite;
  will-change:transform;
}}
.wheel {{ transform-origin:center; animation:wheelSpin 2.4s linear infinite; }}
.glow-trail {{
  position:absolute; right:105px; width:160px; height:8px;
  background:{trail_grad};
  border-radius:4px; filter:blur(2.5px);
  animation:trailPulse 2.5s ease-in-out infinite;
}}
</style>
<div style="display:flex;align-items:center;justify-content:space-between;gap:1rem;">
  <div>
    <div style="display:flex;align-items:center;gap:0.5rem;">
      <span style="font-size:1.2rem;font-weight:800;background:{title_grad};-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-0.01em;">
        Retail Sales &amp; Profitability Analysis Platform
      </span>
      <span style="font-size:0.63rem;background:{badge_bg};color:{badge_col};border:1px solid {badge_brd};border-radius:4px;padding:0.1rem 0.4rem;font-weight:600;">
        v2026.1 Enterprise
      </span>
    </div>
    <div style="font-size:0.75rem;color:{desc_col};margin-top:0.15rem;line-height:1.35;">
      Distributed <b>Apache Spark 4.3</b> pipeline · Random Forest profit simulation · <b>SHAP TreeExplainer</b> loss attribution · 30,000-order retail dataset.
    </div>
  </div>
  <div style="display:flex;gap:0.7rem;flex-shrink:0;">
    <div style="background:{stat_bg};border:1px solid {stat_brd};border-radius:6px;padding:0.25rem 0.65rem;">
      <div style="font-size:0.58rem;color:{stat_lbl};text-transform:uppercase;letter-spacing:0.06em;">Engine</div>
      <div style="font-size:0.74rem;color:{stat_ok_col};font-weight:700;">● Spark Active</div>
    </div>
    <div style="background:{stat_bg};border:1px solid {stat_brd};border-radius:6px;padding:0.25rem 0.65rem;">
      <div style="font-size:0.58rem;color:{stat_lbl};text-transform:uppercase;letter-spacing:0.06em;">Scale</div>
      <div style="font-size:0.74rem;color:{stat_data_col};font-weight:700;">{total_records:,} Orders</div>
    </div>
  </div>
</div>
<div class="cart-track">
  <div class="track-line"></div>
  <div class="cart-vehicle">
    <div class="glow-trail"></div>
    <svg width="110" height="78" viewBox="0 0 44 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 4H10L15 20H31L35 9H12" stroke="{cart_body}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="17" y1="12" x2="17" y2="17" stroke="{bar1}" stroke-width="2" stroke-linecap="round"/>
      <line x1="21.5" y1="10" x2="21.5" y2="17" stroke="{bar2}" stroke-width="2" stroke-linecap="round"/>
      <line x1="26" y1="13" x2="26" y2="17" stroke="{bar3}" stroke-width="2" stroke-linecap="round"/>
      <line x1="30" y1="11" x2="30" y2="17" stroke="{bar4}" stroke-width="2" stroke-linecap="round"/>
      <path d="M1 9H5" stroke="{bar4}" stroke-width="1.3" stroke-linecap="round" opacity="0.7"/>
      <path d="M0 13H4" stroke="{bar2}" stroke-width="1.3" stroke-linecap="round" opacity="0.5"/>
      <g class="wheel">
        <circle cx="17" cy="26" r="3.5" fill="{wheel_fill}" stroke="{wstroke1}" stroke-width="2"/>
        <circle cx="17" cy="26" r="1" fill="{wstroke1}"/>
      </g>
      <g class="wheel">
        <circle cx="29" cy="26" r="3.5" fill="{wheel_fill}" stroke="{wstroke2}" stroke-width="2"/>
        <circle cx="29" cy="26" r="1" fill="{wstroke2}"/>
      </g>
    </svg>
  </div>
</div>
</div>"""


def _footer_html(light):
    if light:
        return """<div style="display:flex;align-items:center;justify-content:space-between;background:rgba(237,232,220,0.5);border:1px solid #C8BFA8;border-radius:6px;padding:0.25rem 0.75rem;margin-top:0.3rem;font-size:0.67rem;color:#7A6B58;">
<div>🌿 <b>Stack:</b> Apache Spark 4.3 · Streamlit 1.67 · Scikit-Learn · SHAP TreeExplainer</div>
<div>Use the <b>Top Navigation Bar</b> to explore modules — no scrolling required.</div>
</div>"""
    else:
        return """<div style="display:flex;align-items:center;justify-content:space-between;background:rgba(31,43,28,0.5);border:1px solid #354A30;border-radius:6px;padding:0.25rem 0.75rem;margin-top:0.3rem;font-size:0.67rem;color:#8A9E82;">
<div>🌿 <b>Stack:</b> Apache Spark 4.3 · Streamlit 1.67 · Scikit-Learn · SHAP TreeExplainer</div>
<div>Use the <b>Top Navigation Bar</b> to explore modules — no scrolling required.</div>
</div>"""


def _cap_card(title, t_color, desc, badge, b_color, light):
    if light:
        cb = "#FDFAF4"; cbrd = "#C8BFA8"; dc = "#7A6B58"
    else:
        cb = "#1F2B1C"; cbrd = "#354A30"; dc = "#8A9E82"
    return f"""<div style="background:{cb};border:1px solid {cbrd};border-radius:8px;padding:0.35rem 0.55rem;height:86px;overflow:hidden;">
<div style="font-size:0.74rem;font-weight:700;color:{t_color};margin-bottom:0.12rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{title}</div>
<div style="font-size:0.64rem;color:{dc};line-height:1.24;">{desc}</div>
<div style="font-size:0.58rem;color:{b_color};margin-top:0.22rem;font-weight:600;">✓ {badge}</div>
</div>"""


def render_home(df, on_navigate=None):
    """
    Earthy-themed landing page.
    Large slow shopping cart animation · 4 KPI cards · 6 capability cards · footer.
    """
    light = st.session_state.get("theme_mode", "dark") == "light"

    total_records = len(df) if df is not None else 30_000
    if df is not None:
        total_sales  = df["Order_Amount"].sum() if "Order_Amount" in df.columns else df.get("Sales", 0).sum() if hasattr(df, "get") else 0
        total_profit = df["Profit_Amount"].sum() if "Profit_Amount" in df.columns else df.get("Profit", 0).sum() if hasattr(df, "get") else 0
    else:
        total_sales = total_profit = 0

    # 1 — Hero
    st.markdown(_hero_html(light, total_records, total_sales, total_profit), unsafe_allow_html=True)

    # 2 — KPI Row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Total Order Volume", f"${total_sales:,.0f}",
                        f"{total_records:,} verified transactions", "🛒", "green")
    with k2:
        render_kpi_card("Enterprise Net Profit", f"${total_profit:,.0f}",
                        "Historical return", "📈", "brown")
    with k3:
        render_kpi_card("Distributed Engine", "Apache Spark",
                        "PySpark 4.3 in-memory Tungsten", "⚡", "sage")
    with k4:
        render_kpi_card("ML Intelligence", "Dual AI Models",
                        "Random Forest + SHAP Explainability", "🤖", "terra")

    # 3 — Capability cards
    sec_col = "#7A6B58" if light else "#8A9E82"
    st.markdown(
        f"""<div style="font-size:0.7rem;font-weight:700;color:{sec_col};text-transform:uppercase;letter-spacing:0.06em;margin-top:0.2rem;margin-bottom:0.12rem;">Core Platform Capabilities</div>""",
        unsafe_allow_html=True,
    )

    if light:
        gc = "#2D5E42"; bc = "#8B6914"; rc = "#A0522D"; sc = "#5C8C6E"; ac = "#2D5E42"; wc = "#8B6914"
    else:
        gc = "#78C8A0"; bc = "#C8A050"; rc = "#E09070"; sc = "#90B890"; ac = "#78C8A0"; wc = "#C8A050"

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(_cap_card("🏠 Executive Dashboard", gc,
            "Centralized summary of gross sales, net profit, and trends.",
            "2×2 Grid · No Scroll", gc, light), unsafe_allow_html=True)
    with c2:
        st.markdown(_cap_card("🧹 Data Engineering", sc,
            "Automated Spark deduplication, imputation, and validation.",
            "Schema Validation", sc, light), unsafe_allow_html=True)
    with c3:
        st.markdown(_cap_card("📈 Multidimensional", bc,
            "Deep-dive across Categories, Regions, and Discount tiers.",
            "Sales · Discounts", bc, light), unsafe_allow_html=True)
    with c4:
        st.markdown(_cap_card("🎯 Loss Detection AI", rc,
            "Predictive classification flagging low-margin transactions.",
            "Risk Distribution", rc, light), unsafe_allow_html=True)
    with c5:
        st.markdown(_cap_card("🧬 SHAP Loss DNA", ac,
            "TreeExplainer attributions revealing exact margin drivers.",
            "Local & Global SHAP", ac, light), unsafe_allow_html=True)
    with c6:
        st.markdown(_cap_card("⚡ What-If Simulator", wc,
            "Interactive discount elasticity simulation identifying optimal profit.",
            "Real-time Slider", wc, light), unsafe_allow_html=True)

    # 4 — Footer
    st.markdown(_footer_html(light), unsafe_allow_html=True)
