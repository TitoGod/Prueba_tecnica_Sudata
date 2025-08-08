# Ejercicio 3: Scraper de terrenos en Argenprop (2 páginas)
# Este script raspa terrenos en venta en Posadas desde Argenprop, extrayendo
# información de las tarjetas de propiedades y guardándola en un CSV.
# Utiliza Selenium para navegar y extraer datos de la web.

# Importar librerías necesarias
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------------------------- CONFIG --------------------------------
URL = "https://www.argenprop.com/terrenos/venta/posadas"
HEADLESS = True   # False para ver el navegador
CSV_OUTPUT = "terrenos_argenprop_posadas.csv"
TIMEOUT = 12
# ------------------------------------------------------------------------

def init_driver(headless=True):
    """
    Inicializa y configura el driver de Chrome para Selenium.
    
    Parámetros:
        headless (bool): Si es True, ejecuta Chrome en modo 'sin ventana' (headless).
    
    Retorna:
        driver (webdriver.Chrome): Instancia de Chrome lista para navegar.
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Ocultar propiedad 'navigator.webdriver' para evitar detección de bots
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
        )
    except Exception:
        pass

    return driver

def close_cookies_if_present(driver):
    """
    Busca y cierra banners o popups de cookies si están presentes.
    
    Parámetros:
        driver (webdriver.Chrome): Driver de Selenium activo.
    """
    # XPaths que buscan variaciones de botones de aceptación de cookies
    xpaths = [
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'acept')]",
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'consent')]",
        "//button[contains(translate(., 'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'ACEPTAR')]"
    ]
    for xp in xpaths:
        try:
            btn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, xp)))
            btn.click()
            time.sleep(0.6)
            break
        except Exception:
            continue

def scroll_page(driver):
    """
    Realiza un scroll progresivo por la página para asegurar carga de contenido dinámico.
    
    Parámetros:
        driver (webdriver.Chrome): Driver de Selenium activo.
    """
    try:
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.25);")
        time.sleep(0.8)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
        time.sleep(0.8)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.0 + random.random() * 0.6)
    except Exception as e:
        print("[warn] scroll_page error:", e)


def extract_cards_on_page(driver):
    """
    Extrae información de todas las tarjetas de propiedades encontradas en la página actual.
    
    Datos extraídos:
        - precio_raw: Texto del precio sin símbolo de moneda.
        - moneda: Símbolo o nombre de la moneda.
        - ubicacion: Dirección o ubicación de la propiedad.
        - titulo_primary: Título principal del aviso.
        - detalle_url: Enlace a la página de detalle de la propiedad.
    
    Parámetros:
        driver (webdriver.Chrome): Driver de Selenium activo.
    
    Retorna:
        results (list[dict]): Lista de diccionarios con datos de cada tarjeta.
    """
    results = []

    # Esperar que el body esté cargado
    try:
        WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception:
        pass

    # Cerrar cookies si aparecen
    close_cookies_if_present(driver)

    # Scroll para cargar contenido dinámico
    scroll_page(driver)

    # Intentar encontrar tarjetas por selectores conocidos
    try:
        cards = driver.find_elements(By.CSS_SELECTOR, "div.card__details-box")
    except Exception:
        cards = []

    if not cards:
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, "article, div.card")
        except Exception:
            cards = []

    print(f"[Info] Tarjetas encontradas en la página: {len(cards)}")

    # Recorrer cada tarjeta encontrada
    for idx, card in enumerate(cards, start=1):
        try:
            # --- PRECIO ---
            price_number = None
            currency = None
            try:
                p_price = card.find_element(By.CSS_SELECTOR, "p.card__price")
                full_price = p_price.text.strip()
                try:
                    currency = p_price.find_element(By.CSS_SELECTOR, "span.card__currency").text.strip()
                    price_number = full_price.replace(currency, "").strip()
                except Exception:
                    price_number = full_price
            except Exception:
                price_number = None
                currency = None

            # --- UBICACIÓN ---
            ubicacion = None
            try:
                p_address = card.find_element(By.CSS_SELECTOR, "p.card__address")
                addr_data = p_address.get_attribute("data-card-direccion")
                addr_text = p_address.text.strip()
                ubicacion = addr_data.strip() if addr_data and addr_data.strip() else addr_text
            except Exception:
                ubicacion = None

            # --- TÍTULO PRINCIPAL ---
            titulo_primary = None
            try:
                titulo_primary = card.find_element(By.CSS_SELECTOR, "p.card__title--primary").text.strip()
            except Exception:
                titulo_primary = None

            # --- LINK DETALLE ---
            link = None
            try:
                a = card.find_element(By.XPATH, ".//ancestor::a[1]")
                if a:
                    link = a.get_attribute("href")
            except Exception:
                # intentar buscar 'a' dentro del contenedor principal
                try:
                    a2 = card.find_element(By.CSS_SELECTOR, "a[href]")
                    link = a2.get_attribute("href")
                except Exception:
                    link = None

            # Guardar datos de la tarjeta
            results.append({
                "precio": price_number,
                "moneda": currency,
                "ubicacion": ubicacion,
                "titulo": titulo_primary,
                "detalle_url": link
            })

            # Pequeña pausa aleatoria para simular comportamiento humano
            time.sleep(random.uniform(0.3, 0.6))

        except Exception as e:
            print(f"[Advertencia] Error extrayendo tarjeta #{idx}: {e}")
            continue

    return results


def click_next_page(driver):
    """
    Intenta hacer clic en el botón o enlace 'Siguiente' para pasar a la próxima página.
    
    Parámetros:
        driver (webdriver.Chrome): Driver de Selenium activo.
    
    Retorna:
        bool: True si se hizo clic y la página cambió, False si no se encontró o no se pudo.
    """
    try:
        # Primero intentar por aria-label
        next_btn = None
        try:
            next_btn = driver.find_element(By.XPATH, "//a[@aria-label='Siguiente' or @rel='next']")
        except Exception:
            # buscar por texto 'Siguiente' dentro de etiquetas <a>
            try:
                next_btn = driver.find_element(By.XPATH, "//a[contains(., 'Siguiente') and (contains(@rel,'next') or @aria-label)]")
            except Exception:
                next_btn = None

        if next_btn:
            # Hacer scroll para que el botón sea visible
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", next_btn)
            time.sleep(0.4)
            try:
                next_btn.click()
            except Exception:
                # fallback click via JS
                driver.execute_script("arguments[0].click();", next_btn)
            # Esperar que cambie la URL o que el body vuelva a cargarse
            time.sleep(1.0 + random.random()*1.0)
            WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("[Info] Click en 'Siguiente' realizado.")
            return True
        else:
            print("[Info] No se encontró botón 'Siguiente'.")
            return False
    except Exception as e:
        print("[Advertencia] Error al hacer click en 'Siguiente':", e)
        return False


def main():
    """
    Función principal:
        - Abre la URL inicial.
        - Extrae tarjetas de la primera y segunda página (máx. 40 registros).
        - Guarda resultados en un CSV.
    """
    driver = init_driver(HEADLESS)
    all_data = []
    try:
        # Página 1
        print(f"[Navegando] {URL}")
        driver.get(URL)
        data_page1 = extract_cards_on_page(driver)
        print(f"[Info] Extraídos de página 1: {len(data_page1)}")
        all_data.extend(data_page1)

        # Intentar click en 'Siguiente' y raspar página 2
        if click_next_page(driver):
            # asegurar que cargó
            time.sleep(1.5)
            data_page2 = extract_cards_on_page(driver)
            print(f"[Info] Extraídos de página 2: {len(data_page2)}")
            all_data.extend(data_page2)
        else:
            print("[Info] No se pudo avanzar a la segunda página.")

        # limitar a 40 si quedaron más (por seguridad)
        if len(all_data) > 40:
            all_data = all_data[:40]

        # Guardar resultados en CSV
        df = pd.DataFrame(all_data)
        df.to_csv(CSV_OUTPUT, index=False, encoding="utf-8")
        print(f"[OK] Guardado CSV -> {CSV_OUTPUT} (Filas: {len(df)})")
        print(df.head(10))

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
