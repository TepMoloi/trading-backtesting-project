#visualize_results.py
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from sma_backtest import SmaCrossStrategy # importing sma strategy
import backtrader as bt
import shutil

def create_performance_dashboard(strat, results):
    """
    Creates a professional performance dashboard from backtest results
    """

    #create figure with subplots
    plt.figure(figsize=(16,12))

    symbol = getattr(strat, "symbol", "unknown")
    timeframe = getattr(strat, "timeframe", "unknown")
    plt.suptitle(f"Algorithmic Trading Performance Dashboard\n{symbol} - {timeframe}", fontsize=16, fontweight="bold")

    #plot 1: Equity Curve
    plt.subplot(3, 2, 1)
    plot_equity_curve(strat)

    #plot 2: Drawdown
    plt.subplot(3, 2, 2)
    plot_drawdown(strat)

    #plot 3: Trade Analysis
    plt.subplot(3, 2, 3)
    plot_trade_analysis(strat)

    #plot 4: Monthly Returns
    plt.subplot(3, 2, 4)
    plot_monthly_returns(strat)

    #plot 5: Position Sizing
    #plt.subplot(3, 2, 5)
    #plot_position_sizing(strat)

    #plot 6: Sharpe Ratio Rolling
    #plt.subplot(3, 2, 6)
    #plot_rolling_sharpe(strat)

    plt.tight_layout()
    plt.savefig(f"performance_dashboard_{symbol}_{timeframe}.png", dpi=300, bbox_inches="tight")
    plt.show()

####################################################################################

def find_data_file():
    """Automatically find the most recent MT5 data file"""
    try:
        # Look in the data_save directory for the most recent file
        data_dir = "c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\in_use"
        all_files = [f for f in os.listdir(data_dir) if f.startswith('MT5_') and f.endswith('_data.csv')]
        
        if not all_files:
            # Fallback: check current directory
            all_files = [f for f in os.listdir('.') if f.startswith('MT5_') and f.endswith('_data.csv')]
            if not all_files:
                print("Error: No data file found!")
                return None, None, None
        
        # Find the most recently modified file
        latest_file = max(all_files, key=lambda f: os.path.getmtime(os.path.join(data_dir, f) if data_dir else f))
        filename_parts = latest_file.replace("MT5_", "").replace("_data.csv", "").split("_")
        symbol = filename_parts[0] if len(filename_parts) > 0 else "Unknown"
        timeframe = filename_parts[1] if len(filename_parts) > 1 else "Unknown"

       
        full_path = os.path.join(data_dir, latest_file)
        print(f"Using most recent file: {full_path}")
        return full_path, symbol, timeframe  # Return FULL PATH

        #shutil.move("c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\in_use\\" + latest_file,"c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\archive\\" + latest_file)
        
        # print(f"Using most recent data file: {latest_file}")
        # return latest_file, symbol, timeframe
        
        
    except Exception as e:
        print(f"Error finding data file: {e}")
        return None, None, None

####################################################################################

def plot_equity_curve(strat):
    """Plot actual equity curve from strat """
    #check if strategy recorded equity data
    try:
        if hasattr(strat, "equity") and strat.equity:
            equity_data = strat.equity
            print(f"Plotting {len(equity_data)} equity points...")
        else:
            final_value = strat.broker.getvalue()
            equity_data = [10000, final_value]
            print("Using simplified equity curve (enable recording in strategy)")

        #create plot
        plt.plot(equity_data, linewidth=2, color="blue", alpha=0.7)
        plt.title("Equity Curve", fontweight="bold")
        plt.xlabel("Time (Bars)")
        plt.ylabel("Portfolio Value ($)")
        plt.grid(True, alpha=0.3)
        
        #add start and end values
        start_val = equity_data[0]
        end_val = equity_data[-1]
        plt.text(0.02, 0.98, f"Start: ${start_val:.2f}", transform=plt.gca().transAxes,
                 verticalalignment="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
        plt.text(0.02, 0.88, f"End: ${end_val:.2f}", transform=plt.gca().transAxes,
                 verticalalignment="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
        
        #add performance annotation
        returns_pct = ((end_val - start_val) / start_val) * 100
        color = "green" if returns_pct >= 0 else "red"
        plt.text(0.02, 0.78, f"Return: {returns_pct:+.2f}%", transform=plt.gca().transAxes,
                 verticalalignment="top", color=color, fontweight="bold",
                 bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
        
    except Exception as e:
        print(f"Error plotting equity curve: {e}")
        plt.text(0.5, 0.5, "Equity data not available\nEnable recording in strategy",
                 transform=plt.gca().transAxes, ha="center", va="centet")
        plt.title("Equity Curve - Data Required", fontweight="bold")

####################################################################################

def plot_drawdown(strat):
    """Plot portfolio drawdown overtime"""
    try:
        if not hasattr(strat, "equity") or not strat.equity:
            plt.text(0.5, 0.5, "Drawdown data not available\nEnable equity recording staregy",
                     transform=plt.gca().transAxes, ha="center", va="center")
            plt.title("Drawdown - Data Required", fontweight="bold")
            return
        
        equity_data = strat.equity
        equity_array = np.array(equity_data)

        #calc running max equity(peak)
        running_max = np.maximum.accumulate(equity_data)

        #calc drawdown in percentage
        drawdown_pct = (equity_array - running_max) / running_max * 100

        #create plot
        plt.fill_between(range(len(drawdown_pct)), drawdown_pct, 0,
                         color="red", alpha=0.3, label="Drawdown")
        plt.plot(drawdown_pct, color="darkred", linewidth=1.5, alpha=0.5)

        plt.title("Portfolio Dradown", fontweight="bold")
        plt.xlabel("Time (bars)")
        plt.ylabel("Drawdown (%)")
        plt.grid(True, alpha=0.3)

        #add max dd annotation
        max_drawdown = np.min(drawdown_pct)
        max_dd_idx = np.argmin(drawdown_pct)
        
        #static 10% dd line
        plt.axhline(y=-5, color="red", linestyle="--", alpha=0.7, linewidth=2,
                    label= "Max DD Limit -5%")
        
        plt.text(0.02, 0.95, f"Max Drawdown: {max_drawdown:.2f}%",
                 transform=plt.gca().transAxes, verticalalignment="top",
                 bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
        
        plt.legend()

    except Exception as e:
        print(f"Error plotting drawdown: {e}")
        plt.text(0.5, 0.5, "Error drawing drawdown chart",
                 transform=plt.gca().transAxes, ha="center", va="center")
        plt.title("Drawdown - Error", fontweight="bold")


###################################################################################
def plot_trade_analysis(strat):
    """Plot trade performance stats"""
    try:
        if not hasattr(strat, "analyzers") or not strat.analyzers.ta:
            plt.text(0.5, 0.5, "Trade data not available\nRun backtest with TradeAnalyzer",
                     transform=plt.gca().transAxes, ha='center', va='center')
            plt.title("Trade Analysis - Data Required", fontweight="bold")
            return
    
        ta = strat.analyzers.ta.get_analysis()

        total_trades = ta.get("total", {}).get("total", 0)
        winning_trades = ta.get("won", {}).get("total", 0)
        losing_trades = ta.get("lost", {}).get("total", 0)

        # Get highest win and loss - check different possible structures
        highest_win = ta.get("won", {}).get("pnl", {}).get("max", 0)
        biggest_loss = ta.get("lost", {}).get("pnl", {}).get("max", 0)
        
        if total_trades == 0:
            plt.text(0.5, 0.5, "No trades executed in backtest",
                    transform=plt.gca().transAxes, ha="center", va="center")
            plt.title("Trade Analysis - No Trades", fontweight="bold")
            return
        
        labels = ["Winning Trades", "Losing Trades"]
        sizes = [winning_trades, losing_trades]
        colors = ["#2ECC71", "#E74C3C"]

        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        plt.axis("equal")
        plt.title(f"Win/Loss Ratio\n({total_trades} Total Trades)", fontweight="bold")

        #basic stats as text
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

        stats_text = [
            f"Win Rate: {win_rate:.1f}%",
            f"Highest Win: {highest_win:.2f}",
            f"Biggest Loss: {biggest_loss:.2f}"
        ]

        for i, text in enumerate(stats_text):
            plt.text(0.5, -0.1 - i*0.08, text,
                     transform=plt.gca().transAxes, ha="center", va="center",
                     bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    except Exception as e:
        print(f"Error plotting trade analysis: {e}")
        plt.text(0.5, 0.5, "Error loading trade data",
                transform=plt.gca().transAxes, ha="center", va="center")
        plt.title("Trade Analysis - Error", fontweight="bold")

###################################################################################

def plot_monthly_returns(strat):
    """Plot calendar heatmap of monthly returns"""
    try:
        if not hasattr(strat, "equity") or not strat.equity:
            plt.text(0.5, 0.5, "Equity data not available\nEnable equity recording in strategy",
                    transform=plt.gca().transAxes, ha="center", va="center")
            plt.title("Monthly Returns - Data Required", fontweight="bold")
            return
        
        equity_data = strat.equity

        df = pd.DataFrame({"equity": equity_data})
        
        #dates for heatmap
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        df["date"] = pd.date_range(start=start_date, end=end_date, periods=len(equity_data))[:len(equity_data)]
        df.set_index("date", inplace=True)

        df["returns"] = df["equity"].pct_change()

        monthly_returns = df["returns"].resample("M").apply(lambda x: (1 + x).prod() - 1)

        monthly_returns_df = pd.DataFrame({
            "returns": monthly_returns,
            "year": monthly_returns.index.year,
            "month": monthly_returns.index.month
        })
        
        pivot_table = monthly_returns_df.pivot_table(
            values="returns",
            index="year",
            columns="month",
            aggfunc="mean"
        )

        #filter out future years that shouldnt exist in data
        current_year = datetime.now().year
        valid_years = [year for year in pivot_table.index if year <= current_year]
        pivot_table = pivot_table.loc[valid_years]

        plt.imshow(pivot_table.values * 100, cmap="RdYlGn", aspect="auto", vmin=-10, vmax=10)
        plt.colorbar(label="Monthly Return (%)")
        plt.title("Monthly Returns Heatmap", fontweight="bold")
        plt.xlabel("Month")
        plt.ylabel("Year")

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        plt.xticks(range(12), months, rotation=45)
        plt.yticks(range(len(pivot_table.index)), pivot_table.index)

        for i in range(len(pivot_table.index)):
            for j in range(12):
                if j < len(pivot_table.columns) and not np.isnan(pivot_table.iloc[i, j]):
                    value = pivot_table.iloc[i, j] * 100
                    plt.text(j, i, f"{value:.1f}%", ha="center", va="center",
                            fontsize=8, fontweight="bold" if abs(value) > 5 else "normal")
                    
    except Exception as e:
        print(f"Error plotting monthly returns: {e}")
        plt.text(0.5, 0.5, "Error creating monthly heatmap",
                 transform=plt.gca().transAxes, ha="center", va="center")
        plt.title("Monthly Returns - Error", fontweight="bold")

###################################################################################

# def plot_position_sizing(strat):
#     """Plot position sizing and trade amounts over"""
#     try:
#         if not hasattr(strat, 'analyzers') or not hasattr(strat.analyzers, 'txn'):
#             plt.text(0.5, 0.5, "Transaction data not available\nEnable transaction recording", 
#                     transform=plt.gca().transAxes, ha='center', va='center')
#             plt.title("Position Sizing - Data Required", fontweight="bold")
#             plt.axis("off")
#             return
        
#         # Get transaction analyzer results
#         txn_analysis = strat.analyzers.txn.get_analysis()
        
#         if not txn_analysis:
#             plt.text(0.5, 0.5, "No transaction data recorded", 
#                     transform=plt.gca().transAxes, ha='center', va='center')
#             plt.title("Position Sizing - No Data", fontweight="bold")
#             plt.axis("off")
#             return
        
#         position_sizes = []

#         #parse transaction data
#         for date, transactions in txn_analysis.items():
#             for txn in transactions:
#                 #tn format: (size, price, value, commission)
#                 if len(txn) >= 3:
#                     size = abs(txn[0])
#                     position_sizes.append(size)
                    

#         if not position_sizes:
#             plt.text(0.5, 0.5, "No position size data available",
#                      transform=plt.gca().transAxes, ha="center", va="center")
#             plt.title("position_sizes - No data", fontweight="bold")
#             plt.axis("off")
#             return
        
#         plt.hist(position_sizes, bins=15, alpha=0.7, color="skyblue", edgecolor="black")
#         plt.title("Position Size Distribution", fontweight="bold")
#         plt.xlabel("Position Size (Units)")
#         plt.ylabel("Frequency")
#         plt.grid(True, alpha=0.3)

#         stats_text = [
#             f"Total Trades: {len(position_sizes)}",
#             f"Avg Size: {np.mean(position_sizes):.2f} units",
#             f"Min: {np.min(position_sizes):.2f} units",
#             f"Max: {np.max(position_sizes):.2f} units"
#         ]

#         for i, text in enumerate(stats_text):
#             plt.text(0.95, 0.85 - i*0.08, text, fontsize=9, transform=plt.gca().transAxes,
#                      ha="right", va="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))       
        
#     except Exception as e:
#         print(f"Error plotting position sizing: {e}")
#         plt.text(0.5, 0.5, "Error loading position data", 
#                 transform=plt.gca().transAxes, ha='center', va='center')
#         plt.title("Position Sizing - Error", fontweight="bold")
#         plt.axis('off')

###################################################################################

def get_backtest_results():
    """Load and run backtest for results"""
    try:
        cerebro = bt.Cerebro()
        cerebro.addstrategy(SmaCrossStrategy)

        data_file, symbol, timeframe = find_data_file()
        if data_file is None:
            return None, None

        print(f"Backtesting {symbol} on {timeframe} timeframe... wait tep u mug")      

        data = bt.feeds.GenericCSVData(
            dataname=data_file,  
            dtformat=("%Y-%m-%d %H:%M:%S"),
            timeframe=bt.TimeFrame.Minutes,
            compression=15,
            open=1,   #column 1: Open (0 based indexing: 0=date, 1=Open, 2=High, etc)
            high=2,   #column 2: High
            low=3,    #column 3: Low
            close=4,  #column 4: Close
            volume=5,    #column 5: Volume
            openinterest=-1,   #no open interest column
            reverse=False
        )

        cerebro.adddata(data)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.0001)
        cerebro.broker.set_slippage_perc(0.00005)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe_ratio")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
        cerebro.addanalyzer(bt.analyzers.Transactions, _name="txn")

        print("Running backtest...")
        results = cerebro.run()
        strat = results[0]
        print("Visualization Backtest Done")

        #store symbol info in strategy for later use
        strat.symbol = symbol
        strat.timeframe = timeframe
        
        # if data_file and os.path.exists(data_file):
        #     archive_path = "c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\archive\\" + os.path.basename(data_file)
        #     shutil.move(data_file, archive_path)
        #     print(f"Moved {data_file} to archive")

        return strat, results
    
    except Exception as e:
        print(f"Error running backtest: {e}")
        return None, None
                            
####################################################################################

if __name__ == "__main__":
    print("Generating Performance Dashboard...")
    strat, results = get_backtest_results()

    if strat is not None and results is not None:
        create_performance_dashboard(strat, results)
        print("Dashboard saved with symbol/timeframe in filename!`")
    else:
        print("Please run mt5_data_export.py first to generate results!")
        print("Then run this visualization tool.")

        
