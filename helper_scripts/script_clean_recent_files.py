import os
import glob
from datetime import datetime
import re

def get_date_from_filename(filename):
    # Extract date from filename (assuming format: *_DDMMMYYYY.parquet)
    match = re.search(r'_(\d{2}[A-Z]{3}\d{4})\.parquet$', filename)
    if match:
        date_str = match.group(1)
        try:
            return datetime.strptime(date_str, '%d%b%Y')
        except ValueError:
            print(f"Warning: Invalid date format in filename: {filename}")
    else:
        print(f"Warning: No date found in filename: {filename}")
    return datetime.min  # Return a default date for invalid filenames

def main():
    # Get all .parquet files in the current directory
    parquet_files = glob.glob('*.parquet')
    
    if not parquet_files:
        print("No .parquet files found in the current directory.")
        return

    print("Parquet files found:")
    for file in parquet_files:
        print(file)
    
    # Sort files by date (most recent first)
    sorted_files = sorted(parquet_files, key=get_date_from_filename, reverse=True)
    
    print("\nParquet files sorted by date (most recent first):")
    for file in sorted_files:
        date = get_date_from_filename(file)
        if date != datetime.min:
            print(f"{file} - {date.strftime('%d%b%Y')}")
        else:
            print(f"{file} - Date not found or invalid")
    
    if len(sorted_files) > 3:
        keep_recent = input("\nDo you want to keep only the most recent three files? (yes/no): ").lower()
        
        if keep_recent == 'yes':
            files_to_delete = sorted_files[3:]
            for file in files_to_delete:
                try:
                    os.remove(file)
                    print(f"Deleted: {file}")
                except OSError as e:
                    print(f"Error deleting {file}: {e}")
            
            print("\nKept the following files:")
            for file in sorted_files[:3]:
                print(file)
        else:
            print("No files were deleted.")
    else:
        print("\nThere are 3 or fewer files. No deletion needed.")

if __name__ == "__main__":
    main()




