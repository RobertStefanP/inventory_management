import datetime

class DataHandler:
    """Calculating indicators"""
    def __init__(self, ib, contract):
        # Initialize the class with an IB connection and a trading contract.
        self.ib = ib  # IB connection object to fetch data from Interactive Brokers.
        self.contract = contract  # The trading instrument/contract (e.g., futures or stocks).
        self.first_run = True  # A flag to check if initial data has already been printed.
        self.daily_bars_details = []  # Initialize the list

    def fetch_historical_data(self, duration, bar_size, what_to_show): # Fetch historical data for the given contract and parameters.        
        bars = self.ib.reqHistoricalData(
            self.contract,  # The trading contract for which data is fetched.
            endDateTime='',  # Use the latest available data.
            durationStr=duration,  # Duration of historical data (e.g., '2 D' for 2 days).
            barSizeSetting=bar_size,  # Bar size (e.g., '5 mins' for 5-minute bars).
            whatToShow=what_to_show,  # Type of data to retrieve (e.g., 'MIDPOINT', 'TRADES').
            useRTH=False,  # Include data outside regular trading hours (RTH).
            formatDate=1)  # Format the dates in the returned data. 

        return util.df(bars) if bars else None

    def calculate_indicators(self, data): # Calculate EMA and SMA indicators based on historical data.
        if data is not None and not data.empty:  # Check if the data exists and is not empty.
            
            data['midpoint'] = (data['high'] + data['low']) / 2  # Calculate the midpoint price for each bar (average of high and low).
            data['EMA'] = data['midpoint'].ewm(span=10, adjust=False).mean().round(2)  # Calculate the 10-period Exponential Moving Average (EMA) of the midpoint.
            data['SMA'] = data['midpoint'].rolling(window=20).mean().round(2)  # Calculate the 20-period Simple Moving Average (SMA) of the midpoint.
            
            data['EMA'] = data['EMA'].round(2) # Round EMA to 2 decimals
            data['SMA'] = data['SMA'].round(2) # Round SMA columns to 2 decimals
            
            current_price = data['close'].iloc[-1]  # Get the most recent closing price from the data.
            latest_ema = data['EMA'].iloc[-1]  # Get the latest EMA value.
            latest_sma = data['SMA'].iloc[-1]  # Get the latest SMA value. 
                                  
            return data, current_price, latest_ema, latest_sma  # # Return data and calculated values.
        else:
            return None, None, None, None  # Return None to indicate no indicators could be calculated.

    def calculate_dailybars_detail(self, historical_data, indicators): # For printing the bars from the minute 00:00 of the day
        if indicators is None or indicators.empty:  
            return self.daily_bars_details  # Return stored list if no indicators
        
        if historical_data is not None and not historical_data.empty:
            historical_data['date'] = pd.to_datetime(historical_data['date'])  # Convert date column to datetime format
            today = datetime.now().date()  # Get today's date
            today_bars = historical_data[historical_data['date'].dt.date == today] # Filter today's data

            if today_bars.empty:  
                return self.daily_bars_details  # No new data, return existing list

            if self.first_run:  # If bot is starting, store all today's data
                for _, row in today_bars.iterrows():
                    self.daily_bars_details.append({
                        "date": row['date'],
                        "open": row['open'],
                        "high": row['high'],
                        "low": row['low'],
                        "close": row['close'],
                        "midpoint": row['midpoint'],
                        "EMA": row['EMA'],
                        "SMA": row['SMA'],
                    })
                self.first_run = False  # Set first_run to False after storing all today's data

            else:  # If bot is running, only add the latest bar
                last_row = today_bars.iloc[-1]  # Get only the last row
                if not self.daily_bars_details or last_row['date'] != self.daily_bars_details[-1]['date']:
                    self.daily_bars_details.append({
                        "date": last_row['date'],
                        "open": last_row['open'],
                        "high": last_row['high'],
                        "low": last_row['low'],
                        "close": last_row['close'],
                        "midpoint": last_row['midpoint'],
                        "EMA": last_row['EMA'],
                        "SMA": last_row['SMA'],
                    })        
        return self.daily_bars_details  # Return updated list