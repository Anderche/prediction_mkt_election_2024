# Prediction Market Election 2024 Data Collection

Built by: Anders Kiss

This project is designed to collect, store, and analyze data related to the **2024 US Presidential Election** prediction markets. It focuses on tracking the odds for the two main parties, total USD amounts, and market percentages for key swing states, as well as relevant financial market indicators.

**Key Swing States**

- Arizona, Georgia, Michigan, Nevada, North Carolina, Pennsylvania, Wisconsin

---

## Created by: Anders Kiss
## Date: September 2024

---

## Features

- Automated data collection from multiple sources:
  - US-wide and state-specific prediction market odds and amounts
  - Financial market indicators
- Storage of data in Parquet format for efficient data management
- Data processing and analysis capabilities
- Visualization of historical data trends
- Spot-checking of the most recent entries
- Prevention of duplicate daily entries

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/prediction-market-election-2024.git
   cd prediction-market-election-2024
   ```

2. Create a Conda environment:
   ```
   conda create --name prediction_market python=3.9
   conda activate prediction_market
   ```

3. Install the required packages:
   ```
   conda install --file requirements.txt
   ```

## Usage

The project consists of several scripts for different purposes:

1. `main.py`: The main script for running the data collection and processing pipeline.
2. `script_ALL_DATA_SCRAPE_DEMO.py`: Demonstrates scraping all required data.
3. `script_demo_scrape_US_data.py`: Focuses on scraping US-specific data.
4. `script_demo_scrape_polymarket.py`: Scrapes data from Polymarket.
5. `script_demo_scrape_full_page.py`: Demonstrates scraping a full webpage.
6. `script_remove_last_record_parquet.py`: Utility to remove the last record from a Parquet file.
7. `script_demo_REMOVE_DEM_DATA.py`: Removes Democratic party data from the dataset.

To run the main data collection pipeline:

```
python main.py
```

For specific data scraping or processing tasks, run the corresponding script.

## Data Collected

- Date of entry
- US Republican odds
- US total market amount
- State-specific data for key swing states:
  - Republican odds
  - Total market amount
  - Percentage of total US market
- Financial indicators:
  - S&P 500 (SPX) price
  - Russell 2000 (IWM) price
  - Bitcoin (BTCUSDT) price

## Data Management

The project uses Parquet files for efficient data storage. To convert Parquet files to CSV format:

1. Run the script: `python convert_parquet_to_csv.py`
2. Choose a Parquet file from the list
3. The script will create a CSV file in the same directory

This facilitates data analysis in spreadsheet applications or other CSV-compatible tools.

## Dependencies

Main dependencies include:
- pandas
- pyarrow
- seaborn
- matplotlib
- requests
- beautifulsoup4

For a full list of dependencies, see `requirements.txt`.

To export the current environment (for reproducibility):
```
conda env export > environment.yml
```

To create an environment from the exported file:
```
conda env create -f environment.yml
```
