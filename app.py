import html
import json

import streamlit as st
import streamlit.components.v1 as components

from config import API_KEY
from modules.document_processor import extract_text
from modules.question_generator import generate_questions, sanitize_generated_questions


st.set_page_config(
    page_title="ExamForge",
    page_icon="EF",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

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
        "dock_bg": "rgba(226, 238, 252, 0.7)",
        "dock_border": "rgba(196, 218, 245, 0.75)",
        "dock_hover": "rgba(255, 255, 255, 0.65)",
        "dock_active_bg": "#ffffff",
        "dock_active_text": "#1d68ed",
        "dock_active_border": "rgba(196, 218, 245, 0.95)",
        "dock_active_shadow": "rgba(20, 50, 95, 0.08)",
        "card_bg": "rgba(255, 255, 255, 0.88)",
        "card_border": "rgba(196, 218, 245, 0.85)",
        "card_shadow": "0 8px 30px -4px rgba(20, 50, 95, 0.06)",
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
        "dock_bg": "rgba(16, 28, 48, 0.8)",
        "dock_border": "rgba(37, 62, 100, 0.85)",
        "dock_hover": "rgba(255, 255, 255, 0.06)",
        "dock_active_bg": "rgba(56, 189, 248, 0.16)",
        "dock_active_text": "#38bdf8",
        "dock_active_border": "rgba(56, 189, 248, 0.4)",
        "dock_active_shadow": "rgba(56, 189, 248, 0.15)",
        "card_bg": "rgba(14, 24, 42, 0.88)",
        "card_border": "rgba(37, 62, 100, 0.85)",
        "card_shadow": "0 8px 30px -4px rgba(0, 0, 0, 0.5)",
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
        --ef-dock-bg: {palette["dock_bg"]};
        --ef-dock-border: {palette["dock_border"]};
        --ef-dock-hover: {palette["dock_hover"]};
        --ef-dock-active-bg: {palette["dock_active_bg"]};
        --ef-dock-active-text: {palette["dock_active_text"]};
        --ef-dock-active-border: {palette["dock_active_border"]};
        --ef-dock-active-shadow: {palette["dock_active_shadow"]};
        --ef-card-bg: {palette["card_bg"]};
        --ef-card-border: {palette["card_border"]};
        --ef-card-shadow: {palette["card_shadow"]};
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

    header,
    .stAppHeader,
    [data-testid="stHeader"],
    .stAppToolbar,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    div[data-testid="stElementContainer"]:has(style),
    div.element-container:has(style) {{
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        max-height: 0 !important;
        visibility: hidden !important;
        opacity: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
        pointer-events: none !important;
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
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.ef-nav-marker) {{
        position: sticky !important;
        top: 14px !important;
        z-index: 99999 !important;
        background: var(--ef-nav-glass) !important;
        backdrop-filter: blur(28px) saturate(210%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(210%) !important;
        border: 1px solid var(--ef-line) !important;
        border-radius: 20px !important;
        margin-top: 14px !important;
        margin-bottom: 22px !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        padding: 0.85rem 1.75rem !important;
        box-shadow: 0 10px 30px -5px var(--ef-nav-shadow), inset 0 1px 1px 0 var(--ef-glass-highlight) !important;
        transition: background 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, border-radius 0.3s ease !important;
    }}

    .st-key-ef_navbar [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-ef_navbar [data-testid="stVerticalBlock"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }}

    .st-key-ef_navbar [data-testid="stHorizontalBlock"] {{
        align-items: center !important;
    }}

    .st-key-ef_navbar [data-testid="stElementContainer"] {{
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
        overflow: visible !important;
    }}

    .st-key-ef_navbar [data-testid="stMarkdownContainer"],
    .st-key-ef_navbar [data-testid="stMarkdownContainer"] p {{
        overflow: visible !important;
    }}

    /* Modern & Bigger Brand Title */
    .ef-brand-container {{
        display: inline-flex;
        align-items: center;
        user-select: none;
        cursor: pointer;
        padding: 4px 0 6px 0;
        overflow: visible !important;
        transition: transform 0.2s ease;
    }}

    .ef-brand-container:hover {{
        transform: translateY(-1px);
    }}

    .ef-brand-title {{
        font-family: "Manrope", sans-serif;
        font-size: clamp(34px, 3.4vw, 44px);
        font-weight: 800;
        letter-spacing: -0.045em;
        color: var(--ef-text) !important;
        line-height: 1.25 !important;
        display: inline-flex;
        align-items: center;
        padding: 4px 0 10px 0 !important;
        overflow: visible !important;
        white-space: nowrap;
    }}

    .ef-brand-title .ef-title-accent {{
        display: inline-block;
        background: linear-gradient(135deg, var(--ef-accent) 0%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        margin-left: 1px;
        line-height: 1.25 !important;
        padding-bottom: 12px !important;
        margin-bottom: -12px !important;
        overflow: visible !important;
    }}

    .ef-brand-title .ef-title-dot {{
        color: var(--ef-accent) !important;
        -webkit-text-fill-color: var(--ef-accent) !important;
        font-size: 1.15em;
        line-height: 1;
        margin-left: 2px;
        display: inline-block;
    }}

    /* Segmented Navigation Dock in Navbar */
    .st-key-ef_navbar [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stHorizontalBlock"] {{
        background: var(--ef-dock-bg) !important;
        border: 1px solid var(--ef-dock-border) !important;
        border-radius: 9999px !important;
        padding: 4px 5px !important;
        gap: 4px !important;
        box-shadow: inset 0 1px 2px rgba(15, 35, 75, 0.04) !important;
        backdrop-filter: blur(12px) !important;
    }}

    .st-key-ef_navbar [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) button {{
        height: 38px !important;
        min-height: 38px !important;
        border-radius: 9999px !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        padding: 0 16px !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        color: var(--ef-muted) !important;
        transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1) !important;
    }}

    .st-key-ef_navbar [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) button[kind="secondary"]:hover {{
        background: var(--ef-dock-hover) !important;
        color: var(--ef-text) !important;
        transform: none !important;
        box-shadow: none !important;
    }}

    .st-key-ef_navbar [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) button[kind="primary"] {{
        background: var(--ef-dock-active-bg) !important;
        color: var(--ef-dock-active-text) !important;
        border: 1px solid var(--ef-dock-active-border) !important;
        box-shadow: 0 3px 12px var(--ef-dock-active-shadow), inset 0 1px 1px 0 rgba(255, 255, 255, 0.8) !important;
        font-weight: 700 !important;
        transform: none !important;
    }}

    .st-key-ef_navbar [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) button[kind="primary"] * {{
        color: var(--ef-dock-active-text) !important;
        -webkit-text-fill-color: var(--ef-dock-active-text) !important;
    }}

    /* Right Action Buttons (Theme toggle & GitHub) */
    .st-key-ef_navbar [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) button,
    .st-key-ef_navbar [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) a {{
        height: 38px !important;
        min-height: 38px !important;
        border-radius: 9999px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        background: var(--ef-surface) !important;
        border: 1px solid var(--ef-line) !important;
        color: var(--ef-text) !important;
        box-shadow: var(--ef-glass-specular) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-decoration: none !important;
        transition: all 0.2s ease !important;
        padding: 0 12px !important;
    }}

    .st-key-ef_navbar [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) button:hover,
    .st-key-ef_navbar [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) a:hover {{
        background: var(--ef-surface-solid) !important;
        border-color: var(--ef-accent) !important;
        color: var(--ef-accent) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px var(--ef-nav-glow) !important;
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

    button[kind="secondary"],
    [data-testid="stLinkButton"] a,
    div[data-testid="stLinkButton"] a,
    a[kind="secondary"],
    a[data-testid^="stBaseButton"] {{
        background: var(--ef-surface) !important;
        background-color: var(--ef-surface) !important;
        border: 1px solid var(--ef-line) !important;
        color: var(--ef-text) !important;
        border-radius: 8px !important;
        min-height: 38px !important;
        text-decoration: none !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }}

    button[kind="secondary"] *,
    button[kind="secondary"] p,
    button[kind="secondary"] span,
    [data-testid="stLinkButton"] a *,
    [data-testid="stLinkButton"] a p,
    [data-testid="stLinkButton"] a span,
    a[kind="secondary"] *,
    a[kind="secondary"] p,
    a[kind="secondary"] span,
    a[data-testid^="stBaseButton"] *,
    a[data-testid^="stBaseButton"] p,
    a[data-testid^="stBaseButton"] span {{
        color: var(--ef-text) !important;
        -webkit-text-fill-color: var(--ef-text) !important;
    }}

    button[kind="secondary"]:hover,
    [data-testid="stLinkButton"] a:hover,
    div[data-testid="stLinkButton"] a:hover,
    a[kind="secondary"]:hover,
    a[data-testid^="stBaseButton"]:hover {{
        background: var(--ef-surface-alt) !important;
        background-color: var(--ef-surface-alt) !important;
        border-color: var(--ef-accent) !important;
        color: var(--ef-accent) !important;
        text-decoration: none !important;
    }}

    button[kind="secondary"]:hover *,
    button[kind="secondary"]:hover p,
    button[kind="secondary"]:hover span,
    [data-testid="stLinkButton"] a:hover *,
    [data-testid="stLinkButton"] a:hover p,
    [data-testid="stLinkButton"] a:hover span,
    a[kind="secondary"]:hover *,
    a[kind="secondary"]:hover p,
    a[kind="secondary"]:hover span,
    a[data-testid^="stBaseButton"]:hover *,
    a[data-testid^="stBaseButton"]:hover p,
    a[data-testid^="stBaseButton"]:hover span {{
        color: var(--ef-accent) !important;
        -webkit-text-fill-color: var(--ef-accent) !important;
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

    .ef-question-card {{
        background: var(--ef-card-bg) !important;
        border: 1px solid var(--ef-card-border) !important;
        border-radius: 16px !important;
        padding: 24px 28px !important;
        margin-bottom: 22px !important;
        box-shadow: var(--ef-card-shadow) !important;
        backdrop-filter: blur(16px) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
    }}

    .ef-question-card:hover {{
        transform: translateY(-2px) !important;
        border-color: var(--ef-accent) !important;
        box-shadow: 0 12px 32px -4px var(--ef-nav-glow) !important;
    }}

    .ef-question-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 14px;
        flex-wrap: wrap;
    }}

    .ef-question-tags {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .ef-tag-index {{
        font-family: "Manrope", sans-serif;
        font-weight: 800;
        font-size: 12px;
        color: var(--ef-accent) !important;
        background: var(--ef-accent-soft);
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid var(--ef-line);
        letter-spacing: 0.04em;
    }}

    .ef-tag-type {{
        font-size: 11.5px;
        font-weight: 700;
        color: var(--ef-muted) !important;
        background: var(--ef-surface-alt);
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid var(--ef-line);
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}

    .ef-tag-quality {{
        font-size: 12px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        border: 1px solid var(--ef-line);
        background: var(--ef-surface);
    }}

    .ef-quality-high {{
        color: #059669 !important;
        background: rgba(5, 150, 105, 0.08) !important;
        border-color: rgba(5, 150, 105, 0.25) !important;
    }}

    .ef-quality-good {{
        color: var(--ef-accent) !important;
        background: var(--ef-accent-soft) !important;
        border-color: rgba(29, 104, 237, 0.25) !important;
    }}

    .ef-quality-review {{
        color: #d97706 !important;
        background: rgba(217, 119, 6, 0.08) !important;
        border-color: rgba(217, 119, 6, 0.25) !important;
    }}

    .ef-question-title {{
        font-size: 17.5px;
        font-weight: 600;
        color: var(--ef-text) !important;
        line-height: 1.5;
        margin: 0 0 16px;
    }}

    /* Option choices */
    .ef-options-list {{
        display: grid;
        gap: 8px;
        margin: 14px 0 18px;
    }}

    .ef-option-item {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        border-radius: 10px;
        background: var(--ef-surface-alt);
        border: 1px solid var(--ef-line);
        color: var(--ef-text);
        font-size: 14px;
        transition: background 0.15s ease, border-color 0.15s ease;
    }}

    .ef-option-item:hover {{
        background: var(--ef-surface-solid);
        border-color: var(--ef-accent);
    }}

    .ef-option-bullet {{
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: var(--ef-surface);
        border: 1px solid var(--ef-line);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 700;
        color: var(--ef-muted);
        flex-shrink: 0;
    }}

    /* Correct Answer Callout */
    .ef-solution-box {{
        background: var(--ef-accent-soft) !important;
        border: 1px solid rgba(29, 104, 237, 0.2) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-top: 16px !important;
    }}

    .ef-solution-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 6px;
    }}

    .ef-solution-pill {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--ef-accent) !important;
        background: var(--ef-surface-solid);
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid rgba(29, 104, 237, 0.25);
    }}

    .ef-solution-answer {{
        font-weight: 700;
        font-size: 14.5px;
        color: var(--ef-text) !important;
    }}

    .ef-solution-explanation {{
        font-size: 13.5px;
        color: var(--ef-muted) !important;
        line-height: 1.5;
        margin: 6px 0 0;
    }}

    /* Quality Metrics Grid */
    .ef-metrics-grid {{
        display: grid;
        grid-template-columns: repeat(5, minmax(90px, 1fr));
        gap: 8px;
        margin-top: 14px;
        padding-top: 14px;
        border-top: 1px solid var(--ef-line-subtle);
    }}

    .ef-metric-tile {{
        background: var(--ef-surface);
        border: 1px solid var(--ef-line-subtle);
        border-radius: 8px;
        padding: 6px 10px;
        text-align: center;
    }}

    .ef-metric-name {{
        font-size: 10.5px;
        font-weight: 600;
        color: var(--ef-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    .ef-metric-val {{
        font-size: 13px;
        font-weight: 700;
        color: var(--ef-text) !important;
        margin-top: 2px;
    }}

    /* GitHub Section in Overview */
    .ef-github-panel {{
        background: var(--ef-card-bg) !important;
        border: 1px solid var(--ef-card-border) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        margin: 16px 0 !important;
        box-shadow: var(--ef-card-shadow) !important;
    }}

    .ef-github-left {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}

    .ef-github-repo-name {{
        font-family: "Manrope", sans-serif;
        font-size: 17px;
        font-weight: 700;
        color: var(--ef-text) !important;
    }}

    .ef-github-repo-desc {{
        font-size: 13px;
        color: var(--ef-muted) !important;
        margin-top: 2px;
    }}

    .ef-summary {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
    }}

    .ef-summary span {{
        border: 1px solid var(--ef-line);
        border-radius: 9999px;
        background: var(--ef-surface);
        padding: 6px 12px;
        color: var(--ef-muted) !important;
        font-size: 12.5px;
        font-weight: 600;
    }}

    .ef-about-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
        margin-top: 18px;
    }}

    .ef-about-card {{
        min-height: 140px;
        border: 1px solid var(--ef-card-border);
        border-radius: 14px;
        background: var(--ef-card-bg);
        padding: 20px;
        box-shadow: var(--ef-card-shadow);
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
            margin-top: 8px !important;
            margin-bottom: 16px !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            padding: 0.65rem 1rem !important;
            border-radius: 16px !important;
        }}
        .ef-brand-title {{ font-size: 26px !important; }}
        .st-key-ef_navbar button {{
            min-height: 34px !important;
            height: 34px !important;
            font-size: 11px !important;
            padding: 0 6px !important;
        }}
        .ef-page-intro {{ grid-template-columns: 1fr; }}
        .ef-page-intro h1 {{ font-size: 32px; }}
        .ef-about-grid {{ grid-template-columns: 1fr; }}
        .ef-metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def show_page_intro(label, title, description):
    st.markdown(
        f'<div class="ef-page-intro">'
        f'<div>'
        f'<div class="ef-kicker">{label}</div>'
        f'<h1>{title}</h1>'
        f'<p>{description}</p>'
        f'</div>'
        f'</div>',
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
    questions = sanitize_generated_questions(
        {"questions": st.session_state.generated["questions"]}
    )["questions"]
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
                width:100%; height:40px; border:1px solid var(--ef-line, #c4daf5);
                border-radius:9999px; background:var(--ef-surface, #ffffff); color:var(--ef-text, #0d192e);
                font-family:inherit; font-size:13.5px; font-weight:600; cursor:pointer;
                box-shadow: 0 2px 8px rgba(15,35,75,0.04); transition:all 0.2s ease;">
                Copy all questions
            </button>
            <script>
            document.getElementById("copy-all").addEventListener("click", async () => {{
                await navigator.clipboard.writeText({json.dumps(text_output)});
                const button = document.getElementById("copy-all");
                button.textContent = "Copied to clipboard!";
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

    st.markdown('<div style="height: 14px;"></div>', unsafe_allow_html=True)

    for index, question in enumerate(questions, start=1):
        quality = check_question_quality(
            question,
            st.session_state.study_material,
            st.session_state.topic,
            st.session_state.difficulty,
        )

        score = quality["score"]
        if score >= 80:
            quality_class = "ef-quality-high"
        elif score >= 60:
            quality_class = "ef-quality-good"
        else:
            quality_class = "ef-quality-review"

        options_html = ""
        if question["type"] in ("MCQ", "True/False") and question.get("options"):
            option_items = []
            letters = ["A", "B", "C", "D", "E", "F"]
            for opt_idx, option in enumerate(question.get("options", [])):
                letter = letters[opt_idx] if opt_idx < len(letters) else str(opt_idx + 1)
                opt_text = html.escape(str(option))
                option_items.append(
                    f'<div class="ef-option-item">'
                    f'<span class="ef-option-bullet">{letter}</span>'
                    f'<span>{opt_text}</span>'
                    f'</div>'
                )
            options_html = f'<div class="ef-options-list">{"".join(option_items)}</div>'

        breakdown = quality["breakdown"]
        breakdown_items = "".join(
            f'<div class="ef-metric-tile">'
            f'<div class="ef-metric-name">{html.escape(name)}</div>'
            f'<div class="ef-metric-val">{value}/'
            f'{25 if name == "Source relevance" else 20 if name in ("Completeness", "Format", "Clarity") else 15}'
            f'</div></div>'
            for name, value in breakdown.items()
        )

        explanation = html.escape(str(question.get("explanation", "No explanation provided."))).replace("\n", "<br>")
        correct_ans = html.escape(str(question["correct_answer"])).replace("\n", "<br>")
        q_title = html.escape(str(question["question"])).replace("\n", "<br>")

        card_html = (
            f'<div class="ef-question-card">'
            f'<div class="ef-question-header">'
            f'<div class="ef-question-tags">'
            f'<span class="ef-tag-index">Question {index:02d}</span>'
            f'<span class="ef-tag-type">{question["type"]}</span>'
            f'</div>'
            f'<span class="ef-tag-quality {quality_class}">{quality["label"]} · {score}/100</span>'
            f'</div>'
            f'<div class="ef-question-title">{q_title}</div>'
            f'{options_html}'
            f'<div class="ef-solution-box">'
            f'<div class="ef-solution-header">'
            f'<span class="ef-solution-pill">Answer</span>'
            f'<span class="ef-solution-answer">{correct_ans}</span>'
            f'</div>'
            f'<div class="ef-solution-explanation">{explanation}</div>'
            f'</div>'
            f'<div class="ef-metrics-grid">{breakdown_items}</div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)


def show_about():
    show_page_intro(
        "ABOUT EXAMFORGE",
        "Assessment Engine",
        "ExamForge helps educators, faculty members and students generate rigorous, structured question sets from course material.",
    )

    st.markdown('<div class="ef-section-heading">Developer & Open Source</div>', unsafe_allow_html=True)
    gh_col1, gh_col2 = st.columns([1.8, 1.2], vertical_alignment="center")
    with gh_col1:
        st.markdown(
            '<div class="ef-github-panel" style="margin: 0 !important;">'
            '<div class="ef-github-left">'
            '<svg viewBox="0 0 24 24" width="34" height="34" fill="var(--ef-text)" style="flex-shrink: 0;">'
            '<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>'
            '</svg>'
            '<div>'
            '<div class="ef-github-repo-name">Exam-Forge by @dev-maegor</div>'
            '<div class="ef-github-repo-desc">AI-powered educational assessment generator. Open-source on GitHub.</div>'
            '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with gh_col2:
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            st.link_button("Repository", "https://github.com/dev-maegor/Exam-Forge", use_container_width=True)
        with btn_c2:
            st.link_button("GitHub Profile", "https://github.com/dev-maegor", use_container_width=True)

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="ef-section-heading">How it works</div>', unsafe_allow_html=True)
    workflow = [
        ("01", "Upload study material", "Use a PDF or TXT document as the authoritative source."),
        ("02", "Configure requirements", "Choose a topic, difficulty level and format breakdown."),
        ("03", "Generate with Gemini", "Synthesize balanced questions with validated correct answers and reasoning."),
        ("04", "Review & Export", "Inspect quality metrics, copy or download the question set for your assessment."),
    ]

    for number, title, description in workflow:
        col1, col2 = st.columns([0.12, 1.88])
        with col1:
            st.markdown(f"<h3 style='color:var(--ef-accent); margin:0;'>{number}</h3>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{title}**")
            st.write(description)

    st.markdown('<div class="ef-section-heading">Supported formats</div>', unsafe_allow_html=True)
    supported = [
        ("Multiple Choice", "Four distinct options with one unambiguously correct answer."),
        ("True / False", "A clear conceptual statement with boolean verification."),
        ("Short Answer", "Concise written questions paired with full model answers."),
        ("Technology Stack", "Python, Streamlit, Google Gemini API and PyMuPDF."),
    ]
    for title, description in supported:
        col1, col2 = st.columns([0.3, 1.7])
        with col1:
            st.markdown(f"**{title}**")
        with col2:
            st.write(description)


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
    brand_col, nav_col, action_col = st.columns([1.6, 2.2, 0.85], vertical_alignment="center", gap="medium")

    with brand_col:
        st.markdown(
            '<div class="ef-brand-container">'
            '<div class="ef-brand-title">Exam<span class="ef-title-accent">Forge</span><span class="ef-title-dot">.</span></div>'
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

    with action_col:
        act1, act2 = st.columns([1, 1], gap="small")
        with act1:
            if st.session_state.theme == "Light":
                st.button(
                    "Dark",
                    key="theme_toggle",
                    type="secondary",
                    help="Switch to dark theme",
                    use_container_width=True,
                    on_click=set_theme,
                    args=("Dark",),
                )
            else:
                st.button(
                    "Light",
                    key="theme_toggle",
                    type="secondary",
                    help="Switch to light theme",
                    use_container_width=True,
                    on_click=set_theme,
                    args=("Light",),
                )
        with act2:
            st.link_button(
                "GitHub",
                "https://github.com/dev-maegor/Exam-Forge",
                use_container_width=True,
                help="View source code on GitHub",
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
