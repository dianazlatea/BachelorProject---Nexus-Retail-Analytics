import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Nexus | Category Analysis", layout="wide", initial_sidebar_state="collapsed")

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
    st.page_link("pages/Page4-Seller_Analysis.py", label="Seller Analysis", icon=":material/group:")

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

# --- CONTENT ---
st.title("Deep Dive: Category Performance")
st.markdown("Advanced operational and financial insights specific to each product category.")

# Filter by Category
all_categories = sorted(df['Category'].unique())
selected_cat = st.selectbox("Select Product Category", all_categories)

# Filter dataframe
cat_df = df[df['Category'] == selected_cat].copy()

# --- ROW 1: SALES EVOLUTION & PAYMENT METHODS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader(f"Sales Trend: {selected_cat.replace('_', ' ').title()}")
    trend_df = cat_df.groupby(cat_df['Modern_Date'].dt.to_period("M")).agg({'Revenue': 'sum'}).reset_index()
    trend_df['Modern_Date'] = trend_df['Modern_Date'].astype(str)
    
    fig_trend = px.line(trend_df, x='Modern_Date', y='Revenue', line_shape='spline', template="plotly_dark", color_discrete_sequence=['#007AFF'])
    fig_trend.update_layout(xaxis_title="Timeline", yaxis_title="Revenue ($)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("Payment Method Distribution")
    pay_df = cat_df.groupby('payment_type').agg({'Revenue': 'count'}).reset_index()
    fig_pay = px.pie(pay_df, names='payment_type', values='Revenue', hole=0.6, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Blues_r)
    fig_pay.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig_pay.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pay, use_container_width=True)

# --- ROW 2: TOP PRODUCTS IN CATEGORY ---
st.markdown("---")
st.subheader(f"Top 10 High-Revenue Products in '{selected_cat}'")

cat_df['Product_Short_ID'] = cat_df['product_id'].astype(str).str[:8]
top_products = cat_df.groupby('Product_Short_ID').agg({
    'Revenue': 'sum',
    'order_id': 'count'
}).rename(columns={'order_id': 'Units_Sold'}).sort_values(by='Revenue', ascending=False).head(10).reset_index()

fig_bar = px.bar(top_products, x='Product_Short_ID', y='Revenue', 
                 color='Revenue', text='Units_Sold',
                 labels={'Units_Sold': 'Orders'},
                 template="plotly_dark", color_continuous_scale='Blues')
fig_bar.update_traces(texttemplate='%{text} orders', textposition='outside')
fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_bar, use_container_width=True)