import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from prophet import Prophet
import os

# Config
st.set_page_config(page_title="Stock Analytics Platform", layout="wide")

# Database connection
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'stock_data.db')
engine = create_engine(f'sqlite:///{DB_PATH}')

# Load data
@st.cache_data
def load_data():
    df = pd.read_sql("SELECT * FROM stock_prices", con=engine)
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Header
st.title("📈 Stock Analytics Platform")
st.markdown("End-to-End Pipeline: Data Engineering → Analytics → ML Prediction")
st.divider()

# Sidebar
st.sidebar.header("⚙️ Settings")
selected_ticker = st.sidebar.selectbox("Select Stock", df['ticker'].unique())
df_ticker = df[df['ticker'] == selected_ticker]

# Row 1 — KPI Cards
col1, col2, col3, col4 = st.columns(4)
latest = df_ticker.iloc[-1]
prev   = df_ticker.iloc[-2]
change = ((latest['close'] - prev['close']) / prev['close']) * 100

col1.metric("Current Price",  f"${latest['close']:.2f}", f"{change:.2f}%")
col2.metric("MA7",            f"${latest['MA7']:.2f}")
col3.metric("MA30",           f"${latest['MA30']:.2f}")
col4.metric("Volatility",     f"{latest['volatility']:.2f}%")

st.divider()

# Row 2 — Price Chart
st.subheader(f"📊 {selected_ticker} Price & Moving Averages")
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=df_ticker['date'], y=df_ticker['close'], name='Close', line=dict(color='gray', width=1)))
fig1.add_trace(go.Scatter(x=df_ticker['date'], y=df_ticker['MA7'],   name='MA7',   line=dict(color='blue')))
fig1.add_trace(go.Scatter(x=df_ticker['date'], y=df_ticker['MA30'],  name='MA30',  line=dict(color='orange')))
fig1.update_layout(height=400)
st.plotly_chart(fig1, use_container_width=True)

# Row 3 — Volatility + Correlation
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📦 Volatility Comparison")
    fig2 = px.box(df, x='ticker', y='volatility', color='ticker')
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

with col_right:
    st.subheader("🔥 Correlation Heatmap")
    pivot = df.pivot_table(index='date', columns='ticker', values='daily_return')
    corr  = pivot.corr()
    fig3  = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# Row 4 — Prophet Prediction
st.subheader(f"🤖 {selected_ticker} Price Prediction (Next 90 Days)")

@st.cache_data
def run_prophet(ticker):
    d = df[df['ticker'] == ticker][['date', 'close']].rename(columns={'date': 'ds', 'close': 'y'})
    m = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=True, changepoint_prior_scale=0.05)
    m.fit(d)
    future   = m.make_future_dataframe(periods=90)
    forecast = m.predict(future)
    return d, forecast

prophet_df, forecast = run_prophet(selected_ticker)

fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=prophet_df['ds'], y=prophet_df['y'], name='Actual', line=dict(color='gray', width=1)))
fig4.add_trace(go.Scatter(x=forecast['ds'],   y=forecast['yhat'], name='Predicted', line=dict(color='blue', width=2)))
fig4.add_trace(go.Scatter(
    x=list(forecast['ds']) + list(forecast['ds'][::-1]),
    y=list(forecast['yhat_upper']) + list(forecast['yhat_lower'][::-1]),
    fill='toself', fillcolor='rgba(0,100,255,0.1)',
    line=dict(color='rgba(255,255,255,0)'), name='Confidence Interval'
))
fig4.add_vline(x=prophet_df['ds'].max().timestamp() * 1000, line_dash='dash', line_color='red', annotation_text='Forecast Start')
fig4.update_layout(height=400)
st.plotly_chart(fig4, use_container_width=True)