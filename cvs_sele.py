from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from datetime import datetime
import time

URL = "https://praca.asseco.pl/OfertyWyszukiwanie"
ZRODLO = "Asseco"

def get_new_offers():
    today_str = datetime.today().strftime("%Y-%m-%d")
    results = []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gcm")  # Wyłączenie GCM
    options.add_argument("--incognito")  # Tryb incognito
    options.add_argument("--disable-blink-features=AutomationControlled")  # Ukrycie WebDrivera

    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(45)
        driver.get(URL)
        time.sleep(3)

        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        oferta_divs = soup.find_all("a", class_="glowny-aplikuj", href=True)

        for a_tag in oferta_divs:
            href = a_tag["href"]
            full_link = "https://praca.asseco.pl" + href
            parent = a_tag.find_parent("div", class_="oferta-box")
            if parent:
                stanowisko = parent.find("div", class_="RekrutacjaNazwa-element")
                if stanowisko:
                    nazwa = stanowisko.get_text(strip=True)
                    results.append({
                        "zrodlo_url": ZRODLO,
                        "nazwa_stanowiska": nazwa,
                        "link": full_link,
                        "data_pobrania": today_str
                    })

    except WebDriverException as e:
        print(f"❌ Nie udało się połączyć z {ZRODLO} – {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

    return results
