#sma_backtest.py
#Backtesting a Simple Moving Average Crossover Strategy

import backtrader as bt
import pandas as pd
import os
import sys
import shutil
#redirect print to nowhere during backtest - this makes my output clean and show me what i only want to see
class Silent:
    def write(self, x):
        pass
    def flush(self):
        pass

#uncomment below line to SILENT ALL OUTPUT during cerebro run()
#sys.stdout = Silent()

#define our trading strategy
class SmaCrossStrategy(bt.Strategy):
    #Define the parameters for the moving averages
    
    #period for the fast moving average (50 days)
    #period for the slow moving average (200 days)
    #medium term
    params = dict(
        pfast=5,
        pslow=10,
        risk_per_trade=0.9,   # acting like MT5 lot size
        stop_loss_pct=0.15,     # setting a 2% SL 4%TP (1:2RR)
        take_profit_pct=0.35,
    )
    

    def __init__(self):

        self.order = None # track current orders
        self.trade_count = 0 # track trade number
        self.equity = []

        # create the moving average indicators
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.pfast)
        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.pslow)
        self.order = None
        self.trade_count = 0
        
        #This indicator will generate crossover signals (1 for up, -1 for down)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

        self.trend_filter = bt.indicators.SimpleMovingAverage(
            self.data.close, period=5
        )

        self.volume_sma = bt.indicators.SimpleMovingAverage(
            self.data.volume, period=20
        )
    
    def next(self):
        if self.order:
            return
        if self.data.close[0] < self.trend_filter[0]:
            return
        if self.data.volume[0] < self.volume_sma[0] * 1.0:
            return
        
        if self.position:
            current_price = self.data.close[0]
            position_value = self.position.size * current_price
            entry_value = self.position.size * self.position.price
            current_pnl = position_value - entry_value

            #if loss exceeds $500 close position
            if current_pnl <= -200:
                print(f"Max SL triggered. Closing position with P&L: ${current_pnl:.2f}")
                self.close()
                return
        
        if not self.position:
            if self.crossover > 0:
                risk_amount = self.broker.getvalue() * self.params.risk_per_trade
                price = self.data.close[0]
                position_size = risk_amount / price


                #calc sl/tp prices
                sl_price = price * (self.params.stop_loss_pct)
                tp_price = price * (1 + self.params.take_profit_pct)
                
                #execute buy with bracket orders sl/tp
                self.buy_bracket(
                    size=position_size,
                    price=price,
                    stopprice=sl_price,
                    limitprice=tp_price,
                    exectype=bt.Order.StopTrail,
                    trailpercent=0.01,
                    
                )

                self.sell_bracket(
                    size=position_size,
                    price=price,
                    stopprice=sl_price,
                    limitprice=tp_price,
                    exectype=bt.Order.StopTrail,
                    trailpercent=0.01
                )

        else:
            if self.crossover < 0:
                self.close()

        self.equity.append(self.broker.getvalue())

    def notify_order(self, order):
        """Track order execution status"""
        if order.status in [order.Completed]:
            if order.isbuy():
                self.trade_count += 1
                print(f"Trade #{self.trade_count} filled at {order.executed.price:.5f}") # - UNCOMMENT IF YOU WANT TO SEE CEREBRO RUN INFO

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            pass #print(f"Order canceled/margin/rejected: {order.status}") - UNCOMMENT AND REMOVE PASS IF YOU WANT TO SEE CEREBRO RUN INFO
        self.order = None
        
    def notify_trade(self, trade):
        """Track trade P&L"""
        if trade.isclosed:
            print(f"trade P&L: ${trade.pnl:.2f} ({trade.pnlcomm:.2f} with commission)") #- UNCOMMENT AND REMOVE PASS IF YOU WANT TO SEE TRADE PNL INFO

def find_data_file():
    """Find the most recent MT5 data file"""
    try:
        # First check if we have metadata from latest export
        if os.path.exists("latest_export_info.txt"):
            with open("latest_export_info.txt", "r") as f:
                symbol, timeframe = f.read().strip().split(",")
                expected_file = f"MT5_{symbol}_{timeframe}_data.csv"

                expected_file_path = "c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\" + expected_file
                if os.path.exists(expected_file_path):
                    print(f"Using latest exported file: {expected_file_path}")
                    new_path = "c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\in_use\\" + expected_file
                    shutil.move(expected_file_path, new_path)
                    return new_path, symbol, timeframe  # Return path to the MOVED file
                
                
                    # shutil.move(expected_file_path, "c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\in_use\\" + expected_file)
                    # return expected_file_path, symbol, timeframe  # Return FULL PATH
                
                # if os.path.exists(expected_file):
                #     print(f"Using latest exported file: {expected_file}")
                #     #shutil.move("c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\" + expected_file,"c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\in_use\\" + expected_file)
                #     return expected_file, symbol, timeframe

        
        # Fallback: find most recent file in data directory
        data_dir = "c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\"
        all_files = [f for f in os.listdir(data_dir) if f.startswith('MT5_') and f.endswith('_data.csv')]
        # First check if we have metadata from latest export
        #shutil.move("c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\" + expected_file,"c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\in_use\\" + expected_file)
        
        if not all_files:
            print("Error: No data files found!")
            return None, None, None
        
        latest_file = max(all_files, key=lambda f: os.path.getmtime(os.path.join(data_dir, f)))
        filename_parts = latest_file.replace("MT5_", "").replace("_data.csv", "").split("_")
        symbol = filename_parts[0] if len(filename_parts) > 0 else "Unknown"
        timeframe = filename_parts[1] if len(filename_parts) > 1 else "Unknown"

        data_dir = "c:\\Users\\Lehasa\\Desktop\\Trading_Backtesting_Project\\data_save\\"
        full_path = os.path.join(data_dir, latest_file)
        print(f"Using most recent file: {full_path}")
        return full_path, symbol, timeframe  # Return FULL PATH

        # print(f"Using most recent file: {latest_file}")
        # return latest_file, symbol, timeframe
    
    except Exception as e:
        print(f"Error finding data file: {e}")
        return None, None, None

#This part is for running the backtest - THIS IS THE BACKTEST/CEREBRO CALLING FROM DATA EXPORT
if __name__ == "__main__":

    data_file, symbol, timeframe = find_data_file()
    if data_file is None:
        exit(1)

    print(f"Backtesting {symbol} on {timeframe} timeframe...")

    #create a cerebro engine (the core of backtrader)
    cerebro = bt.Cerebro()
    #add our strategy
    cerebro.addstrategy(SmaCrossStrategy)

    #load our data from CSV file
    data = bt.feeds.GenericCSVData(
        dataname=data_file,  #Your exported file - CHANGE THE HASHTAGS ON DTFORMAT AND TIMEFORMAT ROUND WHEN SWITICHING FORM MINUTES TO DAYS ON DATA ###########################################
        dtformat=("%Y-%m-%d %H:%M:%S"),  #MT5 MINUTES TIMESTAMP FORMAT
        timeframe=bt.TimeFrame.Minutes,  #Minutes data
        #dtformat=("%Y-%m-%d"),           #MT5 DAILY TIMESTAMP FORMAT
        #timeframe=bt.TimeFrame.Days,  #Daily data
        
        compression=15,  
        open=1,   #column 1: Open (0 based indexing: 0=date, 1=Open, 2=High, etc)
        high=2,   #column 2: High
        low=3,    #column 3: Low
        close=4,  #column 4: Close
        volume=5,    #column 5: Volume
        openinterest=-1,   #no open interest column
        reverse=False
    )

    #add the data to cerebro
    cerebro.adddata(data)

    #set our starting cash
    cerebro.broker.setcash(100000.0) #$100,000 starting capital

    #adding commission and slippage
    cerebro.broker.setcommission(commission=0.0001)  #0.1% commission
    cerebro.broker.set_slippage_perc(0.00005)        #0.05% slippage

    #set the commision - 0.1% per trade
    #cerebro.broker.setcommission(commission=0.001)

    #add analyzers to calculate performance stats
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe_ratio")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")

    #print out the starting portfolio value
    print("Starting Portfolio Value: $%.2f" % cerebro.broker.getvalue())

    #adding trade analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.Transactions, _name="txn")

    #run the backtest over the historical data!
    results = cerebro.run()

    #grab strategy object from results
    strat = results[0]

    #print out the final portfolo value
    print("Final Portfolio Value: $%.2f" % cerebro.broker.getvalue())


    print("Sharpe Ratio:", strat.analyzers.sharpe_ratio.get_analysis()["sharperatio"])
    print("Max Drawdown: %.2f%%" % strat.analyzers.drawdown.get_analysis()["max"]["drawdown"])

    #this is trade analysis
    print("\n" + "=" *50)
    print("TRADE ANALYSIS")
    print("="*50)

    try:
        trade_analysis = strat.analyzers.ta.get_analysis()
        if hasattr(trade_analysis, "total"):
            print(f"Total trades: {trade_analysis.total.total}")
            print(f"Winning Trades: {trade_analysis.won.total}")
            print(f"Losing Trades: {trade_analysis.lost.total}")
            print(f"Win Rate: {(trade_analysis.won.total/trade_analysis.total.total)*100:.2f}%")

            if hasattr(trade_analysis, "pnl"):
                print(f"Net P&L: ${trade_analysis.pnl.net.total:.2f}")
        
    except Exception as e:
        print(f"Trade Analysis Error: {e}")

    #this is transaction log
    print("\n" + "="*50)
    print("TRANSACTIONS LOG")
    print("="*50)
    try:
        transactions = strat.analyzers.txn.get_analysis()
        for date, txns in transactions.items():
            for txn in txns:
                pass #print(f"{date}: {txn}") #UNCOMMENT AND REMOVE PASS IF YOU WANT TO SEE CEREBRO RUN INFO
    except Exception as e:
        print(f"Transaction Error: {e}")


    print("Your backtest is complete Tep!")

    #plotting results
    import matplotlib.pyplot as plt
    plt.rcParams["figure.figsize"] = [12, 8]
    cerebro.plot(style="candlestick", volume=True, barup="green", bardown="red")