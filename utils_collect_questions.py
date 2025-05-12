from urllib.parse import urlparse
import time, os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from GPT_Assistant_utils import Get_answerGPT_for_question, Get_answerGPT_for_radio_group, get_answer_for_dropdown
from utils_collect_questions_Utils import *
from utils_cover_leter import generate_cover_letter_text, save_cover_letter_to_doc, upload_cover_letter
from utils_move import human_sleep, scroll_and_click_element, safe_click_element
from utils_next_page import  click_review_and_submit_and_log


def handle_external_apply(driver, button, job_id):
    original_tabs = driver.window_handles
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
    time.sleep(0.5)
    button.click()
    handle_continue_popup(driver)
    time.sleep(2)

    new_tabs = driver.window_handles
    if len(new_tabs) > len(original_tabs):
        new_tab = [tab for tab in new_tabs if tab not in original_tabs][0]
        driver.switch_to.window(new_tab)
        time.sleep(2)

        url = driver.current_url
        domain = urlparse(url).netloc.replace("www.", "")
        os.makedirs("Data/solicitud_external", exist_ok=True)
        file_path = f"Data/solicitud_external/{domain}_{job_id}.html"

        html_content = driver.page_source
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"🌐 Guardado HTML desde {url} → {file_path}")

        driver.close()
        driver.switch_to.window(original_tabs[0])
    else:
        print("❌ No se abrió nueva pestaña.")
    return (url, file_path)


from GPT_Assistant import LuisAssistant
from utils_chat_send_question import classify_question, normalize_question

# Inicializa el asistente globalmente (puedes moverlo donde se inicialice mejor)
assistant = LuisAssistant(api_key_path="chatGPT/agente.txt")

import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CACHE_PATH = "data/response_cache/CACHE_answered_questions_linke.csv"

# Load cached answers
if os.path.exists(CACHE_PATH):
    cache_df = pd.read_csv(CACHE_PATH)
    cached_answers = dict(zip(cache_df["Question"], cache_df["Answer"]))
else:
    cache_df = pd.DataFrame(columns=["Question", "Type", "Answer"])
    cached_answers = {}

def append_to_cache(question, qtype, answer):
    global cache_df, CACHE_PATH
    if question not in cached_answers:
        new_row = pd.DataFrame([[question, qtype, answer]], columns=["Question", "Type", "Answer"])
        cache_df = pd.concat([cache_df, new_row], ignore_index=True)
        cache_df.to_csv(CACHE_PATH, index=False)
        cached_answers[question] = answer
        print(f"💾 Cached answer: {question}")

def handle_cv_upload(driver, job_data, cities_available):
    if is_CV_resume_required(driver):
        expand_more_resumes(driver)
        full_description = job_data['job']['full_description']
        force_dotnet = mentions_dotnet_stack(full_description)
        if force_dotnet:
            print("✅ El currículum menciona .NET.")
        selected = select_best_resume(driver, cities_available, force_dotnet)
        print(f"📄 CV seleccionado: {selected}")

def handle_cover_letter_upload(driver, job_data):
    if click_cover_letter_upload_if_present(driver):
        print("📎 Uploading cover letter...")
        cl_text = generate_cover_letter_text(job_data, assistant)
        cl_path = save_cover_letter_to_doc(
            cl_text,
            job_data['job']['job_id'],
            job_data['company']['name']
        )
        upload_cover_letter(driver, cl_path)

def handle_radio_or_select(driver, q, el_type, element):
    if el_type == "group_radio":
        selected_label = Get_answerGPT_for_radio_group(q, element, assistant)
        if selected_label:
            success = select_radio_by_label_text(
                driver,
                group_element=driver.find_element(
                    By.XPATH, "//fieldset[contains(@id, 'radio-button-form-component')]"
                ),
                target_label_text=selected_label
            )
            if not success:
                print(f"⚠️ Could not click matching radio for answer: {selected_label}")
        return True

    elif el_type == "select":
        try:
            options = [opt.text.strip() for opt in element.find_elements(By.TAG_NAME, "option")]
            selected_label = get_answer_for_dropdown(q, options, assistant)
            if selected_label:
                success = select_dropdown_option_by_label(driver, q, selected_label)
                if not success:
                    print(f"⚠️ Could not click matching dropdown option for answer: {selected_label}")
        except Exception as e:
            print(f"❌ Failed processing dropdown question: {e}")
        return True

    return False

def handle_easy_apply(driver, button, job_data):
    cities_available = job_data['job']['cities_available']
    all_questions = {}

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
    time.sleep(0.5)
    button.click()
    handle_continue_popup(driver)
    print("🟢 Clicked 'Solicitud sencilla' button.")

    max_passes = 6
    for _ in range(max_passes):
        time.sleep(1)

        questions = collect_questions(driver)
        questions = clean_questions([normalize_question(q) for q in questions])

        # Upload CV and cover letter
        handle_cv_upload(driver, job_data, cities_available)
        handle_cover_letter_upload(driver, job_data)

        # Answer questions
        for q in questions:
            element, el_type = get_input_element_for_question(driver, q)
            if not element:
                print(f"❌ No input element found for: {q}")
                continue

            if is_question_answered_in_form(driver, q):
                print(f"⚪ Pregunta ya respondida en el formulario: {q}")
                continue

            scroll_and_click_element(driver, element)
            safe_click_element(driver, element)
            human_sleep(0.3, 0.7)

            # Handle radio and dropdown questions
            if handle_radio_or_select(driver, q, el_type, element):
                continue

            # Text-based input fields
            if is_salary_question(q):
                answer = "30500"
                print(f"💰 Overriding salary-related question with: {answer}")
            elif q in cached_answers:
                answer = cached_answers[q]
                print(f"📄 Using cached answer: {q}")
            else:
                qtype = classify_question(q)
                answer = Get_answerGPT_for_question(q, qtype, assistant, cities_available)
                append_to_cache(q, qtype, answer)

            all_questions[q] = answer
            error_msg = fill_in_answer(driver, element, el_type, answer, q)

            if error_msg:
                print(f"🔁 Retrying due to format error: {error_msg}")
                qtype = classify_question(q)
                retry = Get_answerGPT_for_question(q, qtype, assistant, cities_available, error_msg)
                all_questions[q] = retry
                append_to_cache(q, qtype, retry)
                fill_in_answer(driver, element, el_type, retry, q)

        if is_review_button_present(driver):
            print("✅ Reached 'Revisar' step.")
            click_review_and_submit_and_log(driver, job_data, csv_path="data/errors/_submitted_jobs.csv")
            break

        if not find_and_click_next(driver):
            print("➡️ No more 'Siguiente' button, stopping.")
            break

    try:
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-test-modal-close-btn]"))
        )
        scroll_and_click_element(driver, close_button)
        print("❎ Closed modal.")
    except Exception as close_err:
        print(f"⚠️ Failed to close modal: {close_err}")

    try:
        discard_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Descartar') or contains(., 'Rule out')]")
        ))
        scroll_and_click_element(driver, discard_button)
        print("🗑️ Clicked 'Descartar'.")
    except Exception as discard_err:
        print(f"⚠️ Failed to click 'Descartar': {discard_err}")

    return all_questions







def click_easy_apply_if_exists(driver, job_id):
    try:
        button, button_type = get_apply_button_and_type(driver)
        if not button or not hasattr(button, 'is_displayed'):
            print("❌ No se encontró ningún botón de solicitud o no es válido.")
            return {},None

        if button_type == "external":
            return button_type, handle_external_apply(driver, button, job_id['job']['job_id'])
        elif button_type == "simple":
            return button_type, handle_easy_apply(driver, button, job_id)

    except (NoSuchElementException, TimeoutException):
        print("No 'Solicitud' button found.")
    # except Exception as e:
    #     print(f"🚨 Unexpected error: {e}")

    return {},None



