"""
This script demonstrates how to fetch the current day's closing price data using the yfinance library.
It retrieves the latest closing price for IWM (iShares Russell 2000 ETF), SPY (SPDR S&P 500 ETF Trust),
and BTC-USD (Bitcoin). The script defines a function to download the data, stores it in a dictionary,
and provides a summary of the retrieved information.
"""

import yfinance as yf
from datetime import datetime, timedelta

def get_current_data():
    # symbols = ['IWM', 'SPY', 'BTC-USD']
    symbols = ['IWM', '^GSPC', 'BTC-USD']

    # Get today's date
    end_date = datetime.now().strftime('%Y-%m-%d')
    # Get yesterday's date (in case today's data is not yet available)
    start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Fetch data
    data = {}
    for symbol in symbols:
        # Download only the 'Close' column for the most recent available date
        df = yf.download(symbol, start=start_date, end=end_date)['Close']
        if not df.empty:
            # Get the last (most recent) closing price
            latest_close = df.iloc[-1].round(2)
            data[symbol] = latest_close
        else:
            data[symbol] = None
    
    return data

if __name__ == "__main__":
    current_data = get_current_data()
    
    print("Current closing price data:")
    for symbol, price in current_data.items():
        if price is not None:
            print(f"{symbol}: {price:.2f}")
        else:
            print(f"{symbol}: Data not available")

    print("\nAccess data with: current_data['IWM'], current_data['SPY'], current_data['BTC-USD']")
