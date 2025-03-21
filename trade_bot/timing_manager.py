import datetime

class TimingManager:
    """Manage the process of placing trades and handling bracket orders."""
    def __init__(self, ib, contract, session_manager):
        self.ib = ib  # IB connection object for interacting with the broker.
        self.contract = contract  # The trading instrument (e.g., futures or stocks).
        self.session_manager = session_manager  # Manages session states (e.g., monitoring open orders).
    
    def calculate_next_signal_check_time(self): # Calculate the next time to check for trading signals (aligned to the 5-minute cycle).
        current_time = datetime.now()  # Get the current date and time.
        minutes_to_next_run = 5 - (current_time.minute % 5)   # Calculate the number of minutes until the next 5-minute interval.
        seconds_to_next_run = (minutes_to_next_run * 60) - current_time.second + 8  # Calculate the total seconds until the next 5-minute interval, with an 8-second buffer.

        if seconds_to_next_run < 8:  # If the calculation results in a very short time (< 8 seconds), adjust for the next interval.
            seconds_to_next_run += 5 * 60  # Add 5 minutes (300 seconds) to ensure the next check is properly aligned.
        return current_time + timedelta(seconds=seconds_to_next_run) # Return the exact timestamp for the next signal check.
    
    def stoploss_type(self, signal_type, sl):
        """Decide stop-loss order type based on market hours."""
        current_time = datetime.now().time() # Get the current time as a `time` object
        start_time = dtime(15, 30) # Define the start time (15:30)
        end_time = dtime(22, 0) # Define the end time (22:00)
        
        if start_time <= current_time < end_time: # Check if the current time is within the specified range
            return StopOrder('SELL' if signal_type == 'bullish' else 'BUY', 1, sl, outsideRth=True)
        else:
            stop_price = sl - 0.25 if signal_type == 'bullish' else sl + 0.25  # Adjust stop price based on signal type
            return StopLimitOrder('SELL' if signal_type == 'bullish' else 'BUY', 1, stop_price, sl, outsideRth=True)
               
market_hours = MarketHours(dtime(0, 5), dtime(22, 15))
iteration_lock = threading.Lock()  # Define the lock at the top level