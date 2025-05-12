from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
import os
import json

# Utilidades
from utils_XPathBuilder import extract_field_questions, extract_apply_buttons_data
from utils_get_oferts import WORDS_JOB_APLICATION, PALABRAS_SOLICITUD_EMPLEO

# Leer CSV
df = pd.read_csv("data/jobs_data_2025_05_05.csv")
paths = df['external_url'].dropna().unique()

available_files = {path: path for path in paths if os.path.exists(path)}
output_form_path = "data/solicitud_external_form"
os.makedirs(output_form_path, exist_ok=True)

form_extracted = {}
all_question_rows = []

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

    # Expandir cada pregunta como fila separada
    matching_rows = df[df['external_html_path'] == path]
    for _, row in matching_rows.iterrows():
        job_id = row["job_job_id"]
        for q in questions_data:
            all_question_rows.append({
                "job_job_id": job_id,
                "external_html_path": path,
                "label": q.get("label"),
                "question": q.get("xpath"),
                # "tag": q.get("tag"),
                "apply_buttons": apply_btn_data  # You may choose to remove or separate this
            })

# Crear y guardar DataFrame
questions_df = pd.DataFrame(all_question_rows)
questions_df.to_csv("data/ext_job_questions_merged.csv", index=False)

# Guardar mapeo de formularios
with open("data/ext_form_extracted_mapping.json", "w", encoding="utf-8") as jf:
    json.dump(form_extracted, jf, indent=2, ensure_ascii=False)

print("Detailed questions DataFrame saved to 'data/job_questions_merged.csv'")
print("Form mapping saved to 'data/form_extracted_mapping.json'")
