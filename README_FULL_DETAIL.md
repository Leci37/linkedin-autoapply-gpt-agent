Great. I’ll prepare technical developer documentation for the LinkedIn AutoApply GPT Agent project. It will include a full breakdown of the code structure, module responsibilities, class and function signatures, and integration flow—designed for developers extending or maintaining the project.

I’ll notify you once it’s ready.

Developer Documentation for LinkedIn AutoApply GPT Agent

# **LinkedIn Auto-Apply GPT Agent – Developer Documentation**

## **Project Overview**

**LinkedIn Auto-Apply GPT Agent** is a Python-based automation tool that uses Selenium for web navigation and OpenAI GPT for question answering. It automatically logs into LinkedIn, scrapes job postings (using LinkedIn’s Easy Apply feature), and submits applications on the user’s behalf. The agent can handle multi-step application forms by answering custom questions using a GPT-4 model (with a knowledge base of the candidate’s CV and related documents). It is intended for developers to study, modify, and integrate; no end-user UI is provided. All interactions (login, form filling, file uploads) happen through code and a headless browser, with GPT providing dynamic answers to application questions.

**Key Technologies:** Python, Selenium WebDriver (for LinkedIn navigation), and OpenAI’s API for GPT. The GPT model is invoked with retrieval augmentation – it uses a *vector store* of the candidate’s documents to answer form questions with relevant context. The project is organized into modular scripts and utilities, each responsible for a segment of the workflow.

## **Setup and Configuration**

Before running the agent, ensure the following setup:

* **Python Environment:** Install required libraries such as `selenium`, `openai`, `pandas`, `unidecode`, etc. (Refer to a `requirements.txt` if provided, or deduce from imports).

* **WebDriver:** Chrome WebDriver must be installed and in your PATH. The main script uses `webdriver.Chrome()` by defaultfile-ezfwzkshpzjeqitapwsjlo.

* **LinkedIn Credentials:** The login routine likely uses stored credentials. Check `utils_login.py` for how it authenticates. It may prompt for credentials or read from environment variables/config. Ensure your LinkedIn username/email and password are provided accordingly (for example, via environment variables or by editing the `linkedin_login()` function).

* **OpenAI API Key:** Acquire an API key from OpenAI. The GPT assistant class expects the key in a text file. By default, `GPT_Assistant.py` loads the API key from a path (e.g. `"chatGPT/agente.txt"`) passed to `LuisAssistant(api_key_path)`file-r1jtdw6ih6yna1fknbvpay. Place your API key in that file or adjust the path as needed.

* **Vector Store ID:** Prepare the vector store containing the candidate’s CV and reference documents. In `GPT_Assistant.py`, the `LuisAssistant` class has a placeholder for a `vector_store_id` that must be setfile-71yzvrmzcfu38ofwxdhmcl. This ID refers to a pre-built vector index of relevant documents (resume, project descriptions, etc.) which the OpenAI API will use for retrieval. You need to create this vector store via OpenAI’s file search tool or an equivalent embedding database and plug in the ID string. For example, if using OpenAI’s beta file search, upload your documents and use the assigned vector store ID. Without this, the GPT agent won’t have context and may give generic answers.

* **File Paths and Output Folders:** The project expects certain folders for data output. For instance, it saves external application HTML pages under `Data/solicitud_external/` and uses `data/response_cache/` for caching answers. Ensure these directories exist or adjust paths in the code. Output CSV/JSON files (for scraped jobs and answered questions) will be written to the working directory by default (e.g., `jobs_data.csv/json`, or under `data/` subfolders as coded).

Once configured, you can run the main script. The typical command to launch the automation is:

`python 02_Run_get_question_and_chatLinke.py`

This will open a Chrome browser, log in to LinkedIn, and begin the job application process.

**Note:** The script prints a message prompting manual navigation to a LinkedIn jobs pagefile-ezfwzkshpzjeqitapwsjlo. By default, it suggests going to the “Recommended jobs” collection. You should ensure the driver is on a jobs listing page (with Easy Apply jobs) after login – either by manually browsing to the URL printed, or by modifying the script to navigate there automatically (e.g. using `driver.get(<jobs search URL>)`). After that, the process is hands-free.

## **Application Workflow (Start to Submission)**

Below is a step-by-step breakdown of how the agent operates, from launch to job application submission. This maps out the flow across the scripts and functions:

1. **Launch and Login:** The developer runs the `02_Run_get_question_and_chatLinke.py` script. This script initializes a Selenium Chrome driver and calls `linkedin_login(driver)` to authenticate the user on LinkedInfile-ezfwzkshpzjeqitapwsjlo. On successful login, a cookie file (`linkedin_cookies.pkl`) is saved for session reusefile-ezfwzkshpzjeqitapwsjlo.

2. **Navigate to Job Listings:** The script (or the user manually) navigates the browser to a LinkedIn job listings page (e.g. a search results or recommended jobs page). The script then waits briefly and scrolls to load all job cards on the page. It uses `smart_scroll_jobs_list(driver)` to ensure all visible job postings are loaded by scrolling the sidebarfile-ezfwzkshpzjeqitapwsjlo.

3. **Iterate Over Job Posts:** The script collects all job card elements on the page (`job_list = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container--clickable")`), then loops through each job cardfile-ezfwzkshpzjeqitapwsjlo. For each job in the list:

   * The job card is scrolled into view (using `gentle_scroll` if not already visible) and clicked to open the job details drawerfile-ezfwzkshpzjeqitapwsjlo. After clicking, the script waits a moment for the job details to load.

   * The HTML of the job detail panel is retrieved (`driver.find_element(...).get_attribute('outerHTML')`) and passed to `parse_linkedin_job()`file-ezfwzkshpzjeqitapwsjlo. This function (in `utils_get_oferts.py`) parses the HTML to extract structured data about the job and company. The result is a dictionary `job_data` containing fields like job title, job ID, full description text, location(s) (cities), and company name, among other details.

   * A debug log is printed indicating which job is being scrapedfile-ezfwzkshpzjeqitapwsjlo (e.g., job title and index).

4. **Apply Decision (Easy Apply vs External):** For each job, after parsing details, the script attempts to apply by calling `click_easy_apply_if_exists(driver, job_id=job_data)`file-ezfwzkshpzjeqitapwsjlo. This function (defined in `utils_collect_questions.py`) checks if the job has a **LinkedIn Easy Apply** option or an **external apply** link:

   * Under the hood, `click_easy_apply_if_exists` uses `get_apply_button_and_type(driver)` to find any apply button on the page and determine its typefile-r1jtdw6ih6yna1fknbvpay. It looks for button text like “Solicitud sencilla” (Easy Apply) versus “Solicitar” (Apply on company site)file-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. It returns a tuple `(button_element, button_type)`.

   * If an **external apply** button is found (`button_type == "external"`), the function invokes `handle_external_apply(driver, button, job_id)`file-r1jtdw6ih6yna1fknbvpay. This will:

     * Click the “Apply on company site” button, handle any “Continue” intermediary popupfile-cbpbgd36qo2m1wv474et6v, then switch to the newly opened browser tab.

     * Grab the URL of the external application page and save the entire page HTML to a file in `Data/solicitud_external/`, naming it with the domain and job IDfile-r1jtdw6ih6yna1fknbvpayfile-r1jtdw6ih6yna1fknbvpay. (For example, an external application for job ID `12345` at `company.com` might be saved as `Data/solicitud_external/company.com_12345.html`.)

     * Close the external tab and switch back to the main LinkedIn tabfile-r1jtdw6ih6yna1fknbvpay.

     * Return the external application URL and saved file path as a tuple. In the main script, this tuple is captured as `dict_info_back`, and the job data is updated with `external_url` and `external_html_path`file-ezfwzkshpzjeqitapwsjlo.

     * No further action is taken on that job (since the application can’t be auto-filled on LinkedIn’s side). The script will move on to the next job.

   * If a **LinkedIn Easy Apply** button is found (`button_type == "simple"`), the function calls `handle_easy_apply(driver, button, job_data)`file-r1jtdw6ih6yna1fknbvpay. This is the core routine that will fully automate the application form. The returned value (`dict_info_back`) will be a dictionary of all questions answered for that job. The main script stores this in `job_data['questions']` and writes those Q\&A to a CSV log via `save_questions_to_csv(job_id, dict_info_back)`file-ezfwzkshpzjeqitapwsjlo.

   * If no apply button is present or clickable (e.g., if the job is already applied or the listing is closed), `click_easy_apply_if_exists` returns an empty resultfile-r1jtdw6ih6yna1fknbvpayfile-r1jtdw6ih6yna1fknbvpay. The main loop would then simply continue to the next job without modifications to `job_data`.

5. **Handling the Easy Apply Form:** When `handle_easy_apply` is triggered for a job, it takes control of the browser to fill out LinkedIn’s multi-step application form. The process is as follows:

   * **Open the Easy Apply Modal:** The function scrolls the Easy Apply button into view and clicks itfile-r1jtdw6ih6yna1fknbvpay. If a “Continue application” popup appears (sometimes LinkedIn prompts to continue if leaving the site or similar), it is handled via `handle_continue_popup(driver)` – this looks for a “Continuar la solicitud” button and clicks itfile-cbpbgd36qo2m1wv474et6v. Once the Easy Apply modal is open, a message is logged (“Clicked 'Solicitud sencilla' button.”)file-r1jtdw6ih6yna1fknbvpay.

   * **Iterate Through Form Steps:** LinkedIn’s Easy Apply may have multiple steps (pages) of questions and fields. `handle_easy_apply` runs a loop up to a maximum of 6 passes (steps)file-r1jtdw6ih6yna1fknbvpay:

     * It waits a moment for the form to render, then calls `collect_questions(driver)` to gather all question texts on the current form stepfile-r1jtdw6ih6yna1fknbvpay. This function (in `utils_collect_questions_Utils.py`) finds all visible labels and legends in the form and returns their text content as a listfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. For example, it might collect questions like “What is your current salary expectation?” or “Do you have experience with X technology?”.

     * The raw questions list is then normalized and filtered: each question string is passed through `normalize_question()` to remove line breaks and punctuation for consistency, and then `clean_questions()` filters out duplicates or meaningless entriesfile-r1jtdw6ih6yna1fknbvpayfile-cbpbgd36qo2m1wv474et6v. (The cleaner drops empty strings and trivial “yes/no” strings – e.g., a lone “Yes” or “No” which might appear as default answers – by using `is_meaningless_answer`file-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.) The result is a set of unique question prompts for that step.

     * **Upload Attachments (if required):** Before answering the questions, `handle_easy_apply` takes care of file uploads:

       * It calls `handle_cv_upload(driver, job_data, cities_available)` to ensure a résumé is attached if neededfile-r1jtdw6ih6yna1fknbvpayfile-r1jtdw6ih6yna1fknbvpay. Internally, `is_CV_resume_required(driver)` checks the form for any text indicating an updated CV is required (for example, LinkedIn might prompt “be sure to include an updated resume”)file-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. If a resume is required, `expand_more_resumes(driver)` will click the “Show more resumes” button (if available) to reveal multiple stored resumesfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. Then `select_best_resume(driver, cities_available, force_dotnet)` is used to pick the appropriate resume from the user’s saved optionsfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. The code uses the job’s available city (location) list and checks if the job description mentions .NET technologiesfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v to decide between a .NET-specific CV or a general one. It prints which CV was selectedfile-r1jtdw6ih6yna1fknbvpay. (This selection likely corresponds to file names or identifiers of resumes uploaded to the LinkedIn profile – e.g., separate resumes for different cities or tech stacks.)

       * It then calls `handle_cover_letter_upload(driver, job_data)`file-r1jtdw6ih6yna1fknbvpay. If the form has an option to upload a cover letter (`click_cover_letter_upload_if_present` returns true), this function will generate a cover letter text on the fly using GPT and attach it:

         * `generate_cover_letter_text(job_data, assistant)` is called to produce a personalized cover letter based on the job info and the candidate’s details. This likely uses the `LuisAssistant` GPT instance with a prompt that includes the job title and company, instructing GPT to write a short cover letter. (The specifics of the prompt can be configured; see **Sample Prompt Template** below for how the GPT is primed.)

         * The returned cover letter text is saved to a Word document or PDF via `save_cover_letter_to_doc(...)`file-r1jtdw6ih6yna1fknbvpay, creating a file named with the job ID and company (e.g., `cover_letter_<company>_<jobid>.docx`). For example, `cover_letter_devoteam_4194879978.docx` is a file that might have been generated for a Devoteam job.

         * Finally, `upload_cover_letter(driver, cl_path)` attaches the generated file to the form (this typically finds the file input for cover letter and uses Selenium to send the file path).

         * A log “📎 Uploading cover letter...” is printed when this process occursfile-r1jtdw6ih6yna1fknbvpay.

     * **Answer Form Questions:** After handling attachments, the script proceeds to answer each collected question on the form:

       * For each question `q`, it finds the corresponding input field by calling `get_input_element_for_question(driver, q)` (from `utils_collect_questions_Utils.py`). This helper tries to locate the form element associated with the question text:

         * It searches for a `<label>` whose text (or child span text) matches the question, then gets the form control (`<input>`, `<select>`, `<textarea>`, etc.) that the label is pointing to via the `for` attributefile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.

         * If not found by label, it searches for a `<legend>` within a `<fieldset>` that matches (for grouped inputs like radio buttons or checkboxes)file-cbpbgd36qo2m1wv474et6v. It then returns the list of input elements in that fieldset and a type like `"group_radio"` or `"group_checkbox"`file-cbpbgd36qo2m1wv474et6v.

         * The function returns a tuple `(element, el_type)`, where `element` is either a single WebElement or a list (for radio groups), and `el_type` is a string describing the field type (`"input"`, `"textarea"`, `"select"`, `"radio"`, `"checkbox"`, or grouped types).

       * If no input element is found for the question, the script logs a warning and skips that questionfile-r1jtdw6ih6yna1fknbvpay. Assuming the element is found, it then checks if the field is already answered (perhaps some fields pre-fill from the profile or previous steps). `is_question_answered_in_form(driver, q)` looks up the input by ID and checks if it has a non-default value (for text it checks if any value is present; for a dropdown it ensures the selected option isn’t just “Select an option”)file-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. If a value is detected, it logs that the question is already answered and skips to the next questionfile-r1jtdw6ih6yna1fknbvpay.

       * Next, the script clicks into the input field to focus it (using `scroll_and_click_element` and `safe_click_element` to ensure the element is interactable)file-r1jtdw6ih6yna1fknbvpay. A short random sleep (`human_sleep(0.3, 0.7)`) is done to mimic human pausefile-r1jtdw6ih6yna1fknbvpay.

       * **Special handling for choice inputs:** If the field type is a radio group or a dropdown, the script delegates to `handle_radio_or_select(driver, q, el_type, element)`file-r1jtdw6ih6yna1fknbvpayfile-r1jtdw6ih6yna1fknbvpay:

         * For a radio button group (`el_type == "group_radio"`), it calls `Get_answerGPT_for_radio_group(q, element, assistant)` to have GPT choose the best optionfile-r1jtdw6ih6yna1fknbvpayfile-r1jtdw6ih6yna1fknbvpay. The `element` in this case is a list of radio `<input>` elements. Inside `Get_answerGPT_for_radio_group`, all visible labels for those radio inputs are collected, and a prompt is constructed listing the question and the optionsfile-hgs7z8kwypbvd3rznucm7dfile-hgs7z8kwypbvd3rznucm7d. GPT’s answer (a text string) is returned and the code attempts to match it to one of the option labelsfile-hgs7z8kwypbvd3rznucm7dfile-hgs7z8kwypbvd3rznucm7d. If a matching option is found, `select_radio_by_label_text` is called to click the radio button with that labelfile-r1jtdw6ih6yna1fknbvpay. A message is printed showing the chosen optionfile-hgs7z8kwypbvd3rznucm7d. If no match is found, it logs a warning and leaves the question unanswered (the form might treat it as required and prompt later).

         * For a dropdown (`el_type == "select"`), it gathers all option texts from the `<select>` elementfile-r1jtdw6ih6yna1fknbvpay and calls `get_answer_for_dropdown(q, options, assistant)`. This function similarly asks GPT to pick one of the provided optionsfile-hgs7z8kwypbvd3rznucm7d. The returned choice is matched against the list (case-insensitively and by containment)file-hgs7z8kwypbvd3rznucm7d; if a match is found, `select_dropdown_option_by_label(driver, q, selected_label)` selects that option in the `<select>`file-r1jtdw6ih6yna1fknbvpay. If GPT’s answer doesn’t match an existing option, a warning is loggedfile-hgs7z8kwypbvd3rznucm7d.

         * Both `Get_answerGPT_for_radio_group` and `get_answer_for_dropdown` handle an `error_msg` parameter as well – if a previous attempt at this question failed validation, they include a note in the prompt to encourage GPT to choose a different optionfile-hgs7z8kwypbvd3rznucm7dfile-hgs7z8kwypbvd3rznucm7d. (More on error handling below.)

         * If either radio or dropdown was handled, `handle_radio_or_select` returns True, and the script proceeds to the next question without further GPT calls for this fieldfile-r1jtdw6ih6yna1fknbvpay.

       * **Textual answers:** If the question is a free-text input/textarea or a numeric field (and not handled by the above), the script uses GPT to generate an answer:

         * **Salary override:** A special case is implemented for salary-related questions. If `is_salary_question(q)` returns true (likely checking if keywords like “salary” appear in the question), the script **overrides GPT** and directly fills a preset answer of `"30500"` (as an annual salary figure)file-r1jtdw6ih6yna1fknbvpay. This shortcut is likely to avoid GPT’s potentially verbose or non-numeric responses for salary expectations. A log “💰 Overriding salary-related question with: 30500” is printed in this casefile-r1jtdw6ih6yna1fknbvpay.

         * **Use cached answer if available:** The tool maintains a cache of previously answered questions across jobs. If the same exact question text has been answered before, it will reuse the stored answer to save API calls. The cache is loaded from a CSV at startup (`CACHE_answered_questions_linke.csv`) into a dictionary `cached_answers`file-r1jtdw6ih6yna1fknbvpay. Before calling GPT, the script checks `elif q in cached_answers:` and if so, uses the cached answer directlyfile-r1jtdw6ih6yna1fknbvpay. It logs “📄 Using cached answer: \<question\>” in that casefile-r1jtdw6ih6yna1fknbvpay.

         * **GPT answer generation:** If not cached, the script classifies the question type and calls the GPT assistant:

           * `qtype = classify_question(q)` determines if the prompt expects a yes/no answer, a number, or free text. This uses keyword heuristics (e.g., if the question contains phrases like “how many/¿cuántos?” it tags it as `"number"`, or yes/no patterns it tags as `"yes_no"`)file-1skxkwueijv5behbbn6jwq.

           * It then calls `answer = Get_answerGPT_for_question(q, qtype, assistant, city_str=cities_available, error_msg=None)`file-r1jtdw6ih6yna1fknbvpay. This function in `GPT_Assistant_utils.py` crafts an appropriate prompt and uses the `LuisAssistant` to get an answer:

             * If the question seems to request an address (it checks if any keyword from a predefined list like “Street”, “City”, “Address” is in the text)file-hgs7z8kwypbvd3rznucm7dfile-cbpbgd36qo2m1wv474et6v,file-cbpbgd36qo2m1wv474et6v, it creates a prompt instructing GPT to provide a fictional but plausible address in the specified city. It knows the job’s city from `cities_available` (usually the job location) and inserts that into the promptfile-hgs7z8kwypbvd3rznucm7d.

             * Otherwise, it chooses a base instruction based on `qtype`: e.g., for "yes\_no" it prefixes “Answer ONLY with YES or NO.”, for "number" it says “Answer ONLY with a DECIMAL NUMBER greater than 0.0. Do NOT explain.”, and for text it says “Answer concisely and conversationally.”file-hgs7z8kwypbvd3rznucm7d. This is appended with the actual question text to form the prompt.

             * If an `error_msg` is passed (meaning a previous attempt failed validation), the prompt is extended to warn GPT: *“⚠️ The previous answer triggered a format validation error: "\<error message\>". Reply ONLY with a corrected value that satisfies the format (integer). No explanations.”*file-hgs7z8kwypbvd3rznucm7d. This guides GPT to produce an answer that meets the expected format (e.g., if a number was required, the assistant will try just a numeric value on retry).

             * The function then calls `assistant.ask(full_prompt)` to get the model’s answerfile-hgs7z8kwypbvd3rznucm7d. The `LuisAssistant.ask()` method sends this prompt to the OpenAI API with the vector store attached (so the model can reference the candidate’s CV data if needed)file-71yzvrmzcfu38ofwxdhmclfile-71yzvrmzcfu38ofwxdhmcl. It sets a relatively focused temperature (e.g. 0.25) for deterministic outputfile-71yzvrmzcfu38ofwxdhmcl. The response is parsed and returned as a cleaned stringfile-71yzvrmzcfu38ofwxdhmcl.

             * A debug print shows the question and the GPT-derived answer in the console (“🧠 Q: ... ➡️ A: ...”)file-hgs7z8kwypbvd3rznucm7d.

           * Once an answer is obtained, the script calls `append_to_cache(q, qtype, answer)` to record this Q\&A in the CSV cachefile-r1jtdw6ih6yna1fknbvpay. The `append_to_cache` function adds a new row to the pandas DataFrame and writes out to `CACHE_answered_questions_linke.csv` so that future runs also remember itfile-r1jtdw6ih6yna1fknbvpay.

         * The chosen `answer` (from cache, override, or GPT) is then input into the form field using `fill_in_answer(driver, element, el_type, answer, q)`file-r1jtdw6ih6yna1fknbvpay. This function handles the actual Selenium input:

           * If the element is a text input or textarea, it does `element.clear()` and `element.send_keys(answer)`, followed by a `TAB` key to trigger LinkedIn’s validation scriptsfile-cbpbgd36qo2m1wv474et6v.

           * If it’s a dropdown (`select`), it iterates over the `<option>` elements to find one that contains the answer text and selects it via `select_by_visible_text`file-cbpbgd36qo2m1wv474et6v (in case `handle_radio_or_select` didn’t already handle it).

           * For completeness, `fill_in_answer` has a placeholder for radio/checkbox (currently just a TODO message, since those are handled earlier)file-cbpbgd36qo2m1wv474et6v.

           * After entering the answer, it calls `get_format_error_message(driver, element)` to check if LinkedIn rendered a validation error for that fieldfile-cbpbgd36qo2m1wv474et6v. This looks for an error message associated with the input (via an `aria-describedby` link to an error span) and returns the text if anyfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.

           * If an error message is returned (e.g., “Please enter a number” or “Invalid format”), `fill_in_answer` returns that string, and the script recognizes a format issue.

       * **Validation Retry:** If `error_msg` is not empty after filling the answerfile-r1jtdw6ih6yna1fknbvpay, the script enters a retry sequence:

         * It logs the error and intent to retry (“🔁 Retrying due to format error: {error\_msg}”)file-r1jtdw6ih6yna1fknbvpay.

         * It classifies the question again (`qtype = classify_question(q)`) – often the type remains the same, but this is done afresh.

         * It calls `Get_answerGPT_for_question(q, qtype, assistant, cities_available, error_msg=error_msg)` with the validation error message providedfile-r1jtdw6ih6yna1fknbvpay. As described, the presence of `error_msg` alters the prompt to request a corrected answerfile-hgs7z8kwypbvd3rznucm7d (for example, GPT might have responded “five years” to a numeric question, causing a format error; the retry prompt will ask it to give just a number like “5”).

         * The new answer (`retry`) is obtained and cached (the cache will update the question’s entry to the new answer)file-r1jtdw6ih6yna1fknbvpay.

         * Finally, `fill_in_answer` is called again with the corrected answerfile-r1jtdw6ih6yna1fknbvpay. In most cases, this second attempt will satisfy the format (if not, the code doesn’t loop again – it would rely on the LinkedIn form’s own validation on submit).

       * Each answered question (and its final answer) is added to an `all_questions` dictionary for record-keepingfile-r1jtdw6ih6yna1fknbvpay.

     * **Proceed to Next Step or Submit:** After answering all questions on the current form page, `handle_easy_apply` checks if the **Review** (Revisar) button is present, which indicates the last step before submission. `is_review_button_present(driver)` simply looks for the “Revisar” button in the DOMfile-cbpbgd36qo2m1wv474et6v. If found:

       * It logs “✅ Reached 'Revisar' step.”file-r1jtdw6ih6yna1fknbvpay and calls `click_review_and_submit_and_log(driver, job_data, csv_path="data/errors/_submitted_jobs.csv")`.

       * This function (in `utils_next_page.py`) likely clicks the final **Submit** button on the review page and logs the application as submitted. The code likely writes an entry to `_submitted_jobs.csv` with details (such as job ID and timestamp) to keep track of successful submissions. After calling this, `handle_easy_apply` breaks out of the form loop since the application is completefile-r1jtdw6ih6yna1fknbvpay.

     * If the review/submit button was **not** present (meaning there are more steps):

       * It calls `find_and_click_next(driver)` to press the **Next (Siguiente)** button on the formfile-r1jtdw6ih6yna1fknbvpay. This utility waits for the “Next” button to be clickable and clicks it, handling occasional interceptsfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. If `find_and_click_next` returns False (no next button found, perhaps implying end of form or an issue), it logs “No more 'Siguiente' button, stopping.” and breaks the loopfile-r1jtdw6ih6yna1fknbvpay.

       * If Next was clicked, the loop iterates again, now on the next page of the form, collecting new questions and repeating the process.

   * **Close the Easy Apply Modal:** After exiting the loop (either after submission or a break), the script attempts to gracefully close the application modal:

     * It waits for the close (X) button and clicks itfile-r1jtdw6ih6yna1fknbvpay. If that fails, it catches the exception.

     * It also looks for a “Discard” (Descartar) button – LinkedIn sometimes shows a prompt "Are you sure you want to discard this application?" if not submitted. The code searches for “Descartar” or “Rule out” and clicks it to clear any leftover modalfile-r1jtdw6ih6yna1fknbvpay. Logs indicate when the modal is closed and the application discarded if neededfile-r1jtdw6ih6yna1fknbvpayfile-r1jtdw6ih6yna1fknbvpay.

   * Finally, `handle_easy_apply` returns the `all_questions` dictionary mapping each question text to the answer it providedfile-r1jtdw6ih6yna1fknbvpay. The main script receives this and attaches it to the job’s data (`job_data['questions'] = ...`).

6. **Post-Application Logging:** Back in the main loop (`02_Run_get_question_and_chatLinke.py`), once `click_easy_apply_if_exists` returns, the script updates the `job_data` dict with either the external apply info or the answered questions, as described. It then appends the `job_data` to a `jobs_data` list that collects all processed jobsfile-ezfwzkshpzjeqitapwsjlofile-ezfwzkshpzjeqitapwsjlo. This ensures that even jobs that were just scraped (but not applied due to external links) are recorded with their details.

7. **Next Page Navigation:** After iterating through all jobs on the current listing page, the script attempts to go to the next page of job results. It calls `close_easy_apply_modal_if_open(driver)` to ensure no Easy Apply dialog is lingering (this likely checks and closes any open modal)file-ezfwzkshpzjeqitapwsjlo. Then it calls `go_to_next_page(driver)`file-ezfwzkshpzjeqitapwsjlo. The `go_to_next_page` function (in `utils_next_page.py`) finds the pagination control (e.g., “→” or page numbers) and clicks the next page. If it returns False (meaning no next page was found, i.e., it was the last page), the main loop breaks out, ending the scraping processfile-ezfwzkshpzjeqitapwsjlo. Otherwise, the loop continues: the script will again scroll the new page, gather jobs, and repeat the apply process.

8. **Saving Results and Exit:** After all pages are processed (or a break condition is met), the script exits the loop. It then saves the accumulated jobs data to files:

   * `save_jobs_data_to_json(jobs_data)` and `save_jobs_data_to_csv(jobs_data)` are called to write out the details of all jobs visitedfile-ezfwzkshpzjeqitapwsjlo. These likely produce `jobs_data.json` and `jobs_data.csv` containing job titles, companies, whether applied, etc., including answers if any.

   * The answered questions for each Easy Applied job were already saved incrementally via `save_questions_to_csv` (probably stored in a CSV per job or a consolidated file for all Q\&A – this can be checked in `utils_save.py`).

   * The script prints a completion message and closes the browser (`driver.quit()` to end the Selenium session)file-ezfwzkshpzjeqitapwsjlo.

Throughout this process, the agent logs informative messages to the console (with emojis for clarity) – e.g., indicating when it cached an answer, selected a resume, or encountered an error – which can help in debugging or monitoring the run.

## **Module Breakdown and Key Components**

The project’s code is organized into multiple modules, each handling a specific aspect of the functionality. Below is a breakdown of the main files and their roles, along with important classes/functions (with signatures and brief descriptions) defined in each:

### **02\_Run\_get\_question\_and\_chatLinke.py – *Main Orchestration Script***

This is the entry-point script that ties everything together. It is responsible for launching the browser, initiating the login, iterating through job listings, and invoking the apply functions.

* **Role:** Orchestrates the overall process (login \-\> scrape \-\> apply \-\> next page \-\> save results).

* **Key Actions:**

  * Initializes Selenium `webdriver.Chrome()` and calls `linkedin_login(driver)`file-ezfwzkshpzjeqitapwsjlo to perform authentication.

  * After login, sets up and enters a loop to process job cards on each page:

    * Uses `smart_scroll_jobs_list(driver)` to load jobs, then finds all job elementsfile-ezfwzkshpzjeqitapwsjlo.

    * For each job, clicks it and uses `parse_linkedin_job(html)` to extract job informationfile-ezfwzkshpzjeqitapwsjlo.

    * Calls `click_easy_apply_if_exists(driver, job_id=job_data)` to attempt an applicationfile-ezfwzkshpzjeqitapwsjlo, and updates the `job_data` with results:

      * If Easy Apply was done, attaches the returned Q\&A dict.

      * If external, attaches the external URL and saved HTML path.

    * Appends `job_data` to the cumulative list.

    * Catches and handles exceptions (e.g., closing pop-ups if click interceptedfile-ezfwzkshpzjeqitapwsjlo).

    * Pauses occasionally to mimic human behaviorfile-ezfwzkshpzjeqitapwsjlo.

  * After each page, uses `go_to_next_page(driver)` to navigate to the next set of jobsfile-ezfwzkshpzjeqitapwsjlo until no more pages.

  * Finally, calls `save_jobs_data_to_json` and `save_jobs_data_to_csv` to persist all scraped datafile-ezfwzkshpzjeqitapwsjlo, and exits.

* **Dependencies:** Imports many utility modules (`utils_login`, `utils_get_oferts`, `utils_move`, `utils_next_page`, `utils_collect_questions`, `utils_save`, etc.) and calls their functions. The main logic is heavily dependent on `utils_collect_questions.click_easy_apply_if_exists` for applying to jobs. It uses `pickle` to save cookies, and random sleeps for timing.

**Snippet – Main loop applying to jobs (excerpt):**file-ezfwzkshpzjeqitapwsjlofile-ezfwzkshpzjeqitapwsjlo

`job_details_html = driver.find_element(By.CSS_SELECTOR, "div.jobs-details__main-content").get_attribute('outerHTML')`  
`job_data = parse_linkedin_job(job_details_html)`  
`print(f"Scraping job {idx}/{total_jobs}: {job_data['job']['title']}")`  
`button_type, dict_info_back = click_easy_apply_if_exists(driver, job_id=job_data)`  
`print(dict_info_back)`  
`if button_type == "external":`  
    `job_data['external_url'] = dict_info_back[0]`  
    `job_data['external_html_path'] = dict_info_back[1]`  
`elif button_type == "simple":`  
    `job_data['questions'] = dict_info_back`  
    `save_questions_to_csv(job_data['job']['job_id'], dict_info_back)`  
`jobs_data.append(job_data)`

This shows how for each job, after parsing, it tries to apply. The `button_type` determines how the `job_data` is updated with resultsfile-ezfwzkshpzjeqitapwsjlo. External applications yield a URL/path, while Easy Apply yields a questions/answers dict which is saved to CSVfile-ezfwzkshpzjeqitapwsjlo.

### **GPT\_Assistant.py – *GPT Agent Interface***

Defines the `LuisAssistant` class which wraps the OpenAI API client. This is the interface through which all GPT queries are made.

* **Class: `LuisAssistant`** – initialized with an API key file.

  * **`__init__(self, api_key_path: str)`**: Reads the API key from the given file pathfile-71yzvrmzcfu38ofwxdhmcl, then constructs an `OpenAI` API client (`self.client = OpenAI(api_key=... )`) using the provided keyfile-71yzvrmzcfu38ofwxdhmcl. It sets `self.model` to a model name (e.g., `"gpt-4o-mini"`) and initializes `self.vector_store_id` (which must be filled with a valid vector store identifier)file-71yzvrmzcfu38ofwxdhmcl.

  * **`ask(self, question: str, history: list = None) -> str`**: Sends a query to the GPT model and returns the assistant’s answer textfile-71yzvrmzcfu38ofwxdhmcl. Key aspects of this method:

    * It constructs the input payload expected by the OpenAI **Responses API**. If a `history` (list of message dicts) is provided, it starts with that; otherwise, it begins with an empty listfile-71yzvrmzcfu38ofwxdhmcl. Then it appends the current user question as the last message in the sequence.

    * It calls `self.client.responses.create(...)` with the specified model and inputsfile-71yzvrmzcfu38ofwxdhmcl. Notably, it includes a `tools` parameter with a file search tool: `tools=[{"type": "file_search", "vector_store_ids": [self.vector_store_id]}]`file-71yzvrmzcfu38ofwxdhmcl. This means the question will be answered by GPT with access to the documents in the given vector store (likely the candidate’s CV and references). The call also sets parameters like `temperature=0.25`, `top_p=1`, and `max_output_tokens=256` for the completionfile-71yzvrmzcfu38ofwxdhmcl. `store=True` indicates the conversation is stored, and the response is requested as plain text formatfile-71yzvrmzcfu38ofwxdhmcl.

    * The response object returned contains a list of outputs (messages). The code loops through `response.output` to find the assistant’s message content and extracts the `output_text`file-71yzvrmzcfu38ofwxdhmcl. It returns the assistant’s answer as a stripped string. In case no message is found or an exception occurs, it returns an error message stringfile-71yzvrmzcfu38ofwxdhmclfile-71yzvrmzcfu38ofwxdhmcl.

* **Usage:** This class is instantiated once as a global `assistant` in `utils_collect_questions.py` (with the path to the API key)file-r1jtdw6ih6yna1fknbvpay. All GPT queries in the project go through `assistant.ask()`. The design centralizes GPT calls, so the same `assistant` (and thus the same conversation context, if history were used) is reused for multiple questions, though in practice the code sends each question independently without carrying a persistent chat history.

**Important:** Ensure you update `LuisAssistant.vector_store_id` with your actual vector store ID (or modify the code to load it from a config). The GPT calls will fail or not retrieve relevant info if `vector_store_id` is left as the placeholder `"xxxxx"`file-71yzvrmzcfu38ofwxdhmcl.

### **GPT\_Assistant\_utils.py – *GPT Query Helper Functions***

This module provides utility functions to generate prompts for GPT and handle certain question types when using the assistant. These functions encapsulate prompting logic so that `handle_easy_apply` can simply call them to get answers. Key functions include:

* **`Get_answerGPT_for_question(question, qtype, assistant, city_str="", error_msg=None)`**: Returns a string answer from GPT for a given question.

  * It builds a custom prompt depending on the question type and contentfile-hgs7z8kwypbvd3rznucm7dfile-hgs7z8kwypbvd3rznucm7d:

    * If the question contains any **address-related keywords** (defined in `ADDRESS_KEYWORDS` list, e.g. "Street address", "City", "ZIP code", etc.)file-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v, it assumes the form is asking for an address. It then prepares a prompt: *“This is an address-related question in a job application form. The job offer is in: {city\_str}. Write an appropriate fictional but plausible address for this field.”* followed by the questionfile-hgs7z8kwypbvd3rznucm7d. The `city_str` parameter is typically the job’s city (or a concatenation of available cities if multiple) – so that the address can be tailored to that location. This prevents GPT from giving a real personal address; instead it fabricates a plausible one.

    * Otherwise, based on `qtype`, it selects a brief instruction:

      * `"yes_no"` \-\> "Answer ONLY with YES or NO."

      * `"number"` \-\> "Answer ONLY with a DECIMAL NUMBER greater than 0.0. Do NOT explain."

      * `"text"` (or default) \-\> "Answer concisely and conversationally. Be as brief as possible."  
         These are defined in a dictionary for quick lookupfile-hgs7z8kwypbvd3rznucm7d.

    * The base instruction is combined with the question. The prompt format is basically: `{instruction}\n\nQuestion: {question}`.

    * If `error_msg` is provided (meaning a previous answer caused a validation error), the prompt is extended with a warning: it appends the text of `error_msg` and explicitly asks for a corrected value that fits the required formatfile-hgs7z8kwypbvd3rznucm7d. For example: “⚠️ The previous answer triggered a format validation error: "\<details\>". Reply ONLY with a corrected value that satisfies the format.”

  * After constructing the prompt, the function simply calls `assistant.ask(full_prompt)` to get the answerfile-hgs7z8kwypbvd3rznucm7d. It strips any surrounding whitespace and returns the result. It also prints the Q and A to console for debugging.

* **`Get_answerGPT_for_radio_group(question, radio_inputs, assistant, error_msg=None)`**: Helps choose an option from a set of radio buttons.

  * It takes the question text and the list of `radio_inputs` elements (the `<input type="radio">` elements from the form).

  * It first collects the visible labels for each radio optionfile-hgs7z8kwypbvd3rznucm7d by finding the corresponding `<label for="...">` elements. These labels’ text are stored in a list `options`.

  * If no options are found (which would be unusual), it logs and returns Nonefile-hgs7z8kwypbvd3rznucm7d.

It then builds a prompt of the form:

 csharp  
`Choose the most appropriate option from this list based on the following question.`

`Question: {question}`

`Options:`  
`- Option1`  
`- Option2`  
`...`

*  If `error_msg` is provided (meaning a previous selection was invalid), it appends a note: *“Note: The last answer caused an error: "{error\_msg}". Please select a better fitting option.”*file-hgs7z8kwypbvd3rznucm7d.

  * It calls `assistant.ask(prompt)` to get GPT’s choicefile-hgs7z8kwypbvd3rznucm7d. The answer might be one of the option texts or something close to it.

  * The function then tries to **match GPT’s answer** to the given options listfile-hgs7z8kwypbvd3rznucm7d:

    * First it does a case-insensitive exact match.

    * If none, it tries a partial match (checking if the answer is a substring of an option or vice-versa).

    * If a match is found, it returns the matching option text. Otherwise, it logs that no option matched and returns Nonefile-hgs7z8kwypbvd3rznucm7d.

* **`get_answer_for_dropdown(question, options, assistant, error_msg=None)`**: Similar to the radio group handler, but for dropdown lists.

  * It filters out any placeholder options like "Selecciona una opción" or "Select an option" from the `options` list (those are not valid selections)file-hgs7z8kwypbvd3rznucm7d.

Builds a prompt:

 css  
`Choose the best answer to the following question from these options.`

`Question: {question}`

`Options:`  
`- Option1`  
`- Option2`  
`...`

*  and appends the error note if applicablefile-hgs7z8kwypbvd3rznucm7d.

  * Calls GPT and prints the chosen answerfile-hgs7z8kwypbvd3rznucm7d.

  * Attempts to find a matching option (exact or partial, similar to above)file-hgs7z8kwypbvd3rznucm7d. Returns the matched option text or None with a warning if not foundfile-hgs7z8kwypbvd3rznucm7d.

* These utility functions abstract away prompt formatting and parsing of GPT responses. They all rely on the global `assistant` object for GPT calls. The `error_msg` parameter in each allows the calling code to provide feedback from validation failures to GPT.

**Example:** If the question is `"How many years of experience do you have with Java?"`, `classify_question` will label it as `"number"` (due to "How many")file-1skxkwueijv5behbbn6jwqfile-1skxkwueijv5behbbn6jwq. `Get_answerGPT_for_question` will then use the numeric instruction prompt. GPT might return `"5"` (a single number) which then gets filled in the form. That answer is cached so if another job asks the same question, the cached `"5"` will be reused.

### **utils\_chat\_send\_question.py – *Question Classification and Normalization***

This module contains simple text-processing helpers, mainly to prepare question strings for GPT and to classify question type. Key functions:

* **`classify_question(q: str) -> str`**: Inspects the question text and categorizes it as `"yes_no"`, `"number"`, or `"text"`file-1skxkwueijv5behbbn6jwq.

  * It converts the question to lowercase (`q_lower`) and by default returns `"text"`.

  * If any of the patterns in `yes_no_indicators_rich` appear in the text, it sets `ret = "yes_no"`file-1skxkwueijv5behbbn6jwq. (These indicators include words and regex for questions likely answered yes/no – e.g., "are you", "do you have", "did you", "¿...?" in Spanish, etc. Notably, many patterns in the provided list are commented out, indicating this might be simplified, but a few might still be active.)

  * If any of the substrings/regex in `number_keywords_full` appear, it sets `ret = "number"`file-1skxkwueijv5behbbn6jwq. This list is extensive, containing phrases like "how many", "cuántos", "porcentaje", "years of experience", "expected salary", etc. in both English and Spanishfile-1skxkwueijv5behbbn6jwqfile-1skxkwueijv5behbbn6jwq. It’s designed to catch questions that expect a numeric response.

  * The order of checks means that if a question contains both yes/no and numeric cues, the latter will override (since the code doesn’t use `elif` – it will potentially set `ret` twice, ending on "number" if both match).

* **`normalize_question(question: str) -> str`**: Cleans up question text for consistent matchingfile-1skxkwueijv5behbbn6jwqfile-1skxkwueijv5behbbn6jwq.

  * It splits the question by any newline characters, trims whitespace, and removes common punctuation (periods, commas, hyphens, quotes, etc.).

  * It then deduplicates any repeated parts. For example, sometimes LinkedIn might show a question with the label repeated or with extra spaces – this ensures we treat them uniformly. The function returns the normalized question as a single string.

  * This is used before caching and comparison, so that minor differences in formatting don’t result in treating the same question as different.

* *(There is some commented-out code in this module related to an older approach of directly querying OpenAI’s ChatCompletion with a system prompt context. That is not used in the current workflow, since the project moved to the `LuisAssistant` with vector store approach.)*

These functions are utilized in `handle_easy_apply` when iterating questions: `normalize_question` is applied to each collected question text, and `classify_question` results guide how GPT is promptedfile-r1jtdw6ih6yna1fknbvpay. They ensure the agent’s behavior can adapt to different question styles.

### **utils\_collect\_questions.py – *Easy Apply Orchestrator***

This module coordinates the entire Easy Apply form process, leveraging many helper utilities. It contains functions for handling external applications, managing file uploads, and answering questions. We covered much of its logic in the workflow, but here are the definitions and relationships:

* **`handle_external_apply(driver, button, job_id) -> tuple`**: Manages clicking an external apply button and capturing the resultfile-r1jtdw6ih6yna1fknbvpayfile-r1jtdw6ih6yna1fknbvpay.

  * It clicks the given `button` (external apply), then calls `handle_continue_popup(driver)` to deal with any intermediate “Continue” promptsfile-r1jtdw6ih6yna1fknbvpay.

  * After clicking, it checks for a new browser tab (`driver.window_handles`). If a new tab opened, it switches to it, waits for the page to load, and collects the URL and HTML contentfile-r1jtdw6ih6yna1fknbvpay.

  * Saves the HTML to `Data/solicitud_external/{domain}_{job_id}.html` on diskfile-r1jtdw6ih6yna1fknbvpay, logs a success message with the path, then closes the tab and switches backfile-r1jtdw6ih6yna1fknbvpay.

  * Returns a tuple `(url, file_path)` for the external application page. If no new tab was detected, it logs an error and returns a failure indicator.

* **`handle_cv_upload(driver, job_data, cities_available)`**: Ensures a resume is selected if requiredfile-r1jtdw6ih6yna1fknbvpay.

  * Checks `is_CV_resume_required(driver)` – which scans the Easy Apply modal content for phrases indicating a resume is neededfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.

  * If required, calls `expand_more_resumes(driver)` to show all resume options (if the user has multiple saved resumes)file-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.

  * Determines if a .NET-specialized resume is needed by analyzing the job description text with `mentions_dotnet_stack(full_description)`file-r1jtdw6ih6yna1fknbvpay. If the job description contains .NET tech keywords, `force_dotnet` is set true (and a log “currículum menciona .NET” is printed)file-r1jtdw6ih6yna1fknbvpay.

  * Calls `select_best_resume(driver, cities_available, force_dotnet)` to choose a resume. This function will normalize city names and attempt to find a resume file that matches one of the job’s cities (e.g., a resume file name containing "Madrid" or "Barcelona"), and possibly choose a .NET version if `force_dotnet` is truefile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. The implementation likely clicks on the corresponding resume option in the UI.

  * Logs which resume was selectedfile-r1jtdw6ih6yna1fknbvpay. (Note: The actual uploading of the resume file is handled by LinkedIn’s interface since the resume is already uploaded in the profile; this function just selects from existing ones.)

* **`handle_cover_letter_upload(driver, job_data)`**: Generates and uploads a cover letter if the application requests onefile-r1jtdw6ih6yna1fknbvpay.

  * Uses `click_cover_letter_upload_if_present(driver)` (likely in `utils_collect_questions_Utils.py`) to detect if a cover letter upload field is present and click the button to add a cover letter.

  * If present, prints “Uploading cover letter...” and then:

    * Calls `generate_cover_letter_text(job_data, assistant)` – this presumably creates a tailored cover letter text. It might send a prompt to GPT containing the job title, maybe the job description and candidate’s profile, asking for a brief cover letter. (This function is part of `utils_cover_letter.py` – see below.)

    * The returned text is passed to `save_cover_letter_to_doc(text, job_id, company_name)`, which creates a `.docx` or `.pdf` file in a designated folder.

    * Finally calls `upload_cover_letter(driver, cl_path)` to attach the file to the form (likely by interacting with the file picker input).

* **`handle_radio_or_select(driver, q, el_type, element) -> bool`**: Handles multiple-choice fields (radio groups or dropdown selects) so that `handle_easy_apply` can delegate those.

  * If `el_type` is `"group_radio"`, it uses GPT to pick a radio option:

    * Calls `Get_answerGPT_for_radio_group(q, element, assistant)` to get a labelfile-r1jtdw6ih6yna1fknbvpay.

    * If a label is returned, calls `select_radio_by_label_text(driver, group_element, target_label_text)` to click the corresponding radio inputfile-r1jtdw6ih6yna1fknbvpay. (The `group_element` here is found by locating the surrounding fieldset – the code explicitly finds a fieldset with id containing `"radio-button-form-component"` to ensure it clicks within the correct group.)

    * If the click was unsuccessful, logs a warningfile-r1jtdw6ih6yna1fknbvpay.

    * Returns True (since the question is considered handled whether success or not, to avoid trying to treat it as a text input).

  * If `el_type` is `"select"` (dropdown):

    * Gathers all option texts from the select elementfile-r1jtdw6ih6yna1fknbvpay.

    * Calls `get_answer_for_dropdown(q, options, assistant)` to get GPT’s choicefile-r1jtdw6ih6yna1fknbvpay.

    * If a choice is returned, calls `select_dropdown_option_by_label(driver, q, selected_label)` to actually select it in the UIfile-r1jtdw6ih6yna1fknbvpay.

    * Logs a warning if it couldn’t select for some reasonfile-r1jtdw6ih6yna1fknbvpay.

    * Returns True (handled).

  * For any other type, it returns False (meaning “not handled here”). This function ensures the main logic in `handle_easy_apply` cleanly separates multiple-choice answers from free-text answers.

* **`handle_easy_apply(driver, button, job_data) -> dict`**: As described in the workflow, this is the central function automating the Easy Apply submission.

  * **Inputs:** a Selenium driver, the Easy Apply button WebElement, and the parsed `job_data` dictionary for context.

  * **Operation:** Opens the Easy Apply modalfile-r1jtdw6ih6yna1fknbvpay, loops through form pages up to `max_passes` (6)file-r1jtdw6ih6yna1fknbvpay, collects and answers questions, handles file uploads, and navigates through steps.

  * **Outputs:** Returns a dictionary `all_questions` of question-\>answer for that job.

We have already examined this logic in detail. To summarize the structure:

 `all_questions = {}`  
`button.click(); handle_continue_popup();`  
`for step in range(max_passes):`  
    `questions = collect_questions(driver)`  
    `questions = clean_questions([normalize_question(q) for q in questions])`  
    `handle_cv_upload(...); handle_cover_letter_upload(...);`  
    `for q in questions:`  
        `element, el_type = get_input_element_for_question(driver, q)`  
        `if not element: ... continue`  
        `if is_question_answered_in_form(driver, q): ... continue`  
        `scroll_and_click_element(driver, element); safe_click_element(driver, element)`  
        `if handle_radio_or_select(driver, q, el_type, element): continue`  
        `# Otherwise, text-based:`  
        `if is_salary_question(q): answer = "30500"`  
        `elif q in cached_answers: answer = cached_answers[q]`  
        `else:`  
            `qtype = classify_question(q)`  
            `answer = Get_answerGPT_for_question(q, qtype, assistant, cities_available)`  
            `append_to_cache(q, qtype, answer)`  
        `all_questions[q] = answer`  
        `error_msg = fill_in_answer(driver, element, el_type, answer, q)`  
        `if error_msg:`  
            `... (retry logic with GPT using error_msg) ...`  
    `if is_review_button_present(driver): click_review_and_submit_and_log(...); break`  
    `if not find_and_click_next(driver): break`  
`# After loop, close modal and discard if needed`  
`return all_questions`

*  This pseudocode illustrates the flow inside `handle_easy_apply` as implemented in the sourcefile-r1jtdw6ih6yna1fknbvpayfile-r1jtdw6ih6yna1fknbvpayfile-r1jtdw6ih6yna1fknbvpay.

  * **Interdependencies:** This function uses many helpers from `utils_collect_questions_Utils.py` (like `collect_questions`, `clean_questions`, `find_and_click_next`, etc.) and from `GPT_Assistant_utils.py` for GPT answers. It also updates/reads the global cache (`cached_answers` and `append_to_cache` from this module). The global `assistant` (LuisAssistant) is referenced here to ask GPT.

* **`click_easy_apply_if_exists(driver, job_id) -> (str, Any)`**: A convenience wrapper used by the main script to handle both external and easy apply with one callfile-r1jtdw6ih6yna1fknbvpayfile-r1jtdw6ih6yna1fknbvpay.

  * It calls `get_apply_button_and_type(driver)` to locate an apply button and determine type.

  * If no valid button is found, it logs and returns `({}, None)`file-r1jtdw6ih6yna1fknbvpay (indicating nothing done).

  * If an external apply, returns `("external", result)` where result is the tuple from `handle_external_apply` (URL, path)file-r1jtdw6ih6yna1fknbvpay.

  * If easy apply, returns `("simple", result)` where result is the dict from `handle_easy_apply` (questions answered)file-r1jtdw6ih6yna1fknbvpay.

  * This function cleanly separates logic in the main loop, so the caller can just branch on the string.

  * It catches `NoSuchElementException` or `TimeoutException` to handle cases where the apply button is not present without failing the whole scriptfile-r1jtdw6ih6yna1fknbvpay.

The `utils_collect_questions.py` module is the centerpiece for application logic. It works closely with its companion `utils_collect_questions_Utils.py` for low-level operations.

### **utils\_collect\_questions\_Utils.py – *Low-level Form Utilities***

This module contains a large number of helper functions that interact with the Selenium driver to find elements and perform actions within the job application form. Many of them have been mentioned, but we list the key ones here with their purpose:

* **`find_and_click_next(driver, timeout=6) -> bool`**: Finds the "Next" button on the form (identified by the span text "Siguiente") and clicks itfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. Waits up to `timeout` seconds for it to appear. Returns True if clicked, False if not found. It also handles `ElementClickInterceptedException` by retrying once after a slight delayfile-cbpbgd36qo2m1wv474et6v.

* **`is_review_button_present(driver) -> bool`**: Checks if the "Revisar" (Review) button is present (and likely clickable) on the current form pagefile-cbpbgd36qo2m1wv474et6v. Used to detect the final step.

* **`collect_questions(driver) -> list[str]`**: Collects all question texts from the current form pagefile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.

  * It waits for all `<label>` elements containing “formElement” in their `for` (these correspond to question labels) to be present, then takes their textfile-cbpbgd36qo2m1wv474et6v.

  * It also collects any `<legend>` text inside `<fieldset>` (for grouped questions)file-cbpbgd36qo2m1wv474et6v.

  * Returns a list of texts (could include empty strings if any labels had no text, which are filtered out later).

* **`is_meaningless_answer(text: str) -> bool`**: Returns True if the string (after stripping and removing accents via `unidecode`) is exactly "yes", "no", or "si"file-cbpbgd36qo2m1wv474et6v. This helps identify trivial answers that are not questions.

* **`clean_questions(questions: list[str]) -> list[str]`**: Filters and deduplicates a list of question textsfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.

  * Removes empty strings.

  * Drops any string that `is_meaningless_answer` (i.e., "yes"/"no")file-cbpbgd36qo2m1wv474et6v.

  * Keeps the first occurrence of each unique question (after stripping) to avoid duplicates.

* **`get_apply_button_and_type(driver) -> (WebElement, str)`**: Searches the job detail pane for an apply buttonfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.

  * It looks for any `<button>` containing text "Solicit" (covers "Solicitud sencilla" and "Solicitar"). It iterates through matches:

    * If the button text (lowercased) contains "solicitud sencilla" (Easy Apply in Spanish) it returns that button with type `"simple"`file-cbpbgd36qo2m1wv474et6v.

    * If it contains "solicitar" or "solicitud" (apply in general, often the external apply) it returns that button with type `"external"`file-cbpbgd36qo2m1wv474et6v.

  * Returns `(None, None)` if no apply-related button is found.

  * Note: This approach is somewhat heuristic and assumes Spanish locale text. If using English UI, these might need to be adjusted (e.g., "Easy Apply" vs "Apply on company site").

* **`handle_continue_popup(driver)`**: After clicking Easy Apply or external, sometimes LinkedIn shows a secondary confirmation (like "Continue to apply on company site"). This waits up to 2 seconds for a "Continuar la solicitud" button and clicks itfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. It simply passes if not found.

* **`mentions_dotnet_stack(description: str) -> bool`**: Checks if a job description text contains .NET tech keywordsfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. Uses regex for terms like ".NET", "C\#", "ASP.NET", etc. Returns True if any found. (Used in resume selection logic.)

* **`normalize_city(text: str) -> str`**: Normalizes city name strings by removing accents and converting to lowercasefile-cbpbgd36qo2m1wv474et6v.

* **`select_best_resume(driver, cities_available: list[str], force_dotnet=False, SimCity=None)`**: Selects the appropriate resume option from the UI.

  * The implementation details would involve clicking on a dropdown or a list of resumes. The code snippet in the question implies mapping city names to certain resume identifiers (like suffixes "Pb", "Pm" for standard resumes and "Cb", "Cm" for .NET resumes for Barcelona (B), Madrid (M), etc.)file-cbpbgd36qo2m1wv474et6v.

  * In practice, it likely scans the list of available resumes (after expanding) and picks one that matches the city or the .NET flag, then clicks it. It returns some identifier or name of the selected resume (the code logs “CV seleccionado: {selected}” with whatever identifier it found)file-r1jtdw6ih6yna1fknbvpay.

* **`is_CV_resume_required(driver) -> bool`**: As described, checks if any text in the Easy Apply modal indicates a resume is required. It searches for certain phrases (in English or Spanish) like “include an updated resume” in any span/p/div inside the modalfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. Returns True if found.

* **`expand_more_resumes(driver) -> bool`**: Clicks the "Show more resumes" button if presentfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. It tries both Spanish and English aria-labels via an XPath. Returns True if it clicked something.

* **`is_question_answered_in_form(driver, label_text) -> bool`**: Checks if the form field corresponding to `label_text` already has a valuefile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.

  * Finds all labels, tries to match `label_text` (normalized) in each label’s text (including span children).

  * Once the matching label is found, gets its `for` attribute (which is the id of the input).

  * Finds that input element by ID and inspects its value:

    * If it’s an `<input>` and `value` is non-empty, returns True.

    * If it’s a `<select>` (dropdown) and a value is selected (and not the default placeholder), returns Truefile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.

    * Otherwise False.

* **`get_input_element_for_question(driver, label_text) -> (WebElement | list[WebElement], str)`**: This crucial function locates the form control(s) for a given question labelfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v (detailed in the workflow above):

  * It tries to find a `<label>` whose text matches the question and then the element with `id` equal to that label’s `for` attributefile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.

  * Determines the type: if it’s an `<input>` it differentiates radio vs checkbox vs others by the `type` attributefile-cbpbgd36qo2m1wv474et6v; returns e.g. ("input", "radio", etc.).

  * If a matching label isn’t found, it then checks for a `<legend>` in fieldsetsfile-cbpbgd36qo2m1wv474et6v. If a legend matches, it retrieves all radio/checkbox inputs under that fieldset and returns them as a list with type `"group_radio"` or `"group_checkbox"`file-cbpbgd36qo2m1wv474et6v.

  * Returns (None, None) if nothing found.

* **`get_format_error_message(driver, input_element) -> str | None`**: Given an input element that was just filled, checks if there’s a validation error message associated with itfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. If the element has an `aria-describedby` attribute pointing to an error container, it retrieves that container’s text (which LinkedIn uses for messages like “Please enter a valid value”). Returns the message or None if no error.

* **`fill_in_answer(driver, element, el_type, answer, question_text) -> str | None`**: Inputs the `answer` into the given form field elementfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v.

  * For text inputs and textareas: clears the field, types the answer, then sends a `TAB` key to move focus (which often triggers validation)file-cbpbgd36qo2m1wv474et6v.

  * For `<select>` dropdowns: iterates through `select.options` to find one that contains the answer text (case-insensitive) and selects itfile-cbpbgd36qo2m1wv474et6v. If none match, logs a warning.

  * For radio/checkbox: currently not implemented in this function (it prints a TODO warning) because those are handled via `handle_radio_or_select` earlierfile-cbpbgd36qo2m1wv474et6v.

  * After attempting to fill, it calls `get_format_error_message(driver, element)` to see if any error was provokedfile-cbpbgd36qo2m1wv474et6v. If an error message is found, it logs the error and returns the message stringfile-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. If no error, it returns None indicating success.

* **`ADDRESS_KEYWORDS`** (constant list): Contains a comprehensive set of terms that indicate address fields (street, city, postal code, etc.)file-cbpbgd36qo2m1wv474et6vfile-cbpbgd36qo2m1wv474et6v. This is used by the GPT prompt logic to detect address-related questions as described.

These utilities are not usually called directly by the main script, but by the higher-level functions in `utils_collect_questions.py`. They encapsulate the Selenium DOM interactions and form-specific logic. For example, `find_and_click_next`, `get_input_element_for_question`, and `fill_in_answer` are fundamental for navigating and filling the form.

### **Other Utility Modules**

In addition to the core modules above, the project likely includes several other helper files. Based on the import statements in the main script, these include:

* **utils\_login.py** – Handles LinkedIn authentication.

  * **Function: `linkedin_login(driver)`**: Opens LinkedIn’s login page and signs in the user. Implementation may use Selenium to find the username and password fields, input credentials, and submit. Credentials might be stored in environment variables or prompted. After login, it’s a good idea to reuse the session cookies (the main script saves them to `linkedin_cookies.pkl` for reuse)file-ezfwzkshpzjeqitapwsjlo.

  * This module might also check if cookies exist and load them to skip login if already logged in. (Developers can extend it to avoid repeated logins).

* **utils\_get\_oferts.py** – Scraping job details (the name suggests “get offers” with a Spanish twist).

  * **Function: `get_job_offers(driver)`** (possibly): Could collect job card links or IDs from a listing page (though in our main loop, they did it manually).

  * **Function: `parse_linkedin_job(html) -> dict`**: Parses the HTML of a job details panelfile-ezfwzkshpzjeqitapwsjlo and returns a structured dictionary. Likely uses an HTML parser or regex to extract:

    * `job['title']`, `job['job_id']` (the LinkedIn job ID can be parsed from the HTML or URL), `job['full_description']` (the text of the job description), `job['cities_available']` (maybe a list of locations if the job is in multiple locations, or just one city).

    * `company['name']` and possibly company ID or LinkedIn company page.

    * Maybe other fields like employment type, etc., if needed for cover letters or context.

  * This function is important because it provides context used by other parts (e.g., cover letter generation might use the job title and company name from this data).

* **utils\_move.py** – Functions to mimic human-like scrolling and waiting.

  * **`human_sleep(min_sec, max_sec)`**: Just uses `time.sleep` for a random duration between `min_sec` and `max_sec`. This is used throughout to avoid being too robotic and to give time for page loadsfile-ezfwzkshpzjeqitapwsjlofile-ezfwzkshpzjeqitapwsjlo.

  * **`gentle_scroll(driver, element)`**: Scrolls the page such that the given element is in view (likely via `execute_script("arguments[0].scrollIntoView({...});", element)`). Used when an element is not initially visiblefile-ezfwzkshpzjeqitapwsjlo.

  * **`smart_scroll_jobs_list(driver)`**: Specifically scrolls the job listing sidebar to load more jobs. Possibly scrolls to bottom multiple times until no new jobs load, or scrolls in steps with delaysfile-ezfwzkshpzjeqitapwsjlo. Ensures all job cards on the page are present in the DOM for collection.

  * These are utility functions to improve reliability of element interactions.

* **utils\_next\_page.py** – Functions for page navigation and final submission.

  * **`go_to_next_page(driver) -> bool`**: Locates and clicks the pagination “next page” button on a job search results pagefile-ezfwzkshpzjeqitapwsjlo. If on the last page, returns False. Might use an XPath like `//button[@aria-label="Next"]` or a CSS selector for the pagination arrow.

  * **`close_easy_apply_modal_if_open(driver)`**: Checks if an Easy Apply modal is currently open and, if so, closes it (perhaps by clicking the X or “Discard”). The main script calls this before page navigationfile-ezfwzkshpzjeqitapwsjlo to ensure a clean state.

  * **`close_any_open_modals(driver)`**: A more general modal closer used when job clicks are interceptedfile-ezfwzkshpzjeqitapwsjlo. Could close things like cookie banners or other pop-ups.

  * **`click_review_and_submit_and_log(driver, job_data, csv_path)`**: Called when the final review step is reachedfile-r1jtdw6ih6yna1fknbvpay. This likely:

    * Clicks the “Submit” button to send the application.

    * Logs the submitted job info to the specified CSV (in this case, `data/errors/_submitted_jobs.csv`). The naming suggests it might record jobs that were submitted or note any errors encountered. Logging ensures that if the script is run again, it could skip already-applied jobs (though that skip logic would need to be implemented in `get_job_offers` or main loop by checking this log).

    * It might also update `job_data` to mark it as submitted.

  * These functions are important for multi-page handling and to finalize applications.

* **utils\_save.py** – Functions to save output data.

  * **`save_jobs_data_to_json(jobs_data)`**, **`save_jobs_data_to_csv(jobs_data)`**: Accept the list of all job data dictionaries and write them to a JSON file and a CSV file, respectivelyfile-ezfwzkshpzjeqitapwsjlo. This provides a record of all jobs processed and their details.

  * **`save_questions_to_csv(job_id, questions_dict)`**: Likely appends the Q\&A for a single job to a CSV file. It might save to a file like `answered_questions.csv` or include the job\_id in the filename. From usage, it is called right after a job’s questions are answeredfile-ezfwzkshpzjeqitapwsjlo. It could either:

    * Append to a global “all questions answered” file (like the `CACHE_answered_questions_linke.csv` but that’s for caching, not for logging all in one run), or

    * Save a separate CSV per job (e.g., named by job\_id).

  * The implementation would simply iterate the `questions_dict` and write each question and answer (and maybe question type) to CSV. Since caching already stores Question/Type/Answer globally, `save_questions_to_csv` might be redundant or is meant for separate logging.

* **utils\_cover\_letter.py** – Cover letter generation and upload.

  * **`generate_cover_letter_text(job_data, assistant)`**: Uses the GPT assistant to create a cover letter string tailored to the job. Likely uses `job_data['job']['title']`, `job_data['company']['name']`, maybe `job_data['job']['full_description']` for context, along with the candidate’s profile info (from the vector store). It might have a predefined prompt template for cover letters, instructing GPT to produce a short letter addressed to the company team, highlighting relevant skills.

  * **`save_cover_letter_to_doc(text, job_id, company_name)`**: Saves the generated cover letter text to a .docx file (possibly using `python-docx` or a simple template). It might store files in a folder, e.g., `Data/cover_letters/`.

  * **`upload_cover_letter(driver, file_path)`**: Finds the file input for cover letter on the form and performs `send_keys(file_path)` to attach the file. Possibly also clicks any confirmation if needed.

  * **`click_cover_letter_upload_if_present(driver) -> bool`**: Checks the form for a “Upload cover letter” option (e.g., a checkbox or button that enables the file input). If present, clicks it to open the file dialog (to then use `upload_cover_letter`). Returns True if such an option was found. (This might also be part of `utils_collect_questions_Utils.py` but given the import in `utils_collect_questions.py`, it seems to come from `utils_cover_leter` which likely contains these cover-letter-related functions.)

Each of these utility modules plays a supporting role. When deploying or modifying this project, a developer might update:

* **Login logic** (in `utils_login.py`) to handle multi-factor or to reuse cookies.

* **Parse logic** (in `utils_get_oferts.py`) if LinkedIn’s HTML structure changes.

* **Answer prompts** (in `GPT_Assistant_utils.py` and `utils_cover_letter.py`) to fine-tune how GPT responds.

* **Resume/cover letter selection** (in `utils_collect_questions_Utils.py`) to match their available files or languages.

* **Limits and delays** (in `utils_move.py` and main script) to avoid detection or rate limiting by LinkedIn.

The code is structured to separate these concerns, making it easier to adjust one aspect without breaking others.

## **Running the Agent and Command-Line Usage**

To run the LinkedIn Auto-Apply GPT Agent, ensure you have completed the setup in terms of API keys and credentials as described. Then use the following steps:

**Start the script:** In a terminal, run:

 `python 02_Run_get_question_and_chatLinke.py`

1.  This will launch the Chrome browser via Selenium. A GUI window may appear (unless you’ve configured headless mode).

2. **Log in:** The script will automatically attempt to log in using `linkedin_login`. If it’s not automated, you may see the LinkedIn login page – in that case, enter your credentials manually in the browser window. Once logged in, the script will detect and proceed (and save cookies for next time).

3. **Navigate to Jobs:** If the script doesn’t automatically load a jobs page, go to a LinkedIn job search or the “Jobs” tab where a list of relevant job postings is visible. For example, go to **Jobs \-\> Recommended for you**, or perform a job search with the filters you want (e.g., specific title, location, Easy Apply on). Once the job cards are visible, the script will pick up and start scrolling.

4. **Automation in action:** The script will scroll and begin iterating through each job posting. In the console/log output, you will see messages like “Scraping job 1/10: \<Job Title\>” as it processes each job. If Easy Apply is available, you’ll see messages about uploading resume/cover letter, Q\&A for each question, and ultimately a message when an application is submitted (or when it moves to next page). If it’s an external apply, you’ll see a message that the HTML was saved and it will skip to the next job.

5. **Completion:** Let it run until it either finishes all pages or you manually stop it. All along, it will create/update output files:

   * **Scraped jobs data** in JSON and CSV (e.g., `jobs_data.json`, `jobs_data.csv`) – containing fields for each job and whether it was applied or external.

   * **Answered questions log** (e.g., `CACHE_answered_questions_linke.csv` and/or a separate file via `save_questions_to_csv`) – with each question and the answer given. The cache file will persist for next runs.

   * **Submitted jobs log** (`_submitted_jobs.csv` in `data/errors/`) – listing jobs that were fully applied. You can use this to avoid duplicate applications later.

   * **External pages** saved in `Data/solicitud_external/` – for your reference, the full HTML of any external application pages encountered.

   * **Cover letters** in whatever location `save_cover_letter_to_doc` uses (possibly a `cover_letters` folder) for each job that needed one.

6. **Close:** The script will close the browser at the end. You can then inspect the output files for results.

Remember that this tool operates on your live LinkedIn account; be mindful of LinkedIn’s usage limits and policies. It’s wise to test with a small number of jobs first and perhaps use a secondary account. Also, ensure the data in the vector store (your CV and related info) is up-to-date and relevant, as GPT’s answers are only as good as the context it has.

## **API Key and Vector Store Setup**

To reiterate configuration details specifically for the GPT integration:

* **OpenAI API Key:** The file path for the API key is provided when instantiating `LuisAssistant`. By default it’s `"chatGPT/agente.txt"`file-r1jtdw6ih6yna1fknbvpay – you can create this path and place your API key string inside (no quotes, just the key). Alternatively, you can modify the code to load from an environment variable or a different file path as preferred.

* **OpenAI API Client:** The code uses `openai.OpenAI` or a similar client. Ensure you have the latest OpenAI Python package installed. The usage of `responses.create` with tools suggests a special interface (possibly OpenAI’s **Beta** retrieval-enabled endpoint or an enterprise feature). If this is not available to you, you might need to adapt the code to use standard `openai.ChatCompletion.create` calls with the documents manually provided in the prompt. However, assuming you do have access, keep the same structure and just provide the correct `vector_store_id`.

* **Vector Store Preparation:** The `vector_store_id` ties to a collection of documents (likely the candidate’s CV, project descriptions, Q\&A transcripts, etc.). To set this up:

  * If using OpenAI’s system: go to your OpenAI file or fine-tuning section where you can upload documents or create a vector index (this might be an internal tool, as of now OpenAI’s public API doesn’t directly offer a persistent vector store by ID without plugins). Possibly this project was using an OpenAI **Plugin** or Azure Cognitive Search behind the scenes. You may need to adjust this to your environment.

  * Alternatively, you can replace the vector store mechanism with your own retrieval. For example, integrate LangChain to do similarity search on documents and add the top results into the GPT prompt.

  * The simplest way if not replicating the exact vector store: concatenate your resume and other supporting text into a single string and pass it in each question prompt (e.g., as part of the system or user prompt). That would eliminate the need for `vector_store_id` but still give GPT context. This requires more custom coding but is an option for those without the specialized API.

**Testing GPT Responses:** It’s recommended to test the `LuisAssistant.ask()` function independently with a known prompt to verify it’s working. For example:

 `assistant = LuisAssistant("chatGPT/agente.txt")`  
`print(assistant.ask("Hello, how are you?"))`

*  If configured correctly, this should return a GPT response. If there’s an error about the model or vector store, double-check the model name (`"gpt-4o-mini"` might need to be replaced with a model you have access to, like `"gpt-3.5-turbo"` or `"gpt-4"` if you have access, and remove the tools parameter if not supported).

**Note:** The `vector_store_id` and model can be configured in `GPT_Assistant.py` without modifying other files. This separation means you can point the agent to a different knowledge base or model by editing just that file. Make sure the ID is kept private (don’t commit your key or vector ID to source control).

## **Sample Prompt Template**

When priming the GPT agent to answer questions about the candidate, it helps to provide a clear initial instruction or system prompt. In this project, the relevant information (CV details, projects, etc.) is supplied via the vector store, and the prompting logic in code is minimal (it adds format instructions as needed). However, a developer may want to use a custom prompt template for consistency.

Here is a **downloadable sample prompt template** (as a text snippet) that could be used as a system message or at the start of the conversation to guide the GPT agent:

pgsql  
`You are an AI assistant helping to fill out job application forms for a candidate named Luis Lecinana. You have access to the candidate's resume and related documents for reference.`   
`Answer any questions in the application form concisely and professionally, using **only** information from the candidate's provided documents.`   
`- If a question asks for a number or a yes/no, respond with just that without extra commentary.`  
`- If an address or contact detail is required, provide a fictional but plausible answer consistent with the candidate’s location.`  
`- For cover letters, draft a short, polite letter addressed to the hiring team (e.g., "Dear {Company} Team,") mentioning the candidate’s relevant experience.`  
`The tone of all answers should be conversational yet formal (no slang, no emojis). Remain brief and to the point.`

Save this text to a file (for example, `prompt_template.txt`) if you wish to use it. In the code, you could then load it and include it as a system prompt in the `assistant.ask()` call (by adjusting the `inputs` list to include a system role with this content). The current implementation mainly uses the vector store to provide context, but adding a directive like this can help maintain consistency in style and constraints.

*This prompt template is a distilled version of the project instructions, ensuring the GPT agent stays on-topic and uses the candidate’s background. Developers can modify it as needed for different candidates or to enforce different answer styles.*

