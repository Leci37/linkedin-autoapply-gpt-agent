from selenium.webdriver.common.by import By

from utils_collect_questions_Utils import ADDRESS_KEYWORDS


def Get_answerGPT_for_question(question, qtype, assistant, city_str="", error_msg=None):
    """
    Generates an answer using GPT. On format error, enforces clearer retry rules.
    """
    if any(keyword.lower() in question.lower() for keyword in ADDRESS_KEYWORDS):
        full_prompt = (
            f"This is an address-related question in a job application form.\n"
            f"The job offer is in: {city_str}.\n"
            f"Write an appropriate fictional but plausible address for this field.\n\n"
            f"Just answer this: {question} , ONLY this: {question}"
        )
    else:
        base_prompt = {
            "yes_no": "Answer ONLY with YES or NO.",
            "number": "Answer ONLY with a DECIMAL NUMBER greater than 0.0. Do NOT explain.",
            "text": "Answer concisely and conversationally. Be as brief as possible."
        }.get(qtype, "Answer concisely and conversationally.")

        full_prompt = f"{base_prompt}\n\nQuestion: {question}"

        if error_msg:
            full_prompt = (
                f"{base_prompt}\n\nQuestion: {question}\n\n"
                f"⚠️ The previous answer triggered a format validation error:\n"
                f"\"{error_msg}\"\n"
                f"Reply ONLY with a corrected value that satisfies the FORMAT (integer).\n"
                f"No explanations, just the raw answer."
            )

    answer = assistant.ask(full_prompt).strip()
    print(f"🧠 Q: {question}\n➡️ A: {answer}")
    return answer


def Get_answerGPT_for_radio_group(question, radio_inputs, assistant, error_msg=None):
    """
    Asks GPT to choose among the visible radio button labels and returns the selected value.
    """
    try:
        # Gather all visible labels for the given inputs
        options = []
        for input_el in radio_inputs:
            try:
                input_id = input_el.get_attribute("id")
                label_el = radio_inputs[0].parent.find_element(By.XPATH, f"//label[@for='{input_id}']")
                label_text = label_el.text.strip()
                if label_text:
                    options.append(label_text)
            except Exception:
                continue

        if not options:
            print("❌ No visible options found for radio group.")
            return None

        # Create the GPT prompt
        prompt = f"Choose the most appropriate option from this list based on the following question.\n\n" \
                 f"Question: {question}\n\nOptions:\n- " + "\n- ".join(options)

        if error_msg:
            prompt += f"\n\nNote: The last answer caused an error: \"{error_msg}\".\nPlease select a better fitting option."

        # Ask GPT
        answer = assistant.ask(prompt).strip()
        print(f"🧠 Radio Q: {question}\nOptions: {options}\n➡️ A: {answer}")

        # Match answer to one of the known options (case-insensitive, trimmed)
        for opt in options:
            if answer.lower() == opt.lower():
                return opt

        # Fallback: attempt partial match
        for opt in options:
            if answer.lower() in opt.lower() or opt.lower() in answer.lower():
                return opt

        print("⚠️ GPT answer did not match any known option.")
        return None

    except Exception as e:
        print(f"❌ Error in get_answer_for_radio_group: {e}")
        return None

def get_answer_for_dropdown(question, options, assistant, error_msg=None):
    """
    Asks GPT to choose the best answer among the given dropdown options.
    """
    clean_options = [opt.strip() for opt in options if opt.strip().lower() not in ["selecciona una opcion", "selecciona una opción"]]
    prompt = f"Choose the best answer to the following question from these options.\n\n" \
             f"Question: {question}\n\nOptions:\n- " + "\n- ".join(clean_options)

    if error_msg:
        prompt += f"\n\nNote: The last answer caused an error: \"{error_msg}\".\nPlease select a better fitting option."

    answer = assistant.ask(prompt).strip()
    print(f"🧠 Dropdown Q: {question}\nOptions: {clean_options}\n➡️ A: {answer}")

    # Try exact or partial match
    for opt in clean_options:
        if answer.lower() == opt.lower():
            return opt
    for opt in clean_options:
        if answer.lower() in opt.lower() or opt.lower() in answer.lower():
            return opt

    print("⚠️ GPT answer did not match any known dropdown option.")
    return None


