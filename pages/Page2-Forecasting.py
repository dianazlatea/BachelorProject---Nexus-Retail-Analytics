import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Nexus | Forecasting", layout="wide", initial_sidebar_state="collapsed")

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
    
    /* Metricile native din Streamlit transparente */
    [data-testid="stMetric"] {
        background-color: transparent !important;
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(255,255,255,0.15) !important;
    }
    [data-testid="stMetricLabel"] * {
        color: #AAAAAA !important;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }
    
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
st.title("Predictive Insights")
st.info("Using Linear Regression to estimate future revenue trends based on historical performance.")

# --- FORECAST FILTERS ---
st.markdown("### Forecast Configuration")
filter_type = st.radio("Predictive Level:", ["Global Revenue", "By Category", "By Product ID"], horizontal=True)

forecast_df = df.copy()

if filter_type == "By Category":
    cat = st.selectbox("Select Category", sorted(df['Category'].unique()))
    forecast_df = df[df['Category'] == cat]
elif filter_type == "By Product ID":
    pid = st.selectbox("Select Product ID", df['product_id'].unique()[:100]) # Primele 100 pt demo
    forecast_df = df[df['product_id'] == pid]

# --- ML PREPARATION (Monthly Aggregation) ---
forecast_df['Month_Year'] = forecast_df['Modern_Date'].dt.to_period('M')
monthly_data = forecast_df.groupby('Month_Year').agg({'Revenue': 'sum'}).reset_index()
monthly_data['Month_Index'] = np.arange(len(monthly_data))

if len(monthly_data) >= 3:
    # Train model
    X = monthly_data[['Month_Index']]
    y = monthly_data['Revenue']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict future (next 6 months)
    future_indices = np.array([len(monthly_data) + i for i in range(1, 7)]).reshape(-1, 1)
    predictions = model.predict(future_indices)
    
    # --- CONFIDENCE INTERVAL ---
    residuals = y - model.predict(X)
    std_dev = np.std(residuals)

    upper = predictions + 1.96 * std_dev
    lower = predictions - 1.96 * std_dev

    # Create future dates for plotting 
    last_date = monthly_data['Month_Year'].max()
    future_dates = [(last_date + i).to_timestamp() for i in range(1, 7)]
    
    # Plotting
    fig = go.Figure()
    
    # History
    fig.add_trace(go.Scatter(
        x=monthly_data['Month_Year'].dt.to_timestamp(), 
        y=y, 
        name="Historical Revenue",
        line=dict(color='#007AFF', width=3)
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=future_dates, 
        y=predictions, 
        name="AI Forecast (6 Months)",
        line=dict(dash='dash', color='#00C6FF', width=3)
    ))
    # Confidence band (zona shaded)
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=upper,
        line=dict(width=0),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=future_dates,
        y=lower,
        fill='tonexty',
        name='Confidence Interval',
        line=dict(width=0),
        fillcolor='rgba(0,198,255,0.2)'
    ))

    fig.update_layout(
        template="plotly_dark",
        title=f"Revenue Trend Prediction: {filter_type}",
        xaxis_title="Time",
        yaxis_title="Revenue ($)",
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # --- METRICS BOX ---
    c1, c2, c3 = st.columns(3)
    avg_future = predictions.mean()
    growth_rate = ((predictions[-1] - y.iloc[-1]) / y.iloc[-1]) * 100
    
    c1.metric("Est. Next Month Revenue", f"${predictions[0]:,.2f}")
    c2.metric("Avg. Forecasted Revenue", f"${avg_future:,.2f}")
    c3.metric("Projected Growth", f"{growth_rate:+.1f}%")

else:
    st.warning("⚠️ Insufficient data points. At least 3 months of history are required for a linear projection.")