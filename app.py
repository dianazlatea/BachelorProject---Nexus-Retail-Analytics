import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import io
import json
import urllib.request
import tempfile
import plotly.graph_objects as go
from datetime import datetime
try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="Nexus Analytics |Olist Dataset|", layout="wide", page_icon="📈", initial_sidebar_state="collapsed")

@st.cache_data
def get_brazil_geojson():
    """Descarca coordonatele poligonale pentru statele din Brazilia necesare hartii Choropleth."""
    try:
        url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception:
        return None

@st.cache_data(show_spinner=False)
def generate_pdf_report_cached(total_rev, total_orders, avg_order, filter_sig, _f1, _f2, _f3, _f4, _f5, _f6):
    if FPDF is None:
        return b""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Nexus Analytics - Executive Summary", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Total Processed Revenue: ${total_rev:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total Orders Volume: {total_orders:,}", ln=True)
    pdf.cell(200, 10, txt=f"Average Ticket Size: ${avg_order:,.2f}", ln=True)
    pdf.ln(10)
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f1, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f2, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f3, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f4, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f5, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f6:
            
            figs = [_f1, _f2, _f3, _f4, _f5, _f6]
            files = [f1, f2, f3, f4, f5, f6]
            
            for f_obj, fig in zip(files, figs):
                fig_copy = go.Figure(fig)
                fig_copy.update_layout(template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=dict(color='black'))
                fig_copy.write_image(f_obj.name, format="png", width=500, height=350)
        
            y_row1 = pdf.get_y()
            pdf.image(f1.name, x=10, y=y_row1, w=60)
            pdf.image(f2.name, x=75, y=y_row1, w=60)
            pdf.image(f3.name, x=140, y=y_row1, w=60)
            
            y_row2 = y_row1 + 45
            pdf.image(f4.name, x=10, y=y_row2, w=60)
            pdf.image(f5.name, x=75, y=y_row2, w=60)
            pdf.image(f6.name, x=140, y=y_row2, w=60)
            
        for f_obj in files:
            os.remove(f_obj.name)
    except Exception as e:
        pdf.cell(200, 10, txt="   [!] Chart export skipped. Run 'pip install -U kaleido' on your server.", ln=True)
        
    return pdf.output(dest='S').encode('latin-1')

# --- CSS PENTRU LAYOUT REVOLUT PREMIUM ---
st.markdown("""
    <style>
    /* Fundal general intunecat (Dark Mode) */
    .stApp { background-color: #0A192F; color: #FFFFFF; }
    
    /* Ascunde complet panoul lateral (sidebar) si butonul hamburger */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    .block-container { padding-top: 4rem !important; max-width: 1400px !important; }
    
    /* Header personalizat */
    .main-header { font-size: 32px; font-weight: 800; color: #FFFFFF; margin-bottom: 5px; }
    .sub-header { color: #AAAAAA; margin-bottom: 30px; }

    /* Stil Carduri Metrici */
    .metric-card {
        background-color: transparent;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: none;
        overflow: hidden; /* Asigură că antetul nu iese din marginile rotunjite */
        text-align: center; /* Aliniem tot conținutul pe centru */
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    /* Extinde headerul (eticheta) pe toata lungimea părții superioare a cardului */
    .metric-label {
        margin: -20px -20px 15px -20px;
        padding: 10px 30px 10px 0px; /* Păstrăm spațiul la dreapta pentru a împinge textul spre stânga */
        color: #FFFFFF;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .value-text { 
        font-size: 28px; font-weight: 800; color: #FFFFFF; margin: 5px 0; 
        padding-right: 30px; /* Decalăm și valoarea ca să fie aliniată perfect cu antetul */
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .delta-wrapper { padding-right: 30px; margin-top: 8px; }

    /* Culori Carduri */
    .bg-transparent { background-color: transparent; }
    .bg-transparent { background-color: #transparent; }
    .bg-transparent { background-color: #transparent; }
    .bg-transparent { background-color: #transparent; }
    
    .delta-pos { background-color: #E8F9EE; color: #34C759; padding: 4px 10px; border-radius: 8px; font-size: 13px; font-weight: 700; }
    .delta-neg { background-color: #FFF0F0; color: #FF3B30; padding: 4px 10px; border-radius: 8px; font-size: 13px; font-weight: 700; }

    /* Butoane de Actiune si Download (Primary & Secondary) */
    button[kind="primary"], button[kind="secondary"] {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
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

# --- SESSION STATE INITIALIZATION ---
if 'users' not in st.session_state:
    st.session_state.users = {'admin': {'password': '123', 'role': 'admin'}}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'role' not in st.session_state:
    st.session_state.role = ''
if 'df' not in st.session_state:
    st.session_state.df = None

# --- AUTHENTICATION (LOGIN & REGISTER) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>Nexus Retail Analytics</h1>", unsafe_allow_html=True)
    col_space1, col_auth, col_space2 = st.columns([1, 2, 1])
    
    with col_auth:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login to your account")
            log_user = st.text_input("Username", key="log_user")
            log_pass = st.text_input("Password", type="password", key="log_pass")
            if st.button("Login", type="primary"):
                if log_user in st.session_state.users and st.session_state.users[log_user]['password'] == log_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = log_user
                    st.session_state.role = st.session_state.users[log_user]['role']
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
                    
        with tab2:
            st.subheader("Create a new account")
            reg_user = st.text_input("New Username", key="reg_user")
            reg_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Register", type="primary"):
                if reg_user in st.session_state.users:
                    st.error("Username already exists.")
                elif reg_user and reg_pass:
                    st.session_state.users[reg_user] = {'password': reg_pass, 'role': 'user'}
                    st.success("Registration successful! Please go to the Login tab.")
                else:
                    st.warning("Please fill in both fields.")
    st.stop()

# --- DATA LOADING (ADMIN FLOW) ---
def load_data_automatically():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, 'Database') + os.sep
    
    # Încărcăm doar fișierele esențiale pentru analize
    orders = pd.read_csv(f"{path}olist_orders_dataset.csv")
    items = pd.read_csv(f"{path}olist_order_items_dataset.csv")
    payments = pd.read_csv(f"{path}olist_order_payments_dataset.csv")
    products = pd.read_csv(f"{path}olist_products_dataset.csv")
    categories = pd.read_csv(f"{path}product_category_name_translation.csv")
    customers = pd.read_csv(f"{path}olist_customers_dataset.csv")
    sellers = pd.read_csv(f"{path}olist_sellers_dataset.csv")
    reviews = pd.read_csv(f"{path}olist_order_reviews_dataset.csv")
    geo = pd.read_csv(f"{path}olist_geolocation_dataset.csv")

    # Unirea tabelelor (Merge)
    # 1. Produse + Categorii (pentru a avea nume în engleză)
    df = pd.merge(items, products, on='product_id')
    df = pd.merge(df, categories, on='product_category_name')
    
    # 2. Adăugăm datele comenzii (pentru timeline/forecasting)
    df = pd.merge(df, orders, on='order_id')
    
    # 3. Adăugăm plățile (pentru Revenue/Anomaly Detection)
    df = pd.merge(df, payments, on='order_id')
    
    # 4. Adăugăm clienții (pentru date demografice/locație)
    df = pd.merge(df, customers, on='customer_id')

    # 5. Adăugăm vânzătorii (pentru analiza performanței)
    df = pd.merge(df, sellers, on='seller_id')

    # 6. Adăugăm review-urile (pentru analiza satisfacției)
    df = pd.merge(df, reviews, on='order_id')
    
    # 7. Adăugăm coordonatele geografice pentru Harta interactiva
    geo_agg = geo.groupby('geolocation_zip_code_prefix').agg({'geolocation_lat': 'mean', 'geolocation_lng': 'mean'}).reset_index()
    df = pd.merge(df, geo_agg, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left')

    # Conversie date și redenumire coloane pentru consistență în pagini
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Creăm coloana Modern_Date (proiecție în prezent pentru realism)
    max_date = df['order_purchase_timestamp'].max()
    diff = pd.Timestamp.now() - max_date
    df['Modern_Date'] = df['order_purchase_timestamp'] + diff
    
    df = df.rename(columns={
        'product_category_name_english': 'Category',
        'payment_value': 'Revenue',
        'review_score': 'Review_Score'
    })
    
    return df

# --- LOGICA DE ÎNCĂRCARE AUTOMATĂ ---
# Această secțiune rulează imediat după login
if st.session_state.logged_in:
    if 'df' not in st.session_state or st.session_state.df is None:
        with st.spinner("🚀 Nexus is connecting to Olist database..."):
            try:
                # Apelăm funcția de încărcare automată definită anterior
                st.session_state.df = load_data_automatically()
                
                # Mesaj discret de succes pentru Admin
                if st.session_state.role == 'admin':
                    st.toast("The database has been successfully loaded.", icon="✅")
            
            except Exception as e:
                # Dacă fișierele lipsesc din folderul /data/
                if st.session_state.role == 'admin':
                    st.error(f"⚠️ Error loading database: CSV files are missing from the 'data/' folder.")
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    expected_path = os.path.join(current_dir, 'data')
                    st.info(f"Please create a folder named **data** exactly here:\n`{expected_path}`\n\nAnd place the 5 Olist CSV files inside it.")
                    st.error(f"Technical error: {e}")
                else:
                    st.error("🖥️ The analytics system is currently unavailable. Please contact the admin .")
                st.stop()

# Din acest punct, variabila df este disponibilă pentru restul aplicației
df = st.session_state.df

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
    for main_page in [__file__, "App.py", "app.py"]:
        try:
            st.page_link(main_page, label="Dashboard", icon=":material/home:")
            break
        except KeyError:
            pass

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

# --- MAIN CONTENT ---
# --- HEADER ---
st.markdown(f'<div class="main-header">Good morning, {st.session_state.username.capitalize()} 👋</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your Nexus business overview for today.</div>', unsafe_allow_html=True)

# --- RAW DATA PREVIEW (Full Width) ---
c_prev, c_clean = st.columns(2)
with c_prev:
    with st.expander("Raw Data Preview", expanded=False, icon=":material/visibility:"):
        st.dataframe(df.head(100), use_container_width=True)
        st.caption("Displaying the first 100 rows of the current dataset.")
with c_clean:
    with st.expander("Data Health & Cleaning Pipeline", expanded=False, icon=":material/sanitizer:"):
        st.write("Inspect and clean the dataset before computing business metrics.")
        
        c_health1, c_health2, c_health3 = st.columns(3)
        missing_vals = df.isnull().sum().sum()
        duplicate_rows = df.duplicated().sum()
        
        c_health1.metric("Missing Values", f"{missing_vals:,}")
        c_health2.metric("Duplicate Rows", f"{duplicate_rows:,}")
        c_health3.metric("Total Records", f"{len(df):,}")
        
        if st.button("Auto-Clean Data (Drop NAs & Duplicates)", type="primary", icon=":material/cleaning_services:"):
            with st.spinner("Cleaning data..."):
                df_cleaned = df.drop_duplicates().dropna()
                st.session_state.df = df_cleaned
                st.success(f"Data successfully cleaned! Removed {len(df) - len(df_cleaned)} problematic rows.")
                st.rerun()
    
st.markdown("<br>", unsafe_allow_html=True)

# --- METRICI (ROW 1) CU YOY REAL ---
m1, m2, m3, m4 = st.columns(4)

# --- GLOBAL METRICS (Used for Sandbox and PDF Export) ---
total_rev = df['Revenue'].sum()
total_orders = df['order_id'].nunique()
avg_order = df.groupby('order_id')['Revenue'].sum().mean()

# --- TIME LOGIC ---
df_time = df.copy()
df_time['Year'] = df_time['Modern_Date'].dt.year

current_year = df_time['Year'].max()
previous_year = current_year - 1

df_current = df_time[df_time['Year'] == current_year]
df_previous = df_time[df_time['Year'] == previous_year]

# fallback daca nu exista anul anterior
if df_previous.empty:
    df_previous = df_time.copy()

# =========================
# 🔵 TOTAL REVENUE
# =========================
rev_current = df_current['Revenue'].sum()
rev_previous = df_previous['Revenue'].sum()

rev_delta = ((rev_current - rev_previous) / rev_previous * 100) if rev_previous > 0 else 0

delta_class_rev = "delta-pos" if rev_delta >= 0 else "delta-neg"
arrow_rev = "↑" if rev_delta >= 0 else "↓"

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">TOTAL REVENUE</div>
        <div class="value-text">${rev_current/1e6:,.2f}M</div>
        <div class="delta-wrapper">
            <span class="{delta_class_rev}">{arrow_rev} {abs(rev_delta):.1f}% YoY</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 🟢 TOP CATEGORY + SHARE
# =========================
top_cat_rev = df.groupby('Category')['Revenue'].sum()
top_cat = top_cat_rev.idxmax().replace('_', ' ')
top_share = (top_cat_rev.max() / top_cat_rev.sum()) * 100

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">TOP CATEGORY</div>
        <div class="value-text" title="{top_cat.title()}">{top_cat.title()}</div>
        <div class="delta-wrapper">
            <span class="delta-pos">{top_share:.1f}% of revenue</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 🟠 AVG TICKET
# =========================
avg_current = df_current.groupby('order_id')['Revenue'].sum().mean()
avg_previous = df_previous.groupby('order_id')['Revenue'].sum().mean()

avg_delta = ((avg_current - avg_previous) / avg_previous * 100) if avg_previous > 0 else 0

delta_class_avg = "delta-pos" if avg_delta >= 0 else "delta-neg"
arrow_avg = "↑" if avg_delta >= 0 else "↓"

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">AVG. TICKET</div>
        <div class="value-text">${avg_current:,.2f}</div>
        <div class="delta-wrapper">
            <span class="{delta_class_avg}">{arrow_avg} {abs(avg_delta):.1f}% YoY</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 🟣 VOLUME (ORDERS)
# =========================
orders_current = df_current['order_id'].nunique()
orders_previous = df_previous['order_id'].nunique()

orders_delta = ((orders_current - orders_previous) / orders_previous * 100) if orders_previous > 0 else 0

delta_class_ord = "delta-pos" if orders_delta >= 0 else "delta-neg"
arrow_ord = "↑" if orders_delta >= 0 else "↓"

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">VOLUME</div>
        <div class="value-text">{orders_current/1000:,.1f}K</div>
        <div class="delta-wrapper">
            <span class="{delta_class_ord}">{arrow_ord} {abs(orders_delta):.1f}% YoY</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- MAP & SLICERS ROW ---
st.subheader("Geographical Overview")
col_map_filters, col_map = st.columns([1, 3])

with col_map_filters:
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("##### Map Filters")
    st.write("Refine revenue map data:")
    map_states = st.multiselect("Filter by State", options=sorted(df['customer_state'].dropna().unique()), key="map_states")
    map_category = st.multiselect("Filter by Category", options=sorted(df['Category'].dropna().unique()), key="map_category")

with col_map:
    map_filter_df = df.copy()
    if map_states:
        map_filter_df = map_filter_df[map_filter_df['customer_state'].isin(map_states)]
    if map_category:
        map_filter_df = map_filter_df[map_filter_df['Category'].isin(map_category)]
        
    map_df = map_filter_df.dropna(subset=['geolocation_lat', 'geolocation_lng'])
    if not map_df.empty:
        state_map_df = map_df.groupby('customer_state').agg({
            'Revenue': 'sum',
            'geolocation_lat': 'mean',
            'geolocation_lng': 'mean'
        }).reset_index()
        
        geojson = get_brazil_geojson()
        
        if geojson:
            fig_map = px.choropleth(
                state_map_df,
                geojson=geojson,
                locations="customer_state",
                featureidkey="properties.sigla",
                color="Revenue",
                color_continuous_scale="Blues",
                template="plotly_dark",
                hover_name="customer_state"
            )

            # --- FUNDAL COMPLET TRANSPARENT ---
            fig_map.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=30, b=0),
                coloraxis_colorbar=dict(
                    title="Revenue",
                    tickfont=dict(color="white")
                )
            )

            # --- ASCUNDE TOT FUNDALUL GEO ---
            fig_map.update_geos(
                fitbounds="locations",
                visible=False,
                bgcolor='rgba(0,0,0,0)'
            )

            # --- STATE LABELS (NEGRU CLAR) ---
            fig_map.add_trace(go.Scattergeo(
                lat=state_map_df['geolocation_lat'],
                lon=state_map_df['geolocation_lng'],
                text=state_map_df['customer_state'],
                mode='text',
                textfont=dict(
                    color='black',
                    size=11,
                    family="Arial Black"
                ),
                hoverinfo='skip',
                showlegend=False
            ))

            # --- HOVER + INTERACTION CLEAN ---
            fig_map.update_traces(
                marker_line_color="rgba(255,255,255,0.2)",
                marker_line_width=0.5
            )

            fig_map.update_layout(clickmode="event+select")
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Failed to load map boundary data.")
    else:
        st.warning("No geographical data available for the selected filters.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 6 CHARTS ROW WITH GLOBAL FILTERS ---
st.subheader("Dashboard Analytics")
col_chart_filters, col_charts = st.columns([1, 3])

with col_chart_filters:
    st.markdown("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
    st.markdown("##### Chart Filters")
    st.write("Apply filters to update all analytics below:")
    chart_states = st.multiselect("Filter by State", options=sorted(df['customer_state'].dropna().unique()), key="c_state")
    chart_cats = st.multiselect("Filter by Category", options=sorted(df['Category'].dropna().unique()), key="c_cats")
    
filtered_df = df.copy()
if chart_states:
    filtered_df = filtered_df[filtered_df['customer_state'].isin(chart_states)]
if chart_cats:
    filtered_df = filtered_df[filtered_df['Category'].isin(chart_cats)]

with col_charts:
    r1c1, r1c2, r1c3 = st.columns(3)
    
    with r1c1:
        trend_df = filtered_df.groupby(filtered_df['Modern_Date'].dt.to_period("M")).agg({'Revenue': 'sum'}).reset_index()
        trend_df['Modern_Date'] = trend_df['Modern_Date'].astype(str)
        fig1 = px.line(trend_df, x='Modern_Date', y='Revenue', template="plotly_dark", title="Monthly Revenue Trend")
        fig1.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="")
        st.plotly_chart(fig1, use_container_width=True)

    with r1c2:
        aov_df = filtered_df.groupby('Category').agg(Revenue=('Revenue', 'sum'), Orders=('order_id', 'nunique')).reset_index()
        aov_df['AOV'] = aov_df['Revenue'] / aov_df['Orders']
        aov_df = aov_df.nlargest(10, 'AOV')
        fig2 = px.bar(aov_df, x='Category', y='AOV', template="plotly_dark", title="Highest Ticket Size by Category", color_discrete_sequence=['#00C6FF'])
        fig2.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    with r1c3:
        filtered_df['Hour'] = filtered_df['order_purchase_timestamp'].dt.hour
        hour_df = filtered_df.groupby('Hour')['order_id'].nunique().reset_index()
        fig3 = px.bar(hour_df, x='Hour', y='order_id', template="plotly_dark", title="Orders by Time of Day", color_discrete_sequence=['#007AFF'])
        fig3.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Hour of Day", yaxis_title="Orders")
        st.plotly_chart(fig3, use_container_width=True)

    r2c1, r2c2, r2c3 = st.columns(3)

    with r2c1:
        vol_trend_df = filtered_df.groupby(filtered_df['Modern_Date'].dt.to_period("M")).agg(Orders=('order_id', 'nunique')).reset_index()
        vol_trend_df['Modern_Date'] = vol_trend_df['Modern_Date'].astype(str)
        fig4 = px.line(vol_trend_df, x='Modern_Date', y='Orders', template="plotly_dark", title="Monthly Order Volume Trend", color_discrete_sequence=['#00C6FF'])
        fig4.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="Orders", xaxis_title="")
        st.plotly_chart(fig4, use_container_width=True)

    with r2c2:
        if not filtered_df.empty:
            weekday_df = filtered_df.copy()
            weekday_df['Weekday'] = weekday_df['order_purchase_timestamp'].dt.day_name()
            cats = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_df = weekday_df.groupby('Weekday')['Revenue'].sum().reindex(cats).reset_index()
            fig5 = px.bar(weekday_df, x='Weekday', y='Revenue', template="plotly_dark", title="Revenue by Day of Week", color_discrete_sequence=['#34C759'])
            fig5.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="")
            st.plotly_chart(fig5, use_container_width=True)

    with r2c3:
        if not filtered_df.empty:
            prod_names = filtered_df['Category'].astype(str).str.title() + " (" + filtered_df['product_id'].astype(str).str[:5] + ")"
            prod_df = filtered_df.groupby(prod_names)['Revenue'].sum().nlargest(10).reset_index()
            prod_df.columns = ['Product_Name', 'Revenue']
            
            fig6 = px.bar(prod_df, x='Revenue', y='Product_Name', orientation='h', template="plotly_dark", title="Top 10 Products by Revenue", color_discrete_sequence=['#007AFF'])
            fig6.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="", xaxis_title="")
            fig6.update_yaxes(autorange="reversed")
            st.plotly_chart(fig6, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- VISUALS ROW ---
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("Revenue Distribution by Category")
    tree_data = df.iloc[:2000] if len(df) > 0 else df
    color_range = [tree_data['Revenue'].quantile(0.05), tree_data['Revenue'].quantile(0.85)] if not tree_data.empty else None
    fig = px.treemap(tree_data, path=['Category'], values='Revenue', 
                     color='Revenue', color_continuous_scale='Blues', range_color=color_range, template="plotly_dark")
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Scenario Sandbox")
    st.write("Simulate Revenue Growth")
    growth = st.select_slider("Projected Growth (%)", options=[-10, 0, 10, 25, 50], value=0)
    simulated_rev = (total_rev * (1 + growth/100)) / 1e6
    
    st.markdown(f"""
        <div style="background-color: transparent; padding: 25px; border-radius: 20px; text-align: center; border: 1px solid rgba(255,255,255,0.15);">
            <p style="color: #AAA;">Estimated 2026 Revenue</p>
            <h2 style="font-size: 40px; color: #FFFFFF;">${simulated_rev:,.1f}M</h2>
        </div>
    """, unsafe_allow_html=True)

# --- EXPORT ---
st.markdown("---")
st.subheader("Export Financial Report")

# Coloane pentru plasarea butoanelor unul lângă altul
c_exp1, c_exp2, c_exp_empty = st.columns([1.5, 1.5, 5])

with c_exp1:
    buffer = io.BytesIO()
    df.head(1000).to_excel(buffer, index=False)
    st.download_button("Export to Excel", data=buffer.getvalue(), file_name="Nexus_Olist_Report.xlsx", icon=":material/table_view:", use_container_width=True)

with c_exp2:
    if FPDF is not None:
        filter_sig = f"{chart_states}_{chart_cats}"
        with st.spinner("Preparing PDF Document..."):
            pdf_data = generate_pdf_report_cached(total_rev, total_orders, avg_order, filter_sig, fig1, fig2, fig3, fig4, fig5, fig6)
        st.download_button("Download PDF", data=pdf_data, file_name="Nexus_Report.pdf", icon=":material/picture_as_pdf:", use_container_width=True)