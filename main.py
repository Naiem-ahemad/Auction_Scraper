import os
import shutil
import time
import Scraper.Scraper
import Scraper.Calendar_scraper
import auction_merger.Auction_merger
from datetime import datetime, timedelta
import requests

BOT_TOKEN = "7882864628:AAEuxABTPagC9EnhFkKlmtI-oVMj92xiNJA"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})

def send_document(chat_id, file_path):
    with open(file_path, "rb") as f:
        url = f"{API_URL}/sendDocument"
        response = requests.post(
            url,
            data={"chat_id": chat_id},
            files={"document": f}
        )
    return response.status_code == 200

def safe_rmtree(path):
    try:
        shutil.rmtree(path)
        print(f"[✓] Removed: {path}")
    except FileNotFoundError:
        print(f"[-] Not found: {path}")
    except Exception as e:
        print(f"[✗] Error removing {path}: {e}")

def cleanup():
    yesterday = datetime.now() - timedelta(days=1)
    folder_name = yesterday.strftime("%m-%d-%Y").replace("/", "-")

    folders_to_remove = [
        folder_name,
        'auction_merger/__pycache__',
        'Scraper/__pycache__',
        'database/__pycache__',
        '__pycache__',
    ]

    for folder in folders_to_remove:
        safe_rmtree(folder)

def run_scraping():
    Scraper.Calendar_scraper.main()
    Scraper.Scraper.main()
    auction_merger.Auction_merger.main()

def get_merged_filename():
    yesterday = datetime.now() - timedelta(days=1)
    folder_name = yesterday.strftime("%m/%d/%Y").replace("/", "-")
    return f"merged_{folder_name}.xlsx"

def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        return resp.json()
    else:
        return None

def main():
    print("[*] Bot started. Waiting for messages...")
    last_update_id = None

    while True:
        updates = get_updates(last_update_id + 1 if last_update_id else None)
        if updates and "result" in updates:
            for item in updates["result"]:
                last_update_id = item["update_id"]
                message = item.get("message")
                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text.lower() == "/start":
                    send_message(chat_id, "Starting scraping and merging. Please wait...")

                    try:
                        run_scraping()
                        merged_file = get_merged_filename()
                        if os.path.exists(merged_file):
                            sent = send_document(chat_id, merged_file)
                            if sent:
                                send_message(chat_id, "Here is the merged Excel file ✅")
                            else:
                                send_message(chat_id, "Failed to send the file.")
                        else:
                            send_message(chat_id, "Merged file not found. Something went wrong.")
                    except Exception as e:
                        send_message(chat_id, f"Error during scraping: {e}")

                    cleanup()
        time.sleep(2)  # small delay to prevent flooding

if __name__ == "__main__":
    main()
