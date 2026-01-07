import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from plotly.subplots import make_subplots

def extract_tech_data(df, column_name):
    """Extract technology data from a column with semicolon-separated values"""
    if column_name not in df.columns:
        return pd.Series()
    
    tech_series = df[column_name].dropna().astype(str).str.split(';').explode()
    tech_series = tech_series.str.strip()
    
    # Remove empty strings
    tech_series = tech_series[tech_series != '']
    
    return tech_series.value_counts()

def plot_top_tech(df, column_name, title, top_n=10):
    """Plot top technologies from a column"""
    tech_counts = extract_tech_data(df, column_name).head(top_n)
    
    if len(tech_counts) == 0:
        return None
    
    fig = px.bar(
        x=tech_counts.values,
        y=tech_counts.index,
        orientation='h',
        title=title,
        labels={'x': 'Count', 'y': 'Technology'},
        color=tech_counts.values,
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        height=400,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    
    return fig

def plot_tech_comparison(df, have_col, want_col, title):
    """Compare technologies between have and want columns"""
    if have_col not in df.columns or want_col not in df.columns:
        return None
    
    have_counts = extract_tech_data(df, have_col).head(10)
    want_counts = extract_tech_data(df, want_col)
    
    # Merge the two series
    comparison_data = []
    for tech in have_counts.index:
        comparison_data.append({
            'Technology': tech,
            'Have': have_counts[tech],
            'Want': want_counts.get(tech, 0)
        })
    
    if not comparison_data:
        return None
    
    comparison_df = pd.DataFrame(comparison_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=comparison_df['Technology'],
        y=comparison_df['Have'],
        name='Currently Use',
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        x=comparison_df['Technology'],
        y=comparison_df['Want'],
        name='Want to Use',
        marker_color='#ff7f0e'
    ))
    
    fig.update_layout(
        title=title,
        barmode='group',
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig

def plot_age_distribution(df):
    """Plot age distribution"""
    if 'Age' not in df.columns:
        return None
    
    age_counts = df['Age'].value_counts()
    
    # Define age order
    age_order = [
        '18-24 years old',
        '25-34 years old', 
        '35-44 years old',
        '45-54 years old',
        '55-64 years old',
        '65 years or older'
    ]
    
    # Reorder based on age order
    age_counts = age_counts.reindex(age_order).dropna()
    
    fig = px.pie(
        values=age_counts.values,
        names=age_counts.index,
        title='Age Distribution of Developers',
        hole=0.3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def plot_experience_distribution(df):
    """Plot coding experience distribution"""
    if 'YearsCodeNum' not in df.columns:
        return None
    
    # Create experience groups
    df_copy = df.copy()
    df_copy['ExpGroup'] = pd.cut(
        df_copy['YearsCodeNum'],
        bins=[0, 2, 5, 10, 20, 100],
        labels=['0-2 years', '3-5 years', '6-10 years', '11-20 years', '20+ years'],
        include_lowest=True
    )
    
    exp_counts = df_copy['ExpGroup'].value_counts().sort_index()
    
    fig = px.bar(
        x=exp_counts.index,
        y=exp_counts.values,
        title='Years of Coding Experience',
        labels={'x': 'Experience Range', 'y': 'Number of Developers'},
        text=exp_counts.values
    )
    
    fig.update_traces(
        marker_color='#F48024',
        textposition='outside'
    )
    
    fig.update_layout(
        height=400,
        xaxis_tickangle=-45
    )
    
    return fig