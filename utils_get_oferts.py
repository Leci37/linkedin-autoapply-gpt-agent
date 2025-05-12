from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from langdetect import detect

def get_job_offers(driver):
    jobs = []

    try:
        # Esperamos que carguen las ofertas
        job_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.scaffold-layout__list-item"))
        )

        for card in job_cards:
            try:
                title_element = card.find_element(By.CSS_SELECTOR, "a.job-card-container__link")
                title = title_element.text.strip()
                link = title_element.get_attribute("href")

                company_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle")
                company = company_element.text.strip()

                location_element = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__caption")
                location = location_element.text.strip()

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link
                })
            except Exception as e:
                print(f"Error leyendo una tarjeta: {e}")

    except Exception as e:
        print(f"Error cargando la lista de empleos: {e}")

    return jobs

from bs4 import BeautifulSoup
import json

from bs4 import BeautifulSoup
import json

from bs4 import BeautifulSoup
import json

def parse_linkedin_job(html_content: str) -> dict:
    soup = BeautifulSoup(html_content, "html.parser")
    container = soup.find("div", class_="jobs-details__main-content")

    if not container:
        return {}

    # COMPANY INFO
    company_link_element = container.select_one(".job-details-jobs-unified-top-card__company-name a")
    company_name = company_link_element.get_text(strip=True) if company_link_element else ""
    company_link = company_link_element["href"] if company_link_element else ""

    company_logo_img = container.select_one(".ivm-view-attr__img-wrapper img")
    company_logo_url = company_logo_img["src"] if company_logo_img else ""

    followers_element = container.select_one(".artdeco-entity-lockup__subtitle")
    followers = followers_element.get_text(strip=True) if followers_element else ""

    # JOB INFO
    job_title_element = container.select_one("h1.t-24")
    job_title = job_title_element.get_text(strip=True) if job_title_element else ""

    location_element = container.select_one(".job-details-jobs-unified-top-card__primary-description-container span")
    location = location_element.get_text(strip=True) if location_element else ""

    offer_link_element = job_title_element.select_one("a") if job_title_element else None
    offer_link = offer_link_element["href"] if offer_link_element else ""

    offer_short_link = ""
    job_id = ""
    if offer_link_element and "view/" in offer_link_element["href"]:
        job_id = offer_link_element["href"].split("view/")[1].split("/")[0]
        offer_short_link = f"https://www.linkedin.com/jobs/view/{job_id}"

    description_text = container.select_one(".job-details-jobs-unified-top-card__primary-description-container")
    posted_time, applicants = "", ""
    if description_text:
        spans = description_text.find_all("span")
        if len(spans) >= 3:
            posted_time = spans[1].get_text(strip=True)
            applicants = spans[2].get_text(strip=True)

    # MODALITY AND SCHEDULE
    modality, schedule = "", ""
    insight_items = container.select("li.job-details-jobs-unified-top-card__job-insight")
    for item in insight_items:
        labels = item.select("span.ui-label")
        if labels:
            if any(x in labels[0].text.lower() for x in ["híbrido", "remoto", "presencial"]):
                modality = labels[0].text.strip()
            if len(labels) > 1:
                schedule = labels[1].text.strip()


    # EASY APPLY BUTTON
    easy_apply = container.select_one(".jobs-apply-button .artdeco-button__text")
    application_button_text = easy_apply.get_text(strip=True) if easy_apply else ""

    # NEW: Type of application
    application_type = "simple" if "solicitud sencilla" in application_button_text.lower() else "not_simple"

    # BUTTON AVAILABILITY
    save_offer_available = bool(container.select_one(".jobs-save-button"))
    share_offer_available = bool(container.select_one(".social-share__dropdown-trigger"))
    more_options_available = bool(container.select_one(".jobs-options button"))

    # DESCRIPTION FULL
    description_article = container.select_one("#job-details")
    description_text_full = description_article.get_text("\n", strip=True) if description_article else ""

    # RESPONSIBILITIES, REQUIREMENTS, BENEFITS
    responsibilities, requirements, desired_skills, soft_skills, benefits = [], [], [], [], []

    # --- NUEVO: descripción completa ---
    description_article = container.select_one("#job-details")
    description_text_full = description_article.get_text("\n", strip=True) if description_article else ""

    # --- NUEVO: detección de idioma ---
    description_language = ""
    if description_text_full.strip():
        try:
            detected_lang = detect(description_text_full)
            description_language = LANG_MAP.get(detected_lang.lower(), "Unknown")
        except Exception:
            description_language = "unknown"

    if description_text_full:
        if "Responsabilidades" in description_text_full:
            responsibilities = description_text_full.split("Responsabilidades")[1].split("Requisitos")[0].splitlines()

        if "Requisitos" in description_text_full:
            req_text = description_text_full.split("Requisitos")[1]
            if "Competencias deseadas" in req_text:
                requirements = req_text.split("Competencias deseadas")[0].splitlines()

        if "Competencias deseadas" in description_text_full:
            desired_text = description_text_full.split("Competencias deseadas")[1]
            if "Soft skills" in desired_text:
                desired_skills = desired_text.split("Soft skills")[0].splitlines()

        if "Soft skills" in description_text_full:
            soft_text = description_text_full.split("Soft skills")[1]
            if "¿Qué ofrecemos?" in soft_text:
                soft_skills = soft_text.split("\u00bfQué ofrecemos?")[0].splitlines()

        if "¿Qué ofrecemos?" in description_text_full:
            benefits_text = description_text_full.split("\u00bfQué ofrecemos?")[1]
            benefits = benefits_text.splitlines()

    # MATCHING SKILLS
    matching_skills_element = container.select_one(".job-details-how-you-match__skills-section-descriptive-skill")
    matching_skills = []
    if matching_skills_element:
        matching_skills = [skill.strip() for skill in matching_skills_element.get_text().split("\u00b7")]

    # PREMIUM OFFER
    premium_offer = ""
    premium_offer_element = container.select_one(".card-upsell-v2__headline")
    if premium_offer_element:
        premium_offer = premium_offer_element.get_text(strip=True)

    # COMPANY ABOUT
    company_about_description = ""
    company_about_element = container.select_one(".jobs-company__company-description div")
    if company_about_element:
        company_about_description = company_about_element.get_text(" ", strip=True)

    # SALARY
    salary_element = container.select_one("#SALARY")
    salary = salary_element.get_text(strip=True) if salary_element else ""

    # CITIES (optional, parsed from location)
    cities = []
    if location:
        cities = location.split("·")[0].strip()

    # HIRING TEAM INFO
    hiring_team = []
    hiring_section = container.select_one(".job-details-people-who-can-help__section--two-pane")
    if hiring_section:
        people = hiring_section.select(".display-flex.align-items-center.mt4")
        for person in people:
            name_element = person.select_one(".jobs-poster__name")
            name = name_element.get_text(strip=True) if name_element else ""

            profile_link_element = person.select_one("a")
            profile_link = profile_link_element["href"] if profile_link_element else ""

            description_element = person.select_one(".linked-area .text-body-small")
            description = description_element.get_text(strip=True) if description_element else ""

            message_button = person.select_one(".entry-point button")
            message_available = bool(message_button)

            hiring_team.append({
                "name": name,
                "profile_link": profile_link,
                "description": description,
                "message_available": message_available
            })

    # FINAL STRUCTURE
    job_data = {
        "company": {
            "name": company_name,
            "followers": followers,
            "logo_url": company_logo_url,
            "description": company_about_description,
            "link": company_link
        },
        "job": {
            "title": job_title,
            "location": location,
            "cities_available": cities,
            "posted_time": posted_time,
            "applicants": applicants,
            "modality": modality,
            "schedule": schedule,
            "application_button": application_button_text,
            "application_type": application_type,
            "save_offer_available": save_offer_available,
            "share_offer_available": share_offer_available,
            "more_options_available": more_options_available,
            "salary": salary,
            "link": offer_link,
            "short_link": offer_short_link,
            "job_id": job_id,
            "full_description": description_text_full,  # <<--- añadido
            "description_language": description_language  # <<--- añadido
        },
        "responsibilities": responsibilities,
        "requirements": {
            "mandatory_skills": requirements,
            "optional_skills": desired_skills,
        },
        "soft_skills": soft_skills,
        "benefits": benefits,
        "matching_skills": matching_skills,
        "premium_offer": premium_offer,
        "hiring_team": hiring_team
    }

    return job_data



LANG_MAP = {
    "af": "Afrikaans",
    "ar": "Arabic",
    "az": "Azerbaijani",
    "be": "Belarusian",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "ca": "Catalan",
    "cs": "Czech",
    "cy": "Welsh",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "et": "Estonian",
    "fa": "Persian",
    "fi": "Finnish",
    "fr": "French",
    "gu": "Gujarati",
    "he": "Hebrew",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ka": "Georgian",
    "kn": "Kannada",
    "ko": "Korean",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ne": "Nepali",
    "nl": "Dutch",
    "no": "Norwegian",
    "pa": "Punjabi",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "so": "Somali",
    "sq": "Albanian",
    "sv": "Swedish",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tl": "Tagalog",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
}



WORDS_JOB_APLICATION = [
    # Core Job Application Terms
    "resume", "CV", "cover letter", "job application", "interview", "recruiter",
    "job posting", "job description", "qualifications", "experience", "skills",
    "references", "networking", "portfolio", "job board", "LinkedIn", "Indeed",
    "Glassdoor", "hiring manager", "candidate", "vacancy", "employment", "career",
    "opportunity", "job offer", "background check", "follow-up", "salary",
    "negotiation", "position", "job fair", "submission", "rejection", "acceptance",
    "onboarding", "talent acquisition", "headhunter", "HR", "career site",
    "application portal", "ATS", "applicant tracking system",

    # Form Fields / Input Labels
    "Name", "First Name", "Last Name", "Full Name", "Preferred Name", "Middle Name", "Email",
    "Phone Number", "Alternate Phone", "Address", "Street Address", "City",
    "Other City", "State", "State/Province", "Zip Code", "Postal Code", "Country",
    "Location", "Current Location", "Preferred Location", "Citizenship", "Nationality",
    "Date of Birth", "Gender", "Pronouns", "Ethnicity", "Disability Status", "Veteran Status",

    # Employment & Work Eligibility
    "Need visa sponsorship?", "Work Authorization", "Are you authorized to work in this country?",
    "Are you currently authorized to work?", "Will you now or in the future require sponsorship?",
    "Available Start Date", "Earliest Start Date", "Current Employment Status", "Current Employer",
    "Previous Employer", "Employment History", "Years of Experience", "Relevant Experience",
    "Notice Period", "Willing to relocate?", "Willing to travel?",

    # Documents
    "Upload Resume", "Attach Resume", "Upload CV", "Attach Cover Letter", "Cover Letter (Optional)",
    "Supporting Documents", "Writing Sample", "Transcripts", "Certifications", "References List",
    "Portfolio URL", "Personal Website", "LinkedIn Profile", "GitHub", "Behance", "Dribbble",

    # Education
    "Education", "School", "University", "Degree", "Field of Study", "Graduation Year",
    "GPA", "Academic Transcript", "Major", "Minor", "Highest Level of Education",

    # Additional Questions & Fields
    "Desired Salary", "Expected Salary", "Referral", "Referred By", "How did you hear about us?",
    "Additional Information", "Why are you interested in this role?", "Why should we hire you?",
    "Tell us about yourself", "Diversity Questions", "Equal Opportunity", "EEO", "Demographic Survey",
    "Reasonable Accommodation", "Do you have any questions for us?", "Motivation", "Career Goals",
    "Relocation Assistance", "Languages Spoken", "Skills Assessment", "Typing Speed", "Availability"
]
PALABRAS_SOLICITUD_EMPLEO = [
    # Términos clave de solicitud de empleo
    "currículum", "CV", "carta de presentación", "solicitud de empleo", "entrevista",
    "reclutador", "oferta de trabajo", "descripción del puesto", "requisitos",
    "experiencia", "habilidades", "referencias", "red de contactos", "portafolio",
    "bolsa de trabajo", "LinkedIn", "Indeed", "Glassdoor", "responsable de selección",
    "candidato", "vacante", "empleo", "carrera profesional", "oportunidad",
    "oferta laboral", "verificación de antecedentes", "seguimiento", "salario",
    "negociación", "puesto", "feria de empleo", "envío", "rechazo", "aceptación",
    "incorporación", "adquisición de talento", "cazatalentos", "recursos humanos",
    "sitio de empleo", "portal de solicitudes", "ATS", "sistema de seguimiento de candidatos",

    # Campos del formulario
    "Nombre", "Apellido", "Nombre completo", "Nombre preferido", "Segundo nombre",
    "Correo electrónico", "Número de teléfono", "Teléfono alternativo", "Dirección",
    "Dirección completa", "Ciudad", "Otra ciudad", "Estado", "Provincia",
    "Código postal", "País", "Ubicación", "Ubicación actual", "Ubicación preferida",
    "Ciudadanía", "Nacionalidad", "Fecha de nacimiento", "Género", "Pronombres",
    "Etnicidad", "Condición de discapacidad", "Condición de veterano",

    # Autorización laboral
    "¿Necesita visa de patrocinio?", "Autorización de trabajo",
    "¿Está autorizado para trabajar en este país?",
    "¿Requiere patrocinio ahora o en el futuro?",
    "Fecha de inicio disponible", "Disponibilidad para empezar",
    "Estado laboral actual", "Empleador actual", "Empleador anterior",
    "Historial laboral", "Años de experiencia", "Experiencia relevante",
    "Período de preaviso", "¿Está dispuesto a reubicarse?", "¿Está dispuesto a viajar?",

    # Documentos
    "Subir currículum", "Adjuntar currículum", "Subir CV", "Adjuntar carta de presentación",
    "Carta de presentación (opcional)", "Documentos de respaldo", "Muestra de escritura",
    "Certificados", "Historial académico", "Lista de referencias", "Enlace al portafolio",
    "Sitio web personal", "Perfil de LinkedIn", "GitHub", "Behance", "Dribbble",

    # Educación
    "Educación", "Escuela", "Universidad", "Título", "Campo de estudio",
    "Año de graduación", "Promedio (GPA)", "Transcripción académica",
    "Especialización", "Subespecialización", "Nivel educativo más alto",

    # Preguntas adicionales
    "Salario deseado", "Expectativas salariales", "Recomendado por", "Referencia",
    "¿Cómo se enteró de esta vacante?", "Información adicional",
    "¿Por qué le interesa este puesto?", "¿Por qué deberíamos contratarle?",
    "Cuéntenos sobre usted", "Preguntas sobre diversidad", "Igualdad de oportunidades",
    "Encuesta demográfica", "¿Necesita ajustes razonables?", "¿Tiene preguntas para nosotros?",
    "Motivación", "Objetivos profesionales", "Ayuda con la reubicación",
    "Idiomas que habla", "Evaluación de habilidades", "Velocidad de escritura", "Disponibilidad"
]
