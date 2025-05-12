
import random
from datetime import datetime
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from utils_collect_questions import click_easy_apply_if_exists
from utils_get_oferts import get_job_offers, parse_linkedin_job
from utils_login import linkedin_login
from utils_move import human_sleep, gentle_scroll, smart_scroll_jobs_list
from utils_next_page import go_to_next_page, close_easy_apply_modal_if_open, close_any_open_modals
from utils_save import *

driver = webdriver.Chrome()
linkedin_login(driver)

print("Login realizado correctamente.")
human_sleep(4, 7)

print("DEBUG: Accede manualmente a https://www.linkedin.com/jobs/collections/recommended")

# Guardar cookies después de login exitoso
COOKIES_FILE = "linkedin_cookies.pkl"
pickle.dump(driver.get_cookies(), open(COOKIES_FILE, "wb"))
print("Login realizado y cookies guardadas.")
human_sleep(4, 6)

jobs_data = []

while True:
    print("Scrolling page to load all job offers...")
    smart_scroll_jobs_list(driver)

    # Grab all job offers
    job_list = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container--clickable")
    print(f"Found {len(job_list)} job offers on this page.")

    human_sleep(1, 3)

    total_jobs = len(job_list)

    for idx, job in enumerate(job_list, start=1):
        if not job.is_displayed():
            gentle_scroll(driver, job)
            human_sleep(1, 2)

        try:
            ActionChains(driver).move_to_element(job).perform()
            human_sleep(0.5, 1.5)

            job.click()
            human_sleep(2, 4)

            job_details_html = driver.find_element(By.CSS_SELECTOR, "div.jobs-details__main-content").get_attribute('outerHTML')
            job_data = parse_linkedin_job(job_details_html)

            print(f"\tScraping job {idx}/{total_jobs}: {job_data['job']['title']}")
            human_sleep(0.5, 1.5)
            button_type, dict_info_back = click_easy_apply_if_exists(driver, job_id=job_data)
            print(dict_info_back)
            if button_type == "external":
                job_data['external_url'] = dict_info_back[0]
                job_data['external_html_path'] = dict_info_back[1]
            elif button_type == "simple":
                job_data['questions'] = dict_info_back
                save_questions_to_csv(job_data['job']['job_id'], dict_info_back)

            jobs_data.append(job_data)

        except Exception as click_err:
            if "element click intercepted" in str(click_err).lower():
                print("⚠️ Click intercepted — attempting to close modals.")
                close_any_open_modals(driver)
                human_sleep(1, 2)
                job.click()  # retry
            else:
                raise click_err
        except Exception as e:
            print(f"Error in job {idx}/{total_jobs}: {e}")
            human_sleep(2, 4)

        # Random longer pause every few jobs
        if idx % random.randint(4, 8) == 0 and idx > 0:
            print(f"\tTaking a short break after {idx} jobs...")
            human_sleep(5, 10)

    print("Finished scraping current page!")

    # Try to go to next page
    close_easy_apply_modal_if_open(driver)
    if not go_to_next_page(driver):
        print("No more pages left. Scraping completed.")
        break

# Save the final data
timestamp = datetime.now().strftime("%Y_%m_%d")
save_jobs_data_to_json(jobs_data )
save_jobs_data_to_csv(jobs_data )

print("Scraping Finished!")
print(jobs_data)

driver.quit()
