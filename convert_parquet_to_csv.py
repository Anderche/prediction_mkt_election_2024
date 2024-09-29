import pandas as pd
import os
import glob
import sys

def list_parquet_files():
    """
    List all .parquet files in the current directory.
    
    Returns:
    list: A list of .parquet filenames, or None if no files are found.
    """
    parquet_files = glob.glob('*.parquet')
    if not parquet_files:
        print("No .parquet files found in the current directory.")
        return None
    
    print("Available .parquet files:")
    for i, file in enumerate(parquet_files):
        print(f"{i}: {file}")
    return parquet_files

def convert_parquet_to_csv(input_file):
    """
    Convert a .parquet file to .csv format.
    
    Args:
    input_file (str): The name of the input .parquet file.
    
    Returns:
    bool: True if conversion is successful, False otherwise.
    """
    print(f"Starting conversion of {input_file}")
    
    # Get the base filename without extension
    base_name = os.path.splitext(input_file)[0]
    
    # Create output filename in current directory
    output_file = f"{base_name}.csv"
    
    try:
        # Read the parquet file
        print("Reading parquet file...")
        df = pd.read_parquet(input_file)
        
        # Write to CSV
        print("Writing to CSV...")
        df.to_csv(output_file, index=False)
        print(f"Successfully converted {input_file} to {output_file}")
        print(f"CSV file saved in the current directory: {os.getcwd()}")
        return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    # List available .parquet files
    parquet_files = list_parquet_files()
    
    if not parquet_files:
        print("No .parquet files found. Exiting the program.")
        sys.exit(1)
    
    # Get user input for file selection
    while True:
        try:
            index = int(input("Enter the index of the file you want to convert: "))
            if 0 <= index < len(parquet_files):
                file_name = parquet_files[index]
                break
            else:
                print("Invalid index. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Convert the selected file
    convert_parquet_to_csv(file_name)
    
    print("Operation completed. Exiting the program.")
    sys.exit(0)