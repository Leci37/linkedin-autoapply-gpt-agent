import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
from GPT_Assistant import LuisAssistant
from utils_get_oferts import WORDS_JOB_APLICATION, PALABRAS_SOLICITUD_EMPLEO


# === Config ===
api_key_path = "chatGPT/agente.txt"  # Update to your actual path
assistant = LuisAssistant(api_key_path)

# Load external URLs
df = pd.read_csv("data/jobs_data_2025_05_05.csv")
urls = df['external_url'].dropna().unique()

# Headless browser setup
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

results = {}

for idx, url in enumerate(urls, 1):
    try:
        print(f"[{idx}/{len(urls)}] Visiting {url}")
        driver.get(url)
        time.sleep(3)

        html = driver.page_source[:12000]  # send trimmed HTML to avoid token limits
        prompt = (
            "Extract all job application questionnaire questions from the HTML below. "
            "Return the result as a JSON array of question strings only. "
            "Skip descriptions or job details.\n\n"
            f"{html}"
        )
        result_json_str = assistant.ask(prompt)

        try:
            result_json = json.loads(result_json_str)
            results[url] = result_json
        except json.JSONDecodeError:
            results[url] = {"error": "Failed to parse response as JSON", "raw": result_json_str}

    except Exception as e:
        print(f"❌ Error with {url}: {e}")
        results[url] = {"error": str(e)}

driver.quit()

# Save
with open("data/questionnaires_extracted.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("✅ Extraction completed and saved to 'questionnaires_extracted.json'")
