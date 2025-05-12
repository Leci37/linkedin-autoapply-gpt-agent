from urllib.parse import urlparse
import time, os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import time

from utils_move import human_sleep


def find_and_click_next(driver, timeout=6):
    try:
        wait = WebDriverWait(driver, timeout)

        # Wait until the 'Siguiente' button appears
        next_button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//button//span[text()='Siguiente']/parent::button")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)

        # Then ensure it is clickable
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button//span[text()='Siguiente']/parent::button")))

        time.sleep(0.5)
        next_button.click()
        print("Clicked 'Siguiente' button.")
        time.sleep(1)
        return True

    except ElementClickInterceptedException:
        print("Click intercepted while trying to click 'Siguiente'. Retrying once...")
        try:
            time.sleep(1)
            next_button = driver.find_element(By.XPATH, "//button//span[text()='Siguiente']/parent::button")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            next_button.click()
            print("Clicked 'Siguiente' button after retry.")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Retry failed: {e}")
            return False

    except (TimeoutException, NoSuchElementException):
        print("No 'Siguiente' button found or not clickable.")
        return False


def is_review_button_present(driver):
    try:
        # WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.XPATH,  "//span[contains(text(), 'Revisar')]")))
        driver.find_element(By.XPATH,"//button//span[text()='Revisar']/parent::button")
        return True
    except NoSuchElementException:
        return False

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def collect_questions(driver):
    questions = []

    try:
        wait = WebDriverWait(driver, 5)

        # 1. Label-based questions (existing logic)
        label_elements = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//label[contains(@for, 'formElement')]"))
        )
        for elem in label_elements:
            text = elem.text.strip()
            if text:
                questions.append(text)

        # 2. Legend-based questions (e.g. radio groups)
        legend_elements = driver.find_elements(By.XPATH, "//fieldset//legend//span[1]")
        for legend in legend_elements:
            text = legend.text.strip()
            if text and text not in questions:
                questions.append(text)

    except TimeoutException:
        print("No questions found on this page.")
    except Exception as e:
        print(f"⚠️ Error in collect_questions: {e}")

    return questions

from unidecode import unidecode

def is_meaningless_answer(text):
    clean = unidecode(text.strip().lower())
    return clean in {"yes", "no", "si"}

def clean_questions(questions):
    seen = set()
    cleaned = []

    for q in questions:
        norm_q = q.strip()
        if not norm_q:
            continue

        if is_meaningless_answer(norm_q):
            continue

        if norm_q not in seen:
            seen.add(norm_q)
            cleaned.append(norm_q)

    return cleaned


from utils_move import gentle_scroll

def get_apply_button_and_type(driver):
    apply_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Solicit')]")
    for btn in apply_buttons:
        try:
            label = btn.text.strip().lower()
            if not btn.is_displayed():
                gentle_scroll(driver, btn)  # Scroll into view if not visible

            if "solicitud sencilla" in label:
                return btn, "simple"
            elif "solicitar" in label or "solicitud" in label:
                return btn, "external"
        except Exception as e:
            print(f"⚠️ Error checking apply button: {e}")
            continue
    return None, None

def handle_continue_popup(driver):
    try:
        # Esperar hasta 3s si aparece el botón "Continuar la solicitud"
        continue_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), 'Continuar la solicitud')]]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
        time.sleep(0.5)
        continue_button.click()
        print("🔄 Clicked 'Continuar la solicitud'.")
    except TimeoutException:
        a = 0

import re

def mentions_dotnet_stack(description: str) -> bool:
    """
    Devuelve True si el texto contiene referencias al stack de tecnologías .NET.
    """
    if not description:
        return False

    tech_keywords = [
        r"\b\.net\b", r"asp\.net", r"\bc#\b", r"visual basic", r"vb\.net",
        r"entity framework", r"blazor", r"winforms", r"wpf", r"mvc", r"razor",
        r"linq", r"ado\.net", r"dotnet core", r"\bnet core\b", r".net framework",
        r"\bmono\b", r"xamarin", r"maui"
    ]

    description = description.lower()
    return any(re.search(kw, description) for kw in tech_keywords)

import unicodedata

def normalize_city(text):
    return unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode().lower().strip()

def select_best_resume(driver, cities_available, force_dotnet=False, SimCity=None):
    """
    Selecciona el currículum adecuado según la ciudad (SimCity) o lista de ciudades.
    Detecta la ciudad ignorando mayúsculas y tildes.
    """
    suffix_dotnet = {"barcelona": "Cb", "madrid": "Cm", "vizcaya": "Cv"}
    suffix_standard = {"barcelona": "Pb", "madrid": "Pm", "vizcaya": "Pv"}

    suffix = "Cm" if force_dotnet else "Pm"  # default

    all_cities_text = " ".join(cities_available) if isinstance(cities_available, list) else str(cities_available)
    city_norm_target = normalize_city(SimCity or all_cities_text)

    for key in suffix_dotnet if force_dotnet else suffix_standard:
        if normalize_city(key) in city_norm_target:
            suffix = (suffix_dotnet if force_dotnet else suffix_standard)[key]
            break

    try:
        human_sleep(1.0, 1.6)
        resume_blocks = driver.find_elements(By.CSS_SELECTOR, "div.jobs-document-upload-redesign-card__container")
        resumes = []

        for block in resume_blocks:
            try:
                file_name_elem = block.find_element(By.CSS_SELECTOR, "h3.jobs-document-upload-redesign-card__file-name")
                file_name = file_name_elem.text.strip()

                is_selected = "jobs-document-upload-redesign-card__container--selected" in block.get_attribute("class")
                label_elem = block.find_element(By.CSS_SELECTOR, "label.jobs-document-upload-redesign-card__toggle-label")

                resumes.append({
                    "file": file_name,
                    "selected": is_selected,
                    "label": label_elem
                })
            except Exception as inner_e:
                print(f"❌ Error parsing resume block: {inner_e}")

        for resume in resumes:
            if resume["file"].endswith(f"_{suffix}.pdf"):
                if not resume["selected"]:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", resume["label"])
                    time.sleep(0.5)
                    resume["label"].click()
                    print(f"✅ CV seleccionado: {resume['file']}")
                else:
                    print(f"✅ Ya estaba seleccionado: {resume['file']}")
                return resume["file"]

        for resume in resumes:
            if resume["file"].endswith("_Cm.pdf"):
                if not resume["selected"]:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", resume["label"])
                    time.sleep(0.5)
                    resume["label"].click()
                    print(f"✅ CV por defecto seleccionado: {resume['file']}")
                else:
                    print(f"✅ Ya estaba seleccionado por defecto: {resume['file']}")
                return resume["file"]

    except Exception as e:
        print(f"⚠️ Error seleccionando currículum: {e}")

    return None


def is_CV_resume_required(driver):
    """
    Checks if the modal explicitly mentions an updated resume is required.
    Now supports detecting generic visible text rather than specific class names.
    """
    TARGET_PHRASES = [
        "asegúrate de incluir un currículum actualizado",
        "be sure to include an updated resume",
        "an updated resume is required"
    ]

    try:
        modal = driver.find_element(By.CSS_SELECTOR, "div.jobs-easy-apply-modal")
        spans = modal.find_elements(By.XPATH, ".//span | .//p | .//div")

        for span in spans:
            if not span.is_displayed():
                continue
            text = span.text.strip().lower()
            if any(phrase in text for phrase in TARGET_PHRASES):
                print(f"🟢 Resume requirement phrase found: {text}")
                return True
    except Exception as e:
        print(f"❌ Error detecting resume requirement: {e}")

    return False


def expand_more_resumes(driver):
    """
    Hace clic en el botón 'Mostrar más currículums' o 'Show more resumes' si está presente.
    Compatible con español e inglés.
    """
    try:
        expand_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜ', 'abcdefghijklmnopqrstuvwxyzáéíóúü'), 'mostrar') and contains(@aria-label, 'currículum')]"
            " | "
            "//button[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'show') and contains(@aria-label, 'resume')]"
        )

        for btn in expand_buttons:
            if btn.is_displayed() and btn.is_enabled():
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.5)
                btn.click()
                print("🔽 Se expandieron los currículums (es/en).")
                return True

        print("ℹ️ Botón de 'Mostrar/Show más currículums/resumes' no encontrado o no visible.")
    except (NoSuchElementException, ElementClickInterceptedException) as e:
        print(f"⚠️ Error al hacer clic en el botón de expansión: {e}")
    return False

def is_question_answered_in_form(driver, label_text):
    """
    Intenta asociar un texto de pregunta con un input/select visible y determinar si tiene valor pre-cargado.
    Ahora detecta correctamente valores por defecto como 'Select an option' y 'Selecciona una opción'.
    """
    try:
        # Normalizar texto de búsqueda
        label_text_norm = label_text.lower().strip()

        # Buscar labels visibles y ocultos
        label_candidates = driver.find_elements(By.XPATH, "//label")

        for label in label_candidates:
            full_text = label.text.strip().lower()
            spans = label.find_elements(By.TAG_NAME, "span")
            for span in spans:
                full_text += " " + span.text.strip().lower()

            if label_text_norm in full_text:
                input_id = label.get_attribute("for")
                if not input_id:
                    continue

                try:
                    field = driver.find_element(By.ID, input_id)
                    tag = field.tag_name.lower()

                    if tag == "input":
                        val = field.get_attribute("value")
                        if val and val.strip():
                            return True

                    elif tag == "select":
                        selected = field.get_attribute("value")
                        # Consider empty or default value as NOT answered
                        if selected and all(default not in selected.lower() for default in ["selecciona", "select an option"]):
                            return True

                except Exception as inner_e:
                    print(f"🔍 Error asociando input para label '{label_text}': {inner_e}")
    except Exception as outer_e:
        print(f"⚠️ Error evaluando pregunta '{label_text}': {outer_e}")

    return False


from utils_move import gentle_scroll  # Reuse your existing smooth scroll function

def get_input_element_for_question(driver, label_text):
    """
    Finds and returns the input/select/textarea/checkbox/radio element(s) associated with a question label or legend.
    Scrolls to the element if not visible.
    Returns a tuple: (WebElement or List[WebElement], type_string), or (None, None) if not found.
    """
    try:
        label_text_norm = label_text.lower().strip()

        # ====== [1] Try label-based ======
        label_candidates = driver.find_elements(By.XPATH, "//label")
        for label in label_candidates:
            full_text = label.text.strip().lower()
            spans = label.find_elements(By.TAG_NAME, "span")
            for span in spans:
                full_text += " " + span.text.strip().lower()

            if label_text_norm in full_text:
                input_id = label.get_attribute("for")
                if input_id:
                    try:
                        field = driver.find_element(By.ID, input_id)
                        # Scroll to field if not displayed
                        if not field.is_displayed():
                            gentle_scroll(driver, field)

                        tag = field.tag_name.lower()
                        input_type = field.get_attribute("type") or ""

                        if tag == "input":
                            if input_type == "radio":
                                return field, "radio"
                            elif input_type == "checkbox":
                                return field, "checkbox"
                            else:
                                return field, "input"
                        elif tag == "select":
                            return field, "select"
                        elif tag == "textarea":
                            return field, "textarea"
                        else:
                            return field, tag
                    except Exception as e:
                        print(f"⚠️ Could not locate field by ID '{input_id}' for label '{label_text}': {e}")

        # ====== [2] Legend-based (radio/checkbox groups) ======
        fieldsets = driver.find_elements(By.XPATH, "//fieldset")
        for fieldset in fieldsets:
            try:
                legend = fieldset.find_element(By.TAG_NAME, "legend")
                legend_text = legend.text.strip().lower()

                if label_text_norm in legend_text:
                    inputs = fieldset.find_elements(By.XPATH, ".//input[@type='radio' or @type='checkbox']")
                    if inputs:
                        if not inputs[0].is_displayed():
                            gentle_scroll(driver, inputs[0])
                        input_type = inputs[0].get_attribute("type")
                        return inputs, f"group_{input_type}"
            except Exception:
                continue

    except Exception as outer_e:
        print(f"❌ Error locating element for question '{label_text}': {outer_e}")

    return None, None



def get_format_error_message(driver, input_element):
    """
    Looks for a validation error message linked to the given input element.
    Returns the message text or None.
    """
    try:
        describedby_id = input_element.get_attribute("aria-describedby")
        if describedby_id:
            error_box = driver.find_element(By.ID, describedby_id)
            message_elem = error_box.find_element(By.CSS_SELECTOR, "span.artdeco-inline-feedback__message")
            error_text = message_elem.text.strip()
            return error_text if error_text else None
    except Exception:
        return None



from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

def fill_in_answer(driver, element, el_type, answer, question_text):
    """
    Fills the given answer into the form field based on element type.
    Prints format errors if found.
    """
    try:
        if el_type in ["input", "textarea"]:
            element.clear()
            element.send_keys(answer)
            human_sleep(0.3, 0.6)
            element.send_keys(Keys.TAB)  # Trigger validation

        elif el_type == "select":
            select = Select(element)
            matched = False
            for option in select.options:
                if answer.lower().strip() in option.text.lower().strip():
                    select.select_by_visible_text(option.text.strip())
                    matched = True
                    break
            if not matched:
                print(f"⚠️ Could not find matching dropdown option for: {answer}")

        elif el_type in ["radio", "checkbox"]:
            # TODO: implement logic to match and click appropriate input
            print(f"⚠️ Checkbox/Radio logic not yet implemented for: '{question_text}'")

        # Check for validation error after input
        error_message = get_format_error_message(driver, element)
        if error_message:
            print(f"❌ Format error after answering '{question_text}': {error_message}")
            return error_message

    except Exception as e:
        print(f"❌ Error while filling answer for '{question_text}': {e}")
        return e
    return None

ADDRESS_KEYWORDS = [
    # Street / Address lines
    "State",
    "Street",
    "Street address",
    "Street address line 1",
    "Street address line 2",
    "Address line 1",
    "Address line 2",
    "Address",
    "Mailing address",
    "Delivery address",
    "Home address",
    "Work address",
    "P.O. Box",
    "PO Box",
    "Apartment",
    "Unit",
    "Suite",
    "Building",
    "Flat",
    "Block",
    "Floor",
    "Room",
    "House number",
    "Street name",
    "Road",
    "Avenue",
    "Boulevard",
    "Lane",
    "Drive",
    "Court",
    "Terrace",
    "Place",
    "Way",
    "Plaza",
    "Town square",
    "Intersection",

    # City / Locality
    "City",
    "Town",
    "Village",
    "Locality",
    "Municipality",
    "Borough",
    "Suburb",
    "Neighborhood",
    "District",
    "Urban area",
    "CityCity",  # Possibly a duplication or error—retained for pattern reference

    # State / Province
    "State",
    "Province",
    "Region",
    "Territory",
    "County",
    "Prefecture",
    "Canton",
    "Emirate",
    "Administrative area",
    "Department",

    # Postal codes
    "ZIP code",
    "ZIP / Postal Code",
    "Postal code",
    "Postcode",
    "PIN code",
    "CEP",
    "PLZ",
    "CAP",
    "ZIP",
    "CP"

    # International variants (examples of common field labels)
    "Código Postal",  # Spanish
    "Codigo Postal",
    "Code Postal",  # French
    "Postleitzahl",  # German
    "Codice Postale",  # Italian
    "郵便番号",  # Japanese
    "Почтовый индекс",  # Russian
    "우편 번호",  # Korean
    "رمز بريدي",  # Arabic

    # Generic
    "Location",
    "Geolocation",
    "Address info",
    "Place"
]



import unicodedata

import unicodedata

def normalize_text(txt):
    return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode().lower().strip()

def select_radio_by_label_text(driver, group_element, target_label_text):
    """
    Clicks the label with matching text inside a radio group (fieldset block).
    Uses accent-insensitive, case-insensitive comparison.
    """
    norm_target = normalize_text(target_label_text)

    try:
        # Re-fetch fresh labels to avoid stale element exceptions
        labels = group_element.find_elements(By.CSS_SELECTOR, "label[data-test-text-selectable-option__label]")

        for label in labels:
            label_text = normalize_text(label.text)
            if norm_target in label_text or label_text in norm_target:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
                driver.execute_script("arguments[0].click();", label)
                print(f"✅ Selected radio option via label: {label.text.strip()}")
                return True

        print(f"❌ No matching radio label found for: {target_label_text}")
    except Exception as e:
        print(f"❌ Failed to click radio label: {e}")

    return False



import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from unicodedata import normalize
from selenium.common.exceptions import NoSuchElementException

def normalize_text(txt):
    return normalize("NFKD", txt).encode("ASCII", "ignore").decode().lower().strip()

def select_dropdown_option_by_label(driver, question_text, answer_text):
    """
    Finds a dropdown (select) by matching the label with the question text,
    and selects the option matching the answer_text.
    """

    try:
        norm_question = normalize_text(question_text)
        norm_answer = normalize_text(answer_text)

        # Step 1: Find label associated with the <select>
        labels = driver.find_elements(By.XPATH, "//label[@for]")
        select_id = None

        for label in labels:
            label_full_text = label.text.strip()
            # Also include nested span text
            spans = label.find_elements(By.TAG_NAME, "span")
            for span in spans:
                label_full_text += " " + span.text.strip()

            if normalize_text(label_full_text).startswith(norm_question):
                select_id = label.get_attribute("for")
                break

        if not select_id:
            print(f"❌ No matching label found for question: {question_text}")
            return False

        # Step 2: Fresh <select> element
        select_el = driver.find_element(By.ID, select_id)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_el)
        time.sleep(0.4)  # simulate natural delay
        select = Select(select_el)

        # Step 3: Attempt exact match
        for option in select.options:
            opt_text = normalize_text(option.text)
            if opt_text == norm_answer:
                select.select_by_visible_text(option.text.strip())
                print(f"✅ Selected dropdown option: {option.text.strip()}")
                return True

        # Step 4: Attempt partial match
        for option in select.options:
            opt_text = normalize_text(option.text)
            if norm_answer in opt_text or opt_text in norm_answer:
                select.select_by_visible_text(option.text.strip())
                print(f"✅ Fuzzy-selected dropdown option: {option.text.strip()}")
                return True

        print(f"❌ No matching option found for: {answer_text}")
        return False

    except NoSuchElementException:
        print(f"❌ Dropdown element not found for question: {question_text}")
    except Exception as e:
        print(f"❌ Failed to select dropdown option: {e}")
    return False

from selenium.webdriver.common.by import By
import time

from utils_move import gentle_scroll

COVER_LETTER_KEYWORDS = [
    # English
    "cover letter", "upload cover letter", "attach cover letter", "add cover letter",
    "covering letter", "motivation letter", "upload motivation letter",
    # Spanish
    "carta de presentación", "adjuntar carta", "añadir carta", "cargar carta",
    "subir carta de presentación", "cargar carta de motivación", "subir carta de motivación"
]

def click_cover_letter_upload_if_present(driver):
    """
    Finds and clicks the upload label for the cover letter input if it exists.
    Matches keywords in both English and Spanish.
    """
    try:
        labels = driver.find_elements(By.XPATH, "//label")
        for label in labels:
            full_text = label.text.strip().lower()
            spans = label.find_elements(By.TAG_NAME, "span")
            for span in spans:
                full_text += " " + span.text.strip().lower()

            if any(keyword in full_text for keyword in COVER_LETTER_KEYWORDS):
                gentle_scroll(driver, label)
                time.sleep(0.5)
                label.click()
                print(f"📎 Clicked cover letter upload: '{label.text.strip()}'")
                return True

    except Exception as e:
        print(f"⚠️ Could not interact with cover letter upload button: {e}")

    print("ℹ️ No cover letter upload found.")
    return False



def is_salary_question(text):
    text = text.lower()
    salary_keywords = [
        "salary", "salary expectations", "expected salary", "desired salary",
        "expected remuneration", "remuneration", "income", "wage",
        "salario","salarial", "sueldo", "remuneración", "expectativas salariales", "ingresos", "expectativas económicas"
    ]
    return any(kw in text for kw in salary_keywords)