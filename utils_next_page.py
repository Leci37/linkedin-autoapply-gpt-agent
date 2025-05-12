import os
import time

from selenium.webdriver.common.by import By

from utils_move import human_sleep, scroll_and_click_element

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def go_to_next_page(driver):
    try:
        # Verifica si ya no hay más resultados útiles
        if "omitido en los resultados" in driver.page_source.lower() :
            print("⛔ Fin de resultados: hay empleos omitidos, END .")
            return False

        wait = WebDriverWait(driver, 10)
        active_page_li = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.artdeco-pagination__indicator--number.active.selected")))
        current_page = int(active_page_li.text.strip())
        print(f"\n\nCurrently on page {current_page}")
        next_page_number = current_page + 1

        # Paso 1: intentar ir directamente al número
        try:
            next_page_button = driver.find_element(By.CSS_SELECTOR, f"li[data-test-pagination-page-btn='{next_page_number}'] button")
            driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
            human_sleep(1, 2)
            next_page_button.click()
            human_sleep(3, 6)
        except NoSuchElementException:
            print("Botón de página siguiente no visible, intentando con último botón '...'")
            ellipsis_buttons = driver.find_elements(By.CSS_SELECTOR, "li.artdeco-pagination__indicator--ellipsis button")
            if not ellipsis_buttons:
                print("No hay botón '...' visible.")
                return False
            # Clic en el último botón ...
            last_ellipsis = ellipsis_buttons[-1]
            driver.execute_script("arguments[0].scrollIntoView();", last_ellipsis)
            human_sleep(1, 2)
            last_ellipsis.click()
            human_sleep(2, 4)

            # Reintentar clic en el botón del número de página
            next_page_button = driver.find_element(By.CSS_SELECTOR, f"li[data-test-pagination-page-btn='{next_page_number}'] button")
            driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
            human_sleep(1, 2)
            next_page_button.click()
            human_sleep(3, 6)

        # Verifica cambio de página
        new_active = driver.find_element(By.CSS_SELECTOR, "li.artdeco-pagination__indicator--number.active.selected")
        new_page = int(new_active.text.strip())
        if new_page == next_page_number:
            print(f"Moved to page {next_page_number}")
            return True
        else:
            print(f"Still on page {new_page}, expected {next_page_number}")
            return False

    except Exception as e:
        print(f"Error avanzando de página: {e}")
        return False


def close_easy_apply_modal_if_open(driver):
    """
    Closes the Easy Apply modal if it is currently open and blocking interactions.
    """
    try:
        modal_overlay = driver.find_element(By.CSS_SELECTOR, "div.artdeco-modal-overlay--is-top-layer")
        if modal_overlay.is_displayed():
            print("🧼 Closing modal overlay before clicking next page...")
            close_btn = driver.find_element(By.XPATH, "//button[@data-test-modal-close-btn]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", close_btn)
            time.sleep(0.5)
            close_btn.click()
            time.sleep(1.0)
    except Exception:
        pass  # Modal is likely not open, or already closed


from selenium.common.exceptions import NoSuchElementException

def close_any_open_modals(driver):
    """
    Closes LinkedIn modal overlays if they are open and blocking interaction.
    """
    try:
        # Close modal overlay (X button)
        close_btn = driver.find_element(By.XPATH, "//button[@data-test-modal-close-btn]")
        if close_btn.is_displayed():
            print("🧼 Closing modal overlay...")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", close_btn)
            time.sleep(0.3)
            close_btn.click()
            time.sleep(1)
    except NoSuchElementException:
        pass

    try:
        # Confirm discard modal
        discard_btn = driver.find_element(By.XPATH, "//button[@data-test-dialog-secondary-btn]")
        if discard_btn.is_displayed():
            print("🗑️ Confirming discard...")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", discard_btn)
            time.sleep(0.3)
            discard_btn.click()
            time.sleep(1)
    except NoSuchElementException:
        pass



#
# def click_review_and_submit(driver, job_data):
#     try:
#         review_btn = driver.find_element(By.XPATH, "//button//span[text()='Revisar']/parent::button")
#         scroll_and_click_element(driver, review_btn)
#         time.sleep(2)
#
#         submit_btn = driver.find_element(By.XPATH, "//button[span[text()='Enviar solicitud']]")
#         scroll_and_click_element(driver, submit_btn)
#         print("🚀 Submitted application.")
#
#         # Close confirmation if appears
#         time.sleep(2)
#         close_confirmation_if_present(driver)
#
#     except Exception as e:
#         print(f"⚠️ Error during submission: {e}")
#         # Save job_data safely
#         job_id = job_data['job'].get('job_id', 'unknown')
#         fallback_path = f"data/errors/failed_submission_{job_id}.json"
#         os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
#         with open(fallback_path, "w", encoding="utf-8") as f:
#             import json
#             json.dump(job_data, f, ensure_ascii=False, indent=2)
#         print(f"📁 Saved fallback job data to: {fallback_path}")


def try_click_review_and_submit(driver) -> bool:
    try:
        review_btn = driver.find_element(By.XPATH, "//button//span[text()='Revisar']/parent::button")
        scroll_and_click_element(driver, review_btn)
        time.sleep(2)

        submit_btn = driver.find_element(By.XPATH, "//button[span[text()='Enviar solicitud']]")
        scroll_and_click_element(driver, submit_btn)
        print("🚀 Submitted application.")

        time.sleep(2)
        close_confirmation_if_present(driver)
        return True

    except Exception as e:
        print(f"⚠️ Error during submission: {e}")
        return False


import os
import csv

def click_review_and_submit_and_log(driver, job_data, csv_path="data/submitted_jobs.csv"):
    success = try_click_review_and_submit(driver)

    job = job_data.get("job", {})
    company = job_data.get("company", {})

    row = {
        "job_id": job.get("job_id", ""),
        "title": job.get("title", ""),
        "company": company.get("name", ""),
        "location": job.get("location", ""),
        "modality": job.get("modality", ""),
        # "schedule": job.get("schedule", ""),
        "application_type": job.get("application_type", ""),
        "short_link": job.get("short_link", ""),
        "submitted": " YES" if success else " NO"
    }

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    write_header = not os.path.exists(csv_path)
    if not os.path.exists(csv_path):
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writeheader()
    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    if not success:
        job_id = row["job_id"] or "unknown"
        fallback_path = f"data/errors/failed_submission_{job_id}.json"
        with open(fallback_path, "w", encoding="utf-8") as f:
            import json
            json.dump(job_data, f, ensure_ascii=False, indent=2)
        print(f"📁 Saved fallback job data to: {fallback_path}")

    return success



def close_confirmation_if_present(driver):
    try:
        wait = WebDriverWait(driver, 5)
        close_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-test-modal-close-btn]"))
        )
        scroll_and_click_element(driver, close_btn)
        print("❎ Closed confirmation modal after submission.")
    except (TimeoutException, NoSuchElementException):
        pass

