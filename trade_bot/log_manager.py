import os
import csv
import json
from datetime import datetime, timedelta


# ---------- Helpers ----------
def get_week_folder(log_type_folder):
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    week_folder_name = start_of_week.strftime('%d.%m.%Y')

    # Now include the master folder "weekly_logs"
    base_folder = os.path.join("weekly_logs", log_type_folder)
    full_path = os.path.join(base_folder, week_folder_name)

    os.makedirs(full_path, exist_ok=True)
    return full_path

def get_day_filename(extension):
    today = datetime.now()
    day_name = today.strftime('%A').lower()
    date_str = today.strftime('%d.%m.%Y')
    return f"{day_name}-{date_str}.{extension}"

# ---------- Log to TXT ----------
def log_to_file(message):
    folder = get_week_folder("weekly_log_txt")
    file_path = os.path.join(folder, get_day_filename("txt"))

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(file_path, 'a') as f:
        f.write(f"{timestamp} - {message}\n")

# ---------- Log to CSV ----------
def log_to_csv(data):
    folder = get_week_folder("weekly_log_csv")
    file_path = os.path.join(folder, get_day_filename("csv"))

    file_exists = os.path.isfile(file_path)
    with open(file_path, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

# ---------- Log to JSON ----------
def log_to_json(data):
    folder = get_week_folder("weekly_log_json")
    file_path = os.path.join(folder, get_day_filename("json"))

    all_data = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = []

    all_data.append(data)

    with open(file_path, 'w') as f:
        json.dump(all_data, f, indent=4)

# ---------- Master Function ----------
def log_and_notify(msg, log=True, console=True, csv_log=False, json_log=False, data=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_msg = f"{timestamp} - {msg}"

    if console:
        print(full_msg)

    if log:
        log_to_file(msg)

    if csv_log and data:
        log_to_csv(data)

    if json_log and data:
        log_to_json(data)

# ---------- Signal Log Builder ----------
def build_signal_log(debug_info, current_price, latest_ema, latest_sma, current_time):
    return {
        "timestamp": current_time,
        "current_low": debug_info["low_price"],
        "current_high": debug_info["high_price"],
        "current_ema": round(debug_info["current_ema"], 2),
        "current_sma": round(debug_info["current_sma"], 2),
        "prev_low": debug_info["previous_5min_low"],
        "prev_high": debug_info["previous_5min_high"],
        "prev_ema": round(debug_info["previous_5min_ema"], 2),
        "prev_sma": round(debug_info["previous_5min_sma"], 2),
        "current_price": round(current_price, 2),
        "latest_ema": round(latest_ema, 2),
        "latest_sma": round(latest_sma, 2),
        "ema_diff": debug_info["ema_diff_formatted"],
        "sma_diff": debug_info["sma_diff_formatted"]
    }
