import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

import os
import csv
import re

from modele import Classification, Colour, EligibleClassifications, Manufacturer, ResultRow

type DriverData = dict[str, int | str]
type EntityDict = dict[str, list[str]]

# Odczytanie id serii, której klasyfikacje mają zostać wygenerowane
def read_championship() -> int:
	from db_zapytania import get_championships

	championships = get_championships()

	num: int = None

	print('Wybierz serię, której klasyfikacje punktowe chcesz wygenerować:')

	while True:
		for x in range(0, len(championships)):
			print(f'{x+1}. {championships[x]['name']}')
		
		try:
			num = int(input(f'Wybór (1-{len(championships)}): '))
		except (TypeError, ValueError):
			print(f'Podaj liczbę naturalną z przedziału 1-{len(championships)}')
			continue

		if num-1 not in range(0, len(championships)):
			print(f'Podaj liczbę naturalną z zakresu 1-{len(championships)}')
			continue
		else:
			return championships[num-1]['id']

# Odczytanie ścieżki do pliku z klasyfikacją wyścigu
def read_csv_path() -> str:
	text = ''

	while True:
		text = input('\nPodaj ścieżkę do pliku .CSV pobranego ze strony Alkamelsystems:\n')

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if not text.lower().endswith('.csv'):
			print('Ścieżka nie prowadzi do pliku z rozszerzeniem .CSV.')
			continue
		else:
			return text

# Wyszukiwanie odpowiednich klasyfikacji
def find_classifications(category: str, team_id: int,
                         classifications: list[Classification]
                        ) -> EligibleClassifications:
    from db_zapytania import check_classification_eligibility

    eligible_cl = EligibleClassifications(None, None, None)

    for cl in classifications:
        if re.search(f'{category}', cl.name, re.IGNORECASE):
            if check_classification_eligibility(cl.id, team_id):
                if re.search('driver', cl.name, re.IGNORECASE):
                    eligible_cl.driver = cl
                elif re.search('manufacturer', cl.name, re.IGNORECASE):
                    eligible_cl.manufacturer = cl
                elif re.search('team', cl.name, re.IGNORECASE):
                    eligible_cl.team = cl
    
    return eligible_cl

# Odczytanie danych z pliku csv zawierającego wyniki
def read_results_csv(path: str, classifications: list[Classification]) -> list[ResultRow]:
    from db_zapytania import get_team_id_and_scoring_by_codename
    from db_zapytania import get_driver_by_codename
    from db_zapytania import get_manufacturers

    rows: list[ResultRow] = list()
    not_found: EntityDict = {'teams': [], 'drivers': []}
    manufacturers: list[Manufacturer] = get_manufacturers()

    championship_id: int = classifications[0].id

    with open(path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        line_count = 0

        for row in csv_reader:
            line_count += 1
            row_data: ResultRow = None
            row_drivers: list[DriverData] = []

            try:            
                row_position = int(row['POSITION'])
                row_car_no = row['NUMBER']
                row_team = row['TEAM']
                row_category = row['CLASS']
                row_status = row['STATUS']
                row_vehicle = row['VEHICLE']
            except:
                error_text = [
					'\nBłąd podczas czytania danych.',
					'W podanym pliku brakuje któregoś z nagłówków:',
					'POSITION, NUMBER, TEAM, CLASS, STATUS lub VEHICLE.\n'
				]
                print(' '.join(error_text))
                return []

            codename = f'#{row_car_no} {row_team}'
            (row_db_team_id, can_score) = get_team_id_and_scoring_by_codename(
                                                codename,
                                                championship_id
                                            )

            if type(row_db_team_id) is not int:
                not_found['teams'].append(codename)
                continue
            
            if not can_score:
                continue

            eligible_cls: EligibleClassifications = find_classifications(
                                                        row_category,
                                                        row_db_team_id,
                                                        classifications
                                                    )

            row_manufacturer = None

            if eligible_cls.manufacturer is not None:
                for m in manufacturers:
                    if re.search(m.codename, row_vehicle, re.IGNORECASE):
                        row_manufacturer = m
                        manufacturers.pop(manufacturers.index(m))

            try:
                for x in range(1, 5):
                    driver = row[f'DRIVER_{x}']
                    if driver is not None and driver != '':
                        driver_data = get_driver_by_codename(driver.lower())
                        if driver_data is None:
                            not_found['drivers'].append(driver)
                        else:
                            row_drivers.append(driver_data)
            except:
                print(f'\nBłąd podczas czytania danych. W podanym pliku brakuje kolumny {driver}.\n')
                return []
            
            row_data = ResultRow(
                position=row_position if row_status == 'Classified' else None,
                drivers=row_drivers,
                category=row_category,
                status=row_status,
                db_team_id=row_db_team_id,
                manufacturer=row_manufacturer,
                eligible_classifications=eligible_cls
            )

            rows.append(row_data)

        print(f'\nPrzetworzone linie: {line_count}')

        entity_not_found: bool = False

        if len(not_found['drivers']) > 0:
            entity_not_found = True
            print('\nW bazie danych nie znaleziono kierowców:')
            for driver in not_found['drivers']:
                print(driver)
            
        if len(not_found['teams']) > 0:
            entity_not_found = True
            print('\nW bazie danych nie znaleziono zespołów:')
            for team in not_found['teams']:
                print(team)

        return [] if entity_not_found else rows

# Wyszukanie stylu kolorowania dla pozycji
def find_result_style(row: ResultRow, colours: list[Colour]) -> int | None:
    match row.status:
        case 'Classified':
            if row.cat_position >= 4 and row.cat_position <= 10:
                el = next((c for c in colours if c.status == 'T10'), None)
            elif row.cat_position > 10:
                el = next((c for c in colours if c.status == 'O10'), None)
            elif row.cat_position == 1:
                el = next((c for c in colours if c.status == 'P1'), None)
            elif row.cat_position == 2:
                el = next((c for c in colours if c.status == 'P2'), None)
            elif row.cat_position == 3:
                el = next((c for c in colours if c.status == 'P3'), None)
            return el.id if el is not None else None
        case 'Not classified':
            el = next((c for c in colours if c.status == 'NC'), None)
            return el.id if el is not None else None
        case 'Retired':
            el = next((c for c in colours if c.status == 'RET'), None)
            return el.id if el is not None else None
        case 'Disqualified':
            el = next((c for c in colours if c.status == 'DSQ'), None)
            return el.id if el is not None else None
        case _:
              return None

# Wyliczenie pozycji w kategoriach i dobranie stylów kolorowania wyników
def calculate_category_positions(rows: list[ResultRow], colours: list[Colour]) -> list[ResultRow]:
    categories = set(r.category for r in rows)

    positions: dict[str, int] = dict()

    for cat in categories:
         positions.update({f'{cat}': 1})

    for row in rows:
        if row.status == 'Classified':
            position = positions.get(row.category)
            row.cat_position = position
            position += 1
            positions.update({f'{row.category}': position})

        result_style_id: int | None = find_result_style(row, colours)

        if result_style_id is None:
            print('Nie znaleziono odpowiedniego stylu kolorowania wyniku.')
            return []
        else:
            row.result_style = result_style_id
    
    return rows

# Odczytanie numeru rundy
def read_round_number(classifications: list[Classification]) -> int | None:
    from db_zapytania import check_round_number_in_classification

    num = None

    while True:
        try:
            num = int(input('\nPodaj numer rundy, której wyniki są w pliku: '))
        except ValueError:
            print('Podaj liczbę naturalną.')
            continue

        if check_round_number_in_classification(classifications[0].id, num):
            print('Wyniki tej rundy już są w bazie.')
            return None
        else:
            return num

# Dodanie wyników do bazy
def add_results_to_db(rows: list[ResultRow], round_number: int) -> None:
    from db_zapytania import add_score
    
    for row in rows:
        print(f'{row.category} | {row.status}')
        if row.eligible_classifications.driver is not None:
            for driver in row.drivers:
                add_score(
                    row.eligible_classifications.driver.id,
                    driver['id'],
                    row.result_style,
                    row.cat_position,
                    -1483,
                    False,
                    round_number
                )
        if row.eligible_classifications.manufacturer is not None:
            if row.manufacturer is not None:
                add_score(
                    row.eligible_classifications.manufacturer.id,
                    row.manufacturer.id,
                    row.result_style,
                    row.cat_position,
                    -1483,
                    False,
                    round_number
                )
        if row.eligible_classifications.team is not None:
            add_score(
                row.eligible_classifications.team.id,
                row.db_team_id,
                row.result_style,
                row.cat_position,
                -1483,
                False,
                round_number
            )
        print('------')

# Główna funkcja skryptu
def main() -> None:
    from db_zapytania import get_classifications_by_championship_id
    from db_zapytania import get_colours

    colours: list[Colour] = get_colours()

    if len(colours) == 0:
        print('Nie udało się pobrać stylów pozycji z bazy danych')
        return

    championship_id: int = read_championship()

    classifications: list[Classification] = get_classifications_by_championship_id(
                                                championship_id
                                            )

    if len(classifications) == 0:
         print('Brak zdefiniowanych klasyfikacji w bazie dla wybranej serii.')
         return

    # C:\Users\User\Downloads\Qatar_Classification_Race.CSV
    path: str = read_csv_path()
    
    rows: list[ResultRow] = read_results_csv(path, classifications)

    if len(rows) == 0:
        return

    rows: list[ResultRow] = calculate_category_positions(rows, colours)

    if len(rows) == 0:
        return
    
    round_num: int | None = read_round_number(classifications)

    if round_num is not None:    
        add_results_to_db(rows, round_num)

if __name__ == '__main__':
    main()