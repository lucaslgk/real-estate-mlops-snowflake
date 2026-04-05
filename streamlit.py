import streamlit as st
import json
import plotly.graph_objects as go
from snowflake.snowpark.context import get_active_session




st.set_page_config(
    page_title="Immo·AI — Estimation immobilière",
    layout="wide",
    initial_sidebar_state="expanded"
)



st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&family=DM+Mono:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
}

.stApp {
    background: #0D0F14;
    color: #E8E0D0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #13161E !important;
    border-right: 1px solid #2A2D38;
}

[data-testid="stSidebar"] label {
    color: #8A8FA0 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    font-family: 'DM Mono', monospace !important;
}

[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stSlider {
    background: #1C2030 !important;
}

/* ── Main heading ── */
.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.8rem;
    font-weight: 300;
    letter-spacing: -0.02em;
    line-height: 1.1;
    color: #E8E0D0;
    margin: 0;
}

.hero-title span {
    color: #C9A84C;
}

.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #5A5F70;
    margin-top: 0.5rem;
}

/* ── Gold divider ── */
.gold-line {
    height: 1px;
    background: linear-gradient(90deg, #C9A84C 0%, #C9A84C44 60%, transparent 100%);
    margin: 1.5rem 0;
}

/* ── Cards ── */
.card {
    background: #13161E;
    border: 1px solid #1E2230;
    border-radius: 2px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.card-label {
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #5A5F70;
    margin-bottom: 0.3rem;
}

.card-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.4rem;
    font-weight: 400;
    color: #C9A84C;
    line-height: 1;
}

.card-unit {
    font-size: 0.8rem;
    color: #5A5F70;
    margin-left: 0.3rem;
}

/* ── Feature chips ── */
.chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.5rem;
}

.chip {
    background: #1C2030;
    border: 1px solid #2A2D38;
    border-radius: 2px;
    padding: 0.2rem 0.5rem;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #8A8FA0;
}

.chip.active {
    background: #C9A84C18;
    border-color: #C9A84C55;
    color: #C9A84C;
}

/* ── Score bar ── */
.score-row {
    display: flex;
    align-items: center;
    margin-bottom: 0.7rem;
    gap: 0.8rem;
}

.score-label {
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #5A5F70;
    width: 120px;
    flex-shrink: 0;
}

.score-bar-bg {
    flex: 1;
    height: 3px;
    background: #1E2230;
    border-radius: 2px;
    overflow: hidden;
}

.score-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #C9A84C, #E8C96C);
    border-radius: 2px;
    transition: width 0.8s ease;
}

.score-val {
    font-size: 0.7rem;
    color: #C9A84C;
    width: 30px;
    text-align: right;
}

/* ── Predict button ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid #C9A84C !important;
    color: #C9A84C !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 0.7rem 2rem !important;
    border-radius: 2px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: #C9A84C18 !important;
    border-color: #E8C96C !important;
}

/* ── Metrics override ── */
[data-testid="metric-container"] {
    background: #13161E;
    border: 1px solid #1E2230;
    padding: 1rem 1.2rem;
    border-radius: 2px;
}

[data-testid="metric-container"] label {
    color: #5A5F70 !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 2rem !important;
    color: #C9A84C !important;
}

/* ── Sidebar section title ── */
.sidebar-section {
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #C9A84C;
    margin: 1.2rem 0 0.5rem 0;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid #C9A84C33;
}

/* ── Info box ── */
.info-box {
    background: #C9A84C0A;
    border-left: 2px solid #C9A84C;
    padding: 0.8rem 1rem;
    font-size: 0.72rem;
    color: #8A8FA0;
    line-height: 1.6;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session ───────────────────────────────────────────────────────────────────
session = get_active_session()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-section">Surface & Structure</div>', unsafe_allow_html=True)
    area     = st.slider("Surface (m²)", 1000, 16000, 5000, step=100)
    stories  = st.selectbox("Nombre d'étages", [1, 2, 3, 4])

    st.markdown('<div class="sidebar-section">Pièces</div>', unsafe_allow_html=True)
    bedrooms  = st.selectbox("Chambres", [1, 2, 3, 4, 5, 6])
    bathrooms = st.selectbox("Salles de bain", [1, 2, 3, 4])
    parking   = st.selectbox("Places parking", [0, 1, 2, 3])

    st.markdown('<div class="sidebar-section">Équipements</div>', unsafe_allow_html=True)
    airconditioning  = st.selectbox("Climatisation", ["yes", "no"])
    hotwaterheating  = st.selectbox("Chauffage eau chaude", ["yes", "no"])
    basement         = st.selectbox("Sous-sol", ["yes", "no"])
    guestroom        = st.selectbox("Chambre d'amis", ["yes", "no"])

    st.markdown('<div class="sidebar-section">Localisation & Finitions</div>', unsafe_allow_html=True)
    mainroad         = st.selectbox("Route principale", ["yes", "no"])
    prefarea         = st.selectbox("Zone privilégiée", ["yes", "no"])
    furnishingstatus = st.selectbox("Ameublement", ["furnished", "semi-furnished", "unfurnished"])

    st.markdown("<br>", unsafe_allow_html=True)
    predict_clicked  = st.button("Estimer le prix →")



# header
st.markdown("""
<div style="padding: 2rem 0 1rem 0;">
    <div class="hero-sub">Snowflake ML · VotingRegressor · R² 0.69</div>
    <div class="hero-title">Estimation<br><span>Immobilière</span></div>
</div>
<div class="gold-line"></div>
""", unsafe_allow_html=True)



def make_gauge(price, min_price=100_000, max_price=600_000):
    """Plotly gauge for predicted price."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=price,
        number={
            'prefix': '',
            'suffix': ' €',
            'font': {'size': 36, 'color': '#C9A84C', 'family': 'Cormorant Garamond'},
            'valueformat': ',.0f'
        },
        gauge={
            'axis': {
                'range': [min_price, max_price],
                'tickfont': {'size': 10, 'color': '#5A5F70', 'family': 'DM Mono'},
                'tickformat': ',.0f',
                'nticks': 5
            },
            'bar': {'color': '#C9A84C', 'thickness': 0.3},
            'bgcolor': '#13161E',
            'bordercolor': '#1E2230',
            'steps': [
                {'range': [min_price, min_price + (max_price-min_price)*0.33], 'color': '#1A1D26'},
                {'range': [min_price + (max_price-min_price)*0.33, min_price + (max_price-min_price)*0.66], 'color': '#1C2030'},
                {'range': [min_price + (max_price-min_price)*0.66, max_price], 'color': '#1E2235'},
            ],
            'threshold': {
                'line': {'color': '#E8C96C', 'width': 2},
                'thickness': 0.8,
                'value': price
            }
        }
    ))
    fig.update_layout(
        height=280,
        margin=dict(t=20, b=0, l=30, r=30),
        paper_bgcolor='#13161E',
        font={'family': 'DM Mono'},
    )
    return fig


def compute_scores(area, bedrooms, bathrooms, airconditioning,
                   hotwaterheating, basement, guestroom,
                   mainroad, prefarea, furnishingstatus, parking):
    """Compute qualitative scores for the property."""
    comfort = sum([
        airconditioning == 'yes',
        hotwaterheating == 'yes',
        basement == 'yes',
        guestroom == 'yes',
    ])
    location = sum([mainroad == 'yes', prefarea == 'yes'])
    furn_score = {'furnished': 3, 'semi-furnished': 2, 'unfurnished': 1}[furnishingstatus]
    size_score = min(int((area / 16000) * 5), 5)
    rooms = min(bedrooms + bathrooms, 8)

    return {
        'Confort':     int((comfort / 4) * 100),
        'Localisation': int((location / 2) * 100),
        'Surface':     int((size_score / 5) * 100),
        'Pièces':      int((rooms / 8) * 100),
        'Finitions':   int((furn_score / 3) * 100),
        'Parking':     int((min(parking, 3) / 3) * 100),
    }


# ── Main content ──────────────────────────────────────────────────────────────
if not predict_clicked:
    # ── Default state — property summary
    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.markdown("""
        <div class="info-box">
            Configurez les caractéristiques du bien dans le panneau de gauche,
            puis cliquez sur <strong style="color:#C9A84C">Estimer le prix</strong> 
            pour obtenir une estimation instantanée générée par le modèle 
            VotingRegressor entraîné et déployé sur Snowflake.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Property summary cards
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="card">
                <div class="card-label">Surface</div>
                <div class="card-value">{area:,}<span class="card-unit">m²</span></div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="card">
                <div class="card-label">Chambres</div>
                <div class="card-value">{bedrooms}<span class="card-unit">ch.</span></div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="card">
                <div class="card-label">Étages</div>
                <div class="card-value">{stories}<span class="card-unit">niv.</span></div>
            </div>""", unsafe_allow_html=True)

        # Feature chips
        chips_data = {
            'Climatisation': airconditioning == 'yes',
            'Eau chaude': hotwaterheating == 'yes',
            'Sous-sol': basement == 'yes',
            'Ch. amis': guestroom == 'yes',
            'Route princ.': mainroad == 'yes',
            'Zone privil.': prefarea == 'yes',
            f'Parking ×{parking}': parking > 0,
            furnishingstatus.replace('-', '‑'): True,
        }
        chips_html = '<div class="chip-row">' + ''.join(
            f'<span class="chip {"active" if v else ""}">{k}</span>'
            for k, v in chips_data.items()
        ) + '</div>'
        st.markdown(chips_html, unsafe_allow_html=True)

    with col2:
        # Score breakdown
        scores = compute_scores(area, bedrooms, bathrooms, airconditioning,
                                hotwaterheating, basement, guestroom,
                                mainroad, prefarea, furnishingstatus, parking)

        st.markdown('<div class="card-label" style="margin-bottom:1rem">Analyse du bien</div>', unsafe_allow_html=True)
        bars_html = ""
        for label, pct in scores.items():
            bars_html += f"""
            <div class="score-row">
                <div class="score-label">{label}</div>
                <div class="score-bar-bg">
                    <div class="score-bar-fill" style="width:{pct}%"></div>
                </div>
                <div class="score-val">{pct}</div>
            </div>"""
        st.markdown(bars_html, unsafe_allow_html=True)

else:
    
    with st.spinner(""):
        try:
            input_data = {
                'AREA': area, 'BEDROOMS': bedrooms, 'BATHROOMS': bathrooms,
                'STORIES': stories, 'MAINROAD': mainroad, 'GUESTROOM': guestroom,
                'BASEMENT': basement, 'HOTWATERHEATING': hotwaterheating,
                'AIRCONDITIONING': airconditioning, 'PARKING': parking,
                'PREFAREA': prefarea, 'FURNISHINGSTATUS': furnishingstatus
            }

            input_df = session.create_dataframe([input_data])
            input_df.create_or_replace_temp_view("TEMP_HOUSE_INPUT")

            result = session.sql("""
                SELECT HOUSE_PRICE_VOTING!PREDICT(
                    AREA, BEDROOMS, BATHROOMS, STORIES,
                    MAINROAD, GUESTROOM, BASEMENT, HOTWATERHEATING,
                    AIRCONDITIONING, PARKING, PREFAREA, FURNISHINGSTATUS
                )['output_feature_0']::FLOAT AS PREDICTED_PRICE
                FROM TEMP_HOUSE_INPUT
            """).collect()

            price = result[0]['PREDICTED_PRICE']

            # ── Layout
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown('<div class="card-label">Prix estimé</div>', unsafe_allow_html=True)
                st.plotly_chart(make_gauge(price), use_container_width=True, config={'displayModeBar': False})

                st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)

                m1, m2, m3 = st.columns(3)
                m1.metric("Prix / m²", f"{price/area:,.0f} €")
                m2.metric("Surface", f"{area:,} m²")
                m3.metric("Chambres", f"{bedrooms} ch.")

            with col2:
                scores = compute_scores(area, bedrooms, bathrooms, airconditioning,
                                        hotwaterheating, basement, guestroom,
                                        mainroad, prefarea, furnishingstatus, parking)

                st.markdown('<div class="card-label" style="margin-bottom:1rem">Facteurs de valorisation</div>', unsafe_allow_html=True)
                bars_html = ""
                for label, pct in scores.items():
                    bars_html += f"""
                    <div class="score-row">
                        <div class="score-label">{label}</div>
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width:{pct}%"></div>
                        </div>
                        <div class="score-val">{pct}</div>
                    </div>"""
                st.markdown(bars_html, unsafe_allow_html=True)

                st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)

                # Active features
                chips_data = {
                    'Climatisation': airconditioning == 'yes',
                    'Eau chaude': hotwaterheating == 'yes',
                    'Sous-sol': basement == 'yes',
                    'Ch. amis': guestroom == 'yes',
                    'Route princ.': mainroad == 'yes',
                    'Zone privil.': prefarea == 'yes',
                    f'Parking ×{parking}': parking > 0,
                    furnishingstatus.replace('-', '‑'): True,
                }
                chips_html = '<div class="card-label" style="margin-bottom:0.5rem">Équipements</div>'
                chips_html += '<div class="chip-row">' + ''.join(
                    f'<span class="chip {"active" if v else ""}">{k}</span>'
                    for k, v in chips_data.items()
                ) + '</div>'
                st.markdown(chips_html, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="info-box">
                    Estimation générée par le modèle <strong style="color:#C9A84C">VotingRegressor</strong>
                    (BayesianRidge · Ridge · GradientBoosting) · R²&nbsp;=&nbsp;0.69 · 
                    Snowflake Model Registry
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erreur : {str(e)}")