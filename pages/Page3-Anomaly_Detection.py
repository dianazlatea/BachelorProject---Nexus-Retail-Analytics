import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest
import os

st.set_page_config(page_title="Nexus | Anomaly Detection", layout="wide", initial_sidebar_state="collapsed")

# --- AUTH CHECK ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in from the main Dashboard page.")
    st.stop()

# --- CSS REVOLUT STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #0A192F; color: #FFFFFF; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    .block-container { padding-top: 4rem !important; max-width: 1400px !important; }
    
    /* Buton Logout Text-Only (Tertiary) */
    button[kind="tertiary"] {
        background-color: transparent !important;
        color: #AAAAAA !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        text-align: right !important;
        font-weight: 600 !important;
        justify-content: flex-end !important;
        transform: translateX(15px) !important; /* Muta butonul usor spre dreapta pentru o aliniere perfecta cu textul */
    }
    button[kind="tertiary"]:hover {
        color: #FF3B30 !important;
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOP NAVIGATION BAR ---
col_logo, col_nav1, col_nav2, col_nav3, col_nav4, col_nav5, col_user = st.columns([2.0, 1.2, 1.4, 1.2, 1.5, 1.5, 1.2], vertical_alignment="center")

with col_logo:
    st.markdown("""
        <div style="display: flex; align-items: center;">
            <div style="margin-right: 10px; display: flex; align-items: center;">
                <svg width="32" height="38" viewBox="0 0 45 55" xmlns="http://www.w3.org/2000/svg">
                    <rect x="0" y="0" width="14" height="55" fill="#007AFF" />
                    <rect x="31" y="0" width="14" height="55" fill="#007AFF" />
                    <polygon points="0,0 14,0 45,55 31,55" fill="#00C6FF" />
                </svg>
            </div>
            <div style="display: flex; flex-direction: column; justify-content: center;">
                <span style="font-size: 22px; font-weight: 800; line-height: 1;">Nexus</span>
                <span style="color: #AAAAAA; font-size: 11px; margin-top: 2px; font-weight: 600; letter-spacing: 0.5px;">Retail Analytics</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_nav1:
    st.page_link("app.py", label="Dashboard", icon=":material/home:")

with col_nav2:
    st.page_link("pages/Page1-Deep_Analysis.py", label="Category Analysis", icon=":material/monitoring:")

with col_nav3:
    st.page_link("pages/Page2-Forecasting.py", label="Forecasting", icon=":material/online_prediction:")

with col_nav4:
    st.page_link("pages/Page3-Anomaly_Detection.py", label="Anomaly Detection", icon=":material/warning:")

with col_nav5:
    st.page_link("pages/Page4-Seller_Analysis.py", label="Network & Customers", icon=":material/group:")

with col_user:
    st.markdown(f"<div style='font-size: 14px; text-align: right; margin-bottom: 5px;'>👤 <b>Hello, {st.session_state.username.capitalize()}</b></div>", unsafe_allow_html=True)
    if st.button("Logout", icon=":material/logout:", use_container_width=True, type="tertiary"):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.role = ''
        st.rerun()

st.markdown("---")

# --- DATA LOADING ---
if 'df' in st.session_state and st.session_state.df is not None:
    df = st.session_state.df
else:
    st.error("No data found. Please initialize the database from the home page.")
    st.stop()

# --- UI CONTENT ---
st.title("Anomaly Detection")
st.info("Using **Isolation Forest** (Machine Learning) to identify outliers in order values. These could represent high-value clients, potential pricing errors, or bulk purchases.")

# --- PREPARE DATA ---
df_anomaly = df.sample(n=min(5000, len(df)), random_state=42).copy()

X = df_anomaly[['Revenue']]

# Contamination slider for user to adjust sensitivity of anomaly detection
contamination_level = st.slider("Select Sensitivity (Contamination %)", 0.01, 0.10, 0.03)

# Model Training
model = IsolationForest(contamination=contamination_level, random_state=42)
df_anomaly['Anomaly_Score'] = model.fit_predict(X)
df_anomaly['Status'] = df_anomaly['Anomaly_Score'].map({1: 'Normal Order', -1: 'Anomalous (Outlier)'})

# --- VISUALIZATION ---
st.subheader("Revenue Distribution & Outliers")

fig = px.scatter(
    df_anomaly, 
    x='Modern_Date', 
    y='Revenue', 
    color='Status',
    hover_data=['Category', 'product_id'],
    color_discrete_map={'Normal Order': '#007AFF', 'Anomalous (Outlier)': '#FF3B30'},
    template="plotly_dark",
    title="Detected Anomalies in Transaction Values"
)

fig.update_layout(xaxis_title="Time (Projected)", yaxis_title="Order Value ($)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

# --- RESULTS TABLE ---
st.subheader("Anomalous Records Detail")
anomalies = df_anomaly[df_anomaly['Anomaly_Score'] == -1].sort_values(by='Revenue', ascending=False)

if not anomalies.empty:
    st.error(f"Nexus AI identified {len(anomalies)} records that deviate significantly from typical purchasing patterns.")
    
    # Formatare coloane pentru tabel
    display_df = anomalies[['order_id', 'Category', 'Modern_Date', 'Revenue', 'payment_type']].head(100)
    st.dataframe(display_df, use_container_width=True)
    
    # Actionable Insight
    st.markdown(f"""
    > **Data Insight:** The highest anomaly detected is an order of **${anomalies['Revenue'].max():,.2f}** > in the **{anomalies.iloc[0]['Category']}** category. 
    > This represents a value {anomalies['Revenue'].max() / df['Revenue'].mean():.1f}x higher than the average order.
    """)
else:
    st.success("No significant anomalies detected with the current sensitivity level.")

    st.markdown("### 📊 Anomaly Distribution")

    hist_fig = px.histogram(df_anomaly, x='Revenue', color='Status',
                        nbins=50, template="plotly_dark")
    st.plotly_chart(hist_fig, use_container_width=True)