import pandas as pd
import numpy as np
import logging
import pandera as pa
from pandera import Column, DataFrameSchema, Check

logger = logging.getLogger(__name__)

# ── Data Validation Schema ──────────────────────────────────────────
RAW_SCHEMA = DataFrameSchema({
    'date':   Column(pa.DateTime, nullable=False),
    'open':   Column(float, Check.greater_than(0)),
    'high':   Column(float, Check.greater_than(0)),
    'low':    Column(float, Check.greater_than(0)),
    'close':  Column(float, Check.greater_than(0)),
    'volume': Column(int,   Check.greater_than_or_equal_to(0)),
    'ticker': Column(str,   nullable=False),
})

def validate_raw(df: pd.DataFrame) -> pd.DataFrame:
    """ตรวจสอบว่า raw data ถูกต้องก่อน transform"""
    try:
        RAW_SCHEMA.validate(df)
        logger.info("Data validation passed")
        return df
    except pa.errors.SchemaError as e:
        logger.error(f"Validation failed: {e}")
        raise

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """เพิ่ม technical indicators แต่ละ ticker"""
    result = []

    for ticker in df['ticker'].unique():
        t = df[df['ticker'] == ticker].copy().sort_values('date')

        # Moving Averages
        t['MA7']  = t['close'].rolling(7).mean()
        t['MA30'] = t['close'].rolling(30).mean()

        # Daily Return
        t['daily_return'] = t['close'].pct_change() * 100

        # Volatility
        t['volatility'] = t['daily_return'].rolling(30).std()

        # RSI (14)
        delta = t['close'].diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rs    = gain / loss.replace(0, np.nan)
        t['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        ema12    = t['close'].ewm(span=12, adjust=False).mean()
        ema26    = t['close'].ewm(span=26, adjust=False).mean()
        t['MACD']        = ema12 - ema26
        t['MACD_signal'] = t['MACD'].ewm(span=9, adjust=False).mean()
        t['MACD_hist']   = t['MACD'] - t['MACD_signal']

        # Bollinger Bands
        rolling_mean     = t['close'].rolling(20).mean()
        rolling_std      = t['close'].rolling(20).std()
        t['BB_upper']    = rolling_mean + (2 * rolling_std)
        t['BB_lower']    = rolling_mean - (2 * rolling_std)
        t['BB_width']    = t['BB_upper'] - t['BB_lower']

        result.append(t)
        logger.info(f"{ticker}:indicators added")

    return pd.concat(result, ignore_index=True)

def transform_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """Main transform function"""
    logger.info("Starting transform...")

    # 1. Fix timezone
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)

    # 2. Rename columns
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # 3. Drop unused columns
    df = df.drop(columns=['dividends', 'stock_splits'], errors='ignore')

    # 4. Validate
    validate_raw(df)

    # 5. Add indicators
    df = add_technical_indicators(df)

    # 6. Drop NaN จาก rolling
    before = len(df)
    df = df.dropna()
    after  = len(df)
    logger.info(f"Dropped {before - after} rows with NaN")

    logger.info(f"Transform complete: {len(df)} rows, {len(df.columns)} columns")
    return df

if __name__ == "__main__":
    from extract import extract_stock_data
    TICKERS = ['AAPL', 'GOOGL', 'META', 'MSFT', 'AMZN', 'NVDA']
    raw   = extract_stock_data(TICKERS)
    clean = transform_stock_data(raw)
    print(clean.columns.tolist())
    print(clean.shape)