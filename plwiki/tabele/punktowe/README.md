# Klasyfikacje punktowe
Narzędzia do tworzenia klasyfikacji punktowych w sezonie.

- **tabela_punktowa.py** — skrypt wypisujący kod tabeli z klasyfikacją sezonu na podstawie wyników zapisanych w bazie danych.
- **elms** — katalog zawierający skrypt generujący kod tabeli z klasyfikacją sezonu ELMS na podstawie pliku pobranego z oficjalnej strony serii. Plik README w tym katalogu zawiera instrukcję jak pobrać dane w formacie .json ze strony ELMS.
- **wec** — katalog zawierający skrypt generujący kod tabeli z klasyfikacją sezonu FIA WEC na podstawie pliku pobranego z oficjalnej strony serii. Plik README w tym katalogu zawiera instrukcję jak pobrać dane w formacie .html ze strony FIA WEC.

Skrypty bazujące na pobranych plikach .json/.html generują mniej szczegółowe tabele, np. miejsca poniżej 10 są oznaczone jako niepunktowane bez podania szczegółowej pozycji. Skrypt **tabela_punktowa.py** poprawnie generuje tabele z dokładnymi wynikami, choć brakuje w nim obsługi rzadkich statusów takich jak np. wycofanie po rozpoczęciu weekendu wyścigowego.  