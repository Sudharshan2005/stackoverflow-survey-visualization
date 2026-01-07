import streamlit as st
import pandas as pd
from utils.data_loader import load_data, preprocess_data
from utils.visualizations import (
    plot_ai_adoption_by_experience,
    plot_ai_sentiment,
    plot_ai_agent_impact,
    plot_ai_workflow_integration
)

st.set_page_config(page_title="AI Trends", page_icon="🤖")

st.title("🤖 AI in Development")
st.markdown("---")

# Load data
df_raw = load_data()
df = preprocess_data(df_raw)

if df.empty:
    st.error("No data available")
    st.stop()

# AI Adoption Overview
st.header("📈 AI Adoption Trends")
col1, col2 = st.columns(2)

with col1:
    # AI usage metric
    ai_users = df['AISelect'].str.contains('Yes').sum()
    ai_percentage = (ai_users / len(df)) * 100
    st.metric("Developers Using AI Tools", f"{ai_percentage:.1f}%")

with col2:
    # AI agent usage
    agent_users = df['AIAgents'].str.contains('Yes').sum()
    agent_percentage = (agent_users / len(df)) * 100
    st.metric("Using AI Agents", f"{agent_percentage:.1f}%")

st.markdown("---")

# Experience vs AI Usage
st.header("🎯 AI Adoption by Experience Level")
fig1 = plot_ai_adoption_by_experience(df)
st.plotly_chart(fig1, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **Key Insights:**
    - Junior developers (0-2 years) show highest AI adoption
    - Experienced developers (10+ years) more cautious
    - AI tools bridge knowledge gaps for beginners
    """)

with col2:
    # Trust metrics
    high_trust = df['AIAcc'].str.contains('Highly trust|Somewhat trust').sum()
    trust_percentage = (high_trust / len(df)) * 100
    st.metric("Trust AI Accuracy", f"{trust_percentage:.1f}%")

st.markdown("---")

# AI Sentiment
st.header("😊 Developer Sentiment")
fig2 = plot_ai_sentiment(df)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
**Sentiment Analysis:**
- Majority positive/neutral toward AI
- Significant group remains skeptical
- Correlates with experience level
""")

st.markdown("---")

# AI Workflow Integration
st.header("⚙️ AI in Development Workflow")
fig3 = plot_ai_workflow_integration(df)
if fig3:
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Workflow integration data not available")

st.markdown("""
**Workflow Integration:**
- Code generation most common use case
- Documentation and testing seeing AI adoption
- Planning and architecture less automated
""")

st.markdown("---")

# AI Agent Impact
st.header("🚀 AI Agent Impact")
fig4 = plot_ai_agent_impact(df)
if fig4:
    st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("""
    **Agent Impact:**
    - Productivity gains widely acknowledged
    - Quality improvements recognized
    - Learning acceleration noted
    - Team collaboration impact mixed
    """)
else:
    st.info("AI agent impact data not available")

# Future Skills
st.markdown("---")
st.header("🔮 Future Skills")
st.markdown("### What skills remain valuable with AI advancement?")

if 'AIOpen' in df.columns:
    # Sample some responses
    ai_responses = df['AIOpen'].dropna().head(10).tolist()
    
    with st.expander("View Developer Responses"):
        for i, response in enumerate(ai_responses, 1):
            if response and len(response) > 10:  # Filter very short responses
                st.markdown(f"{i}. {response}")
else:
    st.info("Future skills data not available in this dataset")