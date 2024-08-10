# Skrypty związane z bazą danych

Źródłem danych do tych skryptów są pliki .csv z wynikami na stronach Alkamelsystems.

W przypadku wygenerowanych plików .csv z danymi <ins>nie należy usuwać z nich nagłówków</ins>. Jeśli wartość tekstowa ma być pusta, to nie należy też usuwać cudzysłowów.

Wyjaśnienie oznaczeń nagłówków w plikach z wygenerowanymi danymi:
- codename — unikalna nazwa kierowcy/zespołu itd. na podstawie dokładnego zapisu nazwy w plikach zawierających wyniki, <ins>nie należy jej zmieniać</ins>
- link/short_link — odnośnik do artykułu na polskiej Wikipedii. Jeśli nie istnieje artykuł na Wikipedii, to z linku można usunąć podwójne nawiasy kwadratowe.
- long_link — odnośnik do elementu w portalu Wikidata. Nie wypełniać, jeśli istnieje artykuł na polskiej Wikipedii. Wykorzystywany jest przy wypisywaniu tabel z wynikami wyścigów, dzięki czemu Wikipedia podaje odnośniki do artykułów w innych językach (o ile istnieją).
- nationality — trzyliterowy kod państwa w formacie ISO 3166-1 alpha-3. W razie braku kolumny z flagą/braku kodu w bazie wypisany zostanie znak zapytania.

Pliki z wygenerowanymi danymi są zapisywane w katalogu ze skryptami. Jeśli nie zostaną przeniesione, to przy wybraniu opcji dodania danych do bazy skrypt automatycznie wykryje te pliki i zaproponuje dodanie ich zawartości do bazy.

Opis skryptów:
- **db_auta.py** — skrypt umożliwiający wygenerowanie pliku .csv z danymi o autach oraz dodanie ich do bazy danych. Do wygenerowania danych aut można skorzystać z dowolnego pliku .csv z wynikami tj. sesji testowej, treningowej, kwalifikacyjnej lub wyścigu.
  - przykładowy fragment pliku z prawidłowo wypełnionymi danymi:
  ```
  "codename","link"
  "Alpine A424","[[Alpine A424]]"
  "Aston Martin Vantage AMR LMGT3","[[Aston Martin Vantage GT3|Aston Martin Vantage AMR LMGT3]]"
  ```
- **db_kierowcy** — skrypt umożliwiający wygenerowanie pliku .csv z danymi o kierowcach oraz dodanie ich do bazy danych. W przypadku serii organizowanych przez IMSA do wygenerowania danych kierowców można skorzystać z dowolnego pliku .csv z wynikami. W seriach organizowanych przez ACO (FIA WEC, ELMS itd.) <ins>nie można</ins> korzystać z plików zawierających wyniki wyścigów.
  - przykładowy fragment pliku z prawidłowo wypełnionymi danymi:
  ```
  "codename","nationality","short_link","long_link"
  "hadrien david","FRA","[[Hadrien David]]","{{link-interwiki|Hadrien David|Q=Q65969301}}"
  "sebastian alvarez","MEX"[[Sebastián Álvarez (kierowca wyścigowy)|Sebastián Álvarez]],"{{link-interwiki|Sebastián Álvarez (kierowca wyścigowy)|tekst=Sebastián Álvarez|Q=Q108743788}}"
  "sven müller","DEU","[[Sven Müller (kierowca wyścigowy)|Sven Müller]]",""
  ```
- **db_punkty** — skrypt umożliwiający dodawanie wyników do bazy danych. Jako źródła skrypt wykorzystuje pliki z wynikami kwalifikacji i wyścigów.
- **db_zespoły** — skrypt umożliwiający wygenerowanie pliku .csv z danymi o zespołach oraz dodanie ich do bazy danych. Do wygenerowania danych można skorzystać z dowolnego pliku .csv z wynikami, ale jedynie wyniki sesji testowych, treningowych i kwalifikacyjnych w seriach ACO zawierają flagi zespołów. Jeśli źródłem jest inny plik niż wymieniony wcześniej, to flaga każdego zespołu zostanie ustawiona jako "?".
  - przykładowy fragment pliku z prawidłowo wypełnionymi danymi:
  ```
  "codename","nationality","car_number","short_link","long_link"
  "#8 Toyota Gazoo Racing","JPN","8","[[Toyota Gazoo Racing Europe|Toyota Gazoo Racing]]",""
  "#27 Heart of Racing Team","USA","27","[[Heart of Racing Team]]","{{link-interwiki|Heart Of Racing Team|Q=Q109789191}}"
  "#85 Iron Dames","ITA","85","[[Iron Lynx|Iron Dames]]","{{link-interwiki|Iron Lynx|tekst=Iron Dames|Q=Q109779058}}"
  ```