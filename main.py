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
import sys
import numpy as np

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

def extract_party_data(content, party):
    pattern = rf"{party}\s*\n\s*\$([\d,]+)\s*Vol\.\s*\n\s*([\d.]+)%"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        volume = match.group(1).replace(',', '')
        percentage = match.group(2)
        return (party, int(volume), float(percentage))
    return None

async def scrape_polymarket(url, crawler):
    print(f"\n🔍 Scraping data from: {url}")
    try:
        result = await crawler.arun(
            url=url,
            bypass_cache=True
        )

        if result.success:
            content = result.markdown
            
            republican_data = extract_party_data(content, "Republican")
            democratic_data = extract_party_data(content, "Democrat")
            
            if republican_data and democratic_data:
                total_amount = republican_data[1] + democratic_data[1]
                republican_odds = republican_data[2]
                return total_amount, republican_odds
            else:
                print(f"Failed to extract data from: {url}")
                return None, None
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

async def scrape_usa_data_polymarket(url, crawler):
    try:
        result = await crawler.arun(
            url=url,
            bypass_cache=True
        )

        if result.success:
            content = result.markdown
            
            # Extract total volume
            volume_match = re.search(r'\$([0-9,]+) Vol\.', content)
            total_volume = int(volume_match.group(1).replace(',', '')) if volume_match else None
            
            # Extract Donald Trump's percentage (assuming this represents the Republican odds)
            trump_match = re.search(r'Donald Trump\s+(\d+\.\d+)%', content)
            republican_odds = float(trump_match.group(1)) if trump_match else None
            
            return total_volume, republican_odds
        else:
            print(f"Failed to scrape data from: {url}")
            return None, None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None, None

async def collect_us_data(crawler):
    print("\n🔍 Collecting US election data...")
    us_data = {}
    us_url = "https://polymarket.com/event/presidential-election-winner-2024"

    try:
        total_amount, republican_odds = await scrape_usa_data_polymarket(us_url, crawler)
        
        if total_amount is not None and republican_odds is not None:
            us_data['Date'] = datetime.now().strftime('%Y-%m-%d')
            us_data['US Repbl. Odds'] = republican_odds
            us_data['US Total Amount'] = total_amount
            print(f"📊 US Data: Republican Odds: {republican_odds}%, Total Amount: ${total_amount:,.2f}")
        else:
            print("⚠️ Warning: Failed to collect complete US data")
            sys.exit(1)  # Exit with error code 1
    except Exception as e:
        print(f"❌ Error collecting US data: {str(e)}")
        print("Please check the URL and ensure the website structure hasn't changed.")
        sys.exit(1)  # Exit with error code 1

    if len(us_data) <= 1:  # Only 'Date' key is present
        print("\n❌ No US data was collected. Please check the issues above and try again.")
        sys.exit(1)  # Exit with error code 1

    # Check for NaN values
    for key, value in us_data.items():
        if isinstance(value, (int, float)) and np.isnan(value):
            print(f"❌ Error: NaN value detected for {key}")
            sys.exit(1)  # Exit with error code 1

    print("\n✅ US data collection complete!")
    return us_data

async def collect_data():
    print("\n= = = = = 🚀 Starting data collection process = = = = =")
    data = {}

    async with AsyncWebCrawler(verbose=True) as crawler:
        # Collect US data first
        us_data = await collect_us_data(crawler)
        if us_data is None:
            return None
        data.update(us_data)

        # Collect data for other states
        urls = {
            "Georgia": "https://polymarket.com/event/georgia-presidential-election-winner",
            "Arizona": "https://polymarket.com/event/arizona-presidential-election-winner",
            "Wisconsin": "https://polymarket.com/event/wisconsin-presidential-election-winner",
            "Pennsylvania": "https://polymarket.com/event/pennsylvania-presidential-election-winner",
            "North Carolina": "https://polymarket.com/event/north-carolina-presidential-election-winner",
            "Nevada": "https://polymarket.com/event/nevada-presidential-election-winner",
            "Michigan": "https://polymarket.com/event/michigan-presidential-election-winner"
        }

        for state, url in urls.items():
            try:
                total_amount, republican_odds = await scrape_polymarket(url, crawler)
                
                if total_amount is not None and republican_odds is not None:
                    data[f"{state} Repbl. Odds"] = republican_odds
                    data[f"{state} Total Amt."] = total_amount
                    data[f"{state} % of total"] = calculate_percentage(total_amount, data['US Total Amount'])
                    print(f"📊 {state} Data: Republican Odds: {republican_odds}%, Total Amount: ${total_amount:,.2f}, % of US Total: {data[f'{state} % of total']}%")
                else:
                    print(f"⚠️ Warning: Failed to collect complete data for {state}")
            except Exception as e:
                print(f"❌ Error collecting data for {state}: {str(e)}")
                print("Please check the URL and ensure the website structure hasn't changed.")

    try:
        financial_data = get_financial_data()
        data['SPX price'] = financial_data['^GSPC']
        data['IWM price'] = financial_data['IWM']
        data['BTCUSDT price'] = financial_data['BTC-USD']

        print("\n💹 Financial Data:")
        print(f"S&P 500: ${data['SPX price']:,.2f}")
        print(f"Russell 2000: ${data['IWM price']:,.2f}")
        print(f"Bitcoin: ${data['BTCUSDT price']:,.2f}")
    except Exception as e:
        print(f"❌ Error collecting financial data: {str(e)}")
        print("Please check your internet connection and try again.")

    if len(data) <= 1:  # Only 'Date' key is present
        print("\n❌ No data was collected. Please check the issues above and try again.")
        return None

    print("\n✅ Data collection complete!")
    return data

def append_to_parquet(data, filename):
    print(f"\n💾 Preparing to append data to {filename}...")
    """
    Append new data to an existing Parquet file or create a new one if it doesn't exist.
    
    Args:
    data (dict): The data to append.
    filename (str): The name of the Parquet file.
    
    Returns:
    pandas.DataFrame or None: The updated DataFrame if successful, None if cancelled.
    """
    df = pd.DataFrame([data])
    
    # Round float64 columns to 2 decimal places
    float_columns = df.select_dtypes(include=['float64']).columns
    df[float_columns] = df[float_columns].round(2)
    
    try:
        existing_df = pd.read_parquet(filename)
        
        # Check if there's already an entry for the current date
        if data['Date'] in existing_df['Date'].values:
            print(f"An entry for {data['Date']} already exists. Cancelling operation.")
            return None
        
        # Round float64 columns in existing_df to 2 decimal places
        existing_float_columns = existing_df.select_dtypes(include=['float64']).columns
        existing_df[existing_float_columns] = existing_df[existing_float_columns].round(2)
        
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass

    # Check for NaN values in the entire DataFrame
    nan_count = df.isna().sum().sum()
    if nan_count > 0:
        print(f"⚠️ Warning: {nan_count} NaN value(s) detected in the data")
        print("Affected features:")
        for column in df.columns[df.isna().any()]:
            print(f"  - {column}: {df[column].isna().sum()} NaN value(s)")
        
        save_anyway = input("Do you want to save the data anyway? (yes/no): ").lower()
        if save_anyway != 'yes':
            print("Operation cancelled. Data not saved.")
            return None

    # Display the data to be appended
    print("\nNew data to be appended:")
    for key, value in data.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    # Ask for confirmation
    confirm = input("\nDo you want to save this data? (yes/no): ").lower()
    if confirm != 'yes':
        print("Operation cancelled. Data not saved.")
        return None

    current_date = datetime.now().strftime('%d%b%Y').upper()
    new_filename = f"DATA_prediction_levels_{current_date}.parquet"
    df.to_parquet(new_filename, engine='pyarrow')
    print(f"✅ Data successfully saved to {new_filename}")
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
    
        # Ask for confirmation to save the .parquet file
        save_parquet = input("Do you want to save the updated .parquet file? (yes/no): ").lower()
        if save_parquet == 'yes':
            current_date = datetime.now().strftime('%d%b%Y').upper()
            parquet_filename = f"DATA_prediction_levels_{current_date}.parquet"
            print(f"The file will be saved as: {parquet_filename}")
            confirm_save = input("Do you want to proceed with saving? (yes/no): ").lower()
            if confirm_save == 'yes':
                df.to_parquet(parquet_filename, engine='pyarrow')
                print(f"✅ Data successfully saved to {parquet_filename}")
            else:
                print("❌ .parquet file not saved.")
        else:
            print("❌ .parquet file not saved.")
        
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
    
    if data is None:
        print("❌ Data collection failed. Please address the issues and try again.")
        return

    print("\n📥 Preparing to append data to Parquet File...")
    df = append_to_parquet(data, filename)
    
    if df is not None:
        print("\n📊 Last 3 entries:")
        last_three = df.tail(3).to_dict('records')
        for i, entry in enumerate(last_three, 1):
            print(f"\nEntry {i}:")
            for key, value in entry.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")

        print("\n📈 Data Visualization")
        visualize = input("Would you like to visualize the data? (yes/no): ").lower()
        if visualize == 'yes':
            visualize_data(df)
    else:
        print("\n❌ Data was not saved. Skipping visualization.")
    
    print("\n= = = = = 🎉 Program Finished! ... the Prediction Market Election 2024 Data Collection and Analysis Complete = = = = =")

if __name__ == "__main__":
    asyncio.run(main())