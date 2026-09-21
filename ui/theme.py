"""
Theme & Visual Styling Engine for E-Commerce IQ.

Provides dynamic 3-theme runtime switching with unique backgrounds,
custom font imports, cards, button styling, dedicated search option & search history styling,
and Plotly chart color schemes:
1. Corporate Executive (Clean Slate & Navy Blue)
2. Modern Dark Mode (Obsidian & Glowing Cyber Accents)
3. Luxury Minimalist (Ivory, Deep Charcoal & Warm Gold)
"""

from pathlib import Path
from typing import Any, Dict
import streamlit as st


RAW_SVG_CORPORATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22" fill="none"><rect width="24" height="24" rx="6" fill="#1E3A8A"/><path d="M4 20H20M5 20V9L12 4L19 9V20M9 13V20M15 13V20" stroke="#60A5FA" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
RAW_SVG_DARK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22" fill="none"><rect width="24" height="24" rx="6" fill="#0B0F19" stroke="#06B6D4" stroke-width="1.5"/><path d="M12 4L13.8 8.5L18.5 9.5L15 13L16 18L12 15.5L8 18L9 13L5.5 9.5L10.2 8.5L12 4Z" fill="#22D3EE" stroke="#A855F7" stroke-width="0.8"/><circle cx="12" cy="12" r="2" fill="#FFFFFF"/></svg>"""
RAW_SVG_LUXURY = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22" fill="none"><rect width="24" height="24" rx="6" fill="#292524" stroke="#D97706" stroke-width="1.5"/><path d="M5 16L4 8L8.5 11L12 6L15.5 11L20 8L19 16H5Z" fill="#F59E0B" stroke="#FDE68A" stroke-width="0.8"/><circle cx="12" cy="18" r="1.5" fill="#FDE68A"/></svg>"""


THEMES: Dict[str, Dict[str, Any]] = {
    "corporate": {
        "id": "corporate",
        "name": "Corporate Executive",
        "icon": "🏛️",
        "tagline": "Clean white/slate background with deep navy blue & emerald green",
        "raw_svg": RAW_SVG_CORPORATE,
        "plotly_template": "plotly_white",
        "primary_color": "#1E3A8A",
        "accent_color": "#059669",
        "bg_color": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "text_color": "#0F172A",
        "secondary_text": "#64748B",
        "border_color": "#E2E8F0",
        "search_bg": "linear-gradient(135deg, #FFFFFF 0%, #F0F7FF 100%)",
        "search_border": "#BFDBFE",
        "history_bg": "linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%)",
        "history_border": "#DBEAFE",
        "chip_bg": "#FFFFFF",
        "chip_text": "#1E3A8A",
        "css": """
        <style>
            /* Corporate Executive Theme */
            .stApp {
                background: radial-gradient(circle at 12% 12%, #FFFFFF 0%, #F8FAFC 35%, #EFF6FF 100%) !important;
                color: #0F172A !important;
            }
            [data-testid="stSidebar"] {
                background: #FFFFFF !important;
                border-right: 1px solid #E2E8F0 !important;
            }
            .metric-card, .custom-card, div[data-testid="stMetric"] {
                background: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 10px !important;
                padding: 1.2rem !important;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04) !important;
            }
            .metric-title {
                color: #64748B !important;
                font-weight: 600 !important;
                font-size: 0.82rem !important;
                text-transform: uppercase !important;
                letter-spacing: 0.05em !important;
            }
            .metric-value {
                color: #0F172A !important;
                font-weight: 700 !important;
                font-size: 1.8rem !important;
            }
            .shoplytic-title {
                font-family: 'Caveat', cursive, sans-serif !important;
                font-size: 2.3rem !important;
                font-weight: 700 !important;
                color: #2563EB !important;
                letter-spacing: 0.02em !important;
            }

            /* Dedicated Search Option Card - Corporate */
            .search-card-wrapper {
                background: linear-gradient(135deg, #FFFFFF 0%, #F0F7FF 100%) !important;
                border: 1.5px solid #BFDBFE !important;
                border-radius: 12px !important;
                padding: 1.25rem !important;
                box-shadow: 0 8px 24px rgba(30, 58, 138, 0.06) !important;
                margin-bottom: 1.2rem !important;
            }
            .search-card-title {
                font-size: 1.15rem !important;
                font-weight: 700 !important;
                color: #1E3A8A !important;
                margin-bottom: 0.3rem !important;
            }
            .search-card-subtitle {
                font-size: 0.86rem !important;
                color: #64748B !important;
                margin-bottom: 0.8rem !important;
            }

            /* Dedicated Search History Box - Corporate */
            .search-history-wrapper {
                background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%) !important;
                border: 1.5px solid #DBEAFE !important;
                border-radius: 10px !important;
                padding: 1.1rem !important;
                margin-bottom: 1.2rem !important;
                box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03) !important;
            }
            .search-badge {
                background-color: #1E3A8A !important;
                color: #FFFFFF !important;
                padding: 3px 10px !important;
                border-radius: 9999px !important;
                font-size: 0.72rem !important;
                font-weight: 700 !important;
                letter-spacing: 0.04em !important;
                display: inline-block !important;
            }

            /* Inputs & Buttons - Corporate */
            div[data-testid="stTextInput"] input {
                background-color: #FFFFFF !important;
                color: #0F172A !important;
                border: 1.5px solid #CBD5E1 !important;
                border-radius: 8px !important;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: #1E3A8A !important;
                box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.15) !important;
            }
            button[data-testid="stBaseButton-primary"], button[kind="primary"] {
                background-color: #1E3A8A !important;
                color: #FFFFFF !important;
                border: 1px solid #1E3A8A !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2) !important;
                transition: all 0.2s ease !important;
            }
            button[data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover {
                background-color: #1D4ED8 !important;
                box-shadow: 0 6px 16px rgba(30, 58, 138, 0.3) !important;
                color: #FFFFFF !important;
            }
            button[data-testid="stBaseButton-secondary"], button[kind="secondary"] {
                background-color: #FFFFFF !important;
                color: #1E3A8A !important;
                border: 1px solid #BFDBFE !important;
                border-radius: 8px !important;
                transition: all 0.2s ease !important;
            }
            button[data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover {
                background-color: #EFF6FF !important;
                border-color: #1E3A8A !important;
                color: #1E3A8A !important;
            }
        </style>
        """
    },
    "dark": {
        "id": "dark",
        "name": "Modern Dark Mode",
        "icon": "⚡",
        "tagline": "Sleek obsidian/charcoal background with glowing neon cyan & purple",
        "raw_svg": RAW_SVG_DARK,
        "plotly_template": "plotly_dark",
        "primary_color": "#22D3EE",
        "accent_color": "#A855F7",
        "bg_color": "#0B0F19",
        "card_bg": "#131B2E",
        "text_color": "#F8FAFC",
        "secondary_text": "#94A3B8",
        "border_color": "#1E293B",
        "search_bg": "linear-gradient(135deg, #111827 0%, #131B2E 100%)",
        "search_border": "#06B6D4",
        "history_bg": "linear-gradient(135deg, #0F172A 0%, #080D1A 100%)",
        "history_border": "rgba(34, 211, 238, 0.35)",
        "chip_bg": "#1E293B",
        "chip_text": "#38BDF8",
        "css": """
        <style>
            /* Modern Dark Mode Theme */
            .stApp {
                background: radial-gradient(circle at 20% 15%, #131C31 0%, #0B0F19 45%, #030712 100%) !important;
                color: #F8FAFC !important;
            }
            [data-testid="stSidebar"] {
                background: #070B14 !important;
                border-right: 1px solid #1E293B !important;
            }
            h1, h2, h3, h4, h5, h6, p, span, label {
                color: #F8FAFC !important;
            }
            .metric-card, .custom-card, div[data-testid="stMetric"] {
                background: #131B2E !important;
                border: 1px solid #1E293B !important;
                border-radius: 10px !important;
                padding: 1.2rem !important;
                box-shadow: 0 4px 20px rgba(6, 182, 212, 0.08) !important;
            }
            .metric-title {
                color: #94A3B8 !important;
                font-weight: 600 !important;
                font-size: 0.82rem !important;
                text-transform: uppercase !important;
                letter-spacing: 0.05em !important;
            }
            .metric-value {
                color: #38BDF8 !important;
                font-weight: 700 !important;
                font-size: 1.8rem !important;
                text-shadow: 0 0 12px rgba(56, 189, 248, 0.25) !important;
            }
            .shoplytic-title {
                font-family: 'Caveat', cursive, sans-serif !important;
                font-size: 2.3rem !important;
                font-weight: 700 !important;
                color: #22D3EE !important;
                text-shadow: 0 0 15px rgba(34, 211, 238, 0.4) !important;
                letter-spacing: 0.02em !important;
            }

            /* Dedicated Search Option Card - Dark */
            .search-card-wrapper {
                background: linear-gradient(135deg, #111827 0%, #131B2E 100%) !important;
                border: 1.5px solid #06B6D4 !important;
                border-radius: 12px !important;
                padding: 1.25rem !important;
                box-shadow: 0 8px 32px rgba(6, 182, 212, 0.22), inset 0 0 20px rgba(6, 182, 212, 0.05) !important;
                margin-bottom: 1.2rem !important;
            }
            .search-card-title {
                font-size: 1.15rem !important;
                font-weight: 700 !important;
                color: #22D3EE !important;
                text-shadow: 0 0 10px rgba(34, 211, 238, 0.4) !important;
                margin-bottom: 0.3rem !important;
            }
            .search-card-subtitle {
                font-size: 0.86rem !important;
                color: #94A3B8 !important;
                margin-bottom: 0.8rem !important;
            }

            /* Dedicated Search History Box - Dark */
            .search-history-wrapper {
                background: linear-gradient(135deg, #0F172A 0%, #080D1A 100%) !important;
                border: 1.5px solid rgba(34, 211, 238, 0.35) !important;
                border-radius: 10px !important;
                padding: 1.1rem !important;
                margin-bottom: 1.2rem !important;
                box-shadow: 0 4px 25px rgba(0, 0, 0, 0.7), inset 0 0 15px rgba(34, 211, 238, 0.06) !important;
            }
            .search-badge {
                background: linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%) !important;
                color: #030712 !important;
                padding: 3px 10px !important;
                border-radius: 9999px !important;
                font-size: 0.72rem !important;
                font-weight: 800 !important;
                letter-spacing: 0.04em !important;
                display: inline-block !important;
            }

            /* Inputs & Buttons - Dark */
            div[data-testid="stTextInput"] input {
                background-color: #1E293B !important;
                color: #F8FAFC !important;
                border: 1.5px solid #334155 !important;
                border-radius: 8px !important;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: #22D3EE !important;
                box-shadow: 0 0 15px rgba(34, 211, 238, 0.35) !important;
            }
            div[data-baseweb="input"], textarea {
                background-color: #1E293B !important;
                color: #FFFFFF !important;
                border-color: #334155 !important;
            }
            div[data-testid="stChatInput"] textarea {
                background-color: #131B2E !important;
                color: #FFFFFF !important;
            }
            button[data-testid="stBaseButton-primary"], button[kind="primary"] {
                background: linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%) !important;
                color: #030712 !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 700 !important;
                box-shadow: 0 0 20px rgba(6, 182, 212, 0.55) !important;
                transition: all 0.2s ease !important;
            }
            button[data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover {
                background: linear-gradient(135deg, #22D3EE 0%, #A855F7 100%) !important;
                box-shadow: 0 0 25px rgba(6, 182, 212, 0.8) !important;
                color: #000000 !important;
            }
            button[data-testid="stBaseButton-secondary"], button[kind="secondary"] {
                background-color: #131B2E !important;
                color: #38BDF8 !important;
                border: 1px solid rgba(34, 211, 238, 0.4) !important;
                border-radius: 8px !important;
                transition: all 0.2s ease !important;
            }
            button[data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover {
                background-color: #1E293B !important;
                border-color: #22D3EE !important;
                color: #22D3EE !important;
                box-shadow: 0 0 15px rgba(34, 211, 238, 0.3) !important;
            }
        </style>
        """
    },
    "luxury": {
        "id": "luxury",
        "name": "Luxury Minimalist",
        "icon": "⚜️",
        "tagline": "Soft ivory/cream background with deep charcoal & warm gold accents",
        "raw_svg": RAW_SVG_LUXURY,
        "plotly_template": "plotly_white",
        "primary_color": "#B45309",
        "accent_color": "#D97706",
        "bg_color": "#FAF7F2",
        "card_bg": "#FFFFFF",
        "text_color": "#1C1917",
        "secondary_text": "#78716C",
        "border_color": "#E7DFD5",
        "search_bg": "linear-gradient(135deg, #FFFFFF 0%, #FBF8F3 100%)",
        "search_border": "#D97706",
        "history_bg": "linear-gradient(135deg, #FAF7F2 0%, #F5EFEB 100%)",
        "history_border": "#E7DFD5",
        "chip_bg": "#FFFDF9",
        "chip_text": "#92400E",
        "css": """
        <style>
            /* Luxury Minimalist Theme */
            .stApp {
                background: linear-gradient(145deg, #FAF7F2 0%, #F5EFEB 40%, #EDE6DE 100%) !important;
                color: #1C1917 !important;
            }
            [data-testid="stSidebar"] {
                background: #FFFFFF !important;
                border-right: 1px solid #E7DFD5 !important;
            }
            .metric-card, .custom-card, div[data-testid="stMetric"] {
                background: #FFFFFF !important;
                border: 1px solid #E7DFD5 !important;
                border-left: 3px solid #D97706 !important;
                border-radius: 8px !important;
                padding: 1.2rem !important;
                box-shadow: 0 4px 15px rgba(217, 119, 6, 0.06) !important;
            }
            .metric-title {
                color: #78716C !important;
                font-weight: 600 !important;
                font-size: 0.82rem !important;
                text-transform: uppercase !important;
                letter-spacing: 0.08em !important;
            }
            .metric-value {
                color: #1C1917 !important;
                font-weight: 700 !important;
                font-size: 1.8rem !important;
            }
            .shoplytic-title {
                font-family: 'Caveat', cursive, sans-serif !important;
                font-size: 2.3rem !important;
                font-weight: 700 !important;
                color: #B45309 !important;
                letter-spacing: 0.03em !important;
            }

            /* Dedicated Search Option Card - Luxury */
            .search-card-wrapper {
                background: linear-gradient(135deg, #FFFFFF 0%, #FBF8F3 100%) !important;
                border: 1.5px solid #D97706 !important;
                border-left: 5px solid #B45309 !important;
                border-radius: 10px !important;
                padding: 1.25rem !important;
                box-shadow: 0 8px 28px rgba(180, 83, 9, 0.09) !important;
                margin-bottom: 1.2rem !important;
            }
            .search-card-title {
                font-size: 1.15rem !important;
                font-weight: 700 !important;
                color: #B45309 !important;
                margin-bottom: 0.3rem !important;
            }
            .search-card-subtitle {
                font-size: 0.86rem !important;
                color: #78716C !important;
                margin-bottom: 0.8rem !important;
            }

            /* Dedicated Search History Box - Luxury */
            .search-history-wrapper {
                background: linear-gradient(135deg, #FAF7F2 0%, #F5EFEB 100%) !important;
                border: 1.5px solid #E7DFD5 !important;
                border-left: 4px solid #D97706 !important;
                border-radius: 8px !important;
                padding: 1.1rem !important;
                margin-bottom: 1.2rem !important;
                box-shadow: 0 4px 16px rgba(217, 119, 6, 0.05) !important;
            }
            .search-badge {
                background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
                color: #FFFFFF !important;
                padding: 3px 10px !important;
                border-radius: 9999px !important;
                font-size: 0.72rem !important;
                font-weight: 700 !important;
                letter-spacing: 0.05em !important;
                display: inline-block !important;
            }

            /* Inputs & Buttons - Luxury */
            div[data-testid="stTextInput"] input {
                background-color: #FFFFFF !important;
                color: #1C1917 !important;
                border: 1.5px solid #E7DFD5 !important;
                border-radius: 8px !important;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: #D97706 !important;
                box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.15) !important;
            }
            button[data-testid="stBaseButton-primary"], button[kind="primary"] {
                background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
                color: #FFFFFF !important;
                border: 1px solid #B45309 !important;
                border-radius: 8px !important;
                font-weight: 700 !important;
                box-shadow: 0 4px 14px rgba(180, 83, 9, 0.28) !important;
                transition: all 0.2s ease !important;
            }
            button[data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover {
                background: linear-gradient(135deg, #B45309 0%, #92400E 100%) !important;
                box-shadow: 0 6px 20px rgba(180, 83, 9, 0.4) !important;
                color: #FFFFFF !important;
            }
            button[data-testid="stBaseButton-secondary"], button[kind="secondary"] {
                background-color: #FFFFFF !important;
                color: #92400E !important;
                border: 1px solid #FDE68A !important;
                border-radius: 8px !important;
                transition: all 0.2s ease !important;
            }
            button[data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover {
                background-color: #FAF5EF !important;
                border-color: #D97706 !important;
                color: #78350F !important;
                box-shadow: 0 2px 8px rgba(217, 119, 6, 0.12) !important;
            }
        </style>
        """
    }
}


def apply_theme() -> str:
    """
    Renders the theme selector in the sidebar with unique theme logo buttons,
    displays the active theme badge with SVG icon, and injects the corresponding CSS.
    Returns the active theme ID ('corporate', 'dark', or 'luxury').
    """
    if "current_theme" not in st.session_state:
        st.session_state.current_theme = "corporate"

    # Import Google Fonts: 'Caveat' for Shoplytic handwriting & 'Inter' for corporate clean UI
    google_fonts_css = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body, p, div, span, button {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
    </style>
    """
    st.markdown(google_fonts_css, unsafe_allow_html=True)

    theme_keys = list(THEMES.keys())

    st.sidebar.markdown(
        """
        <div style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
            🎨 Theme & Vibe Selection
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Quick-Click Unique Logo Buttons for Theme Selection
    t_col1, t_col2, t_col3 = st.sidebar.columns(3)
    with t_col1:
        if st.button("🏛️ Exec", key="theme_btn_corp", use_container_width=True, help="Corporate Executive (Slate & Navy)"):
            if st.session_state.current_theme != "corporate":
                st.session_state.current_theme = "corporate"
                st.rerun()

    with t_col2:
        if st.button("⚡ Dark", key="theme_btn_dark", use_container_width=True, help="Modern Dark Mode (Obsidian & Cyan)"):
            if st.session_state.current_theme != "dark":
                st.session_state.current_theme = "dark"
                st.rerun()

    with t_col3:
        if st.button("⚜️ Luxe", key="theme_btn_luxe", use_container_width=True, help="Luxury Minimalist (Ivory & Gold)"):
            if st.session_state.current_theme != "luxury":
                st.session_state.current_theme = "luxury"
                st.rerun()

    # 2. Synchronized Dropdown Selectbox
    theme_options = [
        f"{THEMES[k]['icon']} {THEMES[k]['name']}" for k in theme_keys
    ]

    current_idx = 0
    for idx, k in enumerate(theme_keys):
        if k == st.session_state.current_theme:
            current_idx = idx
            break

    selected_label = st.sidebar.selectbox(
        "Theme & Vibe",
        theme_options,
        index=current_idx,
        label_visibility="collapsed",
        key="theme_selectbox"
    )

    # Resolve selected key from selectbox
    for k in theme_keys:
        if THEMES[k]["name"] in selected_label:
            if st.session_state.current_theme != k:
                st.session_state.current_theme = k
                st.rerun()
            break

    active_theme = THEMES[st.session_state.current_theme]

    # 3. Active Theme Badge with Embedded Unique Logo SVG
    st.sidebar.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 9px; padding: 7px 10px; background: {active_theme['card_bg']}; border: 1px solid {active_theme['border_color']}; border-radius: 8px; margin-top: 4px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                {active_theme['raw_svg']}
            </div>
            <div>
                <div style="font-size: 0.8rem; font-weight: 700; color: {active_theme['text_color']}; line-height: 1.2;">
                    {active_theme['name']}
                </div>
                <div style="font-size: 0.68rem; color: {active_theme['secondary_text']};">
                    Active Theme Profile
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Inject active theme CSS
    st.markdown(active_theme["css"], unsafe_allow_html=True)

    return st.session_state.current_theme


def get_current_theme() -> Dict[str, Any]:
    """Return dictionary of the active theme properties."""
    current_key = st.session_state.get("current_theme", "corporate")
    return THEMES.get(current_key, THEMES["corporate"])
