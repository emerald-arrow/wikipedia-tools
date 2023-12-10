# Generowanie tabel z wynikami sesji

## Opis
Skrypt **tabela_wynikow.py** tworzy tabele z wynikami sesji treningowych/testowych, kwalifikacyjnych i wyścigów. Skrypt tworzy tabelę na podstawie pliku *Classification.CSV* pobranego ze strony Alkamelsystems.

Obsługiwane strony Alkamelsystems:
- [FIA WEC](fiawec.alkamelsystems.com)
- [IMSA](results.imsa.com)
- [ELMS](elms.alkamelsystems.com)

Plik **db.py** zawiera słowniki, dzięki którym zmniejsza się nakład pracy nad tabelami wyników poprzez wstawianie odpowiednich danych takie jak flagi czy linki do artykułów.
- Słownik *drivers_ACO* zawiera kody krajów, które wykorzystuje ACO/FIA.
- Słownik *drivers* zawiera dane o kierowcach: flagi, pod którymi startują oraz tekst mający się pojawić w tabeli z wynikami (link do artykułu na Wikipedii lub samo imię i nazwisko)
- Słownik *teams* zawiera dane o zespołach: flagi, pod którymi startują oraz tekst mający się pojawić w tabeli z wynikami (link do artykułu na Wikipedii lub sama nazwa zespołu)
- Słownik *cars* zawiera linki do artykułów o samochodach

Skrypt **db_auta.py** generuje dane do słownika *cars* w **db.py**. Każdy samochód w pliku z wynikami jest wypisany jednokrotnie w formacie gotowym do wklejenia do słownika *cars*. Skrypt działa z wynikami dowolnych sesji (treningowe/testowe, kwalifikacje, rozgrzewki, wyścigi).

Skrypt **db_kierowcy.py** generuje dane do słownika *drivers* w **db.py**. Każdy kierowca w pliku z wynikami jest wypisany w formacie gotowym do wklejenia do słownika *drivers*. W przypadku wyścigów organizowanych przez ACO/FIA, skrypt nie działa z wynikami wyścigów.

Skrypt **db_zespoły.py** generuje dane do słownika *teams* w **db.py**. Każdy zespół w pliku z wynikami jest wypisany w formacie gotowym do wklejenia do słownika *teams*. W przypadku wyścigów organizowanych przez ACO/FIA flagi zespołów zostaną wypisane jedynie w przypadku wczytywania wyników sesji treningowych i kwalifikacji. W przypadku wyścigów organizowanych przez IMSA nie ma możliwości generowania danych zespołów z flagami.