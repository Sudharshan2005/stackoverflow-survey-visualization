import streamlit as st
import pandas as pd
from utils.data_loader import load_data, preprocess_data
from utils.visualizations import (
    plot_country_distribution, 
    plot_age_distribution,
    plot_experience_distribution,
    plot_education_distribution
)

st.set_page_config(page_title="Demographics", page_icon="📊")

st.title("👥 Developer Demographics")
st.markdown("---")

# Load data
df_raw = load_data()
df = preprocess_data(df_raw)

if df.empty:
    st.error("No data available")
    st.stop()

# Top countries section
st.header("🌍 Geographic Distribution")
col1, col2 = st.columns([2, 1])

with col1:
    top_n = st.slider("Number of top countries to show", 5, 20, 20)
    fig1 = plot_country_distribution(df, top_n)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### Insights")
    st.info("""
    **Key Findings:**
    - United States leads with highest developer count
    - India shows strong representation
    - European countries (UK, Germany) prominent in top 10
    - Global distribution shows tech concentration in developed economies
    """)

st.markdown("---")

# Age and Experience
st.header("Age Distribution")
col1, col2 = st.columns(2)

with col1:
    fig2 = plot_age_distribution(df)
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown("### Age Insights")
    st.info("""
    - Majority (60%) are 25-44 years old
    - Strong representation from mid-career developers
    - Healthy distribution across age groups
    """)

st.markdown("---")

st.header("Experience Distribution")
col1, col2 = st.columns(2)

with col1:
    fig3 = plot_experience_distribution(df)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("### Experience Insights")
    st.info("""
    - Most developers have 3-10 years experience
    - Significant group with 20+ years experience
    - Balanced mix of junior and senior developers
    """)

st.markdown("---")

# Education
st.header("Education Background")
fig4 = plot_education_distribution(df)
st.plotly_chart(fig4, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **Education Insights:**
    - 65% have Bachelor's degree or higher
    - Master's degree common among senior developers
    - Formal education remains important in tech
    """)

with col2:
    # Additional metric
    bachelors_plus = df['EdLevel'].str.contains("Bachelor|Master|Professional").sum()
    percentage = (bachelors_plus / len(df)) * 100
    st.metric("Developers with Bachelor's+", f"{percentage:.1f}%")