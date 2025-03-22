import os
from datetime import datetime
from datetime import timedelta

def log_to_file(message):
    # Determine the start of the current week (Monday)
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Calculate Monday of the current week
    week_start_str = start_of_week.strftime('%Y-%m-%d')  # Format the week start date
    
    # Define the WeeklyLog folder path
    folder_name = 'WeeklyLog'
    if not os.path.exists(folder_name):  # Ensure the folder exists
        os.makedirs(folder_name)
    
    # Define the log file path for the current week
    log_file_path = os.path.join(folder_name, f'Log_{week_start_str}.txt')
    
    # Append the message to the weekly log file
    timestamp = today.strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file_path, 'a') as f:
        f.write(f"{timestamp} - {message}\n")