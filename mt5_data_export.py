#mt5_data_export.py
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import time
import shutil
import os



def initialize_mt5():
    """Initialize connection to MetaTrader5"""
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        return False
    print("MT5 initialized successfully")
    return True

def get_mt5_data(symbol, timeframe, days_back=365):
    """Get historical data from MT5"""
    try:
        #check if symbol exists
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"Symbol {symbol} not found, trying to add it...")
            mt5.symbol_select(symbol, True)
            time.sleep(2) #wait for symbol to add

        #set timeframe mapping
        tf_mapping = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1,
        }

        timeframe_val = tf_mapping.get(timeframe, mt5.TIMEFRAME_D1)

        #calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        print(f"Downloading {symbol} {timeframe} data from {start_date} to {end_date}...")

        #get historical dates
        rates = mt5.copy_rates_range(symbol, timeframe_val, start_date, end_date)

        if rates is None:
            print("No data returned, error:", mt5.last_error())
            return None
        
        #create dataframe
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("time", inplace=True)

        #rename columns for backtrader
        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "tick_volume": "Volume"
        }, inplace=True)

        #keep only needed columns
        df = df[["Open", "High", "Low", "Close", "Volume"]]

        return df
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def main():
    """Main function to export MT5 data"""
    print("Starting MT5 Data Export...")

    #initialize MT5 connection
    if not initialize_mt5():
        return
    
    try:
        #get available symbols to see whats there
        symbols = mt5.symbols_get()
        print("\nAvailable symbols (first 10):")
        for i, symbol in enumerate(symbols[:10]):
            print(f" {i+1}. {symbol.name}")

        #CHOOSE SYMBOL/TIMEFRAME/DAYSBACK - change this to what u want for more/less data
        symbol = "GBPUSD"
        timeframe = "H4"
        days_back = 365
        
        print(f"\nDownloading {symbol} data...")

        #get data
        df = get_mt5_data(symbol, timeframe, days_back)

        if df is not None and not df.empty:
            #save to csv
            filename = f"MT5_{symbol}_{timeframe}_data.csv"
            df.to_csv(filename)
            --- USER SETUP: Change this path to your desired data directory ---
            # Example: "C:/YourUsername/YourProject/data_save/" or "./data/" - 
            #---FILE WILL INITIALLY SAVE IN YOUR -- C:\\Users\\(Your active user)
            shutil.move("C:\\Users\\Tshepo\\" + filename,"c:\\Users\\Tshepo\\Desktop\\Trading_Backtesting_Project\\data_save\\" + filename)

            with open("latest_export_info.txt", "w") as f:
                f.write(f"{symbol},{timeframe}")

            print(f"\nSUCCESS! Data exported to {filename}")
            print(f"Data shape: {df.shape}")
            print(f"Data range: {df.index[0]} to {df.index[-1]}")
            print(f"\nFirst 5 rows:")
            print(df.head())
        else:
            print("Failed to get data trash boy. Check if:")
            print("  - MT5 in running")
            print("  - Symbol name is correct")
            print("  - You have historical data available")
            

    finally:
        #always shutdown MT5 connection
        mt5.shutdown()
        print("\nMT5 connection closed")

if __name__ == "__main__":

    main()



