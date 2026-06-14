## 🔧 DE Layer — Production-grade ETL Pipeline

- ดึงข้อมูลหุ้น 6 ตัว (AAPL, GOOGL, META, MSFT, AMZN, NVDA) จาก Yahoo Finance API
- Incremental Loading — โหลดเฉพาะข้อมูลใหม่ ไม่ replace ทั้งหมด
- Data Validation ด้วย Pandera — ตรวจสอบ schema และค่าผิดปกติ
- Logging System — บันทึก pipeline activity ลง `pipeline.log`
- Error Handling + Retry Logic — รองรับ API failure อัตโนมัติ
- OOP Design — `StockPipeline` class รัน ETL ในคำสั่งเดียว

```python
pipeline = StockPipeline()
pipeline.run()
```

---

## 📊 DA Layer — Technical Analysis

- Price Trend Analysis (MA7, MA30)
- Volatility Comparison across stocks
- Correlation Analysis of Daily Returns
- Technical Indicators: RSI, MACD, Bollinger Bands

### Key Findings
- META มี volatility สูงสุดในกลุ่ม
- AAPL มี volatility ต่ำสุด — เหมาะกับ conservative portfolio
- AMZN-META มี correlation สูงสุด (0.61) — ไปทิศทางเดียวกัน

---

## 🤖 DS Layer — ML Price Prediction

### Feature Engineering (34 features)
- Lag features (1, 3, 5, 10 วัน)
- Technical signals (RSI overbought/oversold, MACD bullish)
- Price features (high-low range, close-open gap, BB position)

### Model Comparison (Time-based Split)
| Model | MAE | R² |
|---|---|---|
| 🏆 Linear Regression | 3.52 | 0.94 |
| Random Forest | 8.15 | 0.59 |
| Gradient Boosting | 8.54 | 0.54 |

### Key Insight
Linear Regression ชนะ Tree-based models เพราะ:
- Stock price มี linear relationship กับ lag features สูงมาก
- Dataset ขนาด 370 rows ไม่เพียงพอสำหรับ Tree-based models

---

## 🖥️ Dashboard

Interactive Streamlit Dashboard แสดง:
- KPI Cards (Price, MA7, MA30, Volatility)
- Price + Moving Average Chart
- Volatility Comparison
- Correlation Heatmap
- 90-Day Price Forecast (Prophet)

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Data Collection | yfinance, Python |
| Data Validation | Pandera |
| Database | SQLite, SQLAlchemy |
| Analysis | Pandas, Plotly |
| ML | Scikit-learn, Prophet |
| Dashboard | Streamlit |
| Config | PyYAML |

## 📁 Data Source
[Yahoo Finance via yfinance](https://pypi.org/project/yfinance/)