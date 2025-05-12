from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import os
import pickle
import re

# Load data
csv_path = "data/jobs_data_2025_05_05.csv"
df = pd.read_csv(csv_path)
paths = df['external_url'].dropna().unique()

# Keywords to match (extended to include Spanish and synonyms)
KEYWORDS = ["apply", "postul", "applicat", "start", "inscribirme", "enviar solicitud", "solicitar", "postularme"]
PATTERN = re.compile(r"(" + "|".join(KEYWORDS) + ")", re.IGNORECASE)

# Cookies file
COOKIES_FILE = "linkedin_cookies.pkl"

def linkedin_login(driver):
    driver.get("https://www.linkedin.com/")
    time.sleep(2)

    if os.path.exists(COOKIES_FILE):
        print("Cargando cookies guardadas...")
        cookies = pickle.load(open(COOKIES_FILE, "rb"))
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception:
                pass
        driver.refresh()
        time.sleep(3)

# Set up Selenium WebDriver (with GUI for debugging)
options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
service = Service()
driver = webdriver.Chrome(service=service, options=options)
actions = ActionChains(driver)

linkedin_login(driver)

form_data = []

for idx, row in df.iterrows():
    url = row['external_url']
    job_id = row['job_job_id']
    try:
        # Ensure only one tab is open
        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        print(f"Visiting: {url}")
        driver.get(url)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(2)

        elements = driver.find_elements(By.XPATH, "//*[self::button or self::a or self::input[@type='submit'] or self::span]")
        found = False

        for elem in elements:
            try:
                full_text = elem.get_attribute("textContent") or ""
                full_text = full_text.strip()

                if any(kw.lower() in full_text.lower() for kw in KEYWORDS):
                    print("  Found:", full_text)
                    clickable = elem
                    for _ in range(5):
                        if clickable.tag_name.lower() in ['a', 'button', 'input']:
                            break
                        try:
                            clickable = clickable.find_element(By.XPATH, "parent::*")
                        except NoSuchElementException:
                            break

                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'})", clickable)
                    time.sleep(1.5)

                    is_visible = driver.execute_script("""
                        const rect = arguments[0].getBoundingClientRect();
                        return (
                            rect.top >= 0 &&
                            rect.left >= 0 &&
                            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                        );
                    """, clickable)

                    if is_visible:
                        actions.move_to_element(clickable).perform()
                        time.sleep(0.5)
                        clickable.click()
                        time.sleep(4)

                        form_elements = driver.find_elements(By.XPATH, "//label | //input | //textarea | //select")
                        for fe in form_elements:
                            try:
                                label = driver.execute_script("return arguments[0].innerText", fe).strip()
                                placeholder = fe.get_attribute("placeholder")
                                name = fe.get_attribute("name")
                                if label or placeholder or name:
                                    question = label or placeholder or name
                                    form_data.append({"job_job_id": job_id, "question": question})
                            except Exception:
                                continue
                        found = True
                        break
            except StaleElementReferenceException:
                continue

        if not found:
            print("  No relevant buttons found on page.")

    except Exception as e:
        print(f"Error visiting {url}: {e}")

# Clean up
driver.quit()

# Save form data
form_df = pd.DataFrame(form_data)
form_df.to_csv("data/solicitud_external_form.csv", index=False)



# Define a function that cleans the 'question' column in the entire DataFrame
def clean_questions(df):
    if 'question' not in df.columns:
        raise ValueError("DataFrame must contain a 'question' column")

    series = df['question'].dropna().drop_duplicates()

    # Remove entries beginning with "questi" (case-insensitive)
    series = series[~series.str.lower().str.startswith("questi")]

    # Remove entries containing any of these characters: [, ], @, _
    series = series[~series.str.contains(r"[\[\]@_]", regex=True)]

    # Remove entries containing 4 hexadecimal characters separated by a dash (GUID format)
    series = series[~series.str.contains(r"\b[a-fA-F0-9]{4}-[a-fA-F0-9]{4}\b")]

    # Remove entries containing URLs
    series = series[~series.str.contains(r"http[s]?://|www\.", regex=True)]

    # Remove entries with fewer than 4 or more than 250 characters
    series = series[series.str.len().between(4, 250)]

    # Remove entries beginning with an underscore
    series = series[~series.str.startswith("_")]

    # Remove rows where any word is longer than 14 characters
    series = series[~series.str.split().apply(lambda words: any(len(word) > 14 for word in words))]

    # Remove rows where digits outnumber letters
    series = series[~series.apply(lambda x: sum(c.isdigit() for c in x) > sum(c.isalpha() for c in x))]

    # Clean unwanted characters:
    series = (
        series
        .str.replace(r'[\t\n\\]', '', regex=True)
        .str.replace(r'\*', '', regex=True)
        .str.replace(r'[\xa0\u200b\u202f\u00a0]', '', regex=True)
    )

    # Replace the cleaned 'question' column in the original DataFrame
    cleaned_df = df.copy()
    cleaned_df = cleaned_df[df.index.isin(series.index)]
    cleaned_df['question'] = series.reset_index(drop=True)

    cleaned_df = cleaned_df.dropna()

    return cleaned_df.reset_index(drop=True)
# Apply the cleaning function
df_clean  = clean_questions(form_df)

# Save the cleaned DataFrame
df_clean.to_csv("data/ext_solicitud_external_form.csv", index=False)
print(df_clean.head())
print(form_df.head())
