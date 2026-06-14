import yfinance as yf
import pandas as pd
import logging
import time
from datetime import datetime

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),   
        logging.StreamHandler()               
    ], 
    force=True
)
logger = logging.getLogger(__name__)

TICKERS = ['AAPL', 'GOOGL', 'META', 'MSFT', 'AMZN', 'NVDA']

def extract_single_ticker(ticker: str, period: str = '2y') -> pd.DataFrame | None:

    try:
        logger.info(f"Extracting {ticker}...")
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        # Validate ว่าได้ข้อมูลจริง
        if df.empty:
            logger.warning(f"{ticker}: No data returned!")
            return None
        
        if len(df) < 30:
            logger.warning(f"{ticker}: Insufficient data ({len(df)} rows)")
            return None
        
        df['ticker'] = ticker
        df.reset_index(inplace=True)
        logger.info(f"{ticker}: {len(df)} rows extracted")
        return df

    except Exception as e:
        logger.error(f"{ticker}: Failed — {e}")
        return None

def extract_stock_data(tickers: list, period: str = '2y') -> pd.DataFrame:
   
    all_data = []
    failed = []

    for ticker in tickers:
        df = extract_single_ticker(ticker, period)
        
        if df is not None:
            all_data.append(df)
        else:
            # Retry 1 ครั้งถ้าล้มเหลว
            logger.info(f"Retrying {ticker}...")
            time.sleep(2)  # รอก่อน retry
            df = extract_single_ticker(ticker, period)
            
            if df is not None:
                all_data.append(df)
            else:
                failed.append(ticker)

    if failed:
        logger.error(f"Failed tickers: {failed}")

    if not all_data:
        raise ValueError("No data extracted! Check API or tickers.")

    combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"Extraction complete: {len(combined)} rows, {len(all_data)} tickers")
    return combined

if __name__ == "__main__":
    df = extract_stock_data(TICKERS)
    print(df.shape)