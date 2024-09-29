# Prediction Market Election 2024 Data Collection

This project is designed to collect, store, and visualize data related to the 2024 US Presidential Election prediction markets. It focuses on tracking Republican odds, total amounts, and market percentages for key swing states, as well as relevant financial market indicators.

--- 

## Created by: Anders Kiss
## Date: September 2024 

--- 

## Features

- Data collection for US-wide and state-specific prediction market odds and amounts
- Automatic calculation of state percentages relative to the total US market
- Storage of data in Parquet format for efficient data management
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

Run the main script:

```
python main.py
```

Follow the prompts to:
1. Select an existing Parquet file or create a new one
2. Input the latest prediction market data
3. View the last few entries
4. Visualize data trends

## Data Collected

- Date of entry
- US Republican odds
- US total market amount
- For each state (Georgia, Arizona, Wisconsin, Pennsylvania, North Carolina, Nevada, Michigan):
  - Republican odds
  - Total market amount
  - Percentage of total US market
- Financial indicators:
  - S&P 500 (SPX) price
  - Russell 2000 (IWM) price
  - Bitcoin (BTCUSDT) price

## Dependencies

Main dependencies include:
- pandas
- pyarrow
- seaborn
- matplotlib

For a full list of dependencies, see `requirements.txt`.

To export the current environment (for reproducibility):
```
conda env export > environment.yml
```

To create an environment from the exported file:
```
conda env create -f environment.yml
```

## Contributing

Contributions to improve the project are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## Disclaimer

This tool is for educational and research purposes only. It does not constitute financial advice or predictions. Always do your own research before making any investment decisions.


