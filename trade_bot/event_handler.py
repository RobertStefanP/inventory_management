import json
import time
from ib_insync import IB #(BEFORE it was this "*" but it was changed to "IB" to avoid confusion)
from datetime import datetime
from colorama import init, Fore, Style # For colored and styled terminal output

# Initialize colorama
init(autoreset=True)
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=0)  # Use clientId=0 for the master connection
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Get the current timestamp
print(f"{current_time} - Connected to IB") # Confirm connection
order_position_status_file = 'order_position_status.json'  # JSON file to log order and position updates
contract_multipliers = {'MNQ': 0.5,'MES': 0.5} # Define the contract multipliers

last_logged_status = {} # Dictionary to keep track of last logged status for each order ID

def write_status_to_file(status_data):
    """Append order/position status data to the JSON file."""
    with open(order_position_status_file, 'a') as f:
        f.write(json.dumps(status_data) + '\n') # Convert data to JSON and append to the file

def log_to_file(message):
    """Log generic messages to a text file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Get the current timestamp
    with open('trading_bot_output.txt', 'a') as f: # Open the log file in append mode
        f.write(f"{timestamp} - {message}\n") # Append the message with a timestamp

def adjust_price(symbol, price):
    """Adjust the price based on the contract symbol's multiplier."""
    if symbol in ['MNQ', 'MES']: # Only adjust for specific symbols
        return price / 2  # Divide by 2 for the defined multipliers
    return price # Return the original price if no adjustment is needed

def log_open_order(trade):
    """Log details of an open order."""
    order = trade.order  # Extract order details
    status = trade.orderStatus  # Extract order status
    contract = trade.contract  # Extract contract details
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get the current timestamp
    print(f"{current_time} - log_open_order called for {contract.symbol} with status {status.status}")
    
    # Check if the status is the same as the last logged status for this order ID
    if order.orderId in last_logged_status and last_logged_status[order.orderId] == status.status:
        return  # Skip logging if the status hasn't changed
    
    # Update the last logged status for this order ID
    last_logged_status[order.orderId] = status.status
    
    # Ignore statuses that are not relevant
    if status.status not in ['Submitted', 'Filled', 'Cancelled']:  # Filter out irrelevant statuses
        return
    
    # Log all orders but filter the print based on status
    status_data = {
        "time": current_time,
        "type": "order",
        "symbol": contract.symbol,
        "secType": contract.secType,
        "expiry": contract.lastTradeDateOrContractMonth,
        "action": order.action,
        "orderType": order.orderType,
        "quantity": order.totalQuantity,
        "status": status.status,
        "filled": status.filled,
        "remaining": status.remaining,
        "lmtPrice": getattr(order, 'lmtPrice', None),  # Get limit price if available
        "auxPrice": getattr(order, 'auxPrice', None),  # Get stop price if available
        "id": order.orderId,  # Add order ID to status data
    }

    write_status_to_file(status_data)  # Write the status data to the JSON file
    log_to_file(f"Order {status.status}: {contract.symbol} {contract.secType} {contract.lastTradeDateOrContractMonth}, "
                f"Action: {order.action}, Order Type: {order.orderType}, Quantity: {order.totalQuantity}, "
                f"Filled: {status.filled}, Remaining: {status.remaining}, "
                f"LMT Price: {getattr(order, 'lmtPrice', 'N/A')}, STP Price: {getattr(order, 'auxPrice', 'N/A')}, "
                f"Order ID: {order.orderId}")

    # Filter out PreSubmitted status
    if status.status not in ['Submitted', 'Filled', 'Cancelled']:
        return

    # Determine color and style
    color = Fore.WHITE
    style = Style.NORMAL
    if status.status == 'Filled':
        if order.orderType == 'STP':
            color = Fore.RED
            style = Style.BRIGHT
        elif order.orderType == 'LMT':
            color = Fore.GREEN
            style = Style.BRIGHT
        elif order.orderType == 'STP LMT':  # Stop limit orders in bright red
            color = Fore.RED
            style = Style.BRIGHT
    elif status.status == 'Cancelled':
        if order.orderType == 'LMT':
            color = Fore.GREEN
            style = Style.NORMAL
        elif order.orderType == 'STP':
            color = Fore.RED
            style = Style.NORMAL
        elif order.orderType == 'STP LMT':  # Stop limit orders in normal red
            color = Fore.RED
            style = Style.NORMAL

    # Print status with color and style
    print(f"{style}{color}{current_time} - Order {status.status}: {contract.symbol} {contract.secType} {contract.lastTradeDateOrContractMonth}")
    print(f"{style}{color}Action: {order.action}, Order Type: {order.orderType}, Quantity: {order.totalQuantity}")
    print(f"{style}{color}Filled: {status.filled}, Remaining: {status.remaining}")
    if order.orderType == 'LMT':
        print(f"{style}{color}LMT Price: {order.lmtPrice}")
    if order.orderType == 'STP':
        print(f"{style}{color}STP Price: {order.auxPrice}")
    if order.orderType == 'STP LMT':  # Print stop limit prices
        print(f"{style}{color}STP LMT Stop Price: {order.auxPrice}, Limit Price: {order.lmtPrice}")
    print(f"{style}{color}{'-' * 50}")

    
def log_position_update(position):
    contract = position.contract  # Extract contract details
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Get the current timestamp
    avgCost = adjust_price(contract.symbol, position.avgCost) # Adjust average cost if necessary
    
    position_data = {
        "time": current_time,
        "type": "position",
        "symbol": contract.symbol,
        "secType": contract.secType,
        "expiry": contract.lastTradeDateOrContractMonth,
        "position": position.position,
        "avgCost": avgCost
    }
    log_to_file(f"Position Update: {contract.symbol} {contract.secType} {contract.lastTradeDateOrContractMonth}," 
                f"Position: {position.position}, Avg Cost: {avgCost}")    

# Request current open orders and positions at startup
def process_initial_state():
    """Log all open orders and positions at startup."""
    open_orders = ib.reqAllOpenOrders() # Request all active orders
    for order  in open_orders: 
        log_open_order(order) # Log each open order

    positions = ib.positions() # Request all current positions
    for position in positions:
        log_position_update(position) # Log each position

# Request auto open orders
ib.reqAutoOpenOrders(True) # Master Client id 0 needed for requesting and receving ALL statuses updates and orders
ib.reqAllOpenOrders()
ib.openTrades()
ib.openOrders()

# Set up event handlers
ib.orderStatusEvent += log_open_order
ib.newOrderEvent += log_open_order
ib.orderModifyEvent += log_open_order
ib.cancelOrderEvent += log_open_order
ib.openOrderEvent += log_open_order
ib.positionEvent += log_position_update
print(f"{current_time} - Event handlers registered")
process_initial_state()

# Main logic
try:
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{current_time} - Monitoring for open orders/positions...")
    ib.run()
except KeyboardInterrupt:
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{current_time} - Disconnecting...")
    ib.disconnect()

    