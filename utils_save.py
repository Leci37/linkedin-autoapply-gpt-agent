import json
import csv
import os
from datetime import datetime


# Helper to get date-stamped filename
def get_dated_filename(base_name, extension):
    date_str = datetime.now().strftime("%Y_%m_%d")
    return f"{base_name}_{date_str}.{extension}"


# Save questions to CSV with job_id-based keys
def save_questions_to_csv(job_id, questions_dict, folder='data'):
    os.makedirs(folder, exist_ok=True)
    filename = get_dated_filename('questions_output', 'csv')
    filepath = os.path.join(folder, filename)

    file_exists = os.path.isfile(filepath)
    with open(filepath, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['key', 'question'])
        for idx, (qkey, qtext) in enumerate(questions_dict.items(), start=1):
            key_name = f"{job_id}_question_{idx}"
            writer.writerow([key_name, qtext])


# Save jobs data to JSON
def save_jobs_data_to_json(jobs_data, folder='data'):
    os.makedirs(folder, exist_ok=True)
    filename = get_dated_filename('jobs_data', 'json')
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(jobs_data, f, ensure_ascii=False, indent=4)


# Save jobs data to CSV
def save_jobs_data_to_csv(jobs_data, folder='data'):
    os.makedirs(folder, exist_ok=True)
    filename = get_dated_filename('jobs_data', 'csv')
    filepath = os.path.join(folder, filename)
    print(f"Saving CSV to: {filepath}")

    all_rows = []
    headers_set = set()

    for job in jobs_data:
        flat_job = {}
        for section, section_data in job.items():
            if isinstance(section_data, dict):
                for k, v in section_data.items():
                    key = f"{section}_{k}"
                    flat_job[key] = json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                    headers_set.add(key)
            elif isinstance(section_data, list):
                flat_job[section] = json.dumps(section_data, ensure_ascii=False)
                headers_set.add(section)
            else:
                flat_job[section] = section_data
                headers_set.add(section)
        all_rows.append(flat_job)

    headers = sorted(headers_set)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)
