from datetime import datetime
from telegram_message import send_telegram_message
from log_to_file import log_to_file
from broker_connection import BrokerConnection
from session_manager import SessionManager
from ib_insync import IB, Future, MarketOrder, Order, OrderStatus, StopOrder, StopLimitOrder, LimitOrder, Trade, Position



if __name__ == "__main__": 
    timestamp = datetime.now().strftime('%d-%m-%Y - %H:%M:%S')
    broker = BrokerConnection(host='127.0.0.1', port=7497, clientId=2)
    result = broker.check_market_hours()
    if result != "no change":
        send_telegram_message(f"{timestamp} - MESbot {result} to IB")
    contract = Future(symbol='MES', lastTradeDateOrContractMonth='20250620', exchange='CME')
    
    session_manager = SessionManager(broker.ib, contract)
    orders, brackets = session_manager.check_open_orders()
    for parent_id, prices in brackets.items():
        if prices["SellLimit"] and prices["SellStop"]:
            print(f"Bracket active: SellLimit {prices['SellLimit']} - SellStop {prices['SellStop']}")
        
        if prices["BuyLimit"] and prices["BuyStop"]:
            print(f"Bracket active: BuyLimit {prices['BuyLimit']} - BuyStop {prices['BuyStop']}")

        if prices["SellLimit"] and prices["StopLimitOrder"]:
            print(f"Bracket active: SellLimit {prices['SellLimit']} - SellStopLimit {prices['StopLimitOrder']}")

        if prices["BuyLimit"] and prices["StopLimitOrder"]:
            print(f"Bracket active: BuyLimit {prices['BuyLimit']} - BuyStopLimit {prices['StopLimitOrder']}")
         
    positions = session_manager.check_positions()
    if positions:
        for pos in positions:
            print(f"Position: {pos['symbol']}, Qty: {pos['position']}, Avg Cost: {pos['avg_cost']}")
    else:
        print("No open positions.")
    
    
            
    