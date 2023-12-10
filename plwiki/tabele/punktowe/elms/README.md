# Klasyfikacja sezonu European Le Mans Series

## Opis

Skrypt tworzący tabelę z punktami zdobytymi przez kierowców/zespoły na podstawie pliku .json z [oficjalnej strony ELMS](https://europeanlemansseries.com).

## Szczegóły działania

Korzystając z narzędzi deweloperskich przeglądarki należy skopiować plik .json zawierający dane o klasyfikacji. Plik ten pobiera się po kliknięciu na stronie ELMS w "Season", a następnie "Classifications". Przy przełączaniu między klasyfikacjami (kierowców/zespołów/kategorii) pobiera się kolejny plik .json. Zawartość pliku .json z odpowiedzi zapytania należy zapisać do pliku. Następnie należy uruchomić skrypt i postępować zgodnie z instrukcjami podawanymi przez niego. Skrypt przetworzy dane i wypisze tabelę z klasyfikacją.