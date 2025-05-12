import pickle
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Datos de login
LINKEDIN_EMAIL = "x.xxxx@gmail.com"
LINKEDIN_PASSWORD = "XXXXXXXXXXXX"
COOKIES_FILE = "linkedin_cookies.pkl"

def linkedin_login(driver):
    driver.get("https://www.linkedin.com/")
    time.sleep(2)

    # Si tenemos cookies, intentamos cargarlas
    if os.path.exists(COOKIES_FILE):
        print("Cargando cookies guardadas...")
        cookies = pickle.load(open(COOKIES_FILE, "rb"))
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception:
                pass  # Algunas cookies pueden fallar si son de otra sesión
        driver.refresh()
        time.sleep(3)

        # Comprobamos si la sesión sigue activa
        if "feed" in driver.current_url or "jobs" in driver.current_url:
            print("Sesión restaurada con cookies.")
            return
        else:
            print("Las cookies no son válidas. Haciendo login manual...")

    # Hacer login manual
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    try:
        email_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")

        email_input.clear()
        email_input.send_keys(LINKEDIN_EMAIL)

        password_input.clear()
        password_input.send_keys(LINKEDIN_PASSWORD)
        password_input.send_keys(Keys.RETURN)

        time.sleep(5)

        # Guardar cookies después de login exitoso
        print("Guardando cookies nuevas...")
        pickle.dump(driver.get_cookies(), open(COOKIES_FILE, "wb"))
        print("Login realizado y cookies guardadas.")

    except Exception as e:
        print(f"Error en login manual: {e}")
