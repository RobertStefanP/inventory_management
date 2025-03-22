import threading
from ib_insync import Order, StopOrder, LimitOrder, StopLimitOrder
from datetime import datetime
from log_to_file import log_to_file



class SessionManager:
    def __init__(self, ib, contract):
        self.ib = ib 
        self.contract = contract 
        self.open_orders = [] 
        self.open_positions = [] 
        self.checking_for_signals_mode = False 
        self.monitoring_opened_orders_mode = False 
        self.update_event = threading.Event()  
               
    def update_modes(self):
        if self.open_orders or self.open_positions: 
            self.monitoring_orders_mode = True 
            return "open orders found"
        else:  
            self.monitoring_orders_mode = False 
            return "no open orders found"
                    
    def check_open_orders(self, initial_check=False): 
        try:
            self.open_orders.clear()  
            self.ib.reqAllOpenOrders()  
            open_trades = self.ib.openOrders()     
            self.open_orders = []
            brakets = {}      
                                                   
            for trade in open_trades:                 
                if isinstance(trade, (Order, StopOrder, LimitOrder, StopLimitOrder)): 
                    order = trade  
                    contract = self.contract   
                else:
                    order = trade.order 
                    contract = trade.contract    
                                                                               
                if (contract.symbol == self.contract.symbol and
                    contract.lastTradeDateOrContractMonth == self.contract.lastTradeDateOrContractMonth and
                    contract.exchange == self.contract.exchange):                
                    self.open_orders.append(order) 
                                      
                    if order.parentId and order.parentId != 0:  
                        braket_id = order.parentId  
                        if braket_id not in brakets:  
                            brakets[braket_id] = {"SellLimit": None, "SellStop": None, "BuyLimit": None, "BuyStop": None, "StopLimitOrder": None}                                
                        if order.action == "BUY":  
                            if order.orderType == "LMT":
                                brakets[braket_id]["BuyLimit"] = order.lmtPrice
                            elif order.orderType == "STP":
                                brakets[braket_id]["BuyStop"] = order.auxPrice
                            elif order.orderType == "STP LMT":  
                                brakets[braket_id]["StopLimitOrder"] = order.auxPrice

                        elif order.action == "SELL":  
                            if order.orderType == "LMT":
                                brakets[braket_id]["SellLimit"] = order.lmtPrice
                            elif order.orderType == "STP":
                                brakets[braket_id]["SellStop"] = order.auxPrice
                            elif order.orderType == "STP LMT":  
                                brakets[braket_id]["StopLimitOrder"] = order.auxPrice        
            self.update_modes() 
            return self.check_open_orders, brakets                                                
        except Exception as e:  
            return [], {}, f"Error in check_open_orders: {e}"
            
    def check_positions(self):
        self.open_positions.clear()
        self.ib.reqPositions()
        positions = self.ib.positions()

        self.open_positions = [
            pos for pos in positions
            if pos.contract.symbol == self.contract.symbol and
            pos.contract.lastTradeDateOrContractMonth == self.contract.lastTradeDateOrContractMonth
        ]
        position_details = []

        for pos in self.open_positions:
            avg_cost_adjusted = pos.avgCost / float(pos.contract.multiplier)
            rounded_avg_cost = round(avg_cost_adjusted * 4) / 4
            formatted_avg_cost = f"{rounded_avg_cost:.2f}"

            position_details.append({
                "symbol": pos.contract.symbol,
                "position": pos.position,
                "avg_cost": formatted_avg_cost
            })
        self.update_modes()
        
        return position_details


    