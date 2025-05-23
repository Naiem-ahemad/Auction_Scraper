import pytz
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def check_auction_yesterday(url, driver):
    # IST timezone
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    yesterday = now_ist - timedelta(days=1)

    # Format date to match aria-label e.g. "May-31-2025"
    yesterday_str = yesterday.strftime("%B-%d-%Y")  # Month-fullname-Day-Year

    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # Wait for calendar container to load
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "CALDAYBOX")))

    # If today is 1st day, click Previous Month button
    if now_ist.day == 1:
        try:
            prev_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "CALPREV")))
            prev_btn.click()
            # Wait for calendar to reload (you may adjust timeout)
            wait.until(EC.staleness_of(prev_btn))
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "CALDAYBOX")))
        except TimeoutException:
            print("Could not click Previous Month button or it didn't load properly.")

    # Find all day boxes
    day_boxes = driver.find_elements(By.CSS_SELECTOR, "div.CALBOX.CALW5")

    yesterday_box = None
    for box in day_boxes:
        aria_label = box.get_attribute("aria-label")
        if aria_label == yesterday_str:
            yesterday_box = box
            break

    if not yesterday_box:
        print(f"Date {yesterday_str} not found in calendar on page: {url}")
        return False

    # Check for presence of <span class="CALTEXT"> with <span class="CALMSG"> inside
    try:
        caltext = yesterday_box.find_element(By.CLASS_NAME, "CALTEXT")
        calmsg = caltext.find_element(By.CLASS_NAME, "CALMSG")
        # If found, auction data is available
        return True
    except NoSuchElementException:
        # If CALTEXT or CALMSG not found, no auction data for that day
        return False
def main():
    from selenium import webdriver
    from database.calendar_database import URLS  # your county URLs
    
    driver = webdriver.Chrome()  # or your get_driver()

    results = []
    for county, url in URLS.items():
        print(f"Checking {county}...")
        available = check_auction_yesterday(url, driver)
        results.append({"County": county, "Available": available})

    driver.quit()

    import pandas as pd
    df = pd.DataFrame(results)

    yesterday = datetime.now(pytz.timezone('Asia/Kolkata')) - timedelta(days=1)
    filename = yesterday.strftime("availability_of_%m-%d-%Y") + ".xlsx"
    df.to_excel(filename, index=False)
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()
