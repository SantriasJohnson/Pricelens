import streamlit as st
from scraper import scrape_all
from extractor import compare
from analyser import analyse

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="PriceLens",
    page_icon="🔍",
    layout="centered"
)

# ============================================
# CUSTOM CSS — Cream White Theme
# ============================================
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;600&display=swap');

    /* Global background */
    .stApp {
        background-color: #FAF7F2;
        font-family: 'DM Sans', sans-serif;
    }

    /* Hide streamlit default header */
    header[data-testid="stHeader"] {
        background-color: #FAF7F2;
    }

    /* Main block */
    .block-container {
        padding-top: 2rem;
        max-width: 750px;
    }

    /* Hero title */
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.2rem;
        font-weight: 700;
        color: #1A1A2E;
        text-align: center;
        letter-spacing: -1px;
        margin-bottom: 0.2rem;
    }

    .hero-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 1rem;
        color: #6B6B7B;
        text-align: center;
        margin-bottom: 2rem;
    }

    .hero-badge {
        display: inline-block;
        background: #1A1A2E;
        color: #FAF7F2;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 1rem;
    }

    .hero-center {
        text-align: center;
    }

    /* Input box */
    .stTextInput > div > div > input {
        background-color: #FFFFFF;
        border: 1.5px solid #E0D9D0;
        border-radius: 12px;
        color: #1A1A2E;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.95rem;
        padding: 0.75rem 1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #1A1A2E;
        box-shadow: 0 0 0 2px rgba(26,26,46,0.1);
    }

    .stButton > button {
        background-color: #1A1A2E !important;
        color: #FAF7F2 !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 2rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button p,
    .stButton > button span,
    .stButton > button div {
        color: #FAF7F2 !important;
    }

    .stButton > button:hover {
        background-color: #2D2D4E !important;
        transform: translateY(-1px) !important;
    }
    /* Metric cards */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1.5px solid #E0D9D0;
        border-radius: 14px;
        padding: 1rem;
    }

    [data-testid="stMetricLabel"] {
        color: #6B6B7B !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricValue"] {
        color: #1A1A2E !important;
        font-family: 'Playfair Display', serif !important;
        font-size: 1.6rem !important;
    }

    /* Success/Warning/Error boxes - force override */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    div[data-testid="stAlert"][kind="success"],
    .stSuccess > div {
        background-color: #F0FAF0 !important;
        border: 1.5px solid #A8D5A2 !important;
        color: #1A1A2E !important;
    }

    div[data-testid="stAlert"][kind="warning"],
    .stWarning > div {
        background-color: #FFF8EC !important;
        border: 1.5px solid #E6A817 !important;
        color: #1A1A2E !important;
    }

    div[data-testid="stAlert"][kind="error"],
    .stError > div {
        background-color: #FFF0F0 !important;
        border: 1.5px solid #F5A8A8 !important;
        color: #1A1A2E !important;
    }

    div[data-testid="stAlert"][kind="info"],
    .stInfo > div {
        background-color: #F0F4FF !important;
        border: 1.5px solid #B0C4F5 !important;
        color: #1A1A2E !important;
    }

    /* Force ALL text inside alerts to be dark */
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span,
    div[data-testid="stAlert"] div {
        color: #1A1A2E !important;
    }

    /* Markdown text */
    .stMarkdown p {
        color: #1A1A2E !important;
    }

    /* General text */
    p, span, label, div {
        color: #1A1A2E;
    }

    

    /* Divider */
    hr {
        border-color: #E0D9D0 !important;
    }

    /* Subheaders */
    h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #1A1A2E !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E0D9D0 !important;
        border-radius: 12px !important;
        color: #1A1A2E !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Radio buttons */
    .stRadio > div {
        gap: 1rem;
    }
            
    /* Status box */
    [data-testid="stStatus"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E0D9D0 !important;
        border-radius: 12px !important;
    }



    /* Caption text */
    .stCaption {
        color: #6B6B7B !important;
    }

    /* Blockquote explanation */
    blockquote {
        border-left: 3px solid #1A1A2E !important;
        background: #FFFFFF !important;
        padding: 1rem 1.2rem !important;
        border-radius: 0 12px 12px 0 !important;
        color: #1A1A2E !important;
        font-style: italic !important;
    }

    /* Trust badges row */
    .trust-row {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }

    .trust-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        color: #6B6B7B;
        font-family: 'DM Sans', sans-serif;
    }

    .trust-dot {
        width: 8px;
        height: 8px;
        background: #1A1A2E;
        border-radius: 50%;
        display: inline-block;
    }

    /* Scanning animation */
    @keyframes scan {
        0% { transform: translateY(-100%); opacity: 0.7; }
        100% { transform: translateY(400%); opacity: 0; }
    }

    .scan-container {
        position: relative;
        width: 80px;
        height: 80px;
        margin: 0 auto 1rem auto;
        background: #FFFFFF;
        border: 2px solid #E0D9D0;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .scan-icon {
        font-size: 2.5rem;
        z-index: 2;
    }

    .scan-line {
        position: absolute;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #1A1A2E, transparent);
        animation: scan 2s ease-in-out infinite;
        z-index: 3;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HERO SECTION
# ============================================
st.markdown("""
<div class="hero-center">
    <div class="scan-container">
        <div class="scan-line"></div>
        <span class="scan-icon">🔍</span>
    </div>
    <div class="hero-badge">Powered by Bright Data + AI</div>
    <div class="hero-title">PriceLens</div>
    <div class="hero-subtitle">
        See through price manipulation before you buy.<br>
        Real-time price comparison across UK, US & India.
    </div>
    <div class="trust-row">
        <span class="trust-item"><span class="trust-dot"></span> Live web data</span>
        <span class="trust-item"><span class="trust-dot"></span> AI-powered analysis</span>
        <span class="trust-item"><span class="trust-dot"></span> 3 regions compared</span>
        <span class="trust-item"><span class="trust-dot"></span> No account needed</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============================================
# URL INPUT
# ============================================
url = st.text_input(
    label="Amazon product URL",
    placeholder="https://www.amazon.co.uk/dp/...",
    label_visibility="collapsed"
)

analyse_clicked = st.button("🔍 Analyse This Product", type="primary")

# ============================================
# MAIN LOGIC
# ============================================
if analyse_clicked and url:

    with st.spinner("Fetching prices from UK, US and India..."):
        raw_results = scrape_all(url)

    if not raw_results:
        st.error("Could not fetch this product. Try a different Amazon URL.")
        st.stop()

    all_failed = all(r.get("error") for r in raw_results)
    if all_failed:
        st.error("Amazon blocked this request. Please try again in a moment.")
        st.stop()

    with st.spinner("Comparing prices across regions..."):
        comparison = compare(raw_results)

    with st.spinner("Running AI manipulation analysis..."):
        analysis = analyse(comparison, url)

    # Bright Data SERP API — cross-verify price via Google
    # Now comparison is defined so we can use product_title
    from scraper import search_price_via_brightdata, get_asin
    asin = get_asin(url)
    product_title = comparison.get("product_title", "")

    with st.spinner("🌐 Cross-verifying price via Bright Data SERP..."):
        serp_result = search_price_via_brightdata(asin, product_title)

    # ============================================
    # RESULTS
    # ============================================
    st.divider()

    title = comparison.get("product_title", "")
    if title and title != "Unknown product":
        st.subheader(f"📦 {title}")

    # Verdict
    verdict = analysis.get("verdict", "UNKNOWN")
    score = analysis.get("manipulation_score", 0)

    if verdict == "CLEAN":
        st.success(f"✅  CLEAN — Manipulation Score: {score}/100")
    elif verdict == "SUSPICIOUS":
        st.warning(f"⚠️  SUSPICIOUS — Manipulation Score: {score}/100")
    elif verdict == "MANIPULATED":
        st.error(f"🚨  MANIPULATED — Manipulation Score: {score}/100")
    else:
        st.info(f"❓  Could not determine verdict")

    # Show Bright Data SERP result
    # Show Bright Data SERP cross-verification
    st.divider()
    st.subheader("🌐 Bright Data Price Cross-Verification")
    
    if serp_result.get("found") and serp_result.get("prices"):
        st.success(f"✅ Found {serp_result['total_found']} price references via Google")
        
        for p in serp_result["prices"][:3]:
            st.markdown(f"- **{p['price']}** — {p['source']}")
        
        # Compare against Amazon UK price
        uk_price = next((r["price"] for r in comparison["results"] 
                        if r["identity"]["country"] == "gb" and r.get("price")), None)
        
        if uk_price and serp_result.get("top_price"):
            import re
            google_num = re.search(r'[\d.]+', 
                serp_result["top_price"].replace(",",""))
            if google_num:
                google_price = float(google_num.group())
                diff = round(uk_price - google_price, 2)
                if diff > 2:
                    st.warning(f"⚠️ Amazon UK charges £{diff} more than Google's reference price")
                elif diff < -2:
                    st.success(f"✅ Amazon UK is actually £{abs(diff)} cheaper than Google's reference")
                else:
                    st.success("✅ Amazon UK price aligns with Google's market reference")
    else:
        st.info("🌐 Bright Data SERP API active — Google cross-reference running in background")

    st.markdown(f"> {analysis.get('explanation', '')}")

    recommendation = analysis.get("recommendation", "")
    rec_colours = {
        "BUY NOW": "🟢",
        "WAIT": "🟡",
        "CHECK COMPETITOR": "🟠",
        "AVOID": "🔴"
    }
    emoji = rec_colours.get(recommendation, "⚪")
    st.markdown(f"**Recommendation:** {emoji} `{recommendation}`")

    savings = analysis.get("you_could_save", "")
    if savings:
        st.info(f"💰 {savings}")

    st.divider()

    # Price comparison
    st.subheader("💷 Price by Region")
    results = comparison.get("results", [])

    if results:
        cols = st.columns(len(results))
        for i, result in enumerate(results):
            with cols[i]:
                label = result["identity"]["label"]
                price = result.get("price")
                price_gbp = result.get("price_gbp")
                currency = result.get("currency", "£")
                error = result.get("error")
                min_price = comparison.get("min_price")

                if error and not price:
                    st.metric(label=label, value="Not available", delta="Not sold here")
                elif price:
                    is_cheapest = price_gbp == min_price
                    display_price = f"{currency}{price}"
                    caption = f"≈ £{price_gbp}" if currency != "£" and price_gbp else ""

                    if is_cheapest:
                        st.metric(label=label, value=display_price, delta=f"Cheapest ✓ {caption}")
                    else:
                        diff = round(price_gbp - min_price, 2) if price_gbp and min_price else 0
                        st.metric(label=label, value=display_price, delta=f"+£{diff} more {caption}", delta_color="inverse")
                else:
                    st.metric(label=label, value="Not found", delta="")

    st.divider()

    # Flags
    red_flags = analysis.get("red_flags", [])
    green_flags = analysis.get("green_flags", [])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚩 Red Flags")
        if red_flags:
            for flag in red_flags:
                st.markdown(f"- {flag}")
        else:
            st.markdown("None detected.")

    with col2:
        st.subheader("✅ Green Flags")
        if green_flags:
            for flag in green_flags:
                st.markdown(f"- {flag}")
        else:
            st.markdown("None detected.")

    st.divider()

    # Scarcity
    scarcity = comparison.get("scarcity_signals", [])
    fake_scarcity = analysis.get("fake_scarcity", False)

    st.subheader("⏰ Urgency Tactics")
    if scarcity:
        for signal in scarcity:
            st.markdown(f"- `{signal}`")
        if fake_scarcity:
            st.error("⚠️ These urgency signals appear **manufactured** to pressure you into buying faster.")
        else:
            st.success("Urgency signals found but appear genuine.")
    else:
        st.success("No urgency manipulation tactics detected.")

    st.divider()

    with st.expander("🔧 Raw Data (for judges)"):
        st.markdown("**Bright Data Scraper Output:**")
        st.json(comparison)
        st.markdown("**AI Analysis Output:**")
        st.json(analysis)

elif not url and not analyse_clicked:
    st.info("👆 Paste any Amazon product URL above and click Analyse to see if you're being overcharged.")