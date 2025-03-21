import os
import json
import threading
import time 
import time as tm
import pandas as pd
import datetime
import nest_asyncio
from ib_insync import util
from datetime import datetime
from colorama import init, Fore, Style
from datetime import datetime, timezone, timedelta, time as dtime
from ib_insync import IB, Future, MarketOrder, Order, OrderStatus, StopOrder, StopLimitOrder, LimitOrder, Trade, Position

#market_hours = MarketHours(dtime(0, 5), dtime(22, 15))
iteration_lock = threading.Lock()  # Define the lock at the top level
        
if __name__ == "__main__":      
    # Ensure the asyncio event loop works well in the current environment. 
    nest_asyncio.apply() # Fixes nested asyncio event loop issues.
    broker = BrokerConnection('127.0.0.1', 7497, 1) # Create a connection to the broker (IB TWS/Gateway).
    broker.manage_connection() # Start and manage the broker connection.  
    contract = Future(symbol='MES', lastTradeDateOrContractMonth='20250321', exchange='CME') # Define the trading contract (e.g., Micro E-mini S&P 500 futures).
    session_manager = SessionManager(broker.ib, contract) # Initialize a session manager to track open orders and positions.
    timing_manager = TimingManager(broker.ib, contract, session_manager) # Create an instance of TimingManager to handle signal-check timing.
    data_handler = DataHandler(broker.ib, contract) # Initialize DataHandler to fetch and process historical data.      
    json_reader = JsonEventsReader(session_manager, 'order_position_status.json') # Read and handle JSON files for tracking order statuses.
    trader = TradeExecution(broker.ib, contract, session_manager, json_reader, timing_manager) # Initialize TradeExecution for placing trades.
    signal_detector = SignalDetection(data_handler) # Create SignalDetection to detect signals and manage trades.
    #market_hours = MarketHours(dtime(0, 5), dtime(22, 58)) # Set market hours (open at 00:05 and close at 22:58).
    order_position_status_file = 'order_position_status.json' # Define the JSON file for tracking order statuses.
    current_time = datetime.now().strftime('%H:%M:%S')  # Get the current time for logging purposes.    
    next_run_time = timing_manager.calculate_next_signal_check_time()  # Calculate the next 5-minute interval for signal checking.    
    wait_seconds = (next_run_time - datetime.now()).total_seconds() # Calculate the time to wait until the next signal check.
                                                    
    session_manager.check_open_orders(initial_check=True) # Perform an initial check for any open orders.
    session_manager.check_positions(initial_check=True) # Perform an initial check for existing positions.
    log_to_file(f"{current_time} - Startup orders/positions check done!!")  # Log a message indicating the completion of the initial check.
    print(f"{current_time} - Startup orders/positions check done!!")
   
    if session_manager.open_orders or session_manager.open_positions: # If there are existing open orders or positions:
        current_time = datetime.now().strftime('%H:%M:%S')
        json_reader.start_json_reader()       # Initialize EventHandler
        session_manager.monitoring_opened_orders_mode = True # Switch to monitoring open orders/positions mode.                   
        session_manager.checking_for_signals_mode = False # Disable signal checking mode.
        log_to_file(f"{current_time} - Monitoring already existing orders/positions...")  # Log that existing orders/positions are being monitored.
        print(f"{current_time} - Monitoring already existing orders/positions...")
        
        session_manager.update_event.wait(wait_seconds) # This is Event_wait (time sleep) 5 min.  # Wait until the next signal check or event.
        session_manager.update_event.clear() # Clear the event flag.        
        
    else: # If no open orders or positions are found:
        current_time = datetime.now().strftime('%H:%M:%S')
        session_manager.checking_for_signals_mode = True # Enable signal checking mode.
        session_manager.monitoring_opened_orders_mode = False  # Disable monitoring mode.
        print(f"{current_time} - No open orders/positions, starting trading operations!")   
        print("---------------------------------------------")
        log_to_file(f"{current_time} -  START EVENT HANDLER bot !!")
        print(f"{current_time} -  START EVENT HANDLER bot !!")
        print("---------------------------------------------")              
    try:
        while market_hours.is_market_open():  # Continue running the bot while the market is open. 
            current_time = datetime.now().strftime('%H:%M:%S')  # Get the current time for logging/debugging purposes.
            with iteration_lock:  # Acquire a lock to prevent concurrent iterations.                                                                                                            
                next_run_time = timing_manager.calculate_next_signal_check_time()  # Calculate the next run time      
                wait_seconds = (next_run_time - datetime.now()).total_seconds() # Calculate the wait time until the next run     
                indicators = None  # Initialize indicators to None # THIS IS placed for the counting bars function   
                                            
                historical_data = data_handler.fetch_historical_data('2 D', '5 mins', 'TRADES')  # Fetch historical data
                indicators, current_price, latest_ema, latest_sma = data_handler.calculate_indicators(historical_data)  # Calculate EMA and SMA indicators.
                bars_below, bars_above, bars_below_details, bars_above_details = signal_detector.counting_bars(indicators, historical_data) # Bar above/below counting  
                
                daily_bars = data_handler.calculate_dailybars_detail(historical_data, indicators) # Add today's 5min bars details to the list
                df = pd.DataFrame(daily_bars)
                print(df.iloc[-30:])  # This prints the last 30 lines of 5min bars details
            
                SignalDetection.print_bar_details(bars_below_details, label="Bars Below Details") # Print details for bars below                                
                SignalDetection.print_bar_details(bars_above_details, label="Bars Above Details") # Print details for bars above                
                                        
                if bars_below or bars_above:                                       
                    if bars_below != 0:
                        log_to_file(f"{current_time} - Bars below: {bars_below}")  # Log the current count of bars below EMA and SMA
                        print(f"\n{current_time} - Bars below: {bars_below}")
                        
                        # # Maybe here a flag with trading mode off if the bars_bellow > 1 (we need the first bar to take the trade, right?)
                        # # BUT one must exist (the first one) so that the trade could be taken
                        # if bars_below == 1:
                        #     print(f"\n{current_time} - One bar below, trading mode on.")
                        #     session_manager.checking_for_signals_mode = True# Enable signal checking mode.
                        #     session_manager.monitoring_opened_orders_mode = False  # Disable monitoring mode.
                        # else:
                        #     print(f"{current_time} - More than 1 bar below, no trades till a touch happens.")
                        #     session_manager.checking_for_signals_mode = False # Enable signal checking mode.
                        #     session_manager.monitoring_opened_orders_mode = True  # Disable monitoring mode.
                            
                    elif bars_above != 0:
                        log_to_file(f"{current_time} - Bars above: {bars_above}")
                        print(f"\n{current_time} - Bars above: {bars_above}")  # Print the current count of bars above EMA and SMA
                        
                        # # Maybe here a flag with trading mode off if the bars_above > 1 (we need the first bar to take the trade, right?)
                        # # BUT one must exist (the first one) so that the trade could be taken
                        # if bars_above == 1:
                        #     print(f"\n{current_time} - One bar above, trading mode on.")
                        #     session_manager.checking_for_signals_mode = True # Enable signal checking mode.
                        #     session_manager.monitoring_opened_orders_mode = False  # Disable monitoring mode.
                        # else:
                        #     print(f"{current_time} - More than 1 bar above, no trades till a touch happens.")
                        #     session_manager.checking_for_signals_mode = False # Enable signal checking mode.
                        #     session_manager.monitoring_opened_orders_mode = True  # Disable monitoring mode.
                else:
                    log_to_file(f"{current_time} - Bars: no bars above or below.")
                    print(f"\n{current_time} - Bars: no bars above/below.")  
###########################################################################################
                    # Probably here, place a flag to mark trading mode on                    
                    # session_manager.checking_for_signals_mode = False # Enable signal checking mode.
                    # session_manager.monitoring_opened_orders_mode = True  # Disable monitoring mode.
                    
                if indicators is not None and not indicators.empty:  # Ensure indicators is valid  # If data is available:
                    signal, debug_info, debug_message = signal_detector.bar_distance_from_indicators(indicators)                    
                                                     
                    log_to_file(f"{current_time} - Current bar: Low={debug_info['low_price']}, High={debug_info['high_price']}, EMA={round(debug_info['current_ema'], 2)}, SMA={round(debug_info['current_sma'], 2)}")
                    print(f"{current_time} - Current bar: Low={debug_info['low_price']}, High={debug_info['high_price']}, EMA={round(debug_info['current_ema'], 2)}, SMA={round(debug_info['current_sma'], 2)}")
                    log_to_file(f"{current_time} - Previous bar: Low={debug_info['previous_5min_low']}, High={debug_info['previous_5min_high']}, EMA={round(debug_info['previous_5min_ema'], 2)}, SMA={round(debug_info['previous_5min_sma'], 2)}")
                    print(f"{current_time} - Previous bar: Low={debug_info['previous_5min_low']}, High={debug_info['previous_5min_high']}, EMA={round(debug_info['previous_5min_ema'], 2)}, SMA={round(debug_info['previous_5min_sma'], 2)}")
                        
                    log_to_file(f"{current_time} - Current Price: {current_price}, - Latest EMA: {latest_ema}, Latest SMA: {latest_sma}")  # Log the latest price, EMA, and SMA values for debugging.
                    print(f"{current_time} - Current Price: {format(current_price, '.2f')}, - Latest EMA: {format(latest_ema, '.2f')}, Latest SMA: {format(latest_sma, '.2f')}")  # Log the latest price, EMA, and SMA values for debugging.                    
                    log_to_file(f"{current_time} - Difference if price is 0: EMA: {debug_info['ema_diff_formatted']}, SMA: {debug_info['sma_diff_formatted']}") 
                    print(f"{current_time} - Difference if price is 0:        EMA:  {debug_info['ema_diff_formatted']},        SMA:  {debug_info['sma_diff_formatted']}") # Distance from price EMA/SMA
                    
                else:
                    log_to_file(f"{current_time} - No data to calculate indicators.")  # Log a message if there is no data to process.
                    print(f"{current_time} - No data to calculate indicators.")  # Log a message if there is no data to process.
                                                                                                                              
                if session_manager.monitoring_opened_orders_mode: # If monitoring open orders and positions:   
                    current_time = datetime.now().strftime('%H:%M:%S')                 
                    log_to_file(f"{current_time} - Checking open orders and positions.")
                    print(f"{current_time} - Checking open orders and positions.")
                    
                    json_reader.start_json_reader() # Start reading JSON for events.
                    session_manager.check_open_orders() # Check for open orders.
                    session_manager.check_positions() # Check for open positions.
                                       
                    log_to_file(f"{current_time} - Monitoring opened orders/positions, waiting to be filled/canceled...")
                    print(f"{current_time} - Monitoring opened orders/positions, waiting to be filled/canceled...")
                                        
                    session_manager.update_event.wait(wait_seconds) # This is Event_wait (time sleep) 5 min. # Wait for either the event or the sleep timeout
                    session_manager.update_event.clear() # Clear the event flag.                             
            
                    if not session_manager.open_orders and not session_manager.open_positions: # If no open orders or positions remain:
                        current_time = datetime.now().strftime('%H:%M:%S')
                        session_manager.monitoring_opened_orders_mode = False # Disable monitoring mode.
                        json_reader.stop_json_reader()  # Stop the JSON reader thread.
                        log_to_file(f"{current_time} - Order filled, json reader stoped!! ")
                        print(f"{current_time} - Order filled, json reader stoped!! ")
                        continue  # Immediately start checking for signals    
                                                                                                                                                                                        
                elif session_manager.checking_for_signals_mode: # If in signal checking mode:                 
                    json_reader.stop_json_reader()  # Call the method to set stop_reader to True 
                    with session_manager.lock:  # Acquire the lock to ensure thread safety. 
                        current_time = datetime.now().strftime('%H:%M:%S')  
                        log_to_file(f"{current_time} - Waiting until the next signal check...")                 
                        print(f"{current_time} - Waiting until the next signal check...")                   
                                                                
                        session_manager.update_event.wait(wait_seconds) # This is Event_wait (time sleep) 5 min. IF removed, infinite loop!
                        session_manager.update_event.clear() # This will reset the Event_wait # Clear the event flag.                                                      
                        try:
                            current_time = datetime.now().strftime('%H:%M:%S')
                            historical_data = data_handler.fetch_historical_data('2 D', '5 mins', 'TRADES')  # Fetch historical data
                            indicators = None  # Initialize indicators to None
                            
                            if historical_data is not None and not historical_data.empty:  # If historical data is fetched and not empty
                                indicators, current_price, latest_ema, latest_sma = data_handler.calculate_indicators(historical_data)  # Calculate EMA and SMA indicators. 
                                                                          
                                if indicators is not None and not indicators.empty:  # Ensure indicators is valid
                                    signal, debug_info, debug_message = signal_detector.bar_distance_from_indicators(indicators)  # Check for signals 
                                    send_telegram_message(f"\n{current_time} - {debug_message}") # Send debug information to Telegram
                                                                                                         
                                    if signal:  # If a signal (either 'bullish' or 'bearish') is returned                                                                       
                                        current_price = indicators['close'].iloc[-1]  # Get the most recent close price
                                        trader.place_bracket_order(current_price, signal)
                                                                                                                                 
                                        session_manager.check_open_orders()  # Re-check open orders.
                                        session_manager.check_positions()  # Re-check open positions.
                                        session_manager.update_modes()  # Update session modes.                                                                
                                        json_reader.start_json_reader() # Start JSON reader thread after placing a trade
                                    else:  
                                        pass
                                else:
                                    log_to_file(f"{current_time}- Indicators are not available or empty.")  # Log that indicators are not available or empty.
                                    print(f"{current_time}- Indicators are not available or empty.")         
                            else:
                                log_to_file(f"{current_time} - Historical data is not available or empty.")  # Log that historical data is not available or empty.
                                print(f"{current_time} - Historical data is not available or empty.")     
                                         
                        except Exception as e: # Log any errors that occur during signal processing.
                            log_to_file(f"{current_time} - Error during signal processing: {e}")
                            print(f"{current_time} - Error during signal processing: {e}")      
    except KeyboardInterrupt: 
        log_to_file(f"{current_time} - Manual disconnected from IB")
        print(f"{current_time} - Manual disconnected from IB")
                                                                                
    except Exception as e: # Log any critical errors that occur in the main loop.
        log_to_file(f"{current_time} - Critical error in main loop: {e}")
        print(f"{current_time} - Critical error in main loop: {e}")
        
    finally:
        json_reader.stop_json_reader() # Stop the JSON reader thread.
        log_to_file(f"{current_time} - Disconnected and waiting until market opens again.")
        print(f"{current_time} - Disconnected and waiting until market opens again.")
        broker.disconnect() # Disconnect from the broker.