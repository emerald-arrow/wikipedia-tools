import sys
import os
import csv
import re
from pathlib import Path

project_path = str(Path(__file__).parent.parent.parent)
if project_path not in sys.path:
    sys.path.append(project_path)

if True:  # noqa: E402
    from common.db_queries.wikipedia_table import get_wiki_id
    from common.models.car import Car

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True


# Zapisanie nazw samochodów do pliku .csv
def write_cars_csv(cars: list[Car]) -> None:
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filename = f'auta_{timestamp}.csv'

    headers = ['codename', 'link']

    with open(filename, mode='w', encoding='utf-8-sig') as csv_file:
        csv_writer = csv.writer(
            csv_file,
            delimiter=',',
            quoting=csv.QUOTE_NONNUMERIC,
            lineterminator='\n'
        )

        csv_writer.writerow(headers)

        for c in cars:
            csv_writer.writerow(list(c))

    print(f'\nAuta zapisane w pliku {filename}: {len(cars)}')


# Odczytanie samochodów z pliku zawierającego wyniki
def read_results_csv(path: str, wiki_id: int) -> list[Car]:
    from common.db_queries.car_tables import check_car_exists

    cars: list[Car] = list()

    with open(path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        line_count = 0
        checked: set[str] = set()

        print('')

        for row in csv_reader:  # type: dict
            line_count += 1

            codename = row.get('VEHICLE')

            if type(codename) is not str:
                continue

            if codename in checked:
                continue

            checked.add(codename)

            if check_car_exists(codename, wiki_id):
                print(f'{codename} jest już w bazie.')
                continue

            cars.append(
                Car(
                    codename=codename,
                    link=f'[[{codename}]]'
                )
            )

        print(f'\nPrzetworzone linie: {line_count}\nZnalezione auta: {len(cars)}')

    return cars


# Sprawdzenie czy podany plik z wynikami ma wymagane kolumny
def verify_results_csv(path: str) -> bool:
    with open(path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        csv_dict = dict(list(csv_reader)[0])
        headers = list(csv_dict.keys())

        return 'VEHICLE' in headers


# Odczytanie ścieżki do pliku csv zawierającego wyniki
def read_path_to_results_csv() -> str:
    while True:
        text = input('\nPodaj ścieżkę do pliku .CSV pobranego ze strony Alkamelsystems:\n')

        if not os.path.isfile(text):
            print('\nŚcieżka nieprawidłowa, spróbuj ponownie.')
            continue
        if not verify_results_csv(text):
            print('\nPlik nie posiada wymaganej kolumny VEHICLE.')
            continue
        else:
            return text


# Tworzenie pliku .csv z danymi aut
def car_data_to_csv_mode() -> None:
    plwiki_id: int | None = get_wiki_id('plwiki')

    if plwiki_id is None:
        print('Nie znaleziono w bazie danych polskiej wersji Wikipedii')
        return

    path: str = read_path_to_results_csv()

    cars: list[Car] = read_results_csv(path, plwiki_id)

    if len(cars) == 0:
        return

    write_cars_csv(cars)


# Sprawdzenie czy podany plik z danymi aut ma wymagane kolumny
def verify_cars_csv(path: str) -> bool:
    with open(path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        csv_dict = dict(list(csv_reader)[0])
        headers = list(csv_dict.keys())

        return (
            'codename' in headers and
            'link' in headers
        )


# Sprawdzenie czy katalog zawiera pliki z danymi aut
def get_cars_csv_files_in_dir() -> list[str]:
    csv_files: list[str] = []
    files = [f for f in os.listdir() if os.path.isfile(f)]

    for f in files:
        if re.search('auta_.*\\.([Cc][Ss][Vv])', f) is not None:
            if verify_cars_csv(f):
                csv_files.append(f)

    return csv_files


# Wybór pliku z danymi o autach
def choose_car_csv_file() -> str:
    csv_files: list[str] = get_cars_csv_files_in_dir()

    if len(csv_files) > 1:
        while True:
            for x in range(0, len(csv_files)):
                print(f'{x + 1}. {csv_files[x]}')

            try:
                num = int(input(f'Wybór (1-{len(csv_files)}): '))
            except ValueError:
                print('\nPodaj liczbę widoczną przy nazwie pliku')
                continue

            if num - 1 in range(0, len(csv_files)):
                return csv_files[num - 1]
            else:
                print('\nBłędna liczba. Spróbuj ponownie.')
                continue
    elif len(csv_files) == 1:
        options = {
            1: 'Tak',
            2: 'Nie'
        }

        while True:
            msg = [
                f'\nJedyny znaleziony plik to {csv_files[0]}.',
                'Czy chcesz zapisać jego zawartość do bazy danych?'
            ]
            print(' '.join(msg))

            for x in options:
                print(f'{x}. {options[x]}')

            try:
                num = int(input('Wybór (1-2): '))
            except ValueError:
                print('\nPodaj liczbę 1 lub 2.')
                continue

            if num in options:
                if num == 1:
                    return csv_files[0]
                else:
                    break
            else:
                print('\nPodaj liczbę 1 lub 2.')
                continue

    while True:
        text = input('\nPodaj ścieżkę do pliku .csv zawierającego dane o autach:\n')

        if not os.path.isfile(text):
            print('\nŚcieżka nieprawidłowa, spróbuj ponownie.')
            continue
        if not text.lower().endswith('.csv'):
            print('\nPodany plik nie posiada rozszerzenia .csv.')
            continue
        if not verify_cars_csv(text):
            print('\nPodany plik csv nie posiada wymaganych kolumn.')
            continue

        return text


# Odczytanie danych o autach z pliku zawierającego dane o nich
def read_cars_csv(path: str) -> list[Car]:
    cars: list[Car] = list()

    with open(path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:  # type: dict
            codename = row.get('codename')
            link = row.get('link')

            if codename is not None and link is not None:
                cars.append(
                    Car(
                        codename=codename,
                        link=link
                    )
                )

            line_count += 1

        print(f'\nPrzetworzone linie: {line_count}')
        print(f'Liczba znalezionych aut: {len(cars)}')

    return cars


# Zapisanie danych o autach w bazie
def cars_data_to_db_mode() -> None:
    from common.db_queries.car_tables import add_car

    plwiki_id: int | None = get_wiki_id('plwiki')

    if plwiki_id is None:
        error_msg = [
            '\nNie znaleziono id polskiej Wikipedii w bazie danych.',
            'Nie można rozpocząć dodawania danych do bazy danych.'
        ]
        print(' '.join(error_msg))
        return

    chosen_file: str = choose_car_csv_file()

    cars: list[Car] = read_cars_csv(chosen_file)

    if len(cars) == 0:
        return

    for car in cars:
        add_car(car, plwiki_id)


# Wybór trybu pracy skryptu
def choose_mode() -> None:
    options = {
        1: 'Wygenerować plik .csv z danymi o autach',
        2: 'Zapisać dane o autach w bazie',
        3: 'Zakończyć działanie'
    }

    while True:
        print('\nWybierz co ma zrobić skrypt.')

        for o in options:
            print(f'{o}. {options[o]}')

        try:
            num = int(input('Wybór: '))
        except ValueError:
            print('\nPodaj liczbę między 1 a 3.')
            continue

        if num not in options:
            print('\nWybór spoza powyższej listy, spróbuj ponownie.')
            continue
        elif num == 1:
            car_data_to_csv_mode()
            break
        elif num == 2:
            cars_data_to_db_mode()
            break
        elif num == 3:
            return


if __name__ == "__main__":
    choose_mode()
