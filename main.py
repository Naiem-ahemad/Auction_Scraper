import shutil
import Scraper.Scraper
import Scraper.Calendar_scraper
import Scraper.Calendar_scraper
import auction_merger.test_merger
import auction_merger.Auction_merger
from   datetime import datetime, timedelta



yesterday = datetime.now() - timedelta(days=1)
AUCTION_DATE = yesterday.strftime("%m/%d/%Y")
FOLDER_NAME = AUCTION_DATE.replace("/", "-")


# a_test = Scraper.Calendar_scraper.main()
# r = Scraper.Scraper.main()
# m = auction_merger.Auction_merger.main()
shutil.rmtree(f'{FOLDER_NAME}')
def safe_rmtree(path):
    try:
        shutil.rmtree(path)
        print(f"[✓] Removed: {path}")
    except FileNotFoundError:
        print(f"[-] Not found: {path}")
    except Exception as e:
        print(f"[✗] Error removing {path}: {e}")

folders_to_remove = [
    'auction_merger/__pycache__',
    'Scraper/__pycache__',
    'database/__pycache__',
    '__pycache__',
]

for folder in folders_to_remove:
    safe_rmtree(folder)

