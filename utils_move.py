import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def human_sleep(a=1.5, b=3.5):
    time.sleep(random.uniform(a, b))

def gentle_scroll(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
    human_sleep(0.5, 1.5)


import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def smart_scroll_jobs_list(driver, scroll_pause_time=1.5, max_scrolls=100):
    print("Locating the jobs list container...")

    # Locate the job list container using a stable selector
    try:
        job_list_container = driver.find_element(By.CSS_SELECTOR, "#main > div > div.scaffold-layout__list-detail-inner.scaffold-layout__list-detail-inner--grow > div.scaffold-layout__list > div")
    except Exception as e:
        print(f"Could not locate the job list container: {e}")
        return

    last_height = driver.execute_script("return arguments[0].scrollHeight", job_list_container)

    # Scroll DOWN
    for i in range(max_scrolls):
        print(f"Scrolling down iteration {i+1}...")

        # Scroll down a page
        job_list_container.send_keys(Keys.PAGE_DOWN)
        time.sleep(random.uniform(0.3, 0.6))

        # Occasionally scroll up a little
        if random.random() < 0.1:
            job_list_container.send_keys(Keys.PAGE_UP)
            time.sleep(random.uniform(0.4, 0.8))

        # Try to click "Jump to..." buttons if they appear
        try:
            jump_buttons = driver.find_elements(By.CSS_SELECTOR, "button.scaffold-layout__list-jump-button")
            for btn in jump_buttons:
                if btn.is_displayed() and btn.is_enabled():
                    print("Clicking jump button to load more results...")
                    btn.click()
                    time.sleep(random.uniform(1.5, 2.5))
        except:
            pass

        time.sleep(random.uniform(scroll_pause_time - 0.5, scroll_pause_time + 0.5))

        new_height = driver.execute_script("return arguments[0].scrollHeight", job_list_container)

        if new_height == last_height:
            print(f"Scrolling down stopped after {i+1} scrolls (no new content loaded).")
            break

        last_height = new_height

    # Final deep scroll to bottom
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", job_list_container)
    time.sleep(2)
    print("Finished scrolling down.")

    # Small pause before scrolling UP
    time.sleep(1)

    # Scroll UP slowly (simulate user reviewing jobs)
    print("Starting to scroll UP through the list...")
    for _ in range(10):  # 10 times PageUp
        job_list_container.send_keys(Keys.PAGE_UP)
        time.sleep(random.uniform(0.5, 0.8))

    print("Finished scrolling up.")


from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
from utils_move import gentle_scroll, human_sleep

def scroll_and_click_element(driver, element, retries=2):
    """
    Scrolls into view and clicks a WebElement or the first in a list of WebElements.
    Handles most edge cases and retries if needed.

    Returns:
        True if clicked successfully, False otherwise.
    """
    if element is None:
        print("⚠️ No element provided.")
        return False

    # If a list is passed, get the first non-null visible element
    if isinstance(element, list):
        element = next((el for el in element if isinstance(el, WebElement) and el.is_displayed()), None)
        if element is None:
            print("⚠️ No visible element in the list.")
            return False

    if not isinstance(element, WebElement):
        print(f"⚠️ Invalid element type: {type(element)}")
        return False

    for attempt in range(retries):
        try:
            if not element.is_displayed():
                print("⚠️ Element is not visible.")
                return False

            if not element.is_enabled():
                print("⚠️ Element is not enabled.")
                return False

            gentle_scroll(driver, element)
            human_sleep(0.2, 0.5)

            # First try regular click
            element.click()
            human_sleep(0.3, 0.7)
            return True

        except ElementClickInterceptedException:
            print("⚠️ Click intercepted — retrying with JS click...")
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as js_err:
                print(f"❌ JS click failed: {js_err}")

        except StaleElementReferenceException:
            print("⚠️ Stale element — cannot interact.")
            return False

        except Exception as e:
            print(f"❌ Unexpected error clicking element: {e}")

        human_sleep(0.5, 1.0)  # Wait before retry

    print("❌ Failed to click element after retries.")
    return False



def safe_click_element(driver, element):
    from utils_move import human_sleep, gentle_scroll

    if isinstance(element, list):
        if not element:
            print("⚠️ Lista vacía de elementos, no se puede hacer clic.")
            return False
        element = element[0]  # usar el primero

    try:
        gentle_scroll(driver, element)
        element.click()
        human_sleep(0.3, 0.7)
        return True
    except Exception as e:
        print(f"❌ Error al hacer clic en el elemento: {e}")
        return False