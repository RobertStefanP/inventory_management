import datetime
from log_to_file import log_to_file


class TradeExecution:
    """Manage the process of placing trades and handling bracket orders."""
    def __init__(self, ib, contract, session_manager, json_reader, timing_manager):
        self.ib = ib  # IB connection object for interacting with the broker.
        self.contract = contract  # The trading instrument (e.g., futures or stocks).
        self.session_manager = session_manager  # Manages session states (e.g., monitoring open orders).
        self.json_reader = json_reader  # Reads and manages JSON data for order status.
        self.timing_manager = timing_manager  # Manages timing for order placement.
        
    def place_bracket_order(self, current_price, signal_type):
        """Place a bracket order with stop loss and take profit."""
        current_time = datetime.now().strftime('%H:%M:%S')  # Get the current time
        if not current_price:
            log_to_file(f"{current_time} - No current price provided for bracket order placement.")
            print(f"{current_time} - No current price provided for bracket order placement.")
            return

        # Calculate Stop Loss and Take Profit
        sl = current_price - 3 if signal_type == 'bullish' else current_price + 3
        tp = current_price + 5 if signal_type == 'bullish' else current_price - 5

        # Parent order
        parent_order = MarketOrder('BUY' if signal_type == 'bullish' else 'SELL', 1)
        parent_order.transmit = False # Do not transmit immediately
        
        # Place the parent order first
        self.ib.placeOrder(self.contract, parent_order) # Place the parent order first to get the parent ID
        time.sleep(1)  # Allow time for IB to assign an order ID
        
        if parent_order.orderId == 0:
            log_to_file(f"{current_time} - Error: Parent Order ID not assigned. Aborting bracket order placement.")
            print(f"{current_time} - Error: Parent Order ID not assigned. Aborting bracket order placement.")
            return
        
        # Delegate stop-loss decision to TimingManager
        stop_loss_order = self.timing_manager.stoploss_type(signal_type, sl)
        stop_loss_order.parentId = parent_order.orderId
        stop_loss_order.transmit = False
        
        # Take Profit order
        take_profit_order = LimitOrder('SELL' if signal_type == 'bullish' else 'BUY', 1, tp)
        take_profit_order.parentId = parent_order.orderId # Link to parent
        take_profit_order.transmit = True  # Finalize and transmit the chain   
        take_profit_order.outsideRth = True # Enable trigger outside RTH 

        # Place orders
        self.ib.placeOrder(self.contract, stop_loss_order)
        self.ib.placeOrder(self.contract, take_profit_order)
        
        # Enable monitoring mode and disable signal checking mode
        session_manager.monitoring_opened_orders_mode = True
        session_manager.checking_for_signals_mode = False
        log_to_file(f"{current_time} - Bracket order placed successfully with SL at {sl} and TP at {tp}")
        print(f"{current_time} - Bracket order placed successfully with SL at {sl} and TP at {tp}")