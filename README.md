# Trading Backtesting Project

A comprehensive algorithmic trading system with MetaTrader 5 data export, Backtrader backtesting, and performance visualization.

![Chart Output](./images/32k.png?raw=true "Title") 

*Diagram of the system architecture*

## Features

- **MT5 Data Export**: Download historical data from MetaTrader 5
- **SMA Strategy**: Simple Moving Average crossover strategy with risk management
- **Performance Dashboard**: Professional visualization of backtest results
- **File Management**: Automated file organization (data_save → in_use → archive)

## Project Structure

trading-backtesting-project/
├── mt5_data_export.py # MT5 data download and export
├── sma_backtest.py # Backtesting engine with SMA strategy
├── visualize_results.py # Performance dashboard generator
├── data_save/ # Data storage directory
│ ├── in_use/ # Files currently being processed
│ └── archive/ # Completed backtest files
└── README.md

## Setup Instructions

1. **Clone this repository**
2. **Modify the file paths** in these files to match your local system:
   - `mt5_data_export.py` - Line XX: Change data save directory
   - `sma_backtest.py` - Line XX: Change data directory paths  
   - `visualize_results.py` - Line XX: Change data directory paths
3. **Create the necessary directories** on your system
4. **Install required packages**

## Run the scripts in this order

1. python mt5_data_export.py
2. python sma_backtest.py  
3. python visualize_results.py
