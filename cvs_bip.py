import asyncio
import aiohttp
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
from aiohttp import ClientConnectorCertificateError

URL_LIST = [
    "https://bip.bialeblota.pl/oferty-pracy/22",
    "https://bip.osielsko.pl/oferty-pracy/982",
    "https://bip.sicienko.pl/oferty-pracy/587",
    "https://bip.nowawieswielka.pl/oferty-pracy/22",
    "https://bip.um.bydgoszcz.pl/oferty-pracy/1174"
]

URL_LIST_2 = ['https://bip.powiat.bydgoski.pl/kategorie/469-2025?lang=PL','https://bip.powiat.bydgoski.pl/kategorie/117-inne-ogloszenia?lang=PL']

source_map = {
    "https://bip.bialeblota.pl/oferty-pracy/22": "Urząd Białe Błota",
    "https://bip.osielsko.pl/oferty-pracy/982": "Urząd Osielsko",
    "https://bip.sicienko.pl/oferty-pracy/587": "Urząd Sicienko",
    "https://bip.nowawieswielka.pl/oferty-pracy/22": "Urząd Nowa Wieś Wielka",
    "https://bip.um.bydgoszcz.pl/oferty-pracy/1174": "Urząd Miasta Bydgoszcz",
    "https://bip.powiat.bydgoski.pl/kategorie/469-2025?lang=PL": "Powiat Bydgoski",
    "https://bip.powiat.bydgoski.pl/kategorie/117-inne-ogloszenia?lang=PL": "Powiat Bydgoski - inne ogłoszenia"
}

async def fetch_page(session, url):
    zrodlo = source_map.get(url, url)  # nazwa urzędu albo URL jeśli nieznany
    try:
        async with session.get(url) as response:
            html = await response.text()
            return html, url
    except ClientConnectorCertificateError:
        print(f"⚠️  Błąd certyfikatu SSL przy {zrodlo}, próbuję ponownie bez SSL...")
        try:
            async with session.get(url, ssl=False) as response:
                html = await response.text()
                return html, url
        except:
            print(f"❌ Nie udało się połączyć z {zrodlo} (ssl=False)")
            return None, url
    except Exception as e:
        print(f"❌ Nie udało się połączyć z {zrodlo} – {e}")
        return None, url


async def process_page(html, url, today_str):
    results = []
    if html is None:
        return results
    zrodlo = source_map.get(url, "Nieznane źródło")
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table", class_="table table-borderless")
    for table in tables:
        caption = table.find("caption", class_="visuallyhidden")
        link_tag = table.find("a", href=True)
        if caption and link_tag:
            nazwa = caption.get_text(strip=True)
            link = link_tag["href"]
            results.append({
                "zrodlo_url": zrodlo,
                "nazwa_stanowiska": nazwa,
                "link": link,
                "data_pobrania": today_str
            })
    return results

async def process_powiat_page(html, url, today_str):
    results = []
    if html is None:
        return results
    zrodlo = source_map.get(url, "Nieznane źródło")
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        tytul = a.get_text(strip=True)
        href = a["href"]
        if any(kw in tytul.lower() for kw in ["nabór", "stanowisko", "ogłoszenie", "urządnicze"]):
            results.append({
                "zrodlo_url": zrodlo,
                "nazwa_stanowiska": tytul,
                "link": href,
                "data_pobrania": today_str
            })
    return results

async def get_new_offers():
    today_str = datetime.today().strftime("%Y-%m-%d")
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, url) for url in URL_LIST]
        pages = await asyncio.gather(*tasks)
        offers = []
        for html, url in pages:
            offers += await process_page(html, url, today_str)

        tasks2 = [fetch_page(session, url) for url in URL_LIST_2]
        pages2 = await asyncio.gather(*tasks2)
        for html, url in pages2:
            offers += await process_powiat_page(html, url, today_str)

        return offers
