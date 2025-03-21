import datetime
import json
from colorama import init, Fore, Style
from log_to_file import log_to_file

class JsonEventsReader:
    def __init__(self, session_manager, status_file='order_position_status.json'):  # Initialize with update reader and session manager
        self.session_manager = session_manager  # Store session manager instance
        self.status_file = status_file  # Store the status file name in wich the updates will be written
        self.json_reader_thread = None  # Initialize JSON reader thread
        self.last_processed_time = None  # Track the last processed update time
        self.last_processed_id = None  # Initialize last_processed_id
        self.stop_reader = False  # Flag to stop the JSON reader
        self.existing_ids = set()  # Initialize the set to track existing IDs
        self.lock = threading.Lock() # To lock methods
        self.update_event = threading.Event()  # Event to signal updates
        self.displayed_update_ids = set()  # Set to keep track of displayed update IDs
                    
    def start_json_reader(self):  # Method to start the JSON reader thread
        current_time = datetime.now().strftime('%H:%M:%S')  # Get the current time as a string  
        if not self.json_reader_thread or not self.json_reader_thread.is_alive():  # Check if thread is not running
            self.stop_reader = False  # Ensure the flag is reset before starting the thread
            self.json_reader_thread = threading.Thread(target=self.json_reader)  # Create new thread for JSON reader
            self.json_reader_thread.start()  # Start the thread
        else:
            log_to_file(f"{current_time} - Json reader running.") # Log that the thread is already active
            print(f"{current_time} - Json reader running.") # Log that the thread is already active
    
    def stop_json_reader(self):  # Method to set the flag to stop the JSON reader
        self.stop_reader = True # Set the stop_reader flag to True to terminate the loop in `json_reader`
                
    def read_status_from_file(self): # Method to read updates from the JSON file
        updates = []  # Initialize an empty list to store updates
        try:
            with open(self.status_file, 'r') as f:  # Open the status file in read mode
                updates = [json.loads(line) for line in f]  # Read each line, parse JSON, and add to updates list
        except FileNotFoundError: # Handle case where file does not exist
            pass  # Do nothing if file is not found
        return updates  # Return the list of updates 
    
    def display_update(self, update):  # Method to display updates        
        current_time = datetime.now().strftime('%H:%M:%S')  # Get the current time as a string                
        if update['type'] == 'order' and 'status' in update:  # Check if update is an order and has 'status' key
            order_status = update  # Get the order status
                       
            if order_status['status'] == 'Cancelled': # Skip processing canceled orders
                return                     
            if order_status['id'] in self.displayed_update_ids: # Check if the update ID has already been displayed
                return 
                       
            self.displayed_update_ids.add(order_status['id']) # Add the update ID to the set after displaying it
                        
            color = Fore.WHITE # Determine color and style
            style = Style.NORMAL            
            if order_status['status'] in ['Filled']:  # Highlight filled orders
                if order_status['orderType'] == 'STP':  # For stop orders
                    color = Fore.RED  # Use red color for stop orders
                    style = Style.BRIGHT  # Bright style for better visibility
                elif order_status['orderType'] == 'LMT':  # For limit orders
                    color = Fore.GREEN  # Use green color for limit orders
                    style = Style.BRIGHT  # Bright style for better visibility
                elif order_status['orderType'] == 'STP LMT':  # For stop limit orders
                    color = Fore.RED  # Use yellow color for stop limit orders
                    style = Style.BRIGHT  # Bright style for better visibility
                      
            # Print order details 
            log_to_file(f"{current_time} - Order {order_status['status']}: {order_status['symbol']} {order_status['secType']} {order_status['expiry']}")                   
            print(style + color + f"\n{current_time} - Order {order_status['status']}: {order_status['symbol']} {order_status['secType']} {order_status['expiry']}")
            log_to_file(f"{current_time} - Action: {order_status['action']}, Order Type: {order_status['orderType']}, Quantity: {order_status['quantity']}")
            print(style + color + f"Action: {order_status['action']}, Order Type: {order_status['orderType']}, Quantity: {order_status['quantity']}")
            log_to_file(f"{current_time} - Filled: {order_status['filled']}, Remaining: {order_status['remaining']}")
            print(style + color + f"Filled: {order_status['filled']}, Remaining: {order_status['remaining']}")

            if order_status['orderType'] == 'LMT':  # Print limit price if order type is limit
                log_to_file(f"{current_time} - LMT Price: {order_status['lmtPrice']}")
                print(style + color + f"LMT Price: {order_status['lmtPrice']}")
            elif order_status['orderType'] == 'STP':  # Print stop price if order type is stop
                log_to_file(f"{current_time} - STP Price: {order_status['auxPrice']}")
                print(style + color + f"STP Price: {order_status['auxPrice']}")
            elif order_status['orderType'] == 'STP LMT':  # Print stop limit prices
                log_to_file(f"{current_time} - STP LMT Stop Price: {order_status['auxPrice']}, Limit Price: {order_status['lmtPrice']}")
                print(style + color + f"STP LMT Stop Price: {order_status['auxPrice']}, Limit Price: {order_status['lmtPrice']}")
            print(style + color + "-" * 50)
                                                                       
    def clear_trade_data(self):  # Method to clear the json file after updates have been read
        updates = self.read_status_from_file()  # Read updates from file        
        filtered_updates = [update for update in updates if update['symbol'] != 'MES'] # Filter out updates related to the current contract symbol and ID
        with open(self.status_file, 'w') as f:  # Write back only the filtered updates
            for update in filtered_updates: # Iterate over the filtered updates
                f.write(json.dumps(update) + '\n') # Write each update as a JSON line   
                 
    def json_reader(self):  # Method to continuously read updates from JSON file  
        start_time = datetime.now()  # Record the start time   
        while not self.stop_reader:  # Loop will stop if stop_reader is True            
            try: 
                with self.session_manager.iteration_lock:  # Ensure lock is held when checking for updates                               
                    updates = self.read_status_from_file() # Read updates from the JSON file
                    relevant_updates = [update for update in updates # Filter updates for relevant conditions
                                    if update['symbol'] == 'MES' # Ensure the update symbol matches
                                    and 'status' in update # Check that 'status' key exists
                                    and update['status'] in ['Filled', 'Cancelled'] # Focus on filled or canceled statuses
                                    and datetime.strptime(update['time'], '%Y-%m-%d %H:%M:%S') > start_time] # Ensure update is recent                   
                
                    if relevant_updates:        # If there are relevant updates   
                        self.last_processed_time = max(datetime.strptime(update['time'], '%Y-%m-%d %H:%M:%S') for update in relevant_updates) # Update the last processed time
                        self.last_processed_id = relevant_updates[-1]['id'] # Update the last processed ID            
                  
                        for update in relevant_updates: # Display each relevant update
                            self.display_update(update) # Call display_update to log the details
                                                                    
                        self.clear_trade_data()  # Clear the data from JSON file after updates are displayed                          
                        self.session_manager.checking_for_signals_mode = True # Enable signal checking mode
                        self.session_manager.monitoring_opened_orders_mode = False # Disable monitoring mode                                                                                                
                        self.session_manager.update_event.set()   # Trigger the event to signal updates
                                        
                        # Call stop_json_reader() after modes are updated
                        if self.session_manager.checking_for_signals_mode: # Stop reader if signal checking is active
                            self.stop_json_reader()
                            break                                                                                                                                        
                    else:
                        log_to_file(f"{datetime.now().strftime('%H:%M:%S')} - Active orders, waiting.....")
                        print(f"{datetime.now().strftime('%H:%M:%S')} - Active orders, waiting.....") # Log that no relevant updates are found  

            except Exception as e:
                log_to_file(f"Error in json_reader: {e}") # Log any exception that occurs
                print(f"Error in json_reader: {e}") # Log any exception that occurs                        
            time.sleep(30) # Sleep for 30 seconds before the next iteration