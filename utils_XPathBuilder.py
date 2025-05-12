from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
import os
import json

# Palabras clave de botón tipo solicitud
from utils_get_oferts import WORDS_JOB_APLICATION, PALABRAS_SOLICITUD_EMPLEO

# Leer CSV
df = pd.read_csv("data/jobs_data_2025_05_05.csv")
paths = df['external_html_path'].dropna().unique()

available_files = {path: path for path in paths if os.path.exists(path)}
output_form_path = "data/solicitud_external_form"
os.makedirs(output_form_path, exist_ok=True)

form_extracted = {}

def build_xpath(tag, soup, tag_type=""):
    # Preferencia por atributos estables
    if tag.has_attr("id"):
        return f"//*[@id='{tag['id']}']"
    if tag.has_attr("name"):
        return f"//*[@name='{tag['name']}']"
    for attr in ["placeholder", "aria-label", "type"]:
        if tag.has_attr(attr):
            return f"//{tag.name}[contains(@{attr}, '{tag[attr]}')]"

    # Fallback: posición del elemento entre sus hermanos
    same_tags = soup.find_all(tag.name)
    index = same_tags.index(tag) + 1
    return f"//{tag.name}[{index}]"

def extract_field_questions(form_soup, full_soup):
    questions = []
    inputs = form_soup.find_all(["input", "textarea", "select"])
    for tag in inputs:
        label = ""
        if tag.has_attr("placeholder"):
            label = tag["placeholder"]
        elif tag.has_attr("aria-label"):
            label = tag["aria-label"]
        else:
            label_tag = tag.find_previous("label")
            if label_tag:
                label = label_tag.text.strip()

        xpath = build_xpath(tag, full_soup)
        questions.append({
            "label": label,
            "xpath": xpath,
            "tag": tag.name
        })
    return questions

def extract_apply_buttons_data(soup):
    buttons = soup.find_all("button", string=lambda s: s and (
        any(w in s.lower() for w in WORDS_JOB_APLICATION) or
        any(p in s.lower() for p in PALABRAS_SOLICITUD_EMPLEO)
    ))

    btn_html = "<!-- Apply Buttons -->\n" + "\n".join(str(btn) for btn in buttons) if buttons else ""

    btn_data = []
    for tag in buttons:
        text = tag.get_text(strip=True)
        xpath = build_xpath(tag, soup)
        btn_data.append({
            "text": text,
            "xpath": xpath,
            "tag": tag.name
        })

    return btn_html, btn_data

# Procesamiento principal
for path in available_files:
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    form = soup.find("form")
    if not form:
        continue

    if len(form.find_all(["input", "textarea", "select"])) < 2:
        continue

    questions_data = extract_field_questions(form, soup)
    btn_html, apply_btn_data = extract_apply_buttons_data(soup)

    html_output_path = os.path.join(output_form_path, os.path.basename(path))
    with open(html_output_path, "w", encoding="utf-8") as out:
        out.write(str(form) + "\n" + btn_html)

    json_output_path = html_output_path.replace(".html", ".json")
    with open(json_output_path, "w", encoding="utf-8") as jf:
        json.dump({
            "questions": questions_data,
            "apply_buttons": apply_btn_data
        }, jf, indent=2, ensure_ascii=False)

    form_extracted[path] = {
        "html_path": html_output_path,
        "json_path": json_output_path
    }

print(json.dumps(form_extracted, indent=2, ensure_ascii=False))
