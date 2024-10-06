import os
import pandas as pd
from glob import glob

def list_parquet_files():
    parquet_files = glob('*.parquet')
    return parquet_files

def select_file(files):
    print("Found the following .parquet files:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    while True:
        try:
            selection = int(input("\nEnter the number of the file you want to process: "))
            if 1 <= selection <= len(files):
                return files[selection - 1]
            else:
                print(f"Please enter a number between 1 and {len(files)}.")
        except ValueError:
            print("Please enter a valid number.")

def confirm_selection(file):
    while True:
        confirm = input(f"\nDo you want to process this file: {file}? (y/n): ").lower()
        if confirm in ['y', 'yes', 'n', 'no']:
            return confirm.startswith('y')
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")

def remove_dem_features(file):
    df = pd.read_parquet(file)
    dem_columns = [col for col in df.columns if 'Dem. Odds' in col]
    
    if dem_columns:
        print(f"\nRemoving the following columns from {file}:")
        for col in dem_columns:
            print(f"- {col}")
        
        df = df.drop(columns=dem_columns)
        df.to_parquet(file, index=False)
        print(f"Updated {file} saved.")
    else:
        print(f"\nNo 'Dem. Odds' columns found in {file}.")

def main():
    parquet_files = list_parquet_files()
    
    if not parquet_files:
        print("No .parquet files found in the current directory.")
        return
    
    selected_file = select_file(parquet_files)
    
    if not confirm_selection(selected_file):
        print("Operation cancelled.")
        return
    
    while True:
        confirm_remove = input("\nDo you want to remove all 'Dem. Odds' features? (y/n): ").lower()
        if confirm_remove in ['y', 'yes', 'n', 'no']:
            if confirm_remove.startswith('y'):
                remove_dem_features(selected_file)
                print("\nAll specified features have been removed from the selected .parquet file.")
            else:
                print("Operation cancelled.")
            break
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    main()
