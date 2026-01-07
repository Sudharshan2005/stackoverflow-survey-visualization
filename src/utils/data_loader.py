import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st

@st.cache_data
def load_data():
    """Load and cache the dataset"""
    try:
        # Try to load from data directory first
        data_path = Path('/Users/sudharshan/Documents/DeepKlarity/demo_survey.csv')
        if data_path.exists():
            df = pd.read_csv('/Users/sudharshan/Documents/DeepKlarity/demo_survey.csv', low_memory=False)
        else:
            # If not in data directory, try current directory
            df = pd.read_csv('/Users/sudharshan/Documents/DeepKlarity/demo_survey.csv', low_memory=False)
        
        # Basic cleaning
        # Remove columns with >50% null values
        threshold = len(df) * 0.5
        df = df.loc[:, df.isnull().sum() < threshold]
        
        # Clean up text columns
        text_cols = df.select_dtypes(include=['object']).columns
        for col in text_cols:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_schema():
    """Load column schema"""
    try:
        schema_path = Path('/Users/sudharshan/Documents/DeepKlarity/stack-overflow-developer-survey-2025/survey_results_schema.csv')
        if schema_path.exists():
            schema = pd.read_csv('/Users/sudharshan/Documents/DeepKlarity/stack-overflow-developer-survey-2025/survey_results_schema.csv')
        else:
            schema = pd.DataFrame()
        return schema
    except:
        return pd.DataFrame()

def preprocess_data(df):
    """Preprocess data for visualization"""
    # Create cleaned copy
    df_clean = df.copy()
    
    # Convert numeric columns
    numeric_cols = ['WorkExp', 'YearsCode', 'ToolCountWork', 'ToolCountPersonal', 'CompTotal']
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Create YearsCodeNum column for easier filtering
    df_clean['YearsCodeNum'] = pd.to_numeric(df_clean['YearsCode'], errors='coerce')
    
    return df_clean

def get_language_data(df, prefix='LanguageHaveWorkedWith'):
    """Extract language data from the dataset"""
    if prefix not in df.columns:
        return pd.Series(dtype='int64')
    
    # Split by semicolon and count
    languages = df[prefix].dropna().astype(str).str.split(';').explode()
    languages = languages.str.strip()
    
    # Count occurrences
    return languages.value_counts()

def get_tech_stack_data(df, tech_type='Language'):
    """Get technology stack data for different categories"""
    # Define column prefixes for different tech types
    tech_prefixes = {
        'Language': ['LanguageHaveWorkedWith', 'LanguageWantToWorkWith'],
        'Database': ['DatabaseHaveWorkedWith', 'DatabaseWantToWorkWith'],
        'Platform': ['PlatformHaveWorkedWith', 'PlatformWantToWorkWith'],
        'Webframe': ['WebframeHaveWorkedWith', 'WebframeWantToWorkWith']
    }
    
    if tech_type not in tech_prefixes:
        return pd.Series()
    
    prefixes = tech_prefixes[tech_type]
    all_counts = pd.Series(dtype='int64')
    
    for prefix in prefixes:
        if prefix in df.columns:
            tech_data = df[prefix].dropna().astype(str).str.split(';').explode()
            tech_data = tech_data.str.strip()
            counts = tech_data.value_counts()
            
            # Merge counts
            for tech, count in counts.items():
                if tech and tech != 'nan':
                    all_counts[tech] = all_counts.get(tech, 0) + count
    
    return all_counts