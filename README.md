# Nexus Retail Analytics 📈

**Bachelor's Degree Project (Proiect de Licență)**

## 📖 About the Project
Nexus Retail Analytics is a comprehensive, interactive Business Intelligence (BI) and Data Science dashboard built using Python and Streamlit. This project was developed as a Bachelor's degree final project to demonstrate the practical application of data engineering, machine learning, and advanced data visualization techniques on real-world e-commerce data.

The platform features a modern, dark-mode user interface inspired by premium financial apps, offering seamless navigation across multiple analytical domains.

## 🎯 Purpose
The primary goal of this project is to transform raw, distributed e-commerce data into actionable business intelligence. It provides an end-to-end analytical tool intended for retail stakeholders, covering:
- **Performance Monitoring:** Real-time KPI tracking (Total Revenue, Average Order Value, Order Volume) with Year-over-Year (YoY) comparisons.
- **Predictive Analytics:** Forecasting future revenue trends at a global or category level using Machine Learning (Linear Regression).
- **Risk Management:** Identifying unusual purchasing patterns, bulk purchases, or potential pricing errors using Anomaly Detection (Isolation Forest).
- **Customer Intelligence:** Grouping customers based on their purchasing behavior using RFM (Recency, Frequency, Monetary) segmentation and K-Means clustering.
- **Sentiment Analysis:** Extracting Natural Language Processing (NLP) insights and topics from customer reviews to gauge product and seller satisfaction.

## 📊 Dataset Used
This project utilizes the **Olist Brazilian E-Commerce Dataset** (widely available on Kaggle). 
Olist is a Brazilian platform that connects small businesses to major marketplaces. The dataset consists of over 100,000 anonymized orders made at multiple marketplaces in Brazil.

The data pipeline automatically merges multiple relational CSV files, including:
- `olist_orders_dataset.csv` & `olist_order_items_dataset.csv`
- `olist_products_dataset.csv` & `product_category_name_translation.csv`
- `olist_order_payments_dataset.csv`
- `olist_customers_dataset.csv` & `olist_sellers_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_geolocation_dataset.csv` (used for interactive Choropleth maps)

*Note: The system mathematically projects historical timestamps to the present day to simulate a live, modern dashboard environment.*

## ⚙️ Key Features & Modules
1. **Executive Dashboard (`App.py`):** High-level metrics, customizable visual filters, revenue scenario sandbox, interactive geographic maps, and automated PDF/Excel report generation.
2. **Category Deep Analysis (`Page1-Deep_Analysis.py`):** Granular breakdown of sales evolution, payment methods, and top-performing products per specific category.
3. **Forecasting (`Page2-Forecasting.py`):** Time-series predictive insights estimating future performance bounds (confidence intervals) using historical aggregations.
4. **Anomaly Detection (`Page3-Anomaly_Detection.py`):** Unsupervised ML highlighting outliers in transaction values to find "whales" or errors.
5. **Network & Customers (`Page4-Seller_Analysis.py`):** 3D RFM Customer Segmentation (K-Means), geographic distribution of sellers, and NLP sentiment distribution with automated Portuguese-to-English translation.

## 🛠️ Technology Stack
- **Frontend/Framework:** Streamlit
- **Data Manipulation:** Pandas, NumPy
- **Machine Learning:** Scikit-Learn (Linear Regression, Isolation Forest, K-Means, StandardScaler)
- **Visualizations:** Plotly (Express & Graph Objects)
- **NLP / Text Analytics:** `deep-translator`, `re`, Python's `collections`
- **Reporting:** `fpdf` (PDF Generation), `kaleido` (Chart Image Export)

## 🚀 How to Run Locally
1. Clone the repository.
2. Ensure you have Python 3.9+ installed.
3. Install the required dependencies:
   ```bash
   pip install streamlit pandas plotly scikit-learn fpdf deep-translator kaleido openpyxl
   ```
4. Place the Olist CSV files inside the `Database/` folder in the root directory.
5. Run the Streamlit app:
   ```bash
   streamlit run App.py
   ```