# ==========================================
# King County House Pricing Dashboard
# ==========================================
# Fully dynamic, simplified, and portfolio-ready
# Features:
# - Dynamic KPIs, insights, recommendations
# - Interactive map
# - 4 dynamic charts including zipcode and histogram
# - Download buttons
# ==========================================

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------
# 1️⃣ Page Setup
# -----------------------------
st.set_page_config(page_title="King County House Pricing", layout="wide")
st.title("🏡 Property Market Analytics")

# -----------------------------
# 2️⃣ Load Data
# -----------------------------
csv_path = "../data/processed/cleaned_house_prices.csv"

if not os.path.exists(csv_path):
    st.error(f"File not found: {csv_path}")
    st.stop()

df = pd.read_csv(csv_path)

# -----------------------------
# 3️⃣ Sidebar Filters
# -----------------------------
st.sidebar.header("Filter Listings")
with st.sidebar.expander("Adjust Filters", expanded=True):
    min_price, max_price = st.slider(
        "Price Range ($)",
        int(df['price'].min()), int(df['price'].max()),
        (int(df['price'].min()), int(df['price'].max())),
        step=10000
    )
    min_bed, max_bed = st.slider(
        "Bedrooms",
        int(df['bedrooms'].min()), int(df['bedrooms'].max()),
        (int(df['bedrooms'].min()), int(df['bedrooms'].max()))
    )
    min_bath, max_bath = st.slider(
        "Bathrooms",
        int(df['bathrooms'].min()), int(df['bathrooms'].max()),
        (int(df['bathrooms'].min()), int(df['bathrooms'].max()))
    )

    if st.button("🔄 Reset Filters"):
        st.experimental_rerun()

# -----------------------------
# 4️⃣ Apply Filters
# -----------------------------
filtered = df[
    (df['price'] >= min_price) & (df['price'] <= max_price) &
    (df['bedrooms'] >= min_bed) & (df['bedrooms'] <= max_bed) &
    (df['bathrooms'] >= min_bath) & (df['bathrooms'] <= max_bath)
]

if filtered.empty:
    st.info("No listings match the current filters.")
    st.stop()

# -----------------------------
# 5️⃣ Dynamic KPIs
# -----------------------------
st.subheader("KPIs")
avg_price = filtered['price'].mean()
median_price = filtered['price'].median()
avg_sqft = filtered['sqft_living'].mean()
total_listings = len(filtered)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Price", f"${avg_price:,.0f}")
col2.metric("Median Price", f"${median_price:,.0f}")
col3.metric("Average Living Area (sqft)", f"{avg_sqft:,.0f}")
col4.metric("Total Listings", total_listings)

# Dynamic insight text
insight_text = f"""
Based on the selected filters:

- There are **{total_listings:,} listings** available.
- **Average price** is **${avg_price:,.0f}**.
- **Median price** is **${median_price:,.0f}**.
- **Average living area** is **{avg_sqft:,.0f} sqft**.
"""
st.markdown(insight_text)

# Optional commentary
if avg_price < df['price'].mean():
    st.markdown("*Tip: You are exploring properties below the overall market average.*")
else:
    st.markdown("*Tip: You are exploring higher-end properties above the market average.*")

# -----------------------------
# 6️⃣ Dynamic Recommendations
# -----------------------------
st.subheader("Top Recommendations")
filtered['price_per_sqft'] = filtered['price'] / filtered['sqft_living']
recommendations = filtered.sort_values('price_per_sqft').head(10)
rec_text = f"Showing top {len(recommendations)} best-value listings based on price per sqft."
st.markdown(rec_text)

st.dataframe(
    recommendations[['id','price','bedrooms','bathrooms','sqft_living','price_per_sqft']],
    use_container_width=True
)

# Download buttons
csv_rec = recommendations.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Recommendations as CSV",
    data=csv_rec,
    file_name="house_recommendations.csv",
    mime='text/csv'
)

csv_all = filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download All Filtered Data",
    data=csv_all,
    file_name="filtered_houses.csv",
    mime='text/csv'
)

# -----------------------------
# 7️⃣ Dynamic Interactive Map
# -----------------------------
st.subheader("Interactive Map of Listings")
fig_map = px.scatter_mapbox(
    filtered,
    lat="lat",
    lon="long",
    color="price",
    size="sqft_living",
    hover_name="zipcode",
    hover_data=["bedrooms","bathrooms","sqft_living","price","grade"],
    zoom=10,
    mapbox_style="open-street-map",
    title="Filtered King County Houses"
)
st.plotly_chart(fig_map, use_container_width=True)

# -----------------------------
# 8️⃣ Dynamic Charts
# -----------------------------
# Median Price by Bedrooms
st.subheader("Median Price by Bedrooms")
chart_data = filtered.groupby('bedrooms')['price'].median().reset_index()
st.bar_chart(chart_data.rename(columns={'bedrooms':'Bedrooms','price':'Median Price'}).set_index('Bedrooms'))

# Price vs Living Area
st.subheader("Price vs Living Area")
fig2 = px.scatter(
    filtered,
    x="sqft_living",
    y="price",
    color="bedrooms",
    size="sqft_living",
    hover_data=["zipcode","bathrooms"]
)
st.plotly_chart(fig2, use_container_width=True)

# Average Price by Zipcode (new chart)
st.subheader("Average Price by Zipcode")
avg_price_zipcode = (
    filtered.groupby('zipcode')['price']
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)
st.bar_chart(avg_price_zipcode.rename(columns={'zipcode':'Zipcode','price':'Average Price'}).set_index('Zipcode'))

# Price Distribution Histogram (new chart)
st.subheader("Price Distribution")
fig_hist = px.histogram(
    filtered,
    x="price",
    nbins=50,
    title="Distribution of House Prices",
    labels={"price":"Price ($)"},
    color_discrete_sequence=["teal"]
)
st.plotly_chart(fig_hist, use_container_width=True)
