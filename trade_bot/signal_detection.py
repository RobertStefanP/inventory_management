import datetime
from log_to_file import log_to_file

class SignalDetection:
    """Calculating and checking for crossover and differences between EMA/SMA - Price"""
    def __init__(self, data_handler, difference_size=0.50):  # Initialize the class with a data handler, trade manager, and difference_size=0.50.
        self.data_handler = data_handler  # Responsible for fetching and processing market data.
        self.difference_size = difference_size  # Minimum distance between bar and indicators.
        self.bars_below = 0  # Counter for bars with highs below EMA/SMA
        self.bars_above = 0  # Counter for bars with lows above EMA/SMA
               
    def counting_bars(self, indicators, historical_data=None):       
        if not hasattr(self, "bars_below_details"): # Initialize a list to store bar details
            self.bars_below_details = []  # List to store details of bars where the high is below EMA and SMA
        if not hasattr(self, "bars_above_details"):
            self.bars_above_details = []  # List to store details of bars where the low is above EMA and SMA
        
        if indicators is None or indicators.empty: # Check if indicators are valid; return current counts and lists if not
            print("No indicator data available.")
            return self.bars_below, self.bars_above, self.bars_below_details, self.bars_above_details  # Return current counts
        
        if historical_data is not None and not historical_data.empty and self.bars_below == 0 and self.bars_above == 0: # Check if historical data is available and counters are at zero (first run of the bot)
            for _, row in historical_data.iloc[:-2].iloc[::-1].iterrows():  # Iterate through historical data rows, excluding the last two rows, in reverse order
                if row['high'] < row['EMA'] and row['high'] < row['SMA']: # If the high is below both EMA and SMA
                    if row['date'] not in [bar['date'] for bar in self.bars_below_details]: # Check if the current bar's date is already in the list of bars below
                        self.bars_below += 1 # Increment the counter for bars below
                        self.bars_below_details.append(row.to_dict())  # Add the bar's details to the list as a dictionary
                elif row['low'] > row['EMA'] and row['low'] > row['SMA']: # If the low is above both EMA and SMA
                    if row['date'] not in [bar['date'] for bar in self.bars_above_details]: # Check if the current bar's date is already in the list of bars above
                        self.bars_above += 1 # Increment the counter for bars above
                        self.bars_above_details.append(row.to_dict())  # Add the bar's details to the list as a dictionary
                else:
                    break # Stop iterating through historical data
                 
        low_price = indicators['low'].iloc[-2]  # Get the low price of the previous bar
        high_price = indicators['high'].iloc[-2]  # Get the high price of the previous bar
        open_price = indicators['open'].iloc[-2] # Get the open price for the previous bar
        close_price = indicators['close'].iloc[-2] # Get the close price for the previous bar
        midpoint = indicators['midpoint'].iloc[-2] # Get the midpoint of the previous bar
        current_ema = indicators['EMA'].iloc[-2]  # Get the EMA value of the previous bar
        current_sma = indicators['SMA'].iloc[-2]  # Get the SMA value of the previous bar 
        current_date = indicators['date'].iloc[-2]  # Get the timestamp of the previous bar
        
        if high_price < current_ema and high_price < current_sma:  # Check if the high price is below both EMA and SMA
            if current_date not in [bar['date'] for bar in self.bars_below_details]: # Ensure the bar is not already in the list of bars below
                self.bars_below += 1 # Increment the counter for bars below
                self.bars_below_details.append({ # Add the bar's details as a dictionary
                    "date": current_date,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "midpoint": midpoint,
                    "EMA": current_ema,
                    "SMA": current_sma,
                })
            self.bars_above = 0  # Reset the counter for bars above
            self.bars_above_details.clear()  # Clear the list for bars above
                
        elif low_price > current_ema and low_price > current_sma:  # Check if the low price is above both EMA and SMA
            if current_date not in [bar['date'] for bar in self.bars_above_details]: # Ensure the bar is not already in the list of bars above
                self.bars_above += 1  # Increment the counter for bars above
                self.bars_above_details.append({ # Add the bar's details as a dictionary
                    "date": current_date,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "midpoint": midpoint,
                    "EMA": current_ema,
                    "SMA": current_sma,
                })
            self.bars_below = 0  # Reset the counter for bars below
            self.bars_below_details.clear()  # Clear the list of bars below
                   
        else:  # Condition not met
            self.bars_below = 0  # Reset the counter for bars below
            self.bars_above = 0  # Reset the counter for bars above
            self.bars_below_details.clear()  # Clear the list of bars below
            self.bars_above_details.clear() # Clear the list of bars above                           
        return self.bars_below, self.bars_above, self.bars_below_details, self.bars_above_details # Return the current counts for external use
    
    @staticmethod
    def print_bar_details(details, label="Bar Details"): # Function to print bars_above_details or bars_below_details in a table format
        current_time = datetime.now().strftime('%H:%M:%S')
        if details: # Check if the list has any data
            df = pd.DataFrame(details) # Convert the list of dictionaries to a Pandas DataFrame
            
            columns_to_drop = ["volume", "average", "barCount"] # Drop the unwanted columns if they exist in the DataFrame
            df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
            
            table_str = df.to_string(index=False)  # Convert DataFrame to a string without index for better readability
            log_to_file(f"{current_time} - {label}:{table_str}")  # Log the table to a file
            print(f"{current_time} - {label}:") # Print the label
            log_to_file(df)
            print(df)  # Print the DataFrame in tabular format
        else:
            log_to_file(f"{current_time} - {label}: No data to display.")
            print(f"\n{current_time} - {label}: \n\t\tNo data to display.") # Print a message if the list is empty
                     
    def bar_distance_from_indicators(self, indicators):
        """Detect signals based on EMA/SMA indicators and price action."""
        if indicators is None or indicators.empty:
            return None, {}, "No data available for processing."  # Include a debug message
        
        current_price = indicators['close'].iloc[-1] # Retrieve the current bar data
        current_ema = indicators['EMA'].iloc[-1] # Retrieve the current ema data
        current_sma = indicators['SMA'].iloc[-1] # Retrieve the current sma data
        
        low_price = indicators['low'].iloc[-1] # Retrieve the current bar data
        high_price = indicators['high'].iloc[-1] # Retrieve the current bar data
        
        previous_5min_low = indicators['low'].iloc[-2] # Retrieve the previous bar data
        previous_5min_high = indicators['high'].iloc[-2] # Retrieve the previous bar data
        previous_5min_ema = indicators['EMA'].iloc[-2] # Retrieve the previous ema data
        previous_5min_sma = indicators['SMA'].iloc[-2] # Retrieve the previous sma data
       
        ema_diff = current_ema - current_price # Calculate ema differences
        sma_diff = current_sma - current_price # Calculate sma differences
        
        ema_diff_formatted = f"+{ema_diff:.2f}" if ema_diff >= 0 else f"{ema_diff:.2f}"  # Format EMA difference.
        ema_diff_formatted = f"{float(ema_diff):+06.2f}" if abs(ema_diff) < 10 else ema_diff_formatted  # Add leading zero if single digit.
        
        sma_diff_formatted = f"+{sma_diff:.2f}" if sma_diff >= 0 else f"{sma_diff:.2f}"  # Format SMA difference.
        sma_diff_formatted = f"{float(sma_diff):+06.2f}" if abs(sma_diff) < 10 else sma_diff_formatted  # Add leading zero if single digit.
          
        # Debug information to return
        debug_info = { 
            "current_price": current_price,
            "current_ema": current_ema,
            "current_sma": current_sma,
            "low_price": low_price,
            "high_price": high_price,
            "previous_5min_low": previous_5min_low,
            "previous_5min_high": previous_5min_high,
            "previous_5min_ema": previous_5min_ema,
            "previous_5min_sma": previous_5min_sma,
            "ema_diff": round(ema_diff, 2),
            "sma_diff": round(sma_diff, 2),
            "ema_diff_formatted": ema_diff_formatted,
            "sma_diff_formatted": sma_diff_formatted,
        }
      
        if (previous_5min_low - self.difference_size > previous_5min_ema and # Bullish signal conditions
            previous_5min_low - self.difference_size > previous_5min_sma and
            low_price - self.difference_size > current_ema and
            low_price - self.difference_size > current_sma):
            return 'bullish', debug_info, "BULLISH signal detected!"
       
        if (previous_5min_high + self.difference_size < previous_5min_ema and # Bearish signal conditions
            previous_5min_high + self.difference_size < previous_5min_sma and
            high_price + self.difference_size < current_ema and
            high_price + self.difference_size < current_sma):
            return 'bearish', debug_info, "BEARISH signal detected!"     
        return None, debug_info, "NO signal detected!" # No signal