import streamlit as st
import pandas as pd
from utils.data_loader import load_data, preprocess_data
from utils.visualizations import (
    plot_tech_usage,
    plot_have_vs_want,
    plot_remote_work_by_orgsize
)

st.set_page_config(page_title="Technology", page_icon="💻")

st.title("💻 Technology Stack Analysis")
st.markdown("---")

# Load data
df_raw = load_data()
df = preprocess_data(df_raw)

if df.empty:
    st.error("No data available")
    st.stop()

# Programming Languages
st.header("🚀 Programming Languages")
col1, col2 = st.columns([3, 1])

with col1:
    top_n_lang = st.slider("Show top N languages", 5, 20, 15, key="lang_slider")
    fig1 = plot_tech_usage(df, f"Top {top_n_lang} Programming Languages", 
                          "LanguageHaveWorkedWith", top_n_lang)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### Language Insights")
    st.success("""
    **Trends:**
    - JavaScript remains dominant
    - Python continues growth
    - TypeScript adoption increasing
    - Rust gaining popularity
    """)

st.markdown("---")

# Have vs Want Comparison
st.header("🔄 Technology Adoption Trends")

tab1, tab2, tab3, tab4 = st.tabs(["Languages", "Databases", "Platforms", "Frameworks"])

with tab1:
    fig2 = plot_have_vs_want(df, "Language", "Programming Languages")
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("""
    **Language Adoption:**
    - Strong desire to learn Rust, Go, TypeScript
    - JavaScript/Python maintain high current usage
    - Niche languages show learning interest
    """)

with tab2:
    fig3 = plot_have_vs_want(df, "Database", "Databases")
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("""
    **Database Trends:**
    - PostgreSQL most wanted
    - Redis for caching popularity
    - MongoDB still widely used
    """)

with tab3:
    fig4 = plot_have_vs_want(df, "Platform", "Platforms")
    st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("""
    **Platform Preferences:**
    - Docker remains essential
    - Kubernetes learning demand high
    - AWS leads cloud adoption
    """)

with tab4:
    fig5 = plot_have_vs_want(df, "Webframe", "Web Frameworks")
    st.plotly_chart(fig5, use_container_width=True)
    
    st.markdown("""
    **Framework Trends:**
    - React dominates frontend
    - Next.js growing rapidly
    - Node.js strong for backend
    """)

st.markdown("---")

# Work Preferences
st.header("🏢 Work Environment Analysis")
fig6 = plot_remote_work_by_orgsize(df)
st.plotly_chart(fig6, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    remote_percentage = (df['RemoteWork'].str.contains('Remote').sum() / len(df)) * 100
    st.metric("Fully Remote", f"{remote_percentage:.1f}%")

with col2:
    hybrid_percentage = (df['RemoteWork'].str.contains('Hybrid').sum() / len(df)) * 100
    st.metric("Hybrid Work", f"{hybrid_percentage:.1f}%")

with col3:
    in_person = (df['RemoteWork'].str.contains('In-person').sum() / len(df)) * 100
    st.metric("In-Person", f"{in_person:.1f}%")

st.markdown("""
**Work Preference Insights:**
- Smaller companies more likely to offer remote work
- Larger enterprises prefer hybrid models
- Remote work remains popular post-pandemic
""")