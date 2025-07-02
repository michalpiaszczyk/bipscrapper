import asyncio
import sqlite3
from datetime import datetime, timedelta
from tqdm import tqdm
import cvs_bip
import cvs_sele

DB_PATH = "oferty_pracy.db"
OUTPUT_FILE = f"nowe_oferty_{datetime.today().strftime('%Y-%m-%d')}.txt"

def clean_old_entries(cursor):
    one_year_ago = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
    cursor.execute("DELETE FROM oferty WHERE data_pobrania < ?", (one_year_ago,))
    return cursor.rowcount

def save_offers_to_db_and_file(cursor, conn, all_offers, today_str):
    import sqlite3

def save_offers_to_db_and_file(cursor, conn, all_offers, today_str):
    new_entries = []
    skipped = 0

    for offer in tqdm(all_offers, desc="💾 Zapis do bazy"):
        try:
            cursor.execute("""
                INSERT INTO oferty (nazwa_stanowiska, link, data_pobrania, zrodlo_url)
                VALUES (?, ?, ?, ?)
            """, (offer["nazwa_stanowiska"], offer["link"], today_str, offer["zrodlo_url"]))
            new_entries.append(offer)
        except sqlite3.IntegrityError:
            skipped += 1  # Zliczanie duplikatów, które już istnieją w bazie

    conn.commit()

    if new_entries:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            for oferta in new_entries:
                tekst = f"- {oferta['zrodlo_url']} | {oferta['nazwa_stanowiska']}\n  {oferta['link']}\n"
                print(tekst.strip())
                f.write(tekst + "\n")
        print(f"\n📁 Zapisano {len(new_entries)} nowych ofert do pliku: {OUTPUT_FILE}")
    else:
        print("\nℹ️ Brak nowych ogłoszeń.")

    return len(new_entries), skipped

async def main():
    today_str = datetime.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS oferty (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nazwa_stanowiska TEXT,
        link TEXT UNIQUE,
        data_pobrania TEXT,
        zrodlo_url TEXT
    )
    """)

    deleted = clean_old_entries(cursor)
    print(f"🗑 Usunięto przestarzałe wpisy: {deleted}")

    # Pobierz oferty z BIP i Selenium
    loop = asyncio.get_running_loop()
    oferty_bip, oferty_sele = await asyncio.gather(
        cvs_bip.get_new_offers(),
        loop.run_in_executor(None, cvs_sele.get_new_offers)
    )

    all_offers = oferty_bip + oferty_sele
    total_added, total_skipped = save_offers_to_db_and_file(cursor, conn, all_offers, today_str)

    # Podsumowanie
    print("\n📊 Podsumowanie:")
    print(f"✅ Łącznie dodano: {total_added}")
    print(f"⚠️ Łącznie pominięto (duplikaty): {total_skipped}")

    conn.close()

if __name__ == "__main__":
    asyncio.run(main())
