import pandas as pd
import os
from GPT_Assistant import LuisAssistant
from utils_chat_send_question import classify_question, normalize_question

# Initialize assistant
assistant = LuisAssistant(api_key_path="chatGPT/agente.txt")

# Load questions from the main source
# df_main = pd.read_csv("data/questions_output_Cleaned_.csv")
# questions_main = df_main[df_main.columns[1]].dropna().astype(str).tolist()
#
# # Load questions from the external form source
# df_ext = pd.read_csv("data/ext_solicitud_external_form.csv")
# questions_ext = df_ext["question"].dropna().astype(str).tolist()

# Normalize and deduplicate
# questions_combined = list(set(normalize_question(q) for q in questions_main + questions_ext))

df_main = pd.read_csv("data/questions_output_2025_05_07.csv")
questions_main = df_main[df_main.columns[1]].dropna().astype(str).tolist()

questions_combined = list(set(normalize_question(q) for q in questions_main ))


# Load existing answers if available
csv_path = "data/response_cache/CACHE_answered_questions_linke.csv"
if os.path.exists(csv_path):
    existing_df = pd.read_csv(csv_path)
    answered_questions = set(existing_df["Question"].astype(str))
    results = existing_df[["Question", "Type", "Answer"]].values.tolist()
else:
    answered_questions = set()
    results = []

# Start answering
print("Question\tAnswer")
for q in questions_combined:
    if q in answered_questions:
        print("\t Already answered ",q )
        continue  # Skip already answered

for q in questions_combined:
    if q in answered_questions:
        continue  # Skip already answered

    qtype = classify_question(q)
    prompt = {
        "yes_no": "Answer ONLY with YES or NO.",
        "number": "Answer ONLY with a NUMERIC value.",
        "text": "Answer concisely and conversationally. Be as concise as possible brief and conversational. "
    }.get(qtype, "Answer concisely and conversationally. Be as concise as possible brief and conversational. ")

    full_prompt = f"{prompt}\n\nQuestion: {q}"
    answer = assistant.ask(full_prompt)
    print(f"{q}\t::: {answer}\n---")

    results += [(q, qtype, answer)]

    # Save updated CSV after each question
    pd.DataFrame(results, columns=["Question", "Type", "Answer"]).to_csv(csv_path, index=False)

print("✅ All questions answered. Output saved to 'data/response_cache/CACHE_answered_questions_linke.csv'")
