import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

TICKERS = ['AAPL', 'GOOGL', 'META', 'MSFT', 'AMZN', 'NVDA']

def extract_stock_data(tickers: list, period: str='2y') -> pd.DataFrame:

    all_data = []

    for ticker in tickers:
        print(f'Extracting {ticker} ...')
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        df['Ticker'] = ticker
        df.reset_index(inplace=True)
        all_data.append(df)

    combined = pd.concat(all_data, ignore_index=True)
    return combined

if __name__ == "__main__":
    df = extract_stock_data(TICKERS)
    print(f'Total rows extracted: {len(df)}')   
    print(f"Tickers: {df['Ticker'].unique()}") 
    print(df.head())
