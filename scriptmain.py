import os
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
# List of varied messages
messages = [
    """Leave your message here""" ,
    
    """Leave your message here""",
    
    """Leave your message here""",
    
    """Leave your message here""",
    
    """Leave your message here"""
]

# Settings
MAX_PAGES = 50  # Change to the desired number of pages
WAIT_BETWEEN_ACTIONS = (1, 3)  # Range of random wait in seconds

# Driver initialization
service = Service(ChromeDriverManager().install())
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 15)

def random_wait():
    time.sleep(random.uniform(*WAIT_BETWEEN_ACTIONS))

try:
    # Login
    driver.get("https://www.linkedin.com/login/")
    driver.maximize_window()
    
    wait.until(EC.visibility_of_element_located((By.ID, "username"))).send_keys(os.getenv("EMAIL"))
    driver.find_element(By.ID, "password").send_keys(os.getenv("PASSWORD"))
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    # Search
    search_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[role='combobox']")))
    search_box.send_keys("Lawyer" + Keys.RETURN)
    random_wait()

    # People Filter
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'People')]"))).click()
    random_wait()

    # Loop through pages
    for current_page in range(1, MAX_PAGES + 1):
        print(f"\n--- Processing Page {current_page} ---")
        
        # Load profiles
        profiles = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@data-view-name, 'search-entity-result-universal-template')]"))
        )
        
        # Process each profile
        for profile in profiles:
            try:
                connect_button = profile.find_element(By.XPATH, ".//button[contains(.,'Connect') or contains(.,'Follow')]")
                print("Button found:", connect_button.text)
                
                if "Connect" == connect_button.text:
                    user_message = random.choice(messages)
                    connect_button.click()
                    random_wait()
                    
                    # Connection modal
                    add_note = wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(.,'Add a note')]")))
                    
                    # Add note
                    add_note.find_element(By.XPATH, "//button[contains(.,'Add a note')]").click()
                    random_wait()
                    
                    # Message
                    textarea = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "custom-message")))
                    textarea.send_keys(user_message)
                    random_wait()
                    
                    # Send
                    add_note = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(.,'Send')]")))
                    add_note.click()
                    random_wait()
                    
                elif "Follow" == connect_button.text:
                    connect_button.click()
                    wait.until(EC.staleness_of(connect_button))
                    random_wait()
                    
            except Exception as e:
                print(f"Error in profile: {str(e)}")
                continue

        # Page change
        if current_page < MAX_PAGES:
            try:
                next_page_selector = f"li[data-test-pagination-page-btn='{current_page + 1}'] > button"
                next_page = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, next_page_selector))
                )
                next_page.click()
                
                # Wait for new page to load
                wait.until(EC.staleness_of(profiles[0]))
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-view-name='search-entity-result-universal-template']")))
                random_wait()
                
            except Exception as e:
                print(f"Could not change to page {current_page + 1}: {str(e)}")
                

finally:
    driver.quit()