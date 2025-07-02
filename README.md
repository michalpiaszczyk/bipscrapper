# bipscrapper
Scrapper ofert pracy 
Co robi narzędzie?

Aplikacja codziennie zbiera oferty pracy ze stron BIP oraz z portali prywatnych firm, zapisuje je do bazy danych SQLite, ignorując duplikaty, a także zapisuje nowe ogłoszenia do pliku tekstowego. Oferty starsze niż rok są automatycznie usuwane.

🌐 Z jakich stron pobiera dane?
•	Portale BIP gmin i powiatów
•	Portal firm prywatnych
•	
🖼️ Jak je wyświetla / zapisuje?

Nowe ogłoszenia są drukowane na konsoli i zapisywane w pliku .txt, zawierającym źródło, nazwę stanowiska i link. Dane trafiają również do bazy SQLite z unikalnym kluczem link, aby unikać duplikatów.

![Zrzut ekranu 2025-07-02 172356](https://github.com/user-attachments/assets/98e6757b-8792-4cdc-aa40-f90a7d2a5eb6)


🛠️ Jakie narzędzia zostały użyte?
•	Python – język programowania
•	SQLite – baza danych ofert
•	Selenium – automatyzacja przeglądarki 
•	aiohttp + asyncio – równoległe pobieranie treści ze stron BIP
•	BeautifulSoup – analizowanie struktury HTML ofert
•	tqdm – pasek postępu przy zapisie do bazy
