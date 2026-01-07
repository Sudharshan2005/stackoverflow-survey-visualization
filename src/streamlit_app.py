import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import load_data, load_schema, preprocess_data, get_language_data, get_tech_stack_data
import numpy as np
import re

st.set_page_config(
    page_title="Stack Overflow Survey 2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #BCBBBB;
        background: linear-gradient(90deg, #F48024 0%, #BCBBBB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
        margin-bottom: 1rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #F48024;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #333;
    }
    .metric-card {
        background: linear-gradient(135deg, #2C2C2C 0%, #1A1A1A 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #F48024;
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
        height: 100%;
        border: 1px solid #333;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.3);
        border-left: 5px solid #FF9A52;
    }
    .metric-title {
        font-size: 0.9rem;
        color: #BCBBBB;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .insight-card {
        background: linear-gradient(135deg, #1A237E 0%, #283593 100%);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #3949AB;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .role-pill {
        display: inline-block;
        background: linear-gradient(135deg, #F48024 0%, #FF9A52 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .language-pill {
        display: inline-block;
        background: linear-gradient(135deg, #065F46 0%, #059669 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .salary-pill {
        display: inline-block;
        background: linear-gradient(135deg, #7C3AED 0%, #8B5CF6 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .filter-pill {
        display: inline-block;
        background: linear-gradient(135deg, #374151 0%, #4B5563 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.8rem;
        font-weight: 400;
        border: 1px solid #4B5563;
    }
    .stat-box {
        background: rgba(30, 41, 59, 0.5);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    .progress-bar {
        height: 6px;
        background: #334155;
        border-radius: 3px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #F48024 0%, #FF9A52 100%);
        border-radius: 3px;
    }
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #F48024 50%, transparent 100%);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


CURRENCY_RATES = {
    'USD': 1.0,
    'EUR': 1.08,      # European Euro
    'UAH': 0.026,     # Ukrainian hryvnia
    'INR': 0.012,     # Indian rupee
    'AUD': 0.65,      # Australian dollar
    'BDT': 0.0091,    # Bangladeshi taka
    'BRL': 0.20,      # Brazilian real
    'GBP': 1.25,      # Pound sterling
    'SEK': 0.095,     # Swedish krona
    'CZK': 0.044,     # Czech koruna
    'PLN': 0.25,      # Polish zloty
    'HUF': 0.0028,    # Hungarian forint
    'MYR': 0.21,      # Malaysian ringgit
    'CHF': 1.12,      # Swiss franc
    'EGP': 0.032,     # Egyptian pound
    'LKR': 0.0033,    # Sri Lankan rupee
    'RUB': 0.011,     # Russian ruble
    'RSD': 0.0095,    # Serbian dinar
    'JPY': 0.0067,    # Japanese yen
    'RON': 0.22,      # Romanian leu
    'CAD': 0.73,      # Canadian dollar
    'UYU': 0.026,     # Uruguayan peso
    'AED': 0.27,      # United Arab Emirates dirham
    'ARS': 0.0012,    # Argentine peso (hyperinflation adjusted)
    'NOK': 0.095,     # Norwegian krone
    'CRC': 0.0019,    # Costa Rican colon
    'PHP': 0.018,     # Philippine peso
    'CNY': 0.14,      # Chinese Yuan Renminbi
    'ILS': 0.27,      # Israeli new shekel
    'BGN': 0.55,      # Bulgarian lev
    'MAD': 0.10,      # Moroccan dirham
    'MXN': 0.058,     # Mexican peso
    'TRY': 0.033,     # Turkish lira
    'BOB': 0.14,      # Bolivian boliviano
    'NPR': 0.0075,    # Nepalese rupee
    'ZAR': 0.053,     # South African rand
    'TND': 0.32,      # Tunisian dinar
    'PKR': 0.0036,    # Pakistani rupee
    'SGD': 0.74,      # Singapore dollar
    'PYG': 0.00014,   # Paraguayan guarani
    'AZN': 0.59,      # Azerbaijan manat
    'DKK': 0.14,      # Danish krone
    'NGN': 0.00066,   # Nigerian naira
    'IRR': 0.000024,  # Iranian rial
    'HKD': 0.13,      # Hong Kong dollar
    'TWD': 0.031,     # New Taiwan dollar
    'VND': 0.000041,  # Vietnamese dong
    'CLP': 0.0011,    # Chilean peso
    'KRW': 0.00075,   # South Korean won
    'COP': 0.00026,   # Colombian peso
    'UGX': 0.00027,   # Ugandan shilling
    'JOD': 1.41,      # Jordanian dinar
    'IDR': 0.000064,  # Indonesian rupiah
    'ANG': 0.56,      # Netherlands Antillean guilder
    'MGA': 0.00022,   # Malagasy ariary
    'DOP': 0.018,     # Dominican peso
    'GTQ': 0.13,      # Guatemalan quetzal
    'QAR': 0.27,      # Qatari riyal
    'THB': 0.028,     # Thai baht
    'BAM': 0.55,      # Bosnia and Herzegovina convertible mark
    'AMD': 0.0025,    # Armenian dram
    'MZN': 0.016,     # Mozambican metical
    'KZT': 0.0021,    # Kazakhstani tenge
    'HNL': 0.040,     # Honduran lempira
    'GEL': 0.37,      # Georgian lari
    'KGS': 0.011,     # Kyrgyzstani som
    'MDL': 0.056,     # Moldovan leu
    'GHS': 0.081,     # Ghanaian cedi
    'DZD': 0.0074,    # Algerian dinar
    'KES': 0.0074,    # Kenyan shilling
    'NZD': 0.61,      # New Zealand dollar
    'IMP': 1.25,      # Manx pound (same as GBP)
    'XPF': 0.0094,    # CFP franc
    'FJD': 0.45,      # Fijian dollar
    'XCD': 0.37,      # East Caribbean dollar
    'PEN': 0.27,      # Peruvian sol
    'HTG': 0.0078,    # Haitian gourde
    'BHD': 2.65,      # Bahraini dinar
    'IQD': 0.00068,   # Iraqi dinar
    'KHR': 0.00025,   # Cambodian riel
    'UZS': 0.000081,  # Uzbekistani som
    'TJS': 0.091,     # Tajikistani somoni
    'ZMW': 0.040,     # Zambian kwacha
    'YER': 0.0040,    # Yemeni rial
    'ALL': 0.010,     # Albanian lek
    'MUR': 0.022,     # Mauritian rupee
    'LBP': 0.00066,   # Lebanese pound
    'BYN': 0.31,      # Belarusian ruble
    'TTD': 0.15,      # Trinidad and Tobago dollar
    'XOF': 0.0016,    # West African CFA franc
    'MVR': 0.065,     # Maldivian rufiyaa
    'BWP': 0.074,     # Botswana pula
    'RWF': 0.00081,   # Rwandan franc
    'XAF': 0.0016,    # Central African CFA franc
    'SAR': 0.27,      # Saudi Arabian riyal
    'MMK': 0.00048,   # Myanmar kyat
    'NAD': 0.053,     # Namibian dollar (same as ZAR)
    'AFN': 0.014,     # Afghan afghani
    'VES': 0.000036,  # Venezuelan bolivar (hyperinflation)
    'LYD': 0.21,      # Libyan dinar
    'CDF': 0.00037,   # Congolese franc
    'ETB': 0.018,     # Ethiopian birr
    'OMR': 2.60,      # Omani rial
    'BTN': 0.012,     # Bhutanese ngultrum (same as INR)
    'MRU': 0.027,     # Mauritanian ouguiya
    'SYP': 0.00040,   # Syrian pound
    'GYD': 0.0048,    # Guyanese dollar
    'KWD': 3.25,      # Kuwaiti dinar
    'GIP': 1.25,      # Gibraltar pound (same as GBP)
    'MOP': 0.12,      # Macanese pataca
    'ISK': 0.0072,    # Icelandic krona
    'JMD': 0.0064,    # Jamaican dollar
    'MKD': 0.018,     # Macedonian denar
    'CUP': 0.042,     # Cuban peso
    'LAK': 0.000048,  # Lao kip
    'TMT': 0.29,      # Turkmen manat
    'SZL': 0.053,     # Swazi lilangeni (same as ZAR)
    'BBD': 0.50,      # Barbadian dollar
    'MNT': 0.00029,   # Mongolian tugrik
    'TZS': 0.00039,   # Tanzanian shilling
    'BND': 0.74,      # Brunei dollar (same as SGD)
    'SRD': 0.029,     # Surinamese dollar
    'KPW': 0.0011,    # North Korean won
    'BSD': 1.0,       # Bahamian dollar (same as USD)
    'NIO': 0.027,     # Nicaraguan cordoba
    'GMD': 0.018,     # Gambian dalasi
    'MWK': 0.00059,   # Malawian kwacha
    'LSL': 0.053,     # Lesotho loti (same as ZAR)
    'AOA': 0.0012,    # Angolan kwanza
    'SDG': 0.0017,    # Sudanese pound
    'WST': 0.37,      # Samoan tala
    'KYD': 1.20,      # Cayman Islands dollar
    'PGK': 0.27,      # Papua New Guinean kina
    'DJF': 0.0056,    # Djiboutian franc
    'BIF': 0.00035,   # Burundi franc
    'BZD': 0.50,      # Belize dollar
    'HRK': 0.14,      # Croatian kuna
    'SLL': 0.000048,  # Sierra Leonean leone
    'CVE': 0.0098,    # Cape Verdean escudo
    'GNF': 0.00012,   # Guinean franc
    'Unknown': 1.0,   # Unknown currency (assume USD)
    'none': 1.0,      # No currency specified (assume USD)
}

def extract_currency_code(currency_text):
    """Extract 3-letter currency code from currency description"""
    if pd.isna(currency_text) or currency_text is None:
        return 'Unknown'
    
    currency_text = str(currency_text).strip()
    
    if currency_text == 'Unknown' or currency_text == 'none':
        return 'Unknown'
    
    currency_text = currency_text.replace('\t', ' ')
    
    match = re.match(r'^([A-Z]{3})\b', currency_text)
    if match:
        code = match.group(1)
        if code in CURRENCY_RATES:
            return code
    
    for code in CURRENCY_RATES.keys():
        if code in currency_text and code != 'Unknown' and code != 'none':
            return code
    
    if 'dollar' in currency_text.lower():
        if 'US' in currency_text or 'United States' in currency_text:
            return 'USD'
        elif 'Canada' in currency_text or 'Canadian' in currency_text:
            return 'CAD'
        elif 'Australia' in currency_text or 'Australian' in currency_text:
            return 'AUD'
        elif 'New Zealand' in currency_text:
            return 'NZD'
        elif 'Singapore' in currency_text:
            return 'SGD'
        else:
            return 'USD' 
    
    elif 'euro' in currency_text.lower():
        return 'EUR'
    elif 'pound' in currency_text.lower() or 'sterling' in currency_text.lower():
        return 'GBP'
    elif 'yen' in currency_text.lower():
        return 'JPY'
    elif 'rupee' in currency_text.lower():
        if 'India' in currency_text or 'Indian' in currency_text:
            return 'INR'
        elif 'Pakistan' in currency_text:
            return 'PKR'
        elif 'Sri Lanka' in currency_text:
            return 'LKR'
        elif 'Nepal' in currency_text:
            return 'NPR'
        else:
            return 'INR' 
    
    return 'Unknown'

def clean_salary_value(salary):
    """Clean salary value by converting to float and handling edge cases"""
    if pd.isna(salary) or salary is None:
        return None
    
    salary_str = str(salary).strip()
    
    salary_str = re.sub(r'[^\d.-]', '', salary_str)
    
    if salary_str == '' or salary_str == '.' or salary_str == '-':
        return None
    
    try:
        salary_float = float(salary_str)
        
        if salary_float < 1000 or salary_float > 10000000:
            return None
        
        return salary_float
    except (ValueError, TypeError):
        return None

def convert_to_usd(amount, currency_text):
    """Convert amount from any currency to USD"""
    if pd.isna(amount) or pd.isna(currency_text):
        return None
    
    amount_clean = clean_salary_value(amount)
    if amount_clean is None:
        return None
    
    currency_code = extract_currency_code(currency_text)
    
    conversion_rate = CURRENCY_RATES.get(currency_code, 1.0)
    
    usd_amount = amount_clean * conversion_rate
    
    if usd_amount < 1000 or usd_amount > 10000000:
        return None
    
    return usd_amount

def format_currency(value):
    """Format currency values with K, M, B suffixes"""
    if pd.isna(value) or value is None or value == 0:
        return "$0"
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "$0"
    
    abs_value = abs(value)
    if abs_value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif abs_value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif abs_value >= 10_000:
        return f"${value/1_000:.0f}K"
    elif abs_value >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:,.0f}"

def format_number(num):
    """Format numbers with K, M suffixes"""
    if pd.isna(num) or num is None:
        return "0"
    
    try:
        num = float(num)
    except (ValueError, TypeError):
        return "0"
    
    if abs(num) >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif abs(num) >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{int(num):,}"

def convert_all_salaries_to_usd(df, salary_col, currency_col):
    """Convert all salaries in dataframe to USD"""
    usd_salaries = []
    currency_codes = []
    
    for idx, row in df.iterrows():
        salary = row[salary_col] if salary_col in row else None
        currency = row[currency_col] if currency_col in row else None
        
        if pd.notna(salary) and pd.notna(currency):
            usd_amount = convert_to_usd(salary, currency)
            currency_code = extract_currency_code(currency)
            usd_salaries.append(usd_amount)
            currency_codes.append(currency_code)
        else:
            usd_salaries.append(None)
            currency_codes.append(None)
    
    df_usd = df.copy()
    df_usd['Salary_USD'] = usd_salaries
    df_usd['Currency_Code'] = currency_codes
    
    df_usd = df_usd.dropna(subset=['Salary_USD'])
    
    if len(df_usd) > 10:
        mean_salary = df_usd['Salary_USD'].mean()
        std_salary = df_usd['Salary_USD'].std()
        lower_bound = max(1000, mean_salary - 3 * std_salary)
        upper_bound = min(1000000, mean_salary + 3 * std_salary)
        df_usd = df_usd[(df_usd['Salary_USD'] >= lower_bound) & (df_usd['Salary_USD'] <= upper_bound)]
    
    return df_usd

def clean_language_data(languages_series):
    """Clean language data by removing unknowns and empty strings"""
    if languages_series.empty:
        return pd.Series(dtype='int64')
    
    languages = languages_series.dropna().astype(str).str.split(';').explode()
    languages = languages.str.strip()
    exclude_terms = ['unknown', 'none', 'nan', '', 'null', 'na', 'n/a', 'other']
    languages = languages[~languages.str.lower().isin(exclude_terms)]
    languages = languages[languages != '']
    
    return languages.value_counts()

@st.cache_data
def load_all_data():
    with st.spinner("📊 Loading dataset..."):
        df_raw = load_data()
        schema = load_schema()
        df = preprocess_data(df_raw)
    return df, schema, df_raw

df, schema, df_raw = load_all_data()

if df.empty:
    st.error("Failed to load data. Please check if data files exist.")
    st.stop()

st.sidebar.title("🎯 Dashboard Controls")
st.sidebar.markdown("---")

st.sidebar.subheader("🌍 Filter by Country")
if 'Country' in df.columns:
    countries = ['All Countries'] + sorted(df['Country'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox("Select Country", countries, key='country_filter')
else:
    selected_country = 'All Countries'

if selected_country != 'All Countries' and 'Country' in df.columns:
    df_filtered = df[df['Country'] == selected_country]
else:
    df_filtered = df

st.sidebar.subheader("📅 Filter by Experience")
exp_ranges = ['All Experience', '0-2 years', '3-5 years', '6-10 years', '11-20 years', '20+ years']
selected_exp = st.sidebar.selectbox("Years of Experience", exp_ranges, key='exp_filter')

if selected_exp != 'All Experience' and 'YearsCodeNum' in df_filtered.columns:
    if selected_exp == '0-2 years':
        df_filtered = df_filtered[df_filtered['YearsCodeNum'] <= 2]
    elif selected_exp == '3-5 years':
        df_filtered = df_filtered[(df_filtered['YearsCodeNum'] >= 3) & (df_filtered['YearsCodeNum'] <= 5)]
    elif selected_exp == '6-10 years':
        df_filtered = df_filtered[(df_filtered['YearsCodeNum'] >= 6) & (df_filtered['YearsCodeNum'] <= 10)]
    elif selected_exp == '11-20 years':
        df_filtered = df_filtered[(df_filtered['YearsCodeNum'] >= 11) & (df_filtered['YearsCodeNum'] <= 20)]
    elif selected_exp == '20+ years':
        df_filtered = df_filtered[df_filtered['YearsCodeNum'] > 20]

st.sidebar.subheader("👨‍💻 Filter by Role")
if 'DevType' in df_filtered.columns:
    roles = df_filtered['DevType'].dropna().astype(str).str.split(';').explode()
    roles = roles.str.strip()
    unique_roles = ['All Roles'] + sorted([r for r in roles.unique() if r and r.lower() != 'other'])
    selected_role = st.sidebar.selectbox("Select Developer Role", unique_roles[:20], key='role_filter')
    
    if selected_role != 'All Roles':
        # Use regex=False to avoid warning
        df_filtered = df_filtered[df_filtered['DevType'].astype(str).str.contains(selected_role, na=False, regex=False)]
else:
    selected_role = 'All Roles'

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Active Filters")
st.sidebar.markdown(f'<div class="filter-pill">{selected_role}</div>', unsafe_allow_html=True)
st.sidebar.markdown(f'<div class="filter-pill">{selected_country}</div>', unsafe_allow_html=True)
st.sidebar.markdown(f'<div class="filter-pill">{selected_exp}</div>', unsafe_allow_html=True)
st.sidebar.markdown(f'<div style="margin-top: 1rem; color: #9CA3AF; font-size: 0.9rem;">Responses: <strong>{format_number(len(df_filtered))}</strong></div>', unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 6])

with col_logo:
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        justify-content: flex-end;
        height: 100%;
        padding-right: 0.5rem;
    ">
        <div style="
            background: linear-gradient(135deg, #F48024 0%, #FF9A52 100%);
            width: 80px;
            height: 80px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 20px rgba(244, 128, 36, 0.3);
        ">
            <span style="font-size: 2.5rem; color: white;">📊</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_title:
    st.markdown("""
    <div style="
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
        padding-left: 0;
    ">
        <h1 style="
            margin: 0;
            padding: 0;
            line-height: 1.1;
        ">
            Stack Overflow Developer Survey 2025
        </h1>
        <h3 style="
            margin: 0;
            padding: 0;
            color: #6b7280;
            font-weight: 400;
        ">
            Interactive Analytics Dashboard
        </h3>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Row 1: Key Metrics
st.markdown("### 📈 Global Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">Total Developers</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{format_number(len(df_filtered))}</div>', unsafe_allow_html=True)
    
    # Country count
    if 'Country' in df_filtered.columns:
        country_count = df_filtered['Country'].nunique()
        st.markdown(f'<div style="color: #9CA3AF; font-size: 0.9rem;">Across {country_count} countries</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">Avg Experience</div>', unsafe_allow_html=True)
    if 'YearsCodeNum' in df_filtered.columns:
        avg_exp = df_filtered['YearsCodeNum'].mean()
        if pd.notna(avg_exp):
            st.markdown(f'<div class="metric-value">{avg_exp:.1f} years</div>', unsafe_allow_html=True)
            
            # Experience distribution indicator
            if avg_exp > 10:
                exp_level = "Senior"
                color = "#F48024"
            elif avg_exp > 5:
                exp_level = "Mid-Level"
                color = "#FF9A52"
            else:
                exp_level = "Entry-Level"
                color = "#BCBBBB"
            
            st.markdown(f'<div style="color: {color}; font-size: 0.9rem; font-weight: 600;">{exp_level} weighted</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">AI Adoption Rate</div>', unsafe_allow_html=True)
    if 'AISelect' in df_filtered.columns:
        ai_users = df_filtered['AISelect'].astype(str).str.contains('Yes', case=False, na=False).sum()
        ai_percentage = (ai_users / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
        st.markdown(f'<div class="metric-value">{ai_percentage:.1f}%</div>', unsafe_allow_html=True)
        
        # Trend indicator
        if ai_percentage > 50:
            trend = "🔥 High Adoption"
        elif ai_percentage > 25:
            trend = "📈 Growing"
        else:
            trend = "📊 Emerging"
        
        st.markdown(f'<div style="color: #9CA3AF; font-size: 0.9rem;">{trend}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">Remote Work %</div>', unsafe_allow_html=True)
    if 'RemoteWork' in df_filtered.columns:
        remote_count = df_filtered['RemoteWork'].astype(str).str.contains('Remote', case=False, na=False).sum()
        remote_percentage = (remote_count / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
        st.markdown(f'<div class="metric-value">{remote_percentage:.1f}%</div>', unsafe_allow_html=True)
        
        # Additional stats
        hybrid_count = df_filtered['RemoteWork'].astype(str).str.contains('Hybrid', case=False, na=False).sum()
        hybrid_percentage = (hybrid_count / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
        
        st.markdown(f'<div style="color: #9CA3AF; font-size: 0.9rem;">Hybrid: {hybrid_percentage:.1f}%</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Row 2: Developer Roles & Language Trends
st.markdown('<div class="sub-header">👨‍💻 Developer Roles & Tech Stack</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("##### 🎯 Top Developer Roles")
    
    if 'DevType' in df_filtered.columns:
        roles = df_filtered['DevType'].dropna().astype(str).str.split(';').explode()
        roles = roles.str.strip()
        # Filter out irrelevant roles
        roles = roles[~roles.str.contains('Other', case=False, na=False)]
        role_counts = roles.value_counts().head(8)
        
        # Display as pills
        role_html = ""
        for role, count in role_counts.items():
            percentage = (count / len(df_filtered)) * 100
            role_html += f'<span class="role-pill" title="{role}: {percentage:.1f}%">{role[:20]}{"..." if len(role) > 20 else ""} ({percentage:.0f}%)</span>'
        
        st.markdown(role_html, unsafe_allow_html=True)
        
        # Detailed breakdown in expander
        with st.expander("View Detailed Role Analysis"):
            if len(role_counts) > 0:
                fig_roles = px.bar(
                    x=role_counts.values,
                    y=role_counts.index,
                    orientation='h',
                    title="Developer Role Distribution",
                    labels={'x': 'Count', 'y': 'Role'},
                    color=role_counts.values,
                    color_continuous_scale='oranges'
                )
                fig_roles.update_layout(height=400)
                st.plotly_chart(fig_roles, use_container_width=True)
    else:
        st.info("Role data not available")

with col2:
    st.markdown("##### 💻 Top Programming Languages")
    
    if 'LanguageHaveWorkedWith' in df_filtered.columns:
        language_counts = clean_language_data(df_filtered['LanguageHaveWorkedWith']).head(10)
        
        # Display as pills
        lang_html = ""
        for lang, count in language_counts.head(8).items():
            percentage = (count / len(df_filtered)) * 100
            lang_html += f'<span class="language-pill" title="{lang}: {percentage:.1f}%">{lang[:15]}{"..." if len(lang) > 15 else ""} ({percentage:.0f}%)</span>'
        
        st.markdown(lang_html, unsafe_allow_html=True)
        
        if 'LanguageWantToWorkWith' in df_filtered.columns:
            wanted_langs = clean_language_data(df_filtered['LanguageWantToWorkWith'])
            
            trending_langs = []
            for lang in wanted_langs.head(10).index:
                if lang in language_counts.index:
                    have_rank = list(language_counts.index).index(lang) + 1
                    want_rank = list(wanted_langs.index).index(lang) + 1
                    if want_rank < have_rank:  # Higher in wanted list
                        trending_langs.append(lang)
            
            if trending_langs:
                st.markdown("##### 📈 Trending Languages")
                trend_html = ""
                for lang in trending_langs[:3]:
                    trend_html += f'<span class="language-pill" style="background: linear-gradient(135deg, #7C3AED 0%, #8B5CF6 100%);">↑ {lang[:15]}</span> '
                st.markdown(trend_html, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

st.markdown('<div class="sub-header">💰 Global Salary Analysis (Converted to USD)</div>', unsafe_allow_html=True)

salary_col = None
currency_col = None

if 'CompTotal' in df_filtered.columns and 'Currency' in df_filtered.columns:
    salary_col = 'CompTotal'
    currency_col = 'Currency'
elif 'ConvertedCompYearly' in df_filtered.columns:
    salary_col = 'ConvertedCompYearly'
elif 'Compensation' in df_filtered.columns:
    salary_col = 'Compensation'

if salary_col:
    if currency_col and salary_col == 'CompTotal':
        
        # Convert all salaries to USD
        df_usd = convert_all_salaries_to_usd(df_filtered, salary_col, currency_col)
        usd_salary_series = df_usd['Salary_USD']
        
        if 'Currency_Code' in df_usd.columns:
            
            top_currencies = df_usd['Currency_Code'].value_counts().head(10)
            
            with st.expander("🌍 View Currency Distribution"):
                fig_currency = px.bar(
                    x=top_currencies.values,
                    y=top_currencies.index,
                    orientation='h',
                    title="Top 10 Currencies in Dataset",
                    labels={'x': 'Number of Responses', 'y': 'Currency Code'},
                    color_discrete_sequence=['#10B981']
                )
                fig_currency.update_layout(height=300)
                st.plotly_chart(fig_currency, use_container_width=True)
    else:
        usd_salary_series = df_filtered[salary_col].apply(clean_salary_value)
        usd_salary_series = usd_salary_series.dropna()
        df_usd = pd.DataFrame({'Salary_USD': usd_salary_series})
    
    if len(usd_salary_series) > 0:        
        # Salary metrics
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        
        with col_s1:
            avg_salary = usd_salary_series.mean()
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.9rem; color: #9CA3AF;">Average Salary</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 1.8rem; font-weight: 700; color: white;">{format_currency(avg_salary)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.8rem; color: #6B7280;">USD per year</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_s2:
            median_salary = usd_salary_series.median()
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.9rem; color: #9CA3AF;">Median Salary</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 1.8rem; font-weight: 700; color: white;">{format_currency(median_salary)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.8rem; color: #6B7280;">USD per year</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_s3:
            top_25 = usd_salary_series.quantile(0.75)
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.9rem; color: #9CA3AF;">Top 25% Earns</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 1.8rem; font-weight: 700; color: white;">>{format_currency(top_25)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.8rem; color: #6B7280;">USD per year</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_s4:
            bottom_25 = usd_salary_series.quantile(0.25)
            st.markdown('<div class="stat-box">', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.9rem; color: #9CA3AF;">Bottom 25% Earns</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 1.8rem; font-weight: 700; color: white;">{format_currency(bottom_25)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 0.8rem; color: #6B7280;">USD per year</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Salary distribution chart
        fig_salary = px.histogram(
            x=usd_salary_series,
            nbins=30,
            title="Salary Distribution (Converted to USD)",
            labels={'x': 'Annual Salary (USD)', 'y': 'Number of Developers'},
            color_discrete_sequence=['#F48024']
        )
        
        fig_salary.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Annual Salary (USD)",
            yaxis_title="Number of Developers",
            bargap=0.1
        )
        
        fig_salary.add_vline(
            x=avg_salary,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {format_currency(avg_salary)}",
            annotation_position="top right"
        )
        fig_salary.add_vline(
            x=median_salary,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Median: {format_currency(median_salary)}",
            annotation_position="top left"
        )
        
        st.plotly_chart(fig_salary, use_container_width=True)
        
        tab1, tab2 = st.tabs(["📊 Salary by Role", "🌍 Salary by Country"])
        
        with tab1:
            if 'DevType' in df_usd.columns:
                role_salary_data = []
                roles = df_usd['DevType'].dropna().astype(str).str.split(';').explode()
                top_roles = roles.value_counts().head(15).index
                
                for role in top_roles:
                    role_mask = df_usd['DevType'].astype(str).str.contains(role, na=False, regex=False)
                    role_salaries = df_usd[role_mask]['Salary_USD']
                    
                    if len(role_salaries) > 5:
                        avg_salary_role = role_salaries.mean()
                        role_salary_data.append({
                            'Role': role[:30] + ('...' if len(role) > 30 else ''),
                            'Avg Salary (USD)': avg_salary_role,
                            'Count': len(role_salaries)
                        })
                
                if role_salary_data:
                    role_df = pd.DataFrame(role_salary_data).sort_values('Avg Salary (USD)', ascending=False)
                    
                    fig_role_salary = px.bar(
                        role_df.head(10),
                        x='Avg Salary (USD)',
                        y='Role',
                        orientation='h',
                        title="Average Salary by Role (USD, Top 10)",
                        color='Avg Salary (USD)',
                        color_continuous_scale='viridis',
                        labels={'Avg Salary (USD)': 'Average Salary (USD)', 'Role': ''}
                    )
                    fig_role_salary.update_layout(
                        height=400,
                        xaxis_title="Average Salary (USD)",
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig_role_salary, use_container_width=True)
        
        with tab2:
            if 'Country' in df_usd.columns:
                country_salary_data = []
                country_groups = df_usd.groupby('Country')
                
                for country, group in country_groups:
                    country_salaries = group['Salary_USD']
                    
                    if len(country_salaries) >= 3:  # At least 3 responses
                        avg_salary_country = country_salaries.mean()
                        country_salary_data.append({
                            'Country': country,
                            'Avg Salary (USD)': avg_salary_country,
                            'Count': len(country_salaries)
                        })
                
                if country_salary_data:
                    country_df = pd.DataFrame(country_salary_data).sort_values('Avg Salary (USD)', ascending=False)
                    
                    # Top 10 countries
                    top_countries = country_df.head(10)
                    
                    fig_country = px.bar(
                        top_countries,
                        x='Avg Salary (USD)',
                        y='Country',
                        orientation='h',
                        title="Top 10 Countries by Average Salary (USD)",
                        color='Avg Salary (USD)',
                        color_continuous_scale='plasma',
                        labels={'Avg Salary (USD)': 'Average Salary (USD)', 'Country': ''}
                    )
                    fig_country.update_layout(
                        height=400,
                        xaxis_title="Average Salary (USD)",
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig_country, use_container_width=True)
                    
                    
    else:
        st.warning(f"⚠️ No valid salary data available for current filters")
        with st.expander("🔍 Debug Salary Data"):
            st.write("### Raw Salary Data Sample:")
            st.write(df_filtered[[salary_col, currency_col] if currency_col else salary_col].head(10))
            st.write("### Data Types:")
            st.write(f"Salary column type: {df_filtered[salary_col].dtype}")
            if currency_col:
                st.write(f"Currency column type: {df_filtered[currency_col].dtype}")
else:
    st.info("Salary data not available in this dataset")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Row 4: Quick Insights & Summary
st.markdown('<div class="sub-header">🔍 Key Insights & Summary</div>', unsafe_allow_html=True)

col_i1, col_i2, col_i3 = st.columns(3)

with col_i1:
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    st.markdown('##### 📊 Current Filter Summary')
    
    insights = []
    
    filtered_pct = (len(df_filtered) / len(df)) * 100 if len(df) > 0 else 0
    insights.append(f"• Viewing {filtered_pct:.1f}% of total dataset")
    
    if 'Country' in df_filtered.columns and selected_country != 'All Countries':
        country_count_filtered = len(df_filtered)
        insights.append(f"• {country_count_filtered} responses from {selected_country}")
    
    if 'YearsCodeNum' in df_filtered.columns:
        avg_exp_filtered = df_filtered['YearsCodeNum'].mean()
        insights.append(f"• {avg_exp_filtered:.1f} years average experience")
    
    if 'DevType' in df_filtered.columns and selected_role != 'All Roles':
        role_count = len(df_filtered)
        insights.append(f"• {role_count} {selected_role} developers")
    
    for insight in insights:
        st.markdown(f'<div style="color: #E5E7EB; margin: 0.5rem 0;">{insight}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_i2:
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    st.markdown('##### 📈 Market Trends')
    
    trends = []
    
    if 'AISelect' in df_filtered.columns:
        ai_users = df_filtered['AISelect'].astype(str).str.contains('Yes', case=False, na=False).sum()
        ai_percentage = (ai_users / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
        trends.append(f"• AI adoption: {ai_percentage:.1f}%")
    
    if 'RemoteWork' in df_filtered.columns:
        remote_percentage = (df_filtered['RemoteWork'].astype(str).str.contains('Remote', case=False, na=False).sum() / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
        trends.append(f"• Remote work: {remote_percentage:.1f}%")
    
    if 'usd_salary_series' in locals() and len(usd_salary_series) > 0:
        salary_median = usd_salary_series.median()
        trends.append(f"• Median salary: {format_currency(salary_median)}")
    
    if 'LanguageHaveWorkedWith' in df_filtered.columns:
        top_lang = clean_language_data(df_filtered['LanguageHaveWorkedWith'])
        if not top_lang.empty:
            top_lang_name = top_lang.index[0]
            trends.append(f"• Top language: {top_lang_name}")
    
    for trend in trends[:4]:  # Limit to 4 trends
        st.markdown(f'<div style="color: #E5E7EB; margin: 0.5rem 0;">{trend}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_i3:
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    st.markdown('##### 🚀 Recommendations')
    
    recommendations = []
    
    if 'AISelect' in df_filtered.columns:
        ai_percentage = (df_filtered['AISelect'].astype(str).str.contains('Yes', case=False, na=False).sum() / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
        if ai_percentage < 50:
            recommendations.append("• Consider AI skill development")
    
    if 'usd_salary_series' in locals() and len(usd_salary_series) > 0:
        salary_median = usd_salary_series.median()
        if salary_median < 50000:
            recommendations.append("• Entry-level market opportunity")
        elif salary_median > 150000:
            recommendations.append("• High-value specialized skills")
        else:
            recommendations.append("• Competitive market segment")
    
    if 'YearsCodeNum' in df_filtered.columns:
        avg_exp = df_filtered['YearsCodeNum'].mean()
        if avg_exp < 3:
            recommendations.append("• Focus on foundational skills")
        elif avg_exp < 7:
            recommendations.append("• Build specialized expertise")
        else:
            recommendations.append("• Explore leadership roles")
    
    if not recommendations:
        recommendations = [
            "• Stay updated with latest tech",
            "• Network with professionals",
            "• Contribute to open source",
            "• Continuous learning"
        ]
    
    for rec in recommendations[:4]:  # Limit to 4 recommendations
        st.markdown(f'<div style="color: #E5E7EB; margin: 0.5rem 0;">{rec}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

avg_exp_value = None
if 'YearsCodeNum' in df_filtered.columns:
    avg_exp_value = df_filtered['YearsCodeNum'].mean()
avg_exp_text = f"{avg_exp_value:.1f}" if avg_exp_value is not None and pd.notna(avg_exp_value) else "N/A"

st.markdown(f"""
<div style="text-align: center; color: #6B7280; padding: 2rem 1rem; font-size: 0.9rem;">
    <p>📊 <strong>Stack Overflow Developer Survey 2025</strong> • Interactive Analytics Dashboard</p>
    <p>Data Source: Stack Overflow • Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
    <p style="margin-top: 0.5rem; font-size: 0.8rem; color: #4B5563;">
        Filtered Data: {format_number(len(df_filtered))} responses • 
        {df_filtered['Country'].nunique() if 'Country' in df_filtered.columns else 'N/A'} countries • 
        {avg_exp_text} years avg experience
    </p>
</div>
""", unsafe_allow_html=True)

# Debug section
with st.expander("🔧 Debug Information"):
    st.write("### Available Columns")
    st.write(f"Total columns: {len(df.columns)}")
    
    st.write("### Column Groups")
    
    lang_cols = [col for col in df.columns if 'Language' in col]
    st.write(f"Language columns ({len(lang_cols)}): {lang_cols[:5]}{'...' if len(lang_cols) > 5 else ''}")
    
    db_cols = [col for col in df.columns if 'Database' in col]
    st.write(f"Database columns ({len(db_cols)}): {db_cols[:5]}{'...' if len(db_cols) > 5 else ''}")
    
    ai_cols = [col for col in df.columns if 'AI' in col]
    st.write(f"AI columns ({len(ai_cols)}): {ai_cols[:5]}{'...' if len(ai_cols) > 5 else ''}")
    
    currency_cols = [col for col in df.columns if 'Currency' in col or 'currency' in col.lower()]
    st.write(f"Currency columns ({len(currency_cols)}): {currency_cols}")
    
    if currency_col in df_filtered.columns:
        st.write("### Currency Distribution")
        st.write(df_filtered[currency_col].value_counts().head(10))
    
    st.write("### Sample Data (First 5 rows)")
    st.dataframe(df.head())