# Trading Backtesting Project

A comprehensive algorithmic trading system with MetaTrader 5 data export, Backtrader backtesting, and performance visualization.

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

## Run the scripts in this order

1 python mt5_data_export.py
2 python sma_backtest.py  
3 python visualize_results.py
