"""MES bot"""
import requests
from colorama import Fore, Style

def send_telegram_message(message, color=None):
    if color:
        print(color + message + Style.RESET_ALL)  # Print with color
    else:
        print(message)  # Print without color
        
    # Send to Telegram
    BOT_TOKEN = '7185156146:AAHb-8PmZV-ug4nnqehWQbrEAIojWdSAT6E'
    CHAT_ID = '1543472864'
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=payload)

# Example usage
if __name__ == '__main__':
    send_telegram_message("This message should appear in both the terminal and Telegram.")
    