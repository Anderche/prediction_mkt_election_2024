import os
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
import math
import numpy as np
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

def find_files():
    files = glob('*.csv') + glob('*.parquet')
    return sorted(files)

def print_file_options(files):
    for i, file in enumerate(files):
        print(f"{i}: {file}")

def get_user_selection(files):
    while True:
        try:
            selection = int(input("Enter the index of the file you want to process: "))
            if 0 <= selection < len(files):
                return files[selection]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def load_file(filename):
    if filename.endswith('.csv'):
        return pd.read_csv(filename)
    elif filename.endswith('.parquet'):
        return pd.read_parquet(filename)
    else:
        raise ValueError(f"Unsupported file format: {filename}")

def profile_dataframe(df):
    profile = {}
    for column in df.columns:
        dtype = str(df[column].dtype)
        unique_count = df[column].nunique()
        null_count = df[column].isnull().sum()
        profile[column] = {
            'dtype': dtype,
            'unique_count': unique_count,
            'null_count': null_count
        }
    return profile

def plot_features(df):
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    n_cols = len(numeric_columns)
    
    if n_cols == 0:
        print("No numeric columns (int64 or float64) found in the DataFrame.")
        return
    
    plots_per_page = 6
    n_pages = math.ceil(n_cols / plots_per_page)
    
    # Generate default filename with current date
    default_filename = f"numeric_features_{datetime.now().strftime('%d%b%Y')}.pdf"
    
    # Ask user if they want to save the plot
    save_plot = input(f"Do you want to save the plot? (y/n) [default filename: {default_filename}]: ").lower().strip()
    if save_plot == 'y':
        filename = input(f"Enter the filename to save the plot (default: {default_filename}): ") or default_filename
        
        # Ensure the filename ends with .pdf
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        pdf = PdfPages(filename)
    else:
        pdf = None

    try:
        for page in range(n_pages):
            start_idx = page * plots_per_page
            end_idx = min((page + 1) * plots_per_page, n_cols)
            page_columns = numeric_columns[start_idx:end_idx]
            
            n_rows = (len(page_columns) + 1) // 2
            fig, axes = plt.subplots(n_rows, 2, figsize=(20, 7 * n_rows))
            fig.suptitle(f'Time Series Plots of Numeric Features (Page {page + 1}/{n_pages})', fontsize=16)
            
            axes = axes.flatten() if len(page_columns) > 1 else [axes]
            
            for i, column in enumerate(page_columns):
                ax = axes[i]
                ax.plot(df['Date'], df[column])
                ax.set_title(column, fontsize=14)
                ax.set_xlabel('Date', fontsize=12)
                ax.set_ylabel('Value', fontsize=12)
                ax.tick_params(axis='both', which='major', labelsize=10)
                
                # Set x-axis ticks and labels
                ax.set_xticks(df['Date'])
                ax.set_xticklabels(df['Date'], rotation=45, ha='right')
                
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
                
                # Set background color and y-axis limits based on column name
                if column.endswith('Total Amount') or column.endswith('Total Amt.'):
                    ax.set_facecolor('#e6ffe6')  # Light green
                elif column.endswith('Odds'):
                    ax.set_facecolor('#e6f3ff')  # Light blue
                    ax.axhline(y=50, color='red', linestyle='--', linewidth=2)
                    
                    # Calculate y-axis limits for 'Odds' features
                    y_min = df[column].min()
                    y_max = df[column].max()
                    
                    if y_max > 50:
                        new_y_min = max(40, y_min - 5)
                        new_y_max = min(100, y_max + 5)
                    else:
                        new_y_min = max(0, y_min - 5)
                        new_y_max = min(60, y_max + 5)
                    
                    ax.set_ylim(bottom=new_y_min, top=new_y_max)
                else:
                    y_min, y_max = ax.get_ylim()
                    ax.set_ylim(bottom=min(y_min, 0), top=max(y_max, 0) * 1.1)
                
                # Calculate current value and statistical change
                current_value = df[column].iloc[-1]
                last_3_periods = df[column].iloc[-4:-1]  # Exclude the current value
                avg_last_3 = last_3_periods.mean()
                change = current_value - avg_last_3
                percent_change = (change / avg_last_3) * 100 if avg_last_3 != 0 else np.inf

                # Create text box content
                textstr = f'Current: {current_value:.2f}\nChange: {change:.2f}\nChange % (3 vals): {percent_change:.2f}%'
                
                # Add text box to the plot
                props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
                ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
                        verticalalignment='top', bbox=props)
            
            # Remove any unused subplots
            for j in range(i + 1, len(axes)):
                fig.delaxes(axes[j])
            
            plt.tight_layout()
            plt.subplots_adjust(top=0.95)
            
            if pdf:
                pdf.savefig(fig)
            else:
                plt.show()
            
            plt.close(fig)
    
    finally:
        if pdf:
            pdf.close()
            print(f"Plot saved as {filename}")

def main():
    files = find_files()
    if not files:
        print("No .csv or .parquet files found in the current directory.")
        return

    print("Found the following files:")
    print_file_options(files)

    selected_file = get_user_selection(files)
    print(f"Selected file: {selected_file}")

    df = load_file(selected_file)
    print("File loaded into DataFrame successfully.")

    # Remove the profile printing
    profile_dataframe(df)

    plot_features(df)

if __name__ == "__main__":
    main()