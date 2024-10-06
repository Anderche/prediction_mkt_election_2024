"""
This script demonstrates how to fetch historical financial data using the yfinance library.
It retrieves daily price data for IWM (iShares Russell 2000 ETF), SPY (SPDR S&P 500 ETF Trust),
and BTC-USD (Bitcoin) for the year 2023. The script defines a function to download the data,
stores it in a dictionary, and provides a summary of the retrieved information. This can be
used as a starting point for financial data analysis or as a demo for yfinance usage.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

def get_historical_data():
    # Define the symbols
    symbols = ['IWM', 'SPY', 'BTC-USD']
    
    # Define date range
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    # Fetch data
    data = {}
    for symbol in symbols:
        data[symbol] = yf.download(symbol, start=start_date, end=end_date)
    
    return data

if __name__ == "__main__":
    historical_data = get_historical_data()
    
    print("Historical data summary:")
    for symbol, df in historical_data.items():
        print(f"\n{symbol}:")
        print(df.head())
        print(f"Data shape: {df.shape}")
        print(f"Date range: {df.index.min()} to {df.index.max()}")

    print("\nAccess data with: historical_data['IWM'], historical_data['SPY'], historical_data['BTC-USD']")
