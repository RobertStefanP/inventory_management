# import datetime

# class MarketHours:
#     def __init__(self, start_time, end_time): # Initialize the class with the market's start and end times.
#         self.start_time = start_time  # Time when the market opens 
#         self.end_time = end_time  # Time when the market closes 

#     def is_market_open(self): # Check if the current time is within market hours.
#         now = datetime.now().time()  # Get the current time.
#         return self.start_time <= now <= self.end_time  # Return True if the current time is between start_time and end_time, otherwise False.