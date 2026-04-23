THEMES = {
    "dark": {
        "name_ar": "🌙 داكن", "name_en": "🌙 Dark",
        "bg": "#08090d", "sidebar_bg": "#0d0e14", "card_bg": "#0d0e14",
        "border": "#ffffff08", "border_hover": "#ffffff15",
        "text_primary": "#e8eaf6", "text_secondary": "#ffffff40", "text_muted": "#ffffff20",
        "accent": "#00e5ff", "accent2": "#7c4dff",
        "success": "#00e676", "warning": "#ffd740", "danger": "#ff5252",
        "progress_bg": "#ffffff08", "input_bg": "#1a1a2e", "input_border": "#ffffff15",
        "nav_active_bg": "#00e5ff08", "nav_active_border": "#00e5ff", "nav_active_color": "#00e5ff",
        "logo_gradient": "linear-gradient(135deg, #00e5ff, #7c4dff)",
        "card_shadow": "0 4px 20px rgba(0,229,255,0.05)",
    },
    "light": {
        "name_ar": "☀️ فاتح", "name_en": "☀️ Light",
        "bg": "#f0f4f8", "sidebar_bg": "#1a1a2e", "card_bg": "#ffffff",
        "border": "#cbd5e1", "border_hover": "#0891b260",
        "text_primary": "#0f172a", "text_secondary": "#475569", "text_muted": "#64748b",
        "accent": "#0891b2", "accent2": "#0e7490",
        "success": "#16a34a", "warning": "#d97706", "danger": "#dc2626",
        "progress_bg": "#e2e8f0", "input_bg": "#ffffff", "input_border": "#94a3b8",
        "nav_active_bg": "#0891b210", "nav_active_border": "#0891b2", "nav_active_color": "#0891b2",
        "logo_gradient": "linear-gradient(135deg, #0891b2, #0e7490)",
        "card_shadow": "0 2px 12px rgba(0,0,0,0.08)",
    },
    "green": {
        "name_ar": "🌿 أخضر", "name_en": "🌿 Green",
        "bg": "#f5f7f2", "sidebar_bg": "#1c2b1a", "card_bg": "#ffffff",
        "border": "#a7d7a9", "border_hover": "#4caf5060",
        "text_primary": "#14290f", "text_secondary": "#2d5a27", "text_muted": "#3d7a35",
        "accent": "#2e7d32", "accent2": "#1b5e20",
        "success": "#1b5e20", "warning": "#e65100", "danger": "#b71c1c",
        "progress_bg": "#c8e6c9", "input_bg": "#ffffff", "input_border": "#66bb6a",
        "nav_active_bg": "#2e7d3215", "nav_active_border": "#66bb6a", "nav_active_color": "#a5d6a7",
        "logo_gradient": "linear-gradient(135deg, #4caf50, #2e7d32)",
        "card_shadow": "0 2px 12px rgba(46,125,50,0.10)",
    }
}

def get_theme_css(theme_name: str = "dark") -> str:
    th = THEMES.get(theme_name, THEMES["dark"])
    is_dark = theme_name == "dark"
    sidebar_text = '#e8eaf6'  # السايدبار دائماً داكن في الثيمات الثلاثة
    input_border = th.get("input_border", th["border"])

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
* {{ font-family: 'Tajawal', sans-serif !important; }}
.stApp {{ background: {th["bg"]} !important; }}
div[data-testid="stSidebar"] {{ background: {th["sidebar_bg"]} !important; border-left: 1px solid {th["border"]} !important; }}
div[data-testid="stSidebar"] * {{ color: {sidebar_text} !important; }}

.stButton > button {{
    background: {th["accent"]}15 !important;
    border: 1px solid {th["accent"]}60 !important;
    color: {th["accent"]} !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    background: {th["accent"]}30 !important;
    border-color: {th["accent"]}90 !important;
    transform: translateY(-1px) !important;
}}
.stButton > button[kind="primary"] {{
    background: {th["accent"]} !important;
    border: 1px solid {th["accent"]} !important;
    color: #ffffff !important;
    font-weight: 700 !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: {th["accent2"]} !important;
    border-color: {th["accent2"]} !important;
    transform: translateY(-1px) !important;
}}
[data-testid="stFormSubmitButton"] > button {{
    background: {th["accent"]} !important;
    border: 1px solid {th["accent"]} !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    width: 100% !important;
    padding: 12px !important;
    font-size: 14px !important;
    transition: all 0.3s !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    background: {th["accent2"]} !important;
    border-color: {th["accent2"]} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px {th["accent"]}40 !important;
}}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {th["input_bg"]} !important;
    border: 1.5px solid {input_border} !important;
    color: {th["text_primary"]} !important;
    border-radius: 10px !important;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {{
    border-color: {th["accent"]} !important;
    box-shadow: 0 0 0 2px {th["accent"]}25 !important;
}}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {{
    color: {th["text_muted"]} !important;
    opacity: 1 !important;
}}

.stSelectbox > div > div {{
    background: {th["input_bg"]} !important;
    border: 1.5px solid {input_border} !important;
    color: {th["text_primary"]} !important;
    border-radius: 10px !important;
}}
.stSelectbox > div > div > div {{
    color: {th["text_primary"]} !important;
}}
.stSelectbox [data-baseweb="select"] > div {{
    background: {th["input_bg"]} !important;
    color: {th["text_primary"]} !important;
}}
[data-baseweb="popover"] ul {{
    background: {th["card_bg"]} !important;
    border: 1px solid {th["border"]} !important;
    border-radius: 10px !important;
}}
[data-baseweb="popover"] li {{
    background: {th["card_bg"]} !important;
    color: {th["text_primary"]} !important;
}}
[data-baseweb="popover"] li:hover {{
    background: {th["accent"]}20 !important;
    color: {th["accent"]} !important;
}}
[data-baseweb="option"] {{
    background: {th["card_bg"]} !important;
    color: {th["text_primary"]} !important;
}}
[data-baseweb="option"]:hover {{
    background: {th["accent"]}20 !important;
    color: {th["accent"]} !important;
}}
[aria-selected="true"] {{
    background: {th["accent"]}25 !important;
    color: {th["accent"]} !important;
}}
.stSelectbox [data-baseweb="popover"] {{
    background: {th["card_bg"]} !important;
}}

.stRadio > div > label > div > p {{
    color: {th["text_primary"]} !important;
}}
.stRadio > div > label {{
    color: {th["text_primary"]} !important;
}}
.stCheckbox > label > div > p {{
    color: {th["text_primary"]} !important;
}}
p, span, div, label {{
    color: {th["text_primary"]};
}}

.stTabs [data-baseweb="tab-list"] {{
    background: {th["card_bg"]} !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid {th["border"]} !important;
}}
.stTabs [data-baseweb="tab"] {{
    color: {th["text_secondary"]} !important;
    border-radius: 8px !important;
}}
.stTabs [aria-selected="true"] {{
    background: {th["accent"]}20 !important;
    color: {th["accent"]} !important;
}}
.stTabs [data-baseweb="tab"] p {{
    color: {th["text_secondary"]} !important;
}}
.stTabs [aria-selected="true"] p {{
    color: {th["accent"]} !important;
}}

hr {{ border-color: {th["border"]} !important; opacity: 0.6 !important; }}

.stDataFrame {{ border: 1px solid {th["border"]} !important; border-radius: 12px !important; }}
.stDataFrame th {{ background: {th["progress_bg"]} !important; color: {th["text_primary"]} !important; }}
.stDataFrame td {{ color: {th["text_primary"]} !important; }}

.stExpander {{
    border: 1px solid {th["border"]} !important;
    border-radius: 12px !important;
    background: {th["card_bg"]} !important;
}}
.stExpander summary p {{
    color: {th["text_primary"]} !important;
    font-weight: 600 !important;
}}

.stSlider > div > div > div {{
    color: {th["text_primary"]} !important;
}}

.stAlert > div {{
    color: {th["text_primary"]} !important;
}}
.stInfo {{ background: {th["accent"]}15 !important; border-color: {th["accent"]}40 !important; }}
.stInfo p {{ color: {th["accent"]} !important; }}
.stSuccess {{ background: {th["success"]}12 !important; border-color: {th["success"]}40 !important; }}
.stSuccess p {{ color: {th["success"]} !important; }}
.stWarning {{ background: {th["warning"]}12 !important; border-color: {th["warning"]}40 !important; }}
.stWarning p {{ color: {th["warning"]} !important; }}
.stError {{ background: {th["danger"]}12 !important; border-color: {th["danger"]}40 !important; }}
.stError p {{ color: {th["danger"]} !important; }}

.stMarkdown p, .stMarkdown li, .stMarkdown span {{
    color: {th["text_primary"]} !important;
}}
.stCaption, .stCaption p {{
    color: {th["text_muted"]} !important;
}}

.novix-card {{ background: {th["card_bg"]}; border: 1px solid {th["border"]}; border-radius: 16px; padding: 22px; box-shadow: {th["card_shadow"]}; transition: all 0.3s ease; margin-bottom: 16px; }}
.novix-card:hover {{ border-color: {th["border_hover"]}; transform: translateY(-2px); box-shadow: 0 8px 30px {th["accent"]}10; }}
.novix-kpi {{ background: {th["card_bg"]}; border: 1px solid {th["border"]}; border-radius: 16px; padding: 20px; box-shadow: {th["card_shadow"]}; transition: all 0.3s ease; cursor: pointer; text-align: center; }}
.novix-kpi:hover {{ border-color: {th["accent"]}40; transform: translateY(-3px); box-shadow: 0 8px 30px {th["accent"]}15; }}
.kpi-label {{ font-size: 0.75rem; color: {th["text_secondary"]}; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600; text-transform: uppercase; }}
.kpi-value {{ font-family: 'JetBrains Mono', monospace !important; font-size: 1.4rem; font-weight: 700; color: {th["accent"]}; }}
.kpi-value.success {{ color: {th["success"]}; }}
.kpi-value.warning {{ color: {th["warning"]}; }}
.kpi-value.danger {{ color: {th["danger"]}; }}
.kpi-value.primary {{ color: {th["text_primary"]}; }}
.kpi-change-up {{ font-size: 0.73rem; color: {th["success"]}; margin-top: 4px; }}
.kpi-change-down {{ font-size: 0.73rem; color: {th["danger"]}; margin-top: 4px; }}
.kpi-change-neutral {{ font-size: 0.73rem; color: {th["text_secondary"]}; margin-top: 4px; }}
.section-title {{ font-size: 0.75rem; color: {th["text_secondary"]}; letter-spacing: 1px; text-transform: uppercase; font-weight: 700; margin: 16px 0 10px; padding-bottom: 6px; border-bottom: 1px solid {th["border"]}; }}
.novix-progress-info {{ display: flex; justify-content: space-between; font-size: 0.78rem; color: {th["text_secondary"]}; margin-bottom: 6px; font-weight: 500; }}
.novix-progress-bar {{ height: 8px; background: {th["progress_bg"]}; border-radius: 10px; overflow: hidden; margin-bottom: 12px; }}
.novix-progress-fill {{ height: 100%; background: linear-gradient(90deg, {th["accent"]}, {th["accent2"]}); border-radius: 10px; transition: width 1s ease; }}
.novix-progress-fill.success {{ background: linear-gradient(90deg, {th["success"]}, {th["accent2"]}); }}
.novix-progress-fill.warning {{ background: linear-gradient(90deg, {th["warning"]}, #c45000); }}
.novix-txn {{ display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid {th["border"]}; transition: all 0.2s; }}
.novix-txn:last-child {{ border-bottom: none; }}
.novix-txn:hover {{ background: {th["accent"]}08; border-radius: 8px; padding: 10px 6px; }}
.novix-txn-icon {{ width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1rem; }}
.novix-txn-icon.exp {{ background: {th["danger"]}18; }}
.novix-txn-icon.inc {{ background: {th["success"]}18; }}
.novix-txn-name {{ font-size: 0.84rem; color: {th["text_primary"]}; font-weight: 600; }}
.novix-txn-date {{ font-size: 0.7rem; color: {th["text_muted"]}; margin-top: 2px; }}
.novix-txn-amt {{ font-family: 'JetBrains Mono', monospace !important; font-size: 0.88rem; font-weight: 700; }}
.novix-txn-amt.exp {{ color: {th["danger"]}; }}
.novix-txn-amt.inc {{ color: {th["success"]}; }}
.novix-cat-row {{ display: flex; align-items: center; gap: 10px; padding: 10px 12px; margin-bottom: 6px; border-radius: 10px; background: {th["accent"]}08; border: 1px solid {th["border"]}; transition: all 0.2s; }}
.novix-cat-row:hover {{ border-color: {th["accent"]}40; background: {th["accent"]}12; }}
.novix-cat-emoji {{ width: 34px; height: 34px; background: {th["progress_bg"]}; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }}
.novix-cat-name {{ font-size: 0.83rem; color: {th["text_primary"]}; font-weight: 600; }}
.novix-cat-bar {{ height: 3px; background: {th["progress_bg"]}; border-radius: 3px; margin-top: 4px; }}
.novix-cat-bar-fill {{ height: 100%; border-radius: 3px; background: linear-gradient(90deg, {th["accent"]}, {th["accent2"]}); }}
.novix-cat-amount {{ font-family: 'JetBrains Mono', monospace !important; font-size: 0.83rem; color: {th["danger"]}; font-weight: 700; }}
.novix-bal-item {{ background: {th["progress_bg"]}; border: 1px solid {th["border"]}; border-radius: 12px; padding: 16px; text-align: center; }}
.novix-bal-label {{ font-size: 0.7rem; color: {th["text_secondary"]}; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; font-weight: 600; }}
.novix-bal-val {{ font-family: 'JetBrains Mono', monospace !important; font-size: 1.1rem; font-weight: 800; color: {th["accent"]}; }}
.novix-bal-val.savings {{ color: {th["warning"]}; }}
.novix-bal-change {{ font-size: 0.66rem; color: {th["success"]}; margin-top: 4px; font-weight: 600; }}
.notif-card {{ padding: 12px 16px; border-radius: 12px; margin-bottom: 8px; font-size: 0.85rem; border: 1px solid transparent; font-weight: 500; }}
.notif-card.warning {{ background: {th["warning"]}15; border-color: {th["warning"]}50; color: {th["warning"]}; }}
.notif-card.success {{ background: {th["success"]}15; border-color: {th["success"]}50; color: {th["success"]}; }}
.notif-card.info {{ background: {th["accent"]}15; border-color: {th["accent"]}50; color: {th["accent"]}; }}
.notif-card.tip {{ background: {th["accent2"]}15; border-color: {th["accent2"]}50; color: {th["accent2"]}; }}
.goal-segs {{ display: flex; gap: 3px; height: 8px; border-radius: 10px; overflow: hidden; margin-top: 6px; }}
.goal-seg {{ flex: 1; background: {th["progress_bg"]}; border-radius: 2px; }}
.goal-seg.filled {{ background: linear-gradient(90deg, {th["warning"]}, #c45000); }}
.strength-badge {{ text-align: center; padding: 16px; background: {th["warning"]}12; border: 1px solid {th["warning"]}40; border-radius: 16px; margin-bottom: 12px; }}
.strength-icon {{ font-size: 2.5rem; }}
.strength-msg {{ font-size: 0.85rem; color: {th["text_primary"]}; margin-top: 8px; font-weight: 500; }}
.novix-logo-text {{ font-size: 1.4rem; font-weight: 800; background: {th["logo_gradient"]}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 3px; }}
.novix-logo-sub {{ font-size: 0.62rem; color: {'#ffffff30' if is_dark or theme_name == 'green' else '#0e749060'}; letter-spacing: 3px; margin-top: 2px; }}
.novix-page-title {{ font-size: 1.5rem; font-weight: 700; color: {th["text_primary"]}; margin-bottom: 4px; }}
.novix-page-sub {{ font-size: 0.82rem; color: {th["text_secondary"]}; }}
.quick-btn {{ display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background: {th["card_bg"]}; border: 1px solid {th["border"]}; border-radius: 20px; font-size: 0.82rem; color: {th["text_primary"]}; cursor: pointer; transition: all 0.2s; margin: 4px; font-weight: 500; }}

@keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(16px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@keyframes pulse {{ 0%, 100% {{ box-shadow: 0 0 0 0 {th["accent"]}40; }} 50% {{ box-shadow: 0 0 0 8px transparent; }} }}
.anim-fade-up {{ animation: fadeInUp 0.5s ease both; }}
.anim-fade-up-1 {{ animation: fadeInUp 0.5s ease 0.05s both; }}
.anim-fade-up-2 {{ animation: fadeInUp 0.5s ease 0.1s both; }}
.anim-fade-up-3 {{ animation: fadeInUp 0.5s ease 0.15s both; }}
.anim-fade-up-4 {{ animation: fadeInUp 0.5s ease 0.2s both; }}
.anim-pulse {{ animation: pulse 2s infinite; }}
</style>

<script>
function playSuccess() {{
    try {{
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.frequency.setValueAtTime(600, ctx.currentTime);
        osc.frequency.setValueAtTime(800, ctx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.1, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
        osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.3);
    }} catch(e) {{}}
}}
</script>
"""
