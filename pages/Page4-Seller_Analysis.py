import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from collections import Counter
import re
try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False
import os

st.set_page_config(page_title="Nexus | Network & Customers", layout="wide", initial_sidebar_state="collapsed")

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
        transform: translateX(15px) !important;
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

@st.cache_data(show_spinner=False)
def get_translated_reviews(df_reviews, sentiment, sample_size, has_translator):
    filtered = df_reviews[df_reviews['Sentiment'] == sentiment]
    if len(filtered) == 0:
        return []
    sample = filtered.sample(min(sample_size, len(filtered)), random_state=42)
    results = []
    for _, row in sample.iterrows():
        orig = str(row['review_comment_message'])
        score = row['Review_Score']
        if has_translator:
            try:
                trans = GoogleTranslator(source='pt', target='en').translate(orig)
                results.append((score, trans, orig))
            except Exception:
                results.append((score, orig, "translation failed"))
        else:
            results.append((score, orig, None))
    return results

@st.cache_data(show_spinner=False)
def get_translated_topics(text_list, has_translator):
    text = " ".join(text_list).lower()
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
    stopwords = {'the','and','for','with','this','that','was','are','but','not','you','very','have','had','has','they','them','from','all','too','can','just','its','get','got','did','dont','didnt','cant','could','would','product','order','store','seller','delivery','shipping','que','não','com','uma','para','produto','veio','mais','foi','meu','estou','muito','bem','chegou','antes','prazo','entregue','recebi','ainda','mas','como','sem','quando','pois','qualidade','bom','recomendo','otimo','excelente','loja'}
    filtered_words = [w for w in words if w not in stopwords]
    bigrams = [' '.join(b) for b in zip(filtered_words[:-1], filtered_words[1:])]
    common_topics_pt = Counter(bigrams).most_common(10)
    common_topics = []
    for topic, count in common_topics_pt:
        try:
            if has_translator:
                translated_topic = GoogleTranslator(source='pt', target='en').translate(topic)
                common_topics.append((translated_topic.title(), count))
            else:
                common_topics.append((topic.title(), count))
        except Exception:
            common_topics.append((topic.title(), count))
    return common_topics

# --- CONTENT ---
st.title("Sellers & Customers Intelligence")
st.markdown("Unified analysis of seller performance, customer segmentation, and review NLP.")

tab_seller, tab_customer, tab_nlp = st.tabs(["Sellers Deep Dive", "Customer Segments (RFM)", "Review NLP & Sentiment"])

with tab_seller:
    # --- AGGREGATE SELLER DATA ---
    seller_df = df.groupby('seller_id').agg(
        Total_Revenue=('Revenue', 'sum'),
        Total_Orders=('order_id', 'nunique'),
        Avg_Review_Score=('Review_Score', 'mean'),
        City=('seller_city', 'first'),
        State=('seller_state', 'first')
    ).reset_index()

    # --- ROW 1: KPIs ---
    c1, c2, c3, c4 = st.columns(4)

    total_sellers = seller_df['seller_id'].nunique()
    avg_rev = seller_df['Total_Revenue'].mean()
    top_seller_rev = seller_df['Total_Revenue'].max()
    avg_rating = seller_df['Avg_Review_Score'].mean()

    c1.metric("Total Sellers", f"{total_sellers:,}")
    c2.metric("Avg Revenue / Seller", f"${avg_rev:,.0f}")
    c3.metric("Top Seller Revenue", f"${top_seller_rev:,.0f}")
    c4.metric("Avg Rating", f"{avg_rating:.2f} ⭐")

# --- ROW 2: SELLER DISTRIBUTION & ORDER VOLUME ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Seller Distribution by State")
        state_dist = seller_df.groupby('State')['seller_id'].count().reset_index().rename(columns={'seller_id': 'Seller Count'})
        fig_state = px.bar(state_dist.sort_values('Seller Count', ascending=False).head(10), x='Seller Count', y='State', orientation='h', template="plotly_dark", color_discrete_sequence=['#007AFF'])
        fig_state.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_state, use_container_width=True)

    with col2:
        st.subheader("Busiest Sellers (Order Volume)")
        top_vol = seller_df.sort_values('Total_Orders', ascending=False).head(10)
        fig_vol = px.bar(top_vol, x='seller_id', y='Total_Orders', template="plotly_dark", color='Total_Orders', color_continuous_scale='Blues')
        fig_vol.update_xaxes(tickvals=top_vol['seller_id'], ticktext=[sid[:8] for sid in top_vol['seller_id']], title="Seller ID")
        fig_vol.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="Total Orders")
        st.plotly_chart(fig_vol, use_container_width=True)

with tab_customer:
    st.subheader("Machine Learning Customer Segmentation")
    with st.spinner("Processing RFM Clusters..."):
        orders_df = df.drop_duplicates(subset=['order_id'])

        sample_size = min(15000, len(orders_df))
        sample_df = orders_df.sample(sample_size, random_state=42) if sample_size > 0 else orders_df.copy()
        snapshot_date = sample_df['Modern_Date'].max() + pd.Timedelta(days=1)
        
        rfm = sample_df.groupby('customer_unique_id').agg({
            'Modern_Date': lambda x: (snapshot_date - x.max()).days,
            'order_id': 'nunique',
            'Revenue': 'sum'
        }).rename(columns={'Modern_Date': 'Recency', 'order_id': 'Frequency', 'Revenue': 'Monetary'}).reset_index()
        
        scaler = StandardScaler()
        rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])
        
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)
        
        cluster_names = {0: "Churned / Inactive", 1: "Loyal Customers", 2: "Whales / Big Spenders", 3: "New / Potential"}
        rfm['Segment'] = rfm['Cluster'].map(cluster_names)
        
        fig = px.scatter_3d(rfm, x='Recency', y='Frequency', z='Monetary',
                            color='Segment', template='plotly_dark',
                            opacity=0.7, color_discrete_sequence=px.colors.qualitative.Set1)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0))
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 🧠 Segment Insights")

        st.info("""
        - **Loyal Customers** → high frequency, stable revenue
        - **Whales** → few but very high spend
        - **Churned** → inactive users (risk)
        - **New** → growth opportunity
      """)

with tab_nlp:
    st.subheader("Customer Satisfaction & NLP Text Insights")
    if 'review_comment_message' in df.columns:
        reviews = df[['Review_Score', 'review_comment_message']].dropna(subset=['review_comment_message'])
        
        reviews['Sentiment'] = reviews['Review_Score'].apply(lambda x: "Positive" if x >= 4 else ("Neutral" if x == 3 else "Negative"))
        
        c1_nlp, c2_nlp = st.columns([1, 1.5])
        with c1_nlp:
            pie_data = reviews['Sentiment'].value_counts().reset_index()
            fig_pie = px.pie(pie_data, names='Sentiment', values='count', hole=0.5, template="plotly_dark",
                             color='Sentiment', color_discrete_map={'Positive': '#34C759', 'Neutral': '#AAAAAA', 'Negative': '#FF3B30'})
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2_nlp:
            st.markdown("### Customer Reviews Showcase")
            sentiment_filter = st.radio("Select Sentiment to Explore:", ["Positive", "Neutral", "Negative"], horizontal=True)
            if not HAS_TRANSLATOR:
                st.warning("`deep-translator` package not found. Run `pip install deep-translator` to enable English translation.")
            
            with st.spinner(f"Loading {sentiment_filter} reviews..."):
                sample_reviews = get_translated_reviews(reviews[['Review_Score', 'review_comment_message', 'Sentiment']], sentiment_filter, 3, HAS_TRANSLATOR)
                
            if sample_reviews:
                for score, text, orig in sample_reviews:
                    if orig and orig != "translation failed":
                        display_text = f"⭐ {score}/5 - \"{text}\" *(Original: {orig})*"
                    elif orig == "translation failed":
                        display_text = f"⭐ {score}/5 - \"{text}\" *(translation failed)*"
                    else:
                        display_text = f"⭐ {score}/5 - \"{text}\""
                    
                    if sentiment_filter == "Positive":
                        st.success(display_text)
                    elif sentiment_filter == "Neutral":
                        st.info(display_text)
                    else:
                        st.error(display_text)
            else:
                st.write("No reviews available for this sentiment.")

            st.markdown("### 🧠 Most Mentioned Topics in Reviews")

            # --- CACHED TOPIC EXTRACTION ---
            text_list = reviews['review_comment_message'].dropna().astype(str).tolist()
            common_topics = get_translated_topics(text_list, HAS_TRANSLATOR)

            # --- DISPLAY ---
            if common_topics:
                df_topics = pd.DataFrame(common_topics, columns=['Topic', 'Mentions'])
                fig_topics = px.bar(
                    df_topics, x='Mentions', y='Topic', orientation='h',
                    template='plotly_dark', color='Mentions', color_continuous_scale='Blues'
                )
                fig_topics.update_layout(yaxis={'categoryorder': 'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_topics, use_container_width=True)
    else:
        st.warning("Review text data is not available in the current dataset.")
        
       

        