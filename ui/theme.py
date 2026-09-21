"""
Theme & Visual Styling Engine for E-Commerce IQ.

Provides dynamic 3-theme runtime switching with unique backgrounds,
custom font imports, cards, button styling, and Plotly chart color schemes:
1. Corporate Executive (Clean Slate & Navy Blue)
2. Modern Dark Mode (Obsidian & Glowing Cyber Accents)
3. Luxury Minimalist (Ivory, Deep Charcoal & Warm Gold)
"""

from typing import Any, Dict
import streamlit as st


THEMES: Dict[str, Dict[str, Any]] = {
    "corporate": {
        "id": "corporate",
        "name": "Corporate Executive",
        "icon": "🏛️",
        "tagline": "Clean white/slate background with deep navy blue & emerald green",
        "plotly_template": "plotly_white",
        "primary_color": "#1E3A8A",
        "accent_color": "#059669",
        "bg_color": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "text_color": "#0F172A",
        "secondary_text": "#64748B",
        "border_color": "#E2E8F0",
        "css": """
        <style>
            /* Corporate Executive Theme */
            .stApp {
                background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 45%, #F1F5F9 100%) !important;
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
        </style>
        """
    },
    "dark": {
        "id": "dark",
        "name": "Modern Dark Mode",
        "icon": "⚡",
        "tagline": "Sleek obsidian/charcoal background with glowing neon cyan & purple",
        "plotly_template": "plotly_dark",
        "primary_color": "#22D3EE",
        "accent_color": "#A855F7",
        "bg_color": "#0B0F19",
        "card_bg": "#131B2E",
        "text_color": "#F8FAFC",
        "secondary_text": "#94A3B8",
        "border_color": "#1E293B",
        "css": """
        <style>
            /* Modern Dark Mode Theme */
            .stApp {
                background: radial-gradient(circle at 15% 15%, #111827 0%, #0B0F19 55%, #030712 100%) !important;
                color: #F8FAFC !important;
            }
            [data-testid="stSidebar"] {
                background: #0B1120 !important;
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
                box-shadow: 0 4px 20px rgba(6, 182, 212, 0.07) !important;
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
            div[data-baseweb="input"], input, textarea {
                background-color: #1E293B !important;
                color: #FFFFFF !important;
                border-color: #334155 !important;
            }
            div[data-testid="stChatInput"] textarea {
                background-color: #131B2E !important;
                color: #FFFFFF !important;
            }
        </style>
        """
    },
    "luxury": {
        "id": "luxury",
        "name": "Luxury Minimalist",
        "icon": "⚜️",
        "tagline": "Soft ivory/cream background with deep charcoal & warm gold accents",
        "plotly_template": "plotly_white",
        "primary_color": "#B45309",
        "accent_color": "#D97706",
        "bg_color": "#FAF7F2",
        "card_bg": "#FFFFFF",
        "text_color": "#1C1917",
        "secondary_text": "#78716C",
        "border_color": "#E7DFD5",
        "css": """
        <style>
            /* Luxury Minimalist Theme */
            .stApp {
                background: linear-gradient(135deg, #FAF7F2 0%, #F5EFEB 50%, #EDE6DE 100%) !important;
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
        </style>
        """
    }
}


def apply_theme() -> str:
    """
    Renders the theme selector in the sidebar and injects the corresponding CSS.
    Returns the active theme ID ('corporate', 'dark', or 'luxury').
    """
    if "current_theme" not in st.session_state:
        st.session_state.current_theme = "corporate"

    # Always import Google Font 'Caveat' for Shoplytic handwriting
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
    theme_options = [
        f"{THEMES[k]['icon']} {THEMES[k]['name']}" for k in theme_keys
    ]

    current_idx = 0
    for idx, k in enumerate(theme_keys):
        if k == st.session_state.current_theme:
            current_idx = idx
            break

    st.sidebar.markdown(
        """
        <div style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">
            🎨 Theme & Vibe
        </div>
        """,
        unsafe_allow_html=True
    )

    selected_label = st.sidebar.selectbox(
        "Theme & Vibe",
        theme_options,
        index=current_idx,
        label_visibility="collapsed"
    )

    # Resolve selected key
    selected_theme_key = "corporate"
    for k in theme_keys:
        if THEMES[k]["name"] in selected_label:
            selected_theme_key = k
            break

    st.session_state.current_theme = selected_theme_key

    # Inject theme-specific CSS
    active_theme = THEMES[selected_theme_key]
    st.markdown(active_theme["css"], unsafe_allow_html=True)

    return selected_theme_key


def get_current_theme() -> Dict[str, Any]:
    """Return dictionary of the active theme properties."""
    current_key = st.session_state.get("current_theme", "corporate")
    return THEMES.get(current_key, THEMES["corporate"])
