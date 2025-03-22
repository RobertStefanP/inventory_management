from datetime import datetime
from ib_insync import util
import pandas as pd


class DataHandler:
    def __init__(self, ib, contract):        
        self.ib = ib  
        self.contract = contract  
        self.first_run = True  
        self.daily_bars_details = []  

    def fetch_historical_data(self, duration, bar_size, what_to_show):         
        bars = self.ib.reqHistoricalData(
            self.contract,  
            endDateTime='',  
            durationStr=duration,  
            barSizeSetting=bar_size,  
            whatToShow=what_to_show,  
            useRTH=False,  
            formatDate=1)  
        return util.df(bars) if bars else None

    def calculate_indicators(self, fetched_data): 
        if fetched_data is not None and not fetched_data.empty:  
            
            fetched_data['midpoint'] = (fetched_data['high'] + fetched_data['low']) / 2  
            fetched_data['EMA'] = fetched_data['midpoint'].ewm(span=10, adjust=False).mean().round(2) 
            fetched_data['SMA'] = fetched_data['midpoint'].rolling(window=20).mean().round(2)  
            
            fetched_data['EMA'] = fetched_data['EMA'].round(2) 
            fetched_data['SMA'] = fetched_data['SMA'].round(2) 
            
            current_price = fetched_data['close'].iloc[-1]  
            latest_ema = fetched_data['EMA'].iloc[-1]  
            latest_sma = fetched_data['SMA'].iloc[-1]  
                                  
            return fetched_data, current_price, latest_ema, latest_sma  
        else:
            return None, None, None, None  

    def calculate_dailybars_detail(self, fetched_data): 
        if fetched_data is not None and not fetched_data.empty:
            fetched_data['date'] = pd.to_datetime(fetched_data['date']) 
            today = datetime.now().date()  
            today_bars = fetched_data[fetched_data['date'].dt.date == today] 

            if today_bars.empty:  
                return self.daily_bars_details  

            if self.first_run: 
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
                self.first_run = False  

            else:  
                last_row = today_bars.iloc[-1]  
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
        return self.daily_bars_details 