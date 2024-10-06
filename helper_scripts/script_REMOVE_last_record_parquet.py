import os
import pandas as pd

def list_parquet_files():
    parquet_files = [f for f in os.listdir() if f.endswith('.parquet')]
    return parquet_files

def print_parquet_files(files):
    print("Available .parquet files:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

def select_file(files):
    while True:
        try:
            choice = int(input("Enter the number of the file you want to select: "))
            if 1 <= choice <= len(files):
                return files[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def print_last_record(df):
    print("\nLast record:")
    print(df.iloc[-1])

def confirm_removal():
    return input("Do you want to remove the last record? (y/n): ").lower() == 'y'

def main():
    parquet_files = list_parquet_files()
    
    if not parquet_files:
        print("No .parquet files found in the current directory.")
        return

    print_parquet_files(parquet_files)
    selected_file = select_file(parquet_files)

    df = pd.read_parquet(selected_file)
    print_last_record(df)

    if confirm_removal():
        df = df.iloc[:-1]
        df.to_parquet(selected_file, index=False)
        print(f"Last record removed. File '{selected_file}' has been updated.")
    else:
        print("Operation cancelled. No changes were made.")

if __name__ == "__main__":
    main()

    