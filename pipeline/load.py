import pandas as pd
from sqlalchemy import create_engine, text
import logging
import os

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, 'data', 'stock_data.db')

def get_engine():
    return create_engine(f'sqlite:///{DB_PATH}')

def get_latest_date(ticker: str) -> str | None:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(
                f"SELECT MAX(date) FROM stock_prices WHERE ticker = '{ticker}'"
            ))
            row = result.fetchone()
            return row[0] if row[0] else None
    except Exception:
        return None

def load_to_database(df: pd.DataFrame, table_name: str = 'stock_prices') -> None:
    engine = get_engine()
    new_rows = 0

    for ticker in df['ticker'].unique():
        latest = get_latest_date(ticker)
        ticker_df = df[df['ticker'] == ticker].copy()

        if latest:
            # โหลดเฉพาะ rows ที่ใหม่กว่าวันล่าสุดใน DB
            ticker_df['date'] = pd.to_datetime(ticker_df['date'])
            ticker_df = ticker_df[ticker_df['date'] > latest]
            logger.info(f"{ticker}: latest in DB = {latest}, new rows = {len(ticker_df)}")
        else:
            logger.info(f"{ticker}: first load, inserting {len(ticker_df)} rows")

        if len(ticker_df) > 0:
            ticker_df.to_sql(
                name=table_name,
                con=engine,
                if_exists='append',  # append แทน replace
                index=False
            )
            new_rows += len(ticker_df)

    logger.info(f"Load complete: {new_rows} new rows inserted")

def read_from_database(query: str) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(query, con=engine)

if __name__ == "__main__":
    from extract import extract_stock_data
    from transform import transform_stock_data

    TICKERS = ['AAPL', 'GOOGL', 'META', 'MSFT', 'AMZN', 'NVDA']

    print("Starting ETL Pipeline...")
    raw   = extract_stock_data(TICKERS)
    clean = transform_stock_data(raw)
    load_to_database(clean)

    df_test = read_from_database(
        "SELECT ticker, COUNT(*) as rows FROM stock_prices GROUP BY ticker"
    )
    print("\nData in database:")
    print(df_test)