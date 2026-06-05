import pandas as pd
from sqlalchemy import create_engine
import os

# แก้ path ให้ถูกต้องเสมอ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'stock_data.db')

def load_to_database(df: pd.DataFrame, table_name: str = 'stock_prices') -> None:
    engine = create_engine(f'sqlite:///{DB_PATH}')
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='replace',
        index=False
    )
    print(f"✅ Loaded {len(df)} rows to table '{table_name}'")
    print(f"📁 Database saved at: {DB_PATH}")

def read_from_database(query: str) -> pd.DataFrame:
    engine = create_engine(f'sqlite:///{DB_PATH}')
    return pd.read_sql(query, con=engine)

if __name__ == "__main__":
    from extract import extract_stock_data
    from transform import transform_stock_data
    
    TICKERS = ['AAPL', 'GOOGL', 'META', 'MSFT', 'AMZN', 'NVDA']
    
    print("🔄 Starting ETL Pipeline...")
    raw   = extract_stock_data(TICKERS)
    clean = transform_stock_data(raw)
    load_to_database(clean)
    
    df_test = read_from_database(
        "SELECT ticker, COUNT(*) as rows FROM stock_prices GROUP BY ticker"
    )
    print("\n📊 Data in database:")
    print(df_test)