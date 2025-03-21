import time
from datetime import datetime
from ib_insync import IB
from log_to_file import log_to_file
from telegram_message import send_telegram_message


class BrokerConnection:
    def __init__(self, host, port, clientId):
        self.host = host
        self.port = port
        self.clientId = clientId
        self.ib = IB()  
    
    def connect(self):
        """ Connect to the Interactive Brokers TWS or IB Gateway. """
        attempt = 0        
        while True:
            try:
                self.ib.connect(self.host, self.port, clientId=self.clientId)
                return "connected"                  
              
            except Exception as e:
                attempt += 1              
                if attempt % 10 == 0:  
                    return f"failed after {attempt} attempts: {e}"                           
                time.sleep(10) 
         
    def disconnect(self):
        """ Disconnect from IB. """
        if self.ib.isConnected():
            self.ib.disconnect()
            return "disconnected"
        return "already disconnected"

    def check_market_hours(self):
        """ Check if the market is open. """
        now = datetime.now().time()
        start = now.replace(hour=0, minute=5, second=0, microsecond=0)
        end = now.replace(hour=22, minute=55, second=0, microsecond=0)

        if start  <= now <= end:
            if not self.ib.isConnected():
                return self.connect()
        else:
            if self.ib.isConnected():
                return self.disconnect()  
        
        return "no change"  
    