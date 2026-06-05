import pandas as pd
import numpy as np

def transform_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean และเพิ่ม features ที่จะใช้วิเคราะห์
    """
    # 1. แก้ timezone issue
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)

    # 2. rename columns ให้ clean
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # 3. drop columns ที่ไม่ใช้
    df = df.drop(columns=['dividends', 'stock_splits'])

    # 4. เพิ่ม Technical Indicators
    for ticker in df['ticker'].unique():
        mask = df['ticker'] == ticker

        # Moving Averages
        df.loc[mask, 'MA7']  = df.loc[mask, 'close'].rolling(7).mean()
        df.loc[mask, 'MA30'] = df.loc[mask, 'close'].rolling(30).mean()

        # Daily Return %
        df.loc[mask, 'daily_return'] = df.loc[mask, 'close'].pct_change() * 100

        # Volatility (30 วัน)
        df.loc[mask, 'volatility'] = df.loc[mask, 'daily_return'].rolling(30).std()

    # 5. drop rows ที่มี NaN จาก rolling
    df = df.dropna()

    print(f"✅ Transformed: {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")
    return df

if __name__ == "__main__":
    from extract import extract_stock_data
    TICKERS = ['AAPL', 'GOOGL', 'META', 'MSFT', 'AMZN', 'NVDA']
    raw = extract_stock_data(TICKERS)
    clean = transform_stock_data(raw)
    print(clean.head())