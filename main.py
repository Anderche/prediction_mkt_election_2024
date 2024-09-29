import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import os

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

def get_int_input(prompt):
    """
    Get an integer input from the user with error handling.
    
    Args:
    prompt (str): The prompt to display to the user.
    
    Returns:
    int: The user's input as an integer.
    """
    while True:
        try:
            value = input(prompt).replace(',', '')
            return int(value)
        except ValueError:
            print("Please enter a valid integer.")

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

def collect_data():
    """
    Collect prediction market data from user input.
    
    Returns:
    dict: A dictionary containing the collected data.
    """
    data = {}
    data['Date'] = datetime.now().strftime('%Y-%m-%d')
    data['US Repbl. Odds'] = get_float_input("Enter US Republican Odds: ")
    data['US Total Amount'] = get_int_input("Enter US Total Amount: ")

    states = ['Georgia', 'Arizona', 'Wisconsin', 'Pennsylvania', 'North Carolina', 'Nevada', 'Michigan']
    
    for state in states:
        odds = get_float_input(f"Enter {state} Republican Odds: ")
        total_amount = get_int_input(f"Enter {state} Total Amount: ")
        percentage = calculate_percentage(total_amount, data['US Total Amount'])
        
        data[f"{state} Repbl. Odds"] = odds
        data[f"{state} Total Amt."] = total_amount
        data[f"{state} % of total"] = percentage

    data['SPX price'] = get_int_input("Enter SPX price: ")
    data['IWM price'] = get_int_input("Enter IWM price: ")
    data['BTCUSDT price'] = get_int_input("Enter BTCUSDT price: ")

    return data

def append_to_parquet(data, filename):
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
    """
    Visualize a selected column of data over time.
    
    Args:
    df (pandas.DataFrame): The DataFrame containing the data to visualize.
    """
    print("\nAvailable columns for visualization:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")
    
    choice = get_int_input("Enter the number of the column you want to visualize: ")
    
    if 0 <= choice < len(df.columns):
        column = df.columns[choice]
        plt.figure(figsize=(12, 6))
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
            choice = int(input("\nEnter the number of the file you want to use: "))
            if 1 <= choice <= len(parquet_files):
                return parquet_files[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    """
    Main function to run the Prediction Market Election 2024 Data Collection program.
    """
    print("--- Starting Prediction Market Election 2024 Data Collection ---")
    
    filename = list_parquet_files()
    if filename is None:
        print("No .parquet files available. Please create one first.")
        return
    
    print(f"\nSelected file: {filename}")
    
    # Load existing data
    existing_df = load_existing_data(filename)
    
    # Spot check
    if not existing_df.empty:
        spot_check = input("Do you want to see the last record? (yes/no): ").lower()
        if spot_check == 'yes':
            print("\n--- Last Record ---")
            last_record = existing_df.tail(1).to_dict('records')[0]
            for key, value in last_record.items():
                print(f"{key}: {value}")
            print("\n")
    
    # Check for today's entry
    today = datetime.now().strftime('%Y-%m-%d')
    
    if not existing_df.empty and today in existing_df['Date'].values:
        print(f"An entry for {today} already exists. Cancelling operation.")
        return

    print("\n--- Collecting Data ---")
    data = collect_data()
    
    print("\n--- Appending to Parquet File ---")
    df = append_to_parquet(data, filename)
    
    if df is not None:
        print("\n--- Last 3 entries ---")
        last_three = df.tail(3).to_dict('records')
        for i, entry in enumerate(last_three, 1):
            print(f"\nEntry {i}:")
            for key, value in entry.items():
                print(f"{key}: {value}")

        print("\n--- Visualization ---")
        visualize = input("Do you want to visualize the data? (yes/no): ").lower()
        if visualize == 'yes':
            visualize_data(df)
    
    print("\n--- Program Finished ---")

if __name__ == "__main__":
    main()



