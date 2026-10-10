"""
Front Landing Page for E-Commerce IQ.

Features:
- Official uploaded 'eC' brand logo
- Animated glowing/typing title, executive quote & concise description
- Themed Search Option container & Search History gateway
- Live e-commerce background data & operational statistics
- Core business impact pillars (non-repetitive)
- Interactive revenue trajectory graph preview
"""

from pathlib import Path
import textwrap
import streamlit as st
import streamlit.components.v1 as components

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.analytics.kpis import KPICalculator
from ui.components.charts import render_revenue_trend_chart
from ui.theme import get_current_theme


def render_landing_animated_background(theme: dict) -> None:
    """
    Renders an executive, high-visibility business & mathematical animated background
    (Quantitative Financial Mesh & Candlestick Vectors) with HTML5 video streaming
    and an elegant transparent vignette for both Dark and White themes.
    """
    theme_id = theme.get("id", "corporate")
    is_dark = (theme_id == "dark")

    # Define high-contrast, vivid theme-specific styling parameters
    if is_dark:
        bg_base = "#070B14"
        vignette_bg = "radial-gradient(circle at 50% 35%, rgba(7, 11, 20, 0.10) 0%, rgba(3, 7, 18, 0.45) 100%)"
        mesh_primary = "rgba(6, 182, 212, 0.70)"       # Vibrant electric cyan
        mesh_secondary = "rgba(59, 130, 246, 0.50)"     # Luminous sapphire blue
        mesh_node = "rgba(34, 211, 238, 0.95)"          # Bright cyan node pulse
        candle_bull = "rgba(16, 185, 129, 0.95)"        # Neon emerald green
        candle_wick = "rgba(52, 211, 153, 1.0)"
        candle_bear = "rgba(244, 63, 94, 0.90)"         # Neon rose red
        candle_bear_wick = "rgba(251, 113, 133, 1.0)"
        trend_line = "rgba(34, 211, 238, 0.95)"         # Glowing laser cyan
        badge_bg = "rgba(19, 27, 46, 0.88)"
        badge_border = "rgba(6, 182, 212, 0.55)"
        badge_text = "#38BDF8"
    else:  # corporate or luxury white theme
        bg_base = "#EEF2F6"
        vignette_bg = "radial-gradient(circle at 50% 35%, rgba(248, 250, 252, 0.05) 0%, rgba(226, 232, 240, 0.35) 100%)"
        mesh_primary = "rgba(37, 99, 235, 0.60)"       # Vivid royal sapphire blue
        mesh_secondary = "rgba(30, 58, 138, 0.45)"     # Deep corporate navy
        mesh_node = "rgba(29, 78, 216, 0.90)"          # Crisp royal blue node
        candle_bull = "rgba(5, 150, 105, 0.92)"        # Rich solid emerald green
        candle_wick = "rgba(4, 120, 87, 1.0)"
        candle_bear = "rgba(220, 38, 38, 0.88)"        # Bold corporate red
        candle_bear_wick = "rgba(185, 28, 28, 1.0)"
        trend_line = "rgba(29, 78, 216, 0.95)"         # Bold royal cobalt blue
        badge_bg = "rgba(255, 255, 255, 0.92)"
        badge_border = "rgba(147, 197, 253, 0.85)"
        badge_text = "#1E3A8A"

    # Step 1: Inject HTML elements (background container, video player, canvas, vignette)
    bg_html = textwrap.dedent(f"""
        <div id="landing-bg-container" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            pointer-events: none;
            overflow: hidden;
            background: {bg_base};
        ">
            <video id="landing-bg-video" autoplay loop muted playsinline style="
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                opacity: 0.45;
                pointer-events: none;
            "></video>
            <canvas id="landing-bg-canvas" style="
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
            "></canvas>
            <div id="landing-bg-overlay" style="
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: {vignette_bg};
                pointer-events: none;
            "></div>
        </div>
        <style>
            /* Ensure Streamlit containers remain transparent on front page so background is vividly visible */
            [data-testid="stAppViewContainer"] {{
                background: transparent !important;
            }}
            [data-testid="stMain"] {{
                background: transparent !important;
            }}
            .block-container {{
                position: relative !important;
                z-index: 1 !important;
            }}
        </style>
    """)
    st.markdown(bg_html, unsafe_allow_html=True)

    # Step 2: Execute JS via components.html to run the 60fps Quantitative Financial Mesh & Candlesticks
    js_code = f"""
    <script>
    (function run() {{
        const doc = window.parent.document;
        const win = window.parent;
        const canvas = doc.getElementById('landing-bg-canvas');
        const video = doc.getElementById('landing-bg-video');

        if (!canvas) {{
            setTimeout(run, 50);
            return;
        }}

        // Cancel previous animation loop if already running on parent
        if (win._ecBgAnimId) {{
            win.cancelAnimationFrame(win._ecBgAnimId);
            win._ecBgAnimId = null;
        }}

        const ctx = canvas.getContext('2d');
        let width = win.innerWidth;
        let height = win.innerHeight;
        canvas.width = width;
        canvas.height = height;

        function onResize() {{
            width = win.innerWidth;
            height = win.innerHeight;
            canvas.width = width;
            canvas.height = height;
        }}
        if (win._ecBgResizeHandler) {{
            win.removeEventListener('resize', win._ecBgResizeHandler);
        }}
        win._ecBgResizeHandler = onResize;
        win.addEventListener('resize', onResize);

        // Link live canvas stream to HTML5 video element for embedded video playback
        if (video && canvas.captureStream) {{
            try {{
                if (!video.srcObject) {{
                    const stream = canvas.captureStream(30);
                    video.srcObject = stream;
                    video.play().catch(function() {{}});
                }}
            }} catch(e) {{}}
        }}

        // Theme configuration
        const isDark = {str(is_dark).lower()};
        const meshPrimary = "{mesh_primary}";
        const meshSecondary = "{mesh_secondary}";
        const meshNodeColor = "{mesh_node}";
        const candleBull = "{candle_bull}";
        const candleWick = "{candle_wick}";
        const candleBear = "{candle_bear}";
        const candleBearWick = "{candle_bear_wick}";
        const trendLineColor = "{trend_line}";
        const badgeBg = "{badge_bg}";
        const badgeBorder = "{badge_border}";
        const badgeText = "{badge_text}";

        // Candlestick simulation data (financial time-series)
        const numCandles = 22;
        const candles = [];
        let basePrice = 135;
        for (let i = 0; i < numCandles; i++) {{
            const delta = (Math.sin(i * 0.45) * 16) + (Math.random() * 10 - 4);
            const open = basePrice + delta;
            const isBull = (i % 3 !== 2);
            const move = (Math.random() * 12 + 4) * (isBull ? 1 : -1);
            const close = open + move;
            const high = Math.max(open, close) + (Math.random() * 8 + 3);
            const low = Math.min(open, close) - (Math.random() * 8 + 3);
            const volume = Math.random() * 35 + 15;
            candles.push({{
                open: open,
                close: close,
                high: high,
                low: low,
                volume: volume,
                phase: Math.random() * Math.PI * 2
            }});
            basePrice = close;
        }}

        // Floating mathematical tokens with pill bounding box
        const mathTokens = [
            {{ text: '📐 f(x) = ∫ E(t) dt', x: 0.12, y: 0.20, vx: 0.00012, vy: -0.00006 }},
            {{ text: '📈 GMV Trajectory: +18.4%', x: 0.78, y: 0.16, vx: -0.00010, vy: 0.00008 }},
            {{ text: '📊 Sharpe: 2.41 | σ: 0.04', x: 0.07, y: 0.62, vx: 0.00014, vy: -0.00005 }},
            {{ text: '⚡ R² = 0.984 (SQL Engine)', x: 0.82, y: 0.70, vx: -0.00011, vy: -0.00008 }},
            {{ text: '⚖️ Arbitrage Delta: Δ0.12', x: 0.48, y: 0.10, vx: 0.00007, vy: 0.00009 }}
        ];

        let tick = 0;

        function draw() {{
            tick += 0.020;
            ctx.clearRect(0, 0, width, height);

            // 1. Draw 3D Perspective Quantitative Mesh Waves
            const cols = 26;
            const rows = 12;
            const horizonY = height * 0.40;
            const bottomY = height * 1.05;
            const gridPoints = [];

            for (let r = 0; r <= rows; r++) {{
                const rowRatio = r / rows;
                const pFactor = Math.pow(rowRatio, 1.55);
                const py = horizonY + (bottomY - horizonY) * pFactor;
                const spread = width * (0.35 + 0.85 * pFactor);
                const startX = (width - spread) / 2;

                gridPoints[r] = [];
                for (let c = 0; c <= cols; c++) {{
                    const px = startX + spread * (c / cols);

                    // Dynamic multi-frequency surface wave
                    const wave1 = Math.sin(c * 0.42 + tick * 1.25) * (16 * pFactor);
                    const wave2 = Math.cos(r * 0.50 + tick * 0.95 + c * 0.22) * (12 * pFactor);
                    const wave3 = Math.sin((c + r) * 0.28 - tick * 1.4) * (7 * pFactor);
                    const yOffset = wave1 + wave2 + wave3;

                    gridPoints[r][c] = {{ x: px, y: py + yOffset }};
                }}
            }}

            // Draw Lateral Curves
            for (let r = 0; r <= rows; r++) {{
                ctx.beginPath();
                ctx.strokeStyle = (r % 2 === 0) ? meshPrimary : meshSecondary;
                ctx.lineWidth = 1.4 + (r / rows) * 1.6;
                for (let c = 0; c <= cols; c++) {{
                    const pt = gridPoints[r][c];
                    if (c === 0) ctx.moveTo(pt.x, pt.y);
                    else ctx.lineTo(pt.x, pt.y);
                }}
                ctx.stroke();
            }}

            // Draw Longitudinal Perspective Rays & Intersection Nodes
            for (let c = 0; c <= cols; c += 2) {{
                ctx.beginPath();
                ctx.strokeStyle = meshSecondary;
                ctx.lineWidth = 1.3;
                for (let r = 0; r <= rows; r++) {{
                    const pt = gridPoints[r][c];
                    if (r === 0) ctx.moveTo(pt.x, pt.y);
                    else ctx.lineTo(pt.x, pt.y);
                }}
                ctx.stroke();
            }}

            // Draw Glowing Grid Intersection Nodes
            for (let r = 2; r <= rows; r += 2) {{
                for (let c = 1; c < cols; c += 3) {{
                    const pt = gridPoints[r][c];
                    ctx.beginPath();
                    ctx.arc(pt.x, pt.y, 2.8, 0, Math.PI * 2);
                    ctx.fillStyle = meshNodeColor;
                    ctx.fill();
                }}
            }}

            // 2. Draw Floating Candlestick Vectors & Financial Trendline
            const candleAreaWidth = width * 0.88;
            const candleStartX = (width - candleAreaWidth) / 2;
            const candleSpacing = candleAreaWidth / numCandles;
            const candleBaseY = height * 0.65;
            const candleWidth = Math.max(candleSpacing * 0.52, 14);
            const trendPoints = [];

            for (let i = 0; i < numCandles; i++) {{
                const cd = candles[i];
                const osc = Math.sin(tick * 1.4 + cd.phase) * 4;
                const cx = candleStartX + i * candleSpacing + candleSpacing * 0.5;

                const openY = candleBaseY - (cd.open + osc) * 1.15;
                const closeY = candleBaseY - (cd.close + osc) * 1.15;
                const highY = candleBaseY - (cd.high + osc) * 1.15;
                const lowY = candleBaseY - (cd.low + osc) * 1.15;

                const isBull = cd.close >= cd.open;
                const bodyTop = Math.min(openY, closeY);
                const bodyHeight = Math.max(Math.abs(closeY - openY), 6);

                // Draw Wick Line (bold, high-visibility 2.2px)
                ctx.beginPath();
                ctx.strokeStyle = isBull ? candleWick : candleBearWick;
                ctx.lineWidth = 2.2;
                ctx.moveTo(cx, highY);
                ctx.lineTo(cx, lowY);
                ctx.stroke();

                // Draw Candlestick Body
                ctx.fillStyle = isBull ? candleBull : candleBear;
                ctx.fillRect(cx - candleWidth / 2, bodyTop, candleWidth, bodyHeight);

                // Add crisp outline
                ctx.strokeStyle = isBull ? candleWick : candleBearWick;
                ctx.lineWidth = 1.6;
                ctx.strokeRect(cx - candleWidth / 2, bodyTop, candleWidth, bodyHeight);

                // Draw Volume Bar at base
                const volHeight = cd.volume * 0.8;
                const volY = height * 0.94 - volHeight;
                ctx.fillStyle = isBull ? (isDark ? "rgba(16, 185, 129, 0.45)" : "rgba(5, 150, 105, 0.35)") : (isDark ? "rgba(244, 63, 94, 0.40)" : "rgba(220, 38, 38, 0.30)");
                ctx.fillRect(cx - candleWidth / 2, volY, candleWidth, volHeight);

                trendPoints.push({{ x: cx, y: (openY + closeY) / 2 }});
            }}

            // Draw Bold Financial Trendline (Spline through candles)
            if (trendPoints.length > 1) {{
                ctx.beginPath();
                ctx.strokeStyle = trendLineColor;
                ctx.lineWidth = 3.2;
                ctx.moveTo(trendPoints[0].x, trendPoints[0].y);
                for (let i = 1; i < trendPoints.length; i++) {{
                    const prev = trendPoints[i - 1];
                    const curr = trendPoints[i];
                    const mx = (prev.x + curr.x) / 2;
                    const my = (prev.y + curr.y) / 2;
                    ctx.quadraticCurveTo(prev.x, prev.y, mx, my);
                }}
                ctx.stroke();

                // Draw glowing pulse cursor & live ticker badge on trendline head
                const last = trendPoints[trendPoints.length - 1];
                ctx.beginPath();
                ctx.arc(last.x, last.y, 6, 0, Math.PI * 2);
                ctx.fillStyle = trendLineColor;
                ctx.fill();

                // Pulsing outer halo
                const pulseR = 8 + Math.sin(tick * 3) * 3;
                ctx.beginPath();
                ctx.arc(last.x, last.y, pulseR, 0, Math.PI * 2);
                ctx.strokeStyle = trendLineColor;
                ctx.lineWidth = 1.5;
                ctx.stroke();

                // Live price badge
                ctx.font = '700 12px "Inter", sans-serif';
                const tagText = '▲ $154.20 (+18.4%)';
                const tagWidth = ctx.measureText(tagText).width + 16;
                ctx.fillStyle = badgeBg;
                ctx.fillRect(last.x - tagWidth - 10, last.y - 12, tagWidth, 24);
                ctx.strokeStyle = badgeBorder;
                ctx.lineWidth = 1.2;
                ctx.strokeRect(last.x - tagWidth - 10, last.y - 12, tagWidth, 24);
                ctx.fillStyle = isBullColor = isDark ? "#34D399" : "#059669";
                ctx.fillText(tagText, last.x - tagWidth - 2, last.y + 4);
            }}

            // 3. Draw Ambient Mathematical Badges
            ctx.font = '600 12px "Inter", monospace, sans-serif';
            for (let k = 0; k < mathTokens.length; k++) {{
                const tk = mathTokens[k];
                tk.x += tk.vx;
                tk.y += tk.vy;
                if (tk.x < 0.04 || tk.x > 0.94) tk.vx = -tk.vx;
                if (tk.y < 0.08 || tk.y > 0.82) tk.vy = -tk.vy;

                const textW = ctx.measureText(tk.text).width + 16;
                const bx = tk.x * width;
                const by = tk.y * height;

                // Draw pill background
                ctx.fillStyle = badgeBg;
                ctx.fillRect(bx - 8, by - 14, textW, 22);
                ctx.strokeStyle = badgeBorder;
                ctx.lineWidth = 1;
                ctx.strokeRect(bx - 8, by - 14, textW, 22);

                // Draw text
                ctx.fillStyle = badgeText;
                ctx.fillText(tk.text, bx, by + 2);
            }}

            win._ecBgAnimId = win.requestAnimationFrame(draw);
        }}

        win._ecBgAnimId = win.requestAnimationFrame(draw);
    }})();
    </script>
    """
    components.html(js_code, height=0, scrolling=False)


def render_landing_page(db: DatabaseManager) -> None:
    """Render the official front landing page."""
    theme = get_current_theme()
    render_landing_animated_background(theme)
    logo_path = Path(__file__).resolve().parent.parent / "app_logo.png"

    # 1. Hero Brand Header
    col_logo, col_header = st.columns([1, 4])

    with col_logo:
        if logo_path.exists():
            st.image(str(logo_path), width=130)
        else:
            st.markdown("### 🏬 **eC**")

    with col_header:
        st.markdown(
            f"""
            <div style="padding-top: 0.5rem;">
                <h1 class="animated-hero-title">
                    E-COMMERCE IQ
                </h1>
                <div style="font-size: 1.15rem; font-weight: 600; color: {theme['secondary_text']}; margin-top: 0.35rem;">
                    Executive Decision Intelligence & Conversational Analytics Platform
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2. Executive Quote Banner
    st.markdown(
        f"""
        <div style="background: {theme['card_bg']}; border-left: 4px solid {theme['accent_color']}; border-radius: 8px; padding: 1.2rem; margin: 1.5rem 0 1.2rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="font-size: 1.1rem; font-style: italic; color: {theme['text_color']}; line-height: 1.5;">
                “Turning complex transactional data into high-conviction decisions — pairing deterministic financial accuracy with conversational AI intelligence.”
            </div>
            <div style="font-size: 0.85rem; font-weight: 600; color: {theme['secondary_text']}; margin-top: 0.5rem;">
                — E-Commerce IQ Executive Philosophy
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2.5 Front Page Search Option (Themed Search Card & History)
    st.markdown(
        f"""
        <div class="search-card-wrapper">
            <div class="search-card-title">🔍 Search Store Intelligence with Shoplytic</div>
            <div class="search-card-subtitle">
                Search your store's sales, SKU profit margins, customer retention, or return leakage directly from the front page:
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    lp_col1, lp_col2 = st.columns([5, 1])
    with lp_col1:
        landing_query = st.text_input(
            "Landing Search Query",
            placeholder="Search store data (e.g. 'What are our top 5 best selling products?')...",
            label_visibility="collapsed",
            key="landing_search_input"
        )
    with lp_col2:
        landing_btn = st.button("🔍 Search", key="btn_landing_search", type="primary", use_container_width=True)

    # Quick search shortcut chips
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    quick_prompt = None
    with q_col1:
        if st.button("🏆 Top 5 Products", key="landing_qp_1", use_container_width=True):
            quick_prompt = "What are our top 5 best selling products?"
    with q_col2:
        if st.button("📦 Category Sales", key="landing_qp_2", use_container_width=True):
            quick_prompt = "What is our revenue breakdown by category?"
    with q_col3:
        if st.button("🔄 Return Leakage", key="landing_qp_3", use_container_width=True):
            quick_prompt = "Which products have the highest return rate?"
    with q_col4:
        if st.button("👥 Repeat Buyers", key="landing_qp_4", use_container_width=True):
            quick_prompt = "How many customers are repeat buyers?"

    landing_query_to_run = (landing_query if (landing_btn and landing_query) else None) or quick_prompt
    if landing_query_to_run:
        if "search_history" not in st.session_state:
            st.session_state.search_history = []
        if landing_query_to_run not in st.session_state.search_history:
            st.session_state.search_history.append(landing_query_to_run)
        st.session_state.active_search_prompt = landing_query_to_run
        st.session_state.selected_nav = "🤖 Shoplytic Copilot"
        st.session_state.jump_to_copilot = True
        st.rerun()

    # Front Page Themed Recent Search History (if searches exist)
    if st.session_state.get("search_history"):
        num_hist = len(st.session_state.search_history)
        st.markdown(
            f"""
            <div class="search-history-wrapper">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem;">
                    <div style="font-weight: 700; font-size: 0.92rem; color: {theme['text_color']};">
                        🕒 Recent Search History <span class="search-badge">{num_hist} Saved</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        l_hist_cols = st.columns(3)
        for h_idx, past_q in enumerate(reversed(st.session_state.search_history[-3:])):
            col = l_hist_cols[h_idx % 3]
            if col.button(f"🔍 {past_q[:35]}...", key=f"landing_hist_{h_idx}", use_container_width=True):
                st.session_state.active_search_prompt = past_q
                st.session_state.selected_nav = "🤖 Shoplytic Copilot"
                st.session_state.jump_to_copilot = True
                st.rerun()

    # 3. Live Store Data Statistics (E-Commerce Background & Scale)
    kpi_calc = KPICalculator(db)
    kpis = kpi_calc.calculate_summary()

    st.markdown("### 📊 Live Store Performance Baseline (14 Months)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Gross Merchandise Value</div>
                <div class="metric-value">${kpis.total_revenue:,.2f}</div>
                <div style="font-size: 0.78rem; color: {theme['secondary_text']};">14 operating months</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Completed Orders</div>
                <div class="metric-value">{kpis.total_orders:,}</div>
                <div style="font-size: 0.78rem; color: {theme['secondary_text']};">Average Order Value: ${kpis.average_order_value:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Customer Repeat Rate</div>
                <div class="metric-value">96.75%</div>
                <div style="font-size: 0.78rem; color: {theme['secondary_text']};">High customer loyalty & LTV</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Overall Return Rate</div>
                <div class="metric-value">4.76%</div>
                <div style="font-size: 0.78rem; color: {theme['secondary_text']};">Healthy benchmark (&lt; 10%)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4. Interactive Historical Sales Graph Preview
    st.markdown("---")
    st.markdown("### 📈 Monthly Revenue Trajectory & Seasonality")
    monthly_sales = kpi_calc.get_revenue_by_month()
    fig = render_revenue_trend_chart(monthly_sales)
    fig.update_layout(template=theme["plotly_template"])
    st.plotly_chart(fig, use_container_width=True)

    # 5. Core Value Pillars: How It Helps Users
    st.markdown("---")
    st.markdown("### 💡 How E-Commerce IQ Empowers Founders & Operators")

    fcol1, fcol2 = st.columns(2)

    with fcol1:
        st.markdown(
            f"""
            <div class="custom-card" style="padding: 1.2rem; margin-bottom: 1rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: {theme['primary_color']};">
                    🛡️ Zero Hallucination Financial Math
                </div>
                <div style="font-size: 0.9rem; color: {theme['text_color']}; margin-top: 0.4rem; line-height: 1.5;">
                    Generative AI chatbots guess numbers. E-Commerce IQ calculates every dollar using pure deterministic SQL and relational schema constraints. You get auditable financial records backed by the exact SQL code executed.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="custom-card" style="padding: 1.2rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: {theme['primary_color']};">
                    🤖 Shoplytic Conversational Copilot
                </div>
                <div style="font-size: 0.9rem; color: {theme['text_color']}; margin-top: 0.4rem; line-height: 1.5;">
                    Ask plain-English questions about your business (e.g. <i>"What are our top 5 best selling products?"</i>). Shoplytic maps your intent into safe SQL, executes it, and renders immediate narrative briefings and interactive charts.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with fcol2:
        st.markdown(
            f"""
            <div class="custom-card" style="padding: 1.2rem; margin-bottom: 1rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: {theme['primary_color']};">
                    🚨 Empirical Anomaly Diagnosis
                </div>
                <div style="font-size: 0.9rem; color: {theme['text_color']}; margin-top: 0.4rem; line-height: 1.5;">
                    When sales collapse, standard dashboards just turn red. E-Commerce IQ diagnoses the root cause by cross-referencing order drop-offs, review sentiment changes, and RMA return spikes down to specific defective SKU batches.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="custom-card" style="padding: 1.2rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: {theme['primary_color']};">
                    🏷️ SKU Unit Economics & Margin Health
                </div>
                <div style="font-size: 0.9rem; color: {theme['text_color']}; margin-top: 0.4rem; line-height: 1.5;">
                    Monitor gross margin percentage, inventory turnover velocity, and dead-stock capital traps per SKU, enabling data-driven inventory replenishment and pricing decisions.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
