"""
Prediction Market Election 2024 Data Collection and Analysis Tool

This script automates the collection, storage, and analysis of prediction market data for the 2024 US presidential election. It offers the following features:

1. Automated Data Collection: Scrapes odds and volume data from Polymarket for the US presidential election and key swing states.
2. Financial Data Integration: Retrieves closing prices for relevant financial instruments (S&P 500, Russell 2000, Bitcoin) from Yahoo Finance.
3. Efficient Data Storage: Stores collected data in Parquet files for quick access and analysis.
4. Data Visualization: Provides options to visualize trends in collected data over time.
5. User-Friendly Interface: Offers a clear and informative CLI for data collection, viewing, and analysis.

This tool is designed to help researchers, analysts, and enthusiasts track and analyze prediction market trends and related financial indicators leading up to the 2024 US presidential election.
"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import os
import math
import asyncio
import re
from crawl4ai import AsyncWebCrawler
import yfinance as yf

def get_float_input(prompt, decimals=2):
    """
    Get a float input from the user with error handling.
    
    Args:
    prompt (str): The prompt to display to the user.
    decimals (int): The number of decimal places to round to.
    
    Returns:
    float: The user's input as a float, rounded to the specified number of decimal places.
    """
    while True:
        try:
            value = input(prompt).replace(',', '')
            return round(float(value), decimals)
        except ValueError:
            print("Please enter a valid number.")

def calculate_percentage(state_amount, us_amount):
    """
    Calculate the percentage of a state amount relative to the US amount.
    
    Args:
    state_amount (float): The amount for a specific state.
    us_amount (float): The total US amount.
    
    Returns:
    float: The calculated percentage, rounded to 2 decimal places.
    """
    return round((state_amount / us_amount) * 100, 2) if us_amount != 0 else 0

async def scrape_polymarket(url, crawler):
    print(f"\n🔍 Scraping data from: {url}")
    try:
        result = await crawler.arun(
            url=url,
            bypass_cache=True
        )

        if result.success:
            content = result.markdown
            
            # Check if it's the US-wide election URL
            if url == "https://polymarket.com/event/presidential-election-winner-2024":
                volume_match = re.search(r'\$([0-9,]+) Vol\.', content)
                total_volume = float(volume_match.group(1).replace(',', '')) if volume_match else 0.0
                
                trump_match = re.search(r'Donald Trump\s+(\d+\.\d+)%', content)
                trump_percentage = float(trump_match.group(1)) if trump_match else 0.0
                
                return total_volume, trump_percentage
            else:
                volume_match = re.search(r'\$([0-9,]+) Vol\.', content)
                total_volume = float(volume_match.group(1).replace(',', '')) if volume_match else 0.0
                
                republican_match = re.search(r'Republican.*?\n([0-9.]+)%', content, re.DOTALL)
                republican_percentage = float(republican_match.group(1)) if republican_match else 0.0
                
                return total_volume, republican_percentage
        else:
            print(f"Failed to scrape data from: {url}")
            return None, None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None, None

def get_financial_data():
    print("\n📊 Retrieving financial data from Yahoo Finance...")
    symbols = ['IWM', '^GSPC', 'BTC-USD']
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    
    data = {}
    for symbol in symbols:
        df = yf.download(symbol, start=start_date, end=end_date)['Close']
        if not df.empty:
            latest_close = df.iloc[-1].round(2)
            data[symbol] = latest_close
        else:
            data[symbol] = None
    
    return data

async def collect_data():
    """
    Collect prediction market data from Polymarket and financial data from Yahoo Finance.
    
    Returns:
    dict: A dictionary containing the collected data.
    """
    print("\n= = = = = 🚀 Starting data collection process = = = = =")
    data = {}
    data['Date'] = datetime.now().strftime('%Y-%m-%d')

    urls = {
        "US": "https://polymarket.com/event/presidential-election-winner-2024",
        "Georgia": "https://polymarket.com/event/georgia-presidential-election-winner",
        "Arizona": "https://polymarket.com/event/arizona-presidential-election-winner",
        "Wisconsin": "https://polymarket.com/event/wisconsin-presidential-election-winner",
        "Pennsylvania": "https://polymarket.com/event/pennsylvania-presidential-election-winner",
        "North Carolina": "https://polymarket.com/event/north-carolina-presidential-election-winner",
        "Nevada": "https://polymarket.com/event/nevada-presidential-election-winner",
        "Michigan": "https://polymarket.com/event/michigan-presidential-election-winner"
    }

    async with AsyncWebCrawler(verbose=True) as crawler:
        for state, url in urls.items():
            total_amount, republican_odds = await scrape_polymarket(url, crawler)
            
            if state == "US":
                data['US Repbl. Odds'] = republican_odds
                data['US Total Amount'] = total_amount
                print(f"📊 US Data: Republican Odds: {republican_odds}%, Total Amount: ${total_amount:,.2f}")
            else:
                data[f"{state} Repbl. Odds"] = republican_odds
                data[f"{state} Total Amt."] = total_amount
                data[f"{state} % of total"] = round((total_amount / data['US Total Amount']) * 100, 2) if data['US Total Amount'] != 0 else 0
                print(f"📊 {state} Data: Republican Odds: {republican_odds}%, Total Amount: ${total_amount:,.2f}, % of Total: {data[f'{state} % of total']}%")

    financial_data = get_financial_data()
    data['SPX price'] = financial_data['^GSPC']
    data['IWM price'] = financial_data['IWM']
    data['BTCUSDT price'] = financial_data['BTC-USD']

    print("\n💹 Financial Data:")
    print(f"S&P 500: ${data['SPX price']:,.2f}")
    print(f"Russell 2000: ${data['IWM price']:,.2f}")
    print(f"Bitcoin: ${data['BTCUSDT price']:,.2f}")

    print("\n✅ Data collection complete!")
    return data

def append_to_parquet(data, filename):
    print(f"\n💾 Appending data to {filename}...")
    """
    Append new data to an existing Parquet file or create a new one if it doesn't exist.
    
    Args:
    data (dict): The data to append.
    filename (str): The name of the Parquet file.
    
    Returns:
    pandas.DataFrame or None: The updated DataFrame if successful, None if cancelled.
    """
    df = pd.DataFrame([data])
    
    try:
        existing_df = pd.read_parquet(filename)
        
        # Check if there's already an entry for the current date
        if data['Date'] in existing_df['Date'].values:
            print(f"An entry for {data['Date']} already exists. Cancelling operation.")
            return None
        
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass

    df.to_parquet(filename, engine='pyarrow')
    return df

def visualize_data(df):
    print("\n📈 Preparing data visualization...")
    """
    Visualize a selected column of data over time.
    
    Args:
    df (pandas.DataFrame): The DataFrame containing the data to visualize.
    """
    print("\nAvailable columns for visualization:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")
    
    choice = int(get_float_input("Enter the number of the column you want to visualize: "))
    
    if 0 <= choice < len(df.columns):
        column = df.columns[choice]
        plt.figure(figsize=(12, 6))
        
        # Check if the column is an 'Odds' feature
        if column.endswith('Odds'):
            min_value = df[column].min()
            max_value = df[column].max()
            y_min = max(0, min_value * 0.9)  # 10% below the lowest value, but not less than 0
            y_max = min(100, max_value * 1.1)  # 10% above the highest value, but not more than 100
            sns.lineplot(x='Date', y=column, data=df)
            plt.ylim(bottom=y_min, top=y_max)
        else:
            sns.lineplot(x='Date', y=column, data=df)
        
        plt.title(f"{column} Over Time")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        save_image = input("Do you want to save this image? (yes/no): ").lower()
        if save_image == 'yes':
            filename = f"{column.replace(' ', '_')}_visualization.png"
            plt.savefig(filename)
            print(f"Image saved as {filename}")
        
        plt.show()
    else:
        print("Invalid choice. No visualization created.")

def load_existing_data(filename):
    print(f"\n📂 Loading existing data from {filename}...")
    """
    Load data from an existing Parquet file.
    
    Args:
    filename (str): The name of the Parquet file to load.
    
    Returns:
    pandas.DataFrame: The loaded DataFrame, or an empty DataFrame if the file doesn't exist.
    """
    try:
        return pd.read_parquet(filename)
    except FileNotFoundError:
        return pd.DataFrame()

def list_parquet_files():
    print("\n🗂️ Searching for Parquet files...")
    """
    List all Parquet files in the current directory and let the user choose one.
    
    Returns:
    str or None: The name of the chosen Parquet file, or None if no files are found.
    """
    parquet_files = [f for f in os.listdir() if f.endswith('.parquet')]
    if not parquet_files:
        print("No .parquet files found in the current directory.")
        return None
    
    print("\nAvailable .parquet files:")
    for i, file in enumerate(parquet_files, 1):
        print(f"{i}: {file}")
    
    while True:
        try:
            choice = int(get_float_input("\nEnter the number of the file you want to use: "))
            if 1 <= choice <= len(parquet_files):
                return parquet_files[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

async def main():
    """
    Main function to run the Prediction Market Election 2024 Data Collection program.
    """
    print("🏛️ Welcome to the Prediction Market Election 2024 Data Collection and Analysis Tool 🇺🇸")
    print("=" * 80)
    
    filename = list_parquet_files()
    if filename is None:
        print("❌ No .parquet files available. Please create one first.")
        return
    
    print(f"\n📁 Selected file: {filename}")
    
    # Load existing data
    existing_df = load_existing_data(filename)
    
    # Spot check
    if not existing_df.empty:
        spot_check = input("👀 Do you want to see the last record? (yes/no): ").lower()
        if spot_check == 'yes':
            print("\n📜 Last Record:")
            last_record = existing_df.tail(1).to_dict('records')[0]
            for key, value in last_record.items():
                print(f"  {key}: {value}")
            print("\n")
    
    # Check for today's entry
    today = datetime.now().strftime('%Y-%m-%d')
    
    if not existing_df.empty and today in existing_df['Date'].values:
        print(f"⚠️ An entry for {today} already exists. Operation cancelled.")
        return

    print("\n🔄 Initiating data collection...")
    data = await collect_data()
    
    print("\n📥 Appending to Parquet File...")
    df = append_to_parquet(data, filename)
    
    if df is not None:
        print("\n📊 Last 3 entries:")
        last_three = df.tail(3).to_dict('records')
        for i, entry in enumerate(last_three, 1):
            print(f"\nEntry {i}:")
            for key, value in entry.items():
                print(f"  {key}: {value}")

        print("\n📈 Data Visualization")
        visualize = input("Would you like to visualize the data? (yes/no): ").lower()
        if visualize == 'yes':
            visualize_data(df)
    
    print("\n= = = = = 🎉 Program Finished! ... the Prediction Market Election 2024 Data Collection and Analysis Complete = = = = =")

if __name__ == "__main__":
    asyncio.run(main())