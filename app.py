import html
import json

import streamlit as st
import streamlit.components.v1 as components

from config import API_KEY
from modules.document_processor import extract_text
from modules.question_generator import generate_questions


st.set_page_config(
    page_title="ExamForge",
    page_icon="EF",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "active_page" not in st.session_state:
    st.session_state.active_page = "Generate"
    st.session_state.nav_selection = "Generate"

theme = st.session_state.theme
is_dark = theme == "Dark"

palette = {
    "light": {
        "bg": "#f4f8fc",
        "bg_radial": "radial-gradient(130% 90% at 50% -10%, #e6f1fe 0%, #f4f8fc 60%, #edf5fc 100%)",
        "surface": "rgba(255, 255, 255, 0.85)",
        "surface_solid": "#ffffff",
        "surface_alt": "rgba(235, 243, 254, 0.85)",
        "text": "#0d192e",
        "muted": "#4a6282",
        "line": "rgba(196, 218, 245, 0.85)",
        "line_subtle": "rgba(223, 236, 251, 0.75)",
        "accent": "#1d68ed",
        "accent_hover": "#1453c2",
        "accent_soft": "rgba(29, 104, 237, 0.08)",
        "danger": "#dc2626",
        "nav_glass": "rgba(255, 255, 255, 0.82)",
        "nav_glass_border": "rgba(255, 255, 255, 0.95)",
        "nav_shadow": "rgba(20, 50, 95, 0.09)",
        "nav_glow": "rgba(29, 104, 237, 0.16)",
        "accent_glow": "rgba(29, 104, 237, 0.32)",
        "accent_contrast": "#ffffff",
        "glass_highlight": "rgba(255, 255, 255, 0.95)",
        "glass_specular": "inset 0 1px 1px 0 rgba(255, 255, 255, 0.95), 0 8px 32px 0 rgba(20, 50, 95, 0.06)",
        "alert_bg": "rgba(235, 244, 255, 0.95)",
        "alert_border": "rgba(186, 215, 250, 0.9)",
        "expander_bg": "rgba(255, 255, 255, 0.95)",
        "expander_border": "rgba(196, 218, 245, 0.85)",
    },
    "dark": {
        "bg": "#080e18",
        "bg_radial": "radial-gradient(120% 80% at 50% -10%, #0d1a2d 0%, #080e18 70%)",
        "surface": "rgba(14, 24, 42, 0.85)",
        "surface_solid": "#0d1728",
        "surface_alt": "rgba(20, 35, 62, 0.85)",
        "text": "#f1f6fd",
        "muted": "#8da5c7",
        "line": "rgba(37, 62, 100, 0.85)",
        "line_subtle": "rgba(25, 43, 70, 0.7)",
        "accent": "#38bdf8",
        "accent_hover": "#60a5fa",
        "accent_soft": "rgba(56, 189, 248, 0.12)",
        "danger": "#f87171",
        "nav_glass": "rgba(10, 18, 32, 0.86)",
        "nav_glass_border": "rgba(40, 68, 108, 0.65)",
        "nav_shadow": "rgba(0, 0, 0, 0.55)",
        "nav_glow": "rgba(56, 189, 248, 0.22)",
        "accent_glow": "rgba(56, 189, 248, 0.38)",
        "accent_contrast": "#04101e",
        "glass_highlight": "rgba(255, 255, 255, 0.12)",
        "glass_specular": "inset 0 1px 1px 0 rgba(255, 255, 255, 0.15), 0 8px 32px 0 rgba(0, 0, 0, 0.45)",
        "alert_bg": "rgba(16, 30, 54, 0.95)",
        "alert_border": "rgba(37, 62, 100, 0.9)",
        "expander_bg": "rgba(14, 24, 42, 0.95)",
        "expander_border": "rgba(37, 62, 100, 0.85)",
    },
}[theme.lower()]

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

    :root {{
        --ef-bg: {palette["bg"]};
        --ef-bg-radial: {palette["bg_radial"]};
        --ef-surface: {palette["surface"]};
        --ef-surface-solid: {palette["surface_solid"]};
        --ef-surface-alt: {palette["surface_alt"]};
        --ef-text: {palette["text"]};
        --ef-muted: {palette["muted"]};
        --ef-line: {palette["line"]};
        --ef-line-subtle: {palette["line_subtle"]};
        --ef-accent: {palette["accent"]};
        --ef-accent-hover: {palette["accent_hover"]};
        --ef-accent-soft: {palette["accent_soft"]};
        --ef-danger: {palette["danger"]};
        --ef-nav-glass: {palette["nav_glass"]};
        --ef-nav-glass-border: {palette["nav_glass_border"]};
        --ef-nav-shadow: {palette["nav_shadow"]};
        --ef-nav-glow: {palette["nav_glow"]};
        --ef-accent-glow: {palette["accent_glow"]};
        --ef-accent-contrast: {palette["accent_contrast"]};
        --ef-glass-highlight: {palette["glass_highlight"]};
        --ef-glass-specular: {palette["glass_specular"]};
        --ef-alert-bg: {palette["alert_bg"]};
        --ef-alert-border: {palette["alert_border"]};
        --ef-expander-bg: {palette["expander_bg"]};
        --ef-expander-border: {palette["expander_border"]};
    }}

    html {{
        color-scheme: {"dark" if is_dark else "light"} !important;
    }}

    html, body, [class*="css"] {{
        font-family: "DM Sans", sans-serif;
    }}

    .stApp {{
        background: var(--ef-bg) !important;
        color: var(--ef-text) !important;
    }}

    [data-testid="stHeader"] {{
        height: 0;
        background: transparent;
    }}

    [data-testid="stToolbar"] {{
        visibility: hidden;
    }}

    .block-container {{
        max-width: 1180px;
        padding-top: 0 !important;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 4.5rem;
    }}

    h1, h2, h3, h4,
    .stMarkdown p, .stMarkdown li,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] {{
        color: var(--ef-text) !important;
    }}

    h1, h2, h3, h4 {{
        font-family: "Manrope", sans-serif !important;
        letter-spacing: -0.035em;
    }}

    p, li, label, small,
    [data-testid="stCaptionContainer"] {{
        color: var(--ef-muted) !important;
    }}

    /* Permanent Sticky Liquid Glass Navigation Bar */
    .st-key-ef_navbar,
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.ef-nav-marker),
    div[data-testid="stElementContainer"]:has(.ef-nav-marker) {{
        position: sticky !important;
        top: 0 !important;
        z-index: 99999 !important;
        background: var(--ef-nav-glass) !important;
        backdrop-filter: blur(28px) saturate(210%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(210%) !important;
        border-bottom: 1px solid var(--ef-line) !important;
        margin-top: 0 !important;
        margin-left: -2rem !important;
        margin-right: -2rem !important;
        padding: 1.15rem 2.25rem !important;
        box-shadow: 0 12px 36px -4px var(--ef-nav-shadow), inset 0 1.5px 1px 0 var(--ef-glass-highlight) !important;
        transition: background 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), border-color 0.3s ease, box-shadow 0.3s ease !important;
    }}

    .st-key-ef_navbar [data-testid="stHorizontalBlock"] {{
        align-items: center !important;
    }}

    /* Executive Liquid Brand */
    .ef-brand-container {{
        display: inline-flex;
        align-items: center;
        gap: 14px;
        user-select: none;
        cursor: pointer;
        transition: transform 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
    }}

    .ef-brand-container:hover {{
        transform: translateY(-1px) scale(1.015);
    }}

    .ef-brand-logo {{
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--ef-accent) 0%, var(--ef-accent-hover) 100%);
        color: #ffffff !important;
        font-family: "Manrope", sans-serif;
        font-weight: 800;
        font-size: 18px;
        letter-spacing: -0.04em;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 18px -2px var(--ef-accent-glow), inset 0 1px 1px 0 rgba(255, 255, 255, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.25);
    }}

    .ef-brand-text {{
        display: flex;
        flex-direction: column;
        line-height: 1.15;
    }}

    .ef-brand-title {{
        font-family: "Manrope", sans-serif;
        font-size: 24px;
        font-weight: 800;
        color: var(--ef-text) !important;
        letter-spacing: -0.04em;
        line-height: 1.1;
    }}

    .ef-brand-title span {{
        color: var(--ef-accent) !important;
    }}

    .ef-brand-subtitle {{
        font-size: 11px;
        font-weight: 600;
        color: var(--ef-muted) !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 2px;
    }}

    /* Larger, Sleek Liquid Glass Nav Buttons */
    .st-key-ef_navbar button {{
        min-height: 46px !important;
        height: 46px !important;
        border-radius: 12px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        padding: 0 18px !important;
        transition: all 0.24s cubic-bezier(0.2, 0.8, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }}

    /* Inactive Nav Button - Liquid Glass */
    .st-key-ef_navbar button[kind="secondary"] {{
        background: var(--ef-surface) !important;
        border: 1px solid var(--ef-line) !important;
        color: var(--ef-muted) !important;
        box-shadow: var(--ef-glass-specular) !important;
        backdrop-filter: blur(12px) !important;
    }}

    .st-key-ef_navbar button[kind="secondary"]:hover {{
        background: var(--ef-surface-solid) !important;
        border-color: var(--ef-accent) !important;
        color: var(--ef-text) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px -2px var(--ef-nav-glow), inset 0 1px 1px 0 var(--ef-glass-highlight) !important;
    }}

    .st-key-ef_navbar button[kind="secondary"]:active {{
        transform: translateY(0px) scale(0.98) !important;
    }}

    /* Active Nav Button - Luminous Sapphire */
    .st-key-ef_navbar button[kind="primary"] {{
        background: linear-gradient(135deg, var(--ef-accent) 0%, var(--ef-accent-hover) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        color: #ffffff !important;
        box-shadow: 0 8px 26px -2px var(--ef-accent-glow), inset 0 1.5px 1px 0 rgba(255, 255, 255, 0.45) !important;
        transform: translateY(-1px) !important;
    }}

    .st-key-ef_navbar button[kind="primary"]:hover {{
        background: linear-gradient(135deg, var(--ef-accent-hover) 0%, var(--ef-accent) 100%) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px -2px var(--ef-accent-glow), inset 0 1.5px 1px 0 rgba(255, 255, 255, 0.55) !important;
    }}

    .st-key-ef_navbar button[kind="primary"]:active {{
        transform: translateY(0px) scale(0.98) !important;
    }}

    /* Theme Toggle Capsule Button */
    .st-key-theme_toggle button {{
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        letter-spacing: 0.01em !important;
        background: var(--ef-surface) !important;
        border: 1px solid var(--ef-line) !important;
        color: var(--ef-text) !important;
        box-shadow: var(--ef-glass-specular) !important;
    }}

    .st-key-theme_toggle button:hover {{
        background: var(--ef-surface-solid) !important;
        border-color: var(--ef-accent) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px -2px var(--ef-nav-glow), inset 0 1px 1px 0 var(--ef-glass-highlight) !important;
    }}

    .ef-page-intro {{
        display: grid;
        grid-template-columns: minmax(0, 760px) auto;
        align-items: end;
        gap: 32px;
        margin: 12px 0 30px;
    }}

    .ef-kicker {{
        margin-bottom: 9px;
        color: var(--ef-accent) !important;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }}

    .ef-page-intro h1 {{
        margin: 0 0 9px;
        font-size: clamp(32px, 4vw, 46px);
        line-height: 1.06;
        color: var(--ef-text) !important;
    }}

    .ef-page-intro p {{
        max-width: 680px;
        margin: 0;
        color: var(--ef-muted) !important;
        font-size: 15px;
        line-height: 1.65;
    }}

    .ef-section {{
        margin-bottom: 28px;
    }}

    .ef-section-heading {{
        margin: 0 0 5px;
        font-family: "Manrope", sans-serif;
        font-size: 17px;
        font-weight: 700;
        color: var(--ef-text) !important;
    }}

    .ef-section-copy {{
        margin: 0 0 14px;
        color: var(--ef-muted) !important;
        font-size: 13px;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--ef-surface) !important;
        border: 1px solid var(--ef-line) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }}

    [data-testid="stFileUploader"] {{
        background: var(--ef-surface) !important;
        border: 1px dashed var(--ef-line) !important;
        border-radius: 10px !important;
    }}

    [data-testid="stFileUploader"] *,
    [data-testid="stFileUploaderDropzone"] * {{
        color: var(--ef-text) !important;
    }}

    [data-testid="stFileUploader"],
    [data-testid="stFileUploaderDropzone"] {{
        background: var(--ef-surface) !important;
        color: var(--ef-text) !important;
    }}

    [data-testid="stFileUploader"] button {{
        background: var(--ef-surface-alt) !important;
        border: 1px solid var(--ef-line) !important;
        color: var(--ef-text) !important;
    }}

    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] section div {{
        background: var(--ef-surface) !important;
        color: var(--ef-text) !important;
    }}

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div,
    [data-testid="stNumberInput"] > div {{
        background: var(--ef-surface) !important;
        border: 1px solid var(--ef-line) !important;
        border-radius: 8px !important;
        color: var(--ef-text) !important;
    }}

    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"],
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="select"] *,
    [data-testid="stNumberInput"] *,
    [data-testid="stTextInput"] * {{
        background: var(--ef-surface) !important;
        color: var(--ef-text) !important;
        -webkit-text-fill-color: var(--ef-text) !important;
    }}

    div[data-testid="stTextInput"],
    div[data-testid="stTextInput"] > div,
    div[data-testid="stSelectbox"],
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stSelectbox"] [data-baseweb="select"],
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
    div[data-testid="stNumberInput"],
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stNumberInput"] [data-baseweb="input"],
    div[data-testid="stNumberInput"] [data-baseweb="input"] > div {{
        background: var(--ef-surface) !important;
        color: var(--ef-text) !important;
    }}

    div[data-testid="stSelectbox"] svg,
    [data-baseweb="select"] svg {{
        fill: var(--ef-text) !important;
        color: var(--ef-text) !important;
    }}

    [data-baseweb="list"],
    [data-baseweb="menu"],
    [role="listbox"],
    [role="option"] {{
        background: var(--ef-surface) !important;
        color: var(--ef-text) !important;
    }}

    [role="option"]:hover,
    [role="option"][aria-selected="true"] {{
        background: var(--ef-accent-soft) !important;
        color: var(--ef-accent) !important;
    }}

    [data-testid="stSelectbox"],
    [data-testid="stSelectbox"] div,
    [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stSelectbox"] [role="combobox"] > div,
    [data-testid="stSelectbox"] [data-baseweb="select"],
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {{
        background: var(--ef-surface) !important;
        color: var(--ef-text) !important;
    }}

    [data-testid="stSelectbox"] [role="combobox"] span,
    [data-testid="stSelectbox"] [role="combobox"] div,
    [data-testid="stSelectbox"] [role="combobox"] input {{
        color: var(--ef-text) !important;
        -webkit-text-fill-color: var(--ef-text) !important;
    }}

    [data-testid="stNumberInput"] button,
    [data-testid="stNumberInput"] button svg {{
        background: var(--ef-surface-alt) !important;
        color: var(--ef-text) !important;
        fill: var(--ef-text) !important;
    }}

    input, textarea,
    div[data-baseweb="select"] *,
    [data-baseweb="popover"] *,
    [data-baseweb="menu"] * {{
        color: var(--ef-text) !important;
        -webkit-text-fill-color: var(--ef-text) !important;
    }}

    input::placeholder, textarea::placeholder {{
        color: var(--ef-muted) !important;
        opacity: 1;
    }}

    [data-baseweb="popover"], [data-baseweb="menu"] {{
        background: var(--ef-surface) !important;
    }}

    .stButton > button,
    .stFormSubmitButton > button,
    [data-testid="stDownloadButton"] > button {{
        min-height: 42px;
        border: 1px solid var(--ef-accent) !important;
        border-radius: 8px !important;
        background: var(--ef-accent) !important;
        color: { "#09201f" if is_dark else "#ffffff" } !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }}

    .stButton > button p,
    .stButton > button span,
    .stFormSubmitButton > button p,
    .stFormSubmitButton > button span,
    [data-testid="stDownloadButton"] > button p,
    [data-testid="stDownloadButton"] > button span {{
        color: inherit !important;
        -webkit-text-fill-color: inherit !important;
    }}

    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    [data-testid="stDownloadButton"] > button:hover {{
        border-color: var(--ef-accent-hover) !important;
        background: var(--ef-accent-hover) !important;
    }}

    [data-testid="stDownloadButton"] > button {{
        background: var(--ef-surface) !important;
        border-color: var(--ef-line) !important;
        color: var(--ef-text) !important;
    }}

    [data-testid="stDownloadButton"] > button:hover {{
        background: var(--ef-surface-alt) !important;
        color: var(--ef-text) !important;
    }}

    button[kind="secondary"] {{
        background: var(--ef-surface) !important;
        border: 1px solid var(--ef-line) !important;
        color: var(--ef-text) !important;
    }}

    button[kind="secondary"] *,
    button[kind="secondary"] p,
    button[kind="secondary"] span {{
        color: var(--ef-text) !important;
        -webkit-text-fill-color: var(--ef-text) !important;
    }}

    button[kind="secondary"]:hover {{
        background: var(--ef-surface-alt) !important;
        border-color: var(--ef-accent) !important;
        color: var(--ef-text) !important;
    }}

    [data-testid="column"]:has(button[kind="secondary"]) {{
        align-self: center;
    }}

    button[kind="primary"],
    button[kind="secondary"] {{
        min-height: 38px !important;
        border-radius: 8px !important;
        font-size: 14px !important;
    }}

    button[kind="primary"] {{
        border: 1px solid var(--ef-accent) !important;
        background: var(--ef-accent) !important;
        color: { "#0b2220" if is_dark else "#ffffff" } !important;
    }}

    button[kind="primary"] *,
    button[kind="primary"] p,
    button[kind="primary"] span {{
        color: { "#0b2220" if is_dark else "#ffffff" } !important;
        -webkit-text-fill-color: { "#0b2220" if is_dark else "#ffffff" } !important;
    }}

    /* Status Container & Expander (e.g. 'Connecting to Gemini...') */
    .stExpander,
    [data-testid="stExpander"],
    details,
    summary,
    [data-testid="stStatusWidget"],
    [data-testid="stExpanderDetails"] {{
        background: var(--ef-expander-bg) !important;
        background-color: var(--ef-expander-bg) !important;
        border: 1px solid var(--ef-expander-border) !important;
        border-radius: 12px !important;
        color: var(--ef-text) !important;
        box-shadow: var(--ef-glass-specular) !important;
    }}

    [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary {{
        background: var(--ef-expander-bg) !important;
        background-color: var(--ef-expander-bg) !important;
        border: none !important;
        color: var(--ef-text) !important;
    }}

    [data-testid="stExpander"] summary:hover {{
        background: var(--ef-surface-alt) !important;
        background-color: var(--ef-surface-alt) !important;
        color: var(--ef-text) !important;
    }}

    [data-testid="stExpanderDetails"],
    [data-testid="stExpanderDetails"] > div,
    [data-testid="stExpanderDetails"] [data-testid="stVerticalBlock"] {{
        background: var(--ef-expander-bg) !important;
        background-color: var(--ef-expander-bg) !important;
        color: var(--ef-text) !important;
        border-top: 1px solid var(--ef-line-subtle) !important;
    }}

    [data-testid="stExpander"] *,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] strong,
    [data-testid="stExpander"] label,
    [data-testid="stExpander"] div,
    [data-testid="stStatusWidget"] *,
    [data-testid="stStatusWidget"] p,
    [data-testid="stStatusWidget"] span,
    [data-testid="stStatusWidget"] strong,
    [data-testid="stStatusWidget"] div {{
        color: var(--ef-text) !important;
        -webkit-text-fill-color: var(--ef-text) !important;
    }}

    [data-testid="stExpanderStepIcon"],
    [data-testid="stExpanderStepIcon"] *,
    [data-testid="stExpanderStepChevron"],
    [data-testid="stExpanderStepChevron"] *,
    [data-testid="stExpander"] svg,
    [data-testid="stStatusWidget"] svg {{
        fill: var(--ef-accent) !important;
        color: var(--ef-accent) !important;
    }}

    /* Alerts & Notifications (e.g. st.info, st.warning, st.error, st.success) */
    .stAlert,
    [data-testid="stAlert"],
    [data-testid="stAlert"] > div,
    [data-testid="stAlertContainer"],
    [data-testid="stNotification"],
    [data-testid="stNotification"] > div,
    [data-baseweb="notification"],
    [data-baseweb="notification"] > div,
    div[role="alert"],
    div[role="alert"] > div {{
        background: var(--ef-alert-bg) !important;
        background-color: var(--ef-alert-bg) !important;
        border: 1px solid var(--ef-alert-border) !important;
        border-radius: 12px !important;
        color: var(--ef-text) !important;
        box-shadow: var(--ef-glass-specular) !important;
    }}

    .stAlert *,
    [data-testid="stAlert"] *,
    [data-testid="stAlertContainer"] *,
    [data-testid="stNotification"] *,
    [data-baseweb="notification"] *,
    div[role="alert"] *,
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] strong,
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"],
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] * {{
        background: transparent !important;
        background-color: transparent !important;
        color: var(--ef-text) !important;
        -webkit-text-fill-color: var(--ef-text) !important;
    }}

    .stAlert svg,
    [data-testid="stAlert"] svg,
    [data-baseweb="notification"] svg,
    div[role="alert"] svg {{
        fill: var(--ef-accent) !important;
        color: var(--ef-accent) !important;
    }}

    /* Global Containers & Cards in Liquid Glass Theme */
    .stApp {{
        background: var(--ef-bg-radial) !important;
        background-color: var(--ef-bg) !important;
        color: var(--ef-text) !important;
    }}

    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stMain"] {{
        background: transparent !important;
        color: var(--ef-text) !important;
    }}

    [data-testid="stMainBlockContainer"] [class*="stColumn"] {{
        background: transparent !important;
    }}

    [data-testid="stSelectbox"] [data-baseweb="select"] *,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stNumberInput"] [data-baseweb="input"] *,
    [data-testid="stTextInput"] [data-baseweb="input"] *,
    [data-testid="stTextArea"] [data-baseweb="textarea"] * {{
        background: var(--ef-surface-solid) !important;
        color: var(--ef-text) !important;
        -webkit-text-fill-color: var(--ef-text) !important;
        border-color: var(--ef-line) !important;
    }}

    hr {{
        border-color: var(--ef-line) !important;
    }}

    footer {{ visibility: hidden; }}

    .ef-question {{
        padding: 24px 4px;
        border-top: 1px solid var(--ef-line);
    }}

    .ef-question:last-child {{
        border-bottom: 1px solid var(--ef-line);
    }}

    .ef-question-meta {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        color: var(--ef-muted) !important;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}

    .ef-type {{
        border: 1px solid var(--ef-line);
        border-radius: 999px;
        padding: 4px 8px;
        background: var(--ef-surface-alt);
        color: var(--ef-accent) !important;
        font-size: 11px;
        letter-spacing: 0.06em;
    }}

    .ef-quality {{
        border-radius: 999px;
        padding: 4px 8px;
        border: 1px solid var(--ef-line);
        background: var(--ef-surface-alt);
        font-size: 11px;
        letter-spacing: 0.04em;
        text-transform: none;
    }}

    .ef-quality-ready {{
        color: var(--ef-accent) !important;
    }}

    .ef-quality-review {{
        color: var(--ef-danger) !important;
    }}

    .ef-quality-score {{
        margin-left: auto;
        border: 1px solid var(--ef-line);
        border-radius: 999px;
        padding: 4px 9px;
        background: var(--ef-surface-alt);
        color: var(--ef-text) !important;
        font-size: 11px;
        letter-spacing: 0.04em;
    }}

    .ef-quality-details {{
        display: grid;
        grid-template-columns: repeat(5, minmax(90px, 1fr));
        gap: 8px;
        margin: 16px 0 4px;
    }}

    .ef-quality-detail {{
        border: 1px solid var(--ef-line);
        border-radius: 7px;
        background: var(--ef-surface);
        padding: 8px 9px;
        color: var(--ef-muted) !important;
        font-size: 11px;
    }}

    .ef-question h3 {{
        margin: 0 0 14px;
        font-size: 22px;
        line-height: 1.4;
    }}

    .ef-option,
    .ef-answer {{
        font-size: 16px;
    }}

    .ef-options {{
        display: grid;
        gap: 7px;
        margin: 12px 0 16px;
    }}

    .ef-option {{
        max-width: 780px;
        padding: 9px 12px;
        border: 1px solid var(--ef-line);
        border-radius: 7px;
        background: var(--ef-surface);
        color: var(--ef-text);
        font-size: 14px;
    }}

    .ef-answer {{
        display: grid;
        grid-template-columns: 82px 1fr;
        gap: 10px;
        margin-top: 14px;
        font-size: 14px;
    }}

    .ef-answer-label {{
        color: var(--ef-muted) !important;
        font-weight: 700;
    }}

    .ef-summary {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 18px;
    }}

    .ef-summary span {{
        border: 1px solid var(--ef-line);
        border-radius: 7px;
        background: var(--ef-surface);
        padding: 7px 10px;
        color: var(--ef-muted) !important;
        font-size: 13px;
    }}

    .ef-about-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
        margin-top: 18px;
    }}

    .ef-about-card {{
        min-height: 150px;
        border: 1px solid var(--ef-line);
        border-radius: 10px;
        background: var(--ef-surface);
        padding: 20px;
    }}

    .ef-about-card h3 {{
        margin: 0 0 8px;
        font-size: 16px;
    }}

    .ef-about-card p {{
        margin: 0;
        color: var(--ef-muted) !important;
        line-height: 1.65;
    }}

    @media (max-width: 768px) {{
        .block-container {{
            padding-top: 0 !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-bottom: 3rem !important;
        }}
        .st-key-ef_navbar,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.ef-nav-marker),
        div[data-testid="stElementContainer"]:has(.ef-nav-marker) {{
            margin-left: -1rem !important;
            margin-right: -1rem !important;
            padding: 0.65rem 1rem !important;
        }}
        .ef-brand-subtitle {{ display: none !important; }}
        .ef-brand-logo {{ width: 36px !important; height: 36px !important; font-size: 14px !important; }}
        .ef-brand-title {{ font-size: 19px !important; }}
        .st-key-ef_navbar button {{
            min-height: 36px !important;
            height: 36px !important;
            font-size: 11.5px !important;
            padding: 0 6px !important;
        }}
        .ef-page-intro {{ grid-template-columns: 1fr; }}
        .ef-page-intro h1 {{ font-size: 34px; }}
        .ef-about-grid {{ grid-template-columns: 1fr; }}
        .ef-answer {{ grid-template-columns: 72px 1fr; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def show_page_intro(label, title, description):
    st.markdown(
        f"""
        <div class="ef-page-intro">
            <div>
                <div class="ef-kicker">{label}</div>
                <h1>{title}</h1>
                <p>{description}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def reset_exam():
    keys = [
        "generated",
        "study_material",
        "topic",
        "difficulty",
        "question_types",
        "type_counts",
        "num_questions",
        "submitted",
        "score",
        "answers",
    ]
    for key in keys:
        st.session_state.pop(key, None)

    for key in list(st.session_state.keys()):
        if key.startswith("answer_"):
            st.session_state.pop(key, None)

    st.session_state.active_page = "Generate"


def start_new_exam():
    reset_exam()
    st.session_state.nav_selection = "Generate"


def distribute_questions(total, selected_types):
    if not selected_types:
        return {}

    base = total // len(selected_types)
    remainder = total % len(selected_types)
    return {
        question_type: base + (1 if index < remainder else 0)
        for index, question_type in enumerate(selected_types)
    }


def format_type_counts(type_counts):
    return "\n".join(
        f"- {question_type}: exactly {count}"
        for question_type, count in type_counts.items()
    )


def validate_questions(questions, type_counts):
    if not isinstance(questions, list):
        raise ValueError("The AI response does not contain a valid question list.")

    if len(questions) != sum(type_counts.values()):
        raise ValueError("The generated question count does not match the requested count.")

    actual_counts = {key: 0 for key in type_counts}

    for question in questions:
        question_type = question.get("type")
        if question_type not in actual_counts:
            raise ValueError(f"Unexpected question type: {question_type}")

        actual_counts[question_type] += 1

        if not question.get("question") or not question.get("correct_answer"):
            raise ValueError("A question is missing its question text or correct answer.")

        if not question.get("explanation"):
            raise ValueError("A question is missing its explanation.")

        options = question.get("options", [])

        if question_type == "MCQ" and len(options) != 4:
            raise ValueError("Every MCQ must have exactly four options.")

        if question_type == "True/False":
            if options != ["True", "False"]:
                raise ValueError('True/False questions must have ["True", "False"] options.')
            if question["correct_answer"] not in ["True", "False"]:
                raise ValueError("A True/False answer must be exactly True or False.")

        if question_type == "Short Answer" and options:
            raise ValueError("Short Answer questions must not have options.")

    if actual_counts != type_counts:
        raise ValueError("The generated distribution does not match the requested distribution.")


def check_question_quality(question, source_text="", topic="", difficulty=""):
    text = str(question.get("question", "")).strip()
    answer = str(question.get("correct_answer", "")).strip()
    explanation = str(question.get("explanation", "")).strip()
    question_type = question.get("type")
    options = question.get("options", [])

    completeness = 20
    if not text or len(text) < 12:
        completeness -= 12
    if not answer:
        completeness -= 8
    if not explanation:
        completeness -= 8

    format_score = 20
    if question_type == "MCQ":
        if len(options) != 4 or len(set(options)) != 4 or answer not in options:
            format_score -= 12
    elif question_type == "True/False":
        if options != ["True", "False"] or answer not in ("True", "False"):
            format_score -= 12
    elif question_type == "Short Answer":
        if options:
            format_score -= 12
    else:
        format_score = 0

    combined_text = f"{text} {answer} {explanation}".lower()
    stop_words = {
        "the", "a", "an", "and", "or", "of", "to", "in", "on", "for",
        "with", "what", "which", "why", "how", "is", "are", "was",
    }

    def meaningful_words(value):
        return {
            word.strip(".,;:?()[]{}\"'")
            for word in str(value).lower().split()
            if len(word.strip(".,;:?()[]{}\"'")) >= 5
            and word.strip(".,;:?()[]{}\"'") not in stop_words
        }

    source_words = meaningful_words(source_text)
    combined_words = meaningful_words(combined_text)
    topic_words = meaningful_words(topic)
    expected_words = source_words | topic_words

    if expected_words:
        overlap = len(combined_words & expected_words)
        relevance = min(25, round(overlap * 5))
    else:
        relevance = 12

    clarity = 20
    if len(text) < 20 or len(text) > 260:
        clarity -= 8
    if not text.endswith(("?", ".", "!")):
        clarity -= 4
    if explanation and len(explanation) < 25:
        clarity -= 4
    placeholder_terms = ("lorem", "placeholder", "example question", "n/a")
    if any(term in combined_text for term in placeholder_terms):
        clarity = 0

    specificity = 15
    if answer.lower() in ("true", "false", "yes", "no"):
        specificity = 12
    if len(answer) < 2:
        specificity -= 8
    if len(explanation) >= 40:
        specificity += 0
    elif len(explanation) < 20:
        specificity -= 5
    specificity = max(0, min(15, specificity))

    score = max(
        0,
        min(
            100,
            max(0, completeness)
            + max(0, format_score)
            + max(0, relevance)
            + max(0, clarity)
            + max(0, specificity),
        ),
    )

    if score >= 85:
        label = "Excellent"
    elif score >= 70:
        label = "Good"
    elif score >= 50:
        label = "Needs review"
    else:
        label = "Low quality"

    return {
        "score": score,
        "label": label,
        "breakdown": {
            "Completeness": max(0, completeness),
            "Format": max(0, format_score),
            "Source relevance": max(0, relevance),
            "Clarity": max(0, clarity),
            "Specificity": max(0, specificity),
        },
    }


def format_question_set(questions, topic, difficulty, source_text=""):
    lines = [
        "EXAMFORGE — GENERATED QUESTION SET",
        f"Topic: {topic}",
        f"Difficulty: {difficulty}",
        "",
    ]

    for index, question in enumerate(questions, start=1):
        quality = check_question_quality(question, source_text, topic, difficulty)
        lines.append(
            f"{index}. [{question['type']}] "
            f"[Quality: {quality['label']} - {quality['score']}/100]"
            f" {question['question']}"
        )
        for option in question.get("options", []):
            lines.append(f"   {option}")
        lines.append(f"Answer: {question['correct_answer']}")
        lines.append(f"Explanation: {question.get('explanation', '')}")
        lines.append("")

    return "\n".join(lines)


def create_exam():
    show_page_intro(
        "QUESTION GENERATOR",
        "Create an assessment",
        "Turn educational material into a balanced question set for your next lesson or examination.",
    )

    st.markdown('<div class="ef-section"><div class="ef-section-heading">Study material</div>', unsafe_allow_html=True)
    st.markdown('<div class="ef-section-copy">Upload the document that should provide the source material.</div></div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload PDF or TXT",
        type=["pdf", "txt"],
        help="Supported formats: PDF and TXT",
    )

    st.markdown('<div class="ef-section"><div class="ef-section-heading">Question requirements</div>', unsafe_allow_html=True)
    st.markdown('<div class="ef-section-copy">Set the topic, difficulty and individual format counts.</div></div>', unsafe_allow_html=True)

    topic = st.text_input("Topic", placeholder="e.g. Photosynthesis")
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    mcq_count = st.number_input("MCQ", min_value=0, max_value=30, value=5, step=1)
    tf_count = st.number_input("True / False", min_value=0, max_value=30, value=2, step=1)
    short_count = st.number_input("Short Answer", min_value=0, max_value=30, value=2, step=1)

    type_counts = {
        name: int(count)
        for name, count in (
            ("MCQ", mcq_count),
            ("True/False", tf_count),
            ("Short Answer", short_count),
        )
        if int(count) > 0
    }

    num_questions = sum(type_counts.values())
    question_types = list(type_counts)

    summary_parts = [f"{count} {name}" for name, count in type_counts.items()]
    st.markdown(
        f'<div class="ef-summary"><span>{num_questions} total</span>'
        + "".join(f"<span>{part}</span>" for part in summary_parts)
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("")
    generate_clicked = st.button("Generate question set", type="primary", use_container_width=True)
    st.caption(
        "Generation may occasionally fail or take longer than expected due to API availability, "
        "rate limits or network issues. If generation fails, please try again."
    )

    if not generate_clicked:
        return

    if uploaded_file is None:
        st.error("Please upload a PDF or TXT file.")
        return
    if not topic.strip():
        st.error("Please enter a topic.")
        return
    if not question_types:
        st.error("Please select at least one question format.")
        return
    if num_questions > 30:
        st.error("The combined number of questions cannot exceed 30.")
        return

    question_type_text = format_type_counts(type_counts)

    if not API_KEY:
        st.error("Gemini API key is not configured.")
        st.info("Add GEMINI_API_KEY to Streamlit Secrets or to the local .env file.")
        return

    try:
        with st.status("Extracting text from your document...", expanded=True) as extraction_status:
            st.write(f"Reading: {uploaded_file.name}")

            def update_extraction_progress(current_page, total_pages):
                st.write(f"Extracted page {current_page} of {total_pages}")

            study_material = extract_text(
                uploaded_file.name,
                uploaded_file.getvalue(),
                progress_callback=update_extraction_progress,
            )

            st.write(f"Text extraction complete — {len(study_material):,} characters found")
            extraction_status.update(
                label="Text extracted successfully",
                state="complete",
                expanded=False,
            )

        with st.status("Connecting to Gemini...", expanded=True) as generation_status:
            def update_generation_progress(attempt, max_attempts, message=None):
                if message:
                    st.write(f"Attempt {attempt}/{max_attempts}: {message}")
                else:
                    st.write(f"Attempt {attempt}/{max_attempts}: Sending question request...")

            generated = generate_questions(
                study_material,
                topic,
                difficulty,
                question_type_text,
                num_questions,
                progress_callback=update_generation_progress,
                max_attempts=5,
            )

            st.write("Gemini replied successfully.")
            generation_status.update(
                label="Question generation complete",
                state="complete",
                expanded=False,
            )

        validate_questions(generated["questions"], type_counts)

        st.session_state.generated = generated
        st.session_state.study_material = study_material
        st.session_state.topic = topic
        st.session_state.difficulty = difficulty
        st.session_state.question_types = question_types
        st.session_state.type_counts = type_counts
        st.session_state.num_questions = num_questions
        st.session_state.active_page = "Generated Questions"
        st.session_state.nav_selection = "Generated Questions"
        st.rerun()

    except Exception as error:
        if "generation_status" in locals():
            generation_status.update(
                label="Question generation failed",
                state="error",
                expanded=True,
            )
        st.error(f"Generation failed: {error}")
        st.info("All automatic retries finished. Check the API connection and try again.")


def show_generated_questions():
    questions = st.session_state.generated["questions"]
    type_counts = st.session_state.type_counts

    show_page_intro(
        "FACULTY QUESTION BANK",
        st.session_state.topic,
        f"{st.session_state.difficulty} difficulty · {len(questions)} questions",
    )

    summary_items = "".join(
        f'<span>{count} {name}</span>'
        for name, count in type_counts.items()
    )
    st.markdown(
        f'<div class="ef-summary"><span>{len(questions)} total</span>{summary_items}</div>',
        unsafe_allow_html=True,
    )

    text_output = format_question_set(
        questions,
        st.session_state.topic,
        st.session_state.difficulty,
        st.session_state.study_material,
    )

    action_col1, action_col2, action_col3 = st.columns([1, 1, 1.3])

    with action_col1:
        components.html(
            f"""
            <button id="copy-all" style="
                width:100%; height:42px; border:1px solid var(--ef-line, #dbe5e2);
                border-radius:8px; background:transparent; color:inherit;
                font-family:inherit; font-weight:700; cursor:pointer;">
                Copy all questions
            </button>
            <script>
            document.getElementById("copy-all").addEventListener("click", async () => {{
                await navigator.clipboard.writeText({json.dumps(text_output)});
                const button = document.getElementById("copy-all");
                button.textContent = "Copied";
                setTimeout(() => button.textContent = "Copy all questions", 1600);
            }});
            </script>
            """,
            height=44,
        )

    with action_col2:
        st.download_button(
            "Download TXT",
            data=text_output,
            file_name="examforge_questions.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with action_col3:
        if st.button("Create another question set", use_container_width=True, on_click=start_new_exam):
            pass

    st.markdown("")

    for index, question in enumerate(questions, start=1):
        quality = check_question_quality(
            question,
            st.session_state.study_material,
            st.session_state.topic,
            st.session_state.difficulty,
        )

        st.markdown(
            f"""
            <div class="ef-question">
                <div class="ef-question-meta">
                    <span>Question {index:02d}</span>
                    <span class="ef-type">{question["type"]}</span>
                    <span class="ef-quality-score">
                        Quality {quality["score"]}/100 · {quality["label"]}
                    </span>
                </div>
                <h3>{html.escape(str(question["question"]))}</h3>
            """,
            unsafe_allow_html=True,
        )

        if question["type"] in ("MCQ", "True/False"):
            option_html = "".join(
                f'<div class="ef-option">{html.escape(str(option))}</div>'
                for option in question.get("options", [])
            )
            st.markdown(f'<div class="ef-options">{option_html}</div>', unsafe_allow_html=True)

        breakdown = quality["breakdown"]
        breakdown_items = "".join(
            f'<div class="ef-quality-detail">'
            f'<strong>{html.escape(name)}</strong><br>{value}/'
            f'{25 if name == "Source relevance" else 20 if name in ("Completeness", "Format", "Clarity") else 15}'
            f'</div>'
            for name, value in breakdown.items()
        )
        st.markdown(
            f'<div class="ef-quality-details">{breakdown_items}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
                <div class="ef-answer">
                    <div class="ef-answer-label">Answer</div>
                    <div>{html.escape(str(question["correct_answer"]))}</div>
                </div>
                <div class="ef-answer">
                    <div class="ef-answer-label">Explanation</div>
                    <div>{html.escape(str(question.get("explanation", "No explanation provided.")))}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_about():
    show_page_intro(
        "ABOUT EXAMFORGE",
        "Built for faculty",
        "ExamForge helps faculty members and teaching assistants create focused question sets from educational material.",
    )

    st.markdown('<div class="ef-section-heading">How it works</div>', unsafe_allow_html=True)
    workflow = [
        ("01", "Upload study material", "Use a PDF or TXT document as the source."),
        ("02", "Configure requirements", "Choose a topic, difficulty and question format counts."),
        ("03", "Generate with Gemini", "Create questions, answers and explanations from the source."),
        ("04", "Review the question set", "Copy or download the questions for your examination paper."),
    ]

    for number, title, description in workflow:
        col1, col2 = st.columns([0.12, 1.88])
        with col1:
            st.markdown(f"<h3 style='color:var(--ef-accent)'>{number}</h3>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{title}**")
            st.write(description)

    st.markdown('<div class="ef-section-heading">Supported formats</div>', unsafe_allow_html=True)
    supported = [
        ("Multiple Choice", "Four distinct options with one correct answer."),
        ("True / False", "A clear statement with one two-part answer."),
        ("Short Answer", "A concise written response with an explanation."),
        ("Technology", "Python, Streamlit, Gemini API and PyMuPDF."),
    ]
    for title, description in supported:
        col1, col2 = st.columns([0.3, 1.7])
        with col1:
            st.markdown(f"**{title}**")
        with col2:
            st.write(description)

    st.caption(
        "ExamForge is an academic prototype. Generated questions should be reviewed "
        "before use in formal assessment."
    )


def set_active_page(page_name):
    st.session_state.active_page = page_name
    st.session_state.nav_selection = page_name


def set_theme(theme_name):
    st.session_state.theme = theme_name
    st.session_state.theme_selection = theme_name


has_generated = "generated" in st.session_state and bool(st.session_state.generated.get("questions"))
q_count = len(st.session_state.generated["questions"]) if has_generated else 0
q_btn_label = f"Question Bank ({q_count})" if has_generated else "Question Bank"

with st.container(key="ef_navbar"):
    st.markdown('<div class="ef-nav-marker" style="display:none;"></div>', unsafe_allow_html=True)
    brand_col, nav_col, theme_col = st.columns([1.3, 2.7, 0.7], vertical_alignment="center", gap="medium")

    with brand_col:
        st.markdown(
            '<div class="ef-brand-container">'
            '<div class="ef-brand-logo">EF</div>'
            '<div class="ef-brand-text">'
            '<div class="ef-brand-title">Exam<span>Forge</span></div>'
            '<div class="ef-brand-subtitle">Assessment Architecture</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with nav_col:
        nav1, nav2, nav3 = st.columns(3)
        with nav1:
            st.button(
                "Create Exam",
                key="nav_generate",
                type="primary" if st.session_state.active_page == "Generate" else "secondary",
                use_container_width=True,
                on_click=set_active_page,
                args=("Generate",),
            )
        with nav2:
            st.button(
                q_btn_label,
                key="nav_generated",
                type="primary" if st.session_state.active_page == "Generated Questions" else "secondary",
                use_container_width=True,
                on_click=set_active_page,
                args=("Generated Questions",),
                help="Inspect and export generated questions" if has_generated else "Generate an exam first",
            )
        with nav3:
            st.button(
                "Overview",
                key="nav_about",
                type="primary" if st.session_state.active_page == "About" else "secondary",
                use_container_width=True,
                on_click=set_active_page,
                args=("About",),
            )

    with theme_col:
        if st.session_state.theme == "Light":
            st.button(
                "Dark Mode",
                key="theme_toggle",
                type="secondary",
                help="Switch to dark theme",
                use_container_width=True,
                on_click=set_theme,
                args=("Dark",),
            )
        else:
            st.button(
                "Light Mode",
                key="theme_toggle",
                type="secondary",
                help="Switch to light theme",
                use_container_width=True,
                on_click=set_theme,
                args=("Light",),
            )

st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

page = st.session_state.active_page

if page == "Generate":
    create_exam()
elif page == "Generated Questions":
    if "generated" in st.session_state:
        show_generated_questions()
    else:
        show_page_intro(
            "GENERATED QUESTIONS",
            "No question set yet",
            "Generate a question set before opening this page.",
        )
        st.info("Use Generate to create questions from your study material.")
elif page == "About":
    show_about()
