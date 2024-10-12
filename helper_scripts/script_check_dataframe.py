import os
import pandas as pd
from datetime import datetime

def list_parquet_files():
    parquet_files = [f for f in os.listdir() if f.endswith('.parquet')]
    return parquet_files

def select_file(files):
    print("Available .parquet files:")
    for i, file in enumerate(files, 1):
        print(f"{i}: {file}")
    
    while True:
        try:
            choice = int(input("\nEnter the number of the file you want to use: "))
            if 1 <= choice <= len(files):
                return files[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def remediate_dataframe(df):
    try:
        print("\nChecking 'US Total Amount' feature for missing/nan values...")
        missing_count = df['US Total Amount'].isna().sum()
        print(f"Found {missing_count} missing/nan values in 'US Total Amount'")

        if missing_count > 0:
            print("Copying values from 'US Total Amt.' to 'US Total Amount' where needed...")
            df.loc[df['US Total Amount'].isna(), 'US Total Amount'] = df.loc[df['US Total Amount'].isna(), 'US Total Amt.']
            
            remaining_missing = df['US Total Amount'].isna().sum()
            print(f"After remediation, {remaining_missing} missing/nan values remain in 'US Total Amount'")
        
        return df
    except Exception as e:
        print(f"An error occurred during remediation: {str(e)}")
        return None

def main():
    parquet_files = list_parquet_files()
    
    if not parquet_files:
        print("No .parquet files found in the current directory.")
        return

    selected_file = select_file(parquet_files)
    print(f"\n📁 Selected file: {selected_file}")

    # Load the selected .parquet file
    df = pd.read_parquet(selected_file)

    # Print features (column names)
    print("\nFeatures (column names):")
    for column in df.columns:
        print(f"- {column}")

    # Print the last record
    print("\nLast record:")
    print(df.iloc[-1].to_string())

    # Remediate the dataframe
    remediated_df = remediate_dataframe(df)

    if remediated_df is not None:
        # Ask user if they want to drop 'US Total Amt.' feature
        drop_choice = input("\nDrop 'US Total Amt.' feature? (yes/no): ").lower()
        if drop_choice == 'yes':
            if 'US Total Amt.' in remediated_df.columns:
                remediated_df = remediated_df.drop(columns=['US Total Amt.'])
                print("'US Total Amt.' feature has been dropped.")
            else:
                print("'US Total Amt.' feature not found in the dataframe.")

        save_choice = input("\nSave to new file? (yes/no): ").lower()
        if save_choice == 'yes':
            current_date = datetime.now().strftime("%d%b%Y").upper()
            new_filename = f'remediated_file_{current_date}.parquet'
            remediated_df.to_parquet(new_filename)
            print(f"File saved as {new_filename}")
            
            # Print the features of the saved file
            print("\nFeatures of the saved file:")
            for column in remediated_df.columns:
                print(f"- {column}")
    else:
        print("Remediation failed. No file saved.")

if __name__ == "__main__":
    main()
