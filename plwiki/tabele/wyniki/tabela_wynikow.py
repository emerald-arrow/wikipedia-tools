import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

import os
import csv
import sqlite3
from enum import Enum

# Typy sesji
class Session(Enum):
	FP = 1
	QUALI = 2
	RACE = 3

# Organizatorzy
class Organiser(Enum):
	ACO = 1
	IMSA = 2

# Serie wyścigowe
class Series:
	def __init__(self, db_id: int, name: str, organiser: Organiser) -> None:
		self.db_id = db_id
		self.name = name
		self.organiser = organiser

# Połączenie z bazą danych
def connect_db():
    db_relative = '../../../common/database.db'
    db_absolute = os.path.abspath(db_relative)
    
    db = sqlite3.connect(db_absolute)
    return db

# Pobieranie id wybranej wersji wikipedii
def get_wiki_id(version: str) -> int | None:
	db = connect_db()
	
	with db:
		query = 'SELECT id FROM wikipedia WHERE version = :version;'
		params = {'version': version}

		result = db.execute(query, params).fetchone()

		if result is not None:
			return int(result[0])
		else:
			return None

# Pobieranie danych zespołu
def get_team_data(codename: str, championship_id: int) -> dict[str, any] | None:
	db = connect_db()

	wiki_id = get_wiki_id('plwiki')

	with db:
		query = '''
			SELECT short_link, long_link, t.flag, t.car_number, team_id
			FROM team_wikipedia tw
			JOIN team t
			ON t.id = tw.team_id
			WHERE t.codename = :codename
			AND t.championship_id = :championship_id
			AND wikipedia_id = :wikipedia_id;
		'''
		params = {
			'codename': codename,
			'championship_id': championship_id,
			'wikipedia_id': wiki_id
		}

		result = db.execute(query, params).fetchone()

		if result is None:
			return None
		else:
			query = 'UPDATE team SET last_used = CURRENT_TIMESTAMP WHERE id = :team_id;'
			params = {'team_id': int(result[4])}

			db.execute(query, params)

			return {
				'short_link': result[0],
				'long_link': result[1],
				'nationality': result[2],
				'car_number': int(result[3])
			}

# Pobieranie danych kierowcy
def get_driver_data(codename: str) -> dict[str, any] | None:
	db = connect_db()

	wiki_id = get_wiki_id('plwiki')

	with db:
		query = '''
			SELECT short_link, long_link, d.flag, driver_id
			FROM driver_wikipedia dw
			JOIN driver d
			ON d.id = dw.driver_id
			WHERE d.codename = :codename
			AND wikipedia_id = :wikipedia_id;
		'''
		params = {
			'codename': codename,
			'wikipedia_id': wiki_id
		}

		result = db.execute(query, params).fetchone()

		if result is None:
			return None
		else:
			query = 'UPDATE driver SET last_used = CURRENT_TIMESTAMP WHERE id = :driver_id;'

			db.execute(query, {'driver_id': int(result[3])})

			return {
				'short_link': result[0],
				'long_link': result[1],
				'nationality': result[2]
			}

# Pobieranie linku do artykułu z autem
def get_car_link(codename: str) -> str | None:
	db = connect_db()

	wiki_id = get_wiki_id('plwiki')

	with db:
		query = '''
			SELECT link, car_id
			FROM car_wikipedia cw
			JOIN car c
			ON c.id = cw.car_id
			WHERE c.codename = :codename
			AND wikipedia_id = :wikipedia_id;
		'''
		params = {'codename': codename, 'wikipedia_id': wiki_id}

		result = db.execute(query, params).fetchone()

		if result is None:
			return None
		else:
			query = 'UPDATE car SET last_used = CURRENT_TIMESTAMP WHERE id = :car_id;'

			db.execute(query, {'car_id': result[1]})

			return result[0]

# Pobranie listy serii wyścigowych wraz z ich organizatorami
def get_series() -> dict[int, Series]:
	db = connect_db()

	with db:
		query = '''
			SELECT c.id, c.name, o.name
			FROM championship c
			JOIN organiser o
			ON o.id = c.organiser_id;
		'''

		result = db.execute(query).fetchall()

		if result is None:
			return []
		else:
			i = 1
			series: dict[int, Series] = dict()
			
			for s in result:
				series.update({i: Series(int(s[0]), s[1], Organiser[str(s[2]).upper()])})
				i += 1
			
			return series

# Odczytanie pliku .CSV i wypisanie kodu tabeli dla wyników wyścigu
def print_race_table(series: Series, filename: str) -> None:
	table_header = [
		'{| class="wikitable" style="font-size:95%;"',
		'|+ Klasyfikacja wstępna/ostateczna',
		'! {{Tooltip|Poz.|Pozycja}}',
		'! Klasa',
		'! Zespół',
		'! Kierowcy',
		'! Samochód',
		'! Opony',
		'! {{Tooltip|Okr.|Okrążenia}}',
		'! Czas/Strata'
	]

	print('\nKod tabeli:')
	print('\n'.join(table_header))
	
	with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		class_winners = set()
		statuses = set()

		for row in csv_reader:
			status = row['STATUS']

			if status != 'Classified' and status not in statuses:
				statuses.add(status)
				print('|-')
				print(f'! colspan="8" | {status}')

			category = row['CLASS']
			
			# Pogrubienie wierszy ze zwycięzcami klas
			if category not in class_winners:
				print('|- style="font-weight: bold;')
				class_winners.add(category)
			else:
				print('|-')
			
			# Pozycja zajęta w klasyfikacji ogólen wyścigu
			if status == 'Classified':
				print(f'! {row['POSITION']}')
			else:
				print('!')

			# Wypisanie klasy z ewentualną dodatkową grupą (np. Pro/Am)
			if row['GROUP'] != '':
				print(f'| align="center" | {category}<br />{row['GROUP']}')
			else:
				print(f'| align="center" | {category}')

			# Wypisanie nazwy zespołu, numeru auta i odpowiedniej flagi
			team_data = get_team_data(f'#{row["NUMBER"]} {row["TEAM"]}', series.db_id)

			if team_data is None:
				print(f'| {{{{Flaga|?}}}} #{row["NUMBER"]} [[{row["TEAM"]}]]')
			else:
				if team_data['long_link'] != '':
					print('| {{Flaga|%s}} #%d %s' % (
						team_data['nationality'],
						team_data['car_number'],
						team_data['long_link']
					))
				else:
					print('| {{Flaga|%s}} #%d %s' % (
						team_data['nationality'],
						team_data['car_number'],
						team_data['short_link']
					))

			# Wypisanie listy kierowców z flagami
			drivers: list[dict[str, any]] = list()

			# Składy są najwyżej czteroosobowe
			for x in range(1, 5):
				driver_data = None
				
				if series.organiser == Organiser.ACO and row[f'DRIVER_{x}'] != '':
					driver_data = get_driver_data(row[f'DRIVER_{x}'].lower())
					if driver_data is None:
						driver_name = row[f'DRIVER_{x}'].split(" ", 1)
						driver_data = {
							'short_link': f'[[{driver_name[0]} {driver_name[1].capitalize()}]]',
							'long_link': '',
							'nationality': '?'
						}
				elif series.organiser == Organiser.IMSA and row[f'DRIVER{x}_FIRSTNAME'] != '':
					codename = row[f'DRIVER{x}_FIRSTNAME'] + " " + row[f'DRIVER{x}_SECONDNAME'].capitalize()
					driver_data = get_driver_data(codename.lower())
					if driver_data is None:
						driver_data = {
							'short_link': f'[[{codename}]]',
							'long_link': '',
							'nationality': '?'
						}
				
				if driver_data is not None:
					drivers.append(driver_data)

			for x in range(0, len(drivers)):
				if x == 0:
					print('| {{Flaga|%s}} %s' % (
						drivers[x]['nationality'],
						drivers[x]['long_link'] if drivers[x]['long_link'] != '' else drivers[x]['short_link']
					), end='')
				elif x == len(drivers) - 1:
					print('<br />{{Flaga|%s}} %s' % (
						drivers[x]['nationality'],
						drivers[x]['long_link'] if drivers[x]['long_link'] != '' else drivers[x]['short_link']
					))
				else:
					print('<br />{{Flaga|%s}} %s' % (
						drivers[x]['nationality'],
						drivers[x]['long_link'] if drivers[x]['long_link'] != '' else drivers[x]['short_link']
					), end='')

			# Wypisanie auta
			car = get_car_link(row['VEHICLE'])

			if car is None:
				car = f'[[{row["VEHICLE"]}]]'

			print(f'| {car}')

			# Wypisanie opon
			tyre_oem = row['TYRES'] if 'TYRES' in row else row['TIRES']

			print('| align="center" | {{Opony|%s}}' % (tyre_oem))

			# Wypisanie liczby okrążeń
			print(f'| align="center" | {row["LAPS"]}')
			
			# Wypisanie czasu wyścigu/straty/statusu
			if status == 'Classified':
				# Wypisanie straty czasowej/liczby okrążeń
				if line_count > 0:
					gap = row['GAP_FIRST'].replace('.',',').replace('\'',':')

					gap = gap if gap.startswith('+') else f'+{gap}'

					print(f'| {gap}')
				# Wypisanie czasu wyścigu u zwycięzcy
				elif line_count == 0:
					total_time = row['TOTAL_TIME'].replace('.',',').replace('\'',':')
					print(f'| align="center" | {total_time}')
			else:
				# Wypisanie pustej komórki jeśli nieklasyfikowany, zdyskwalifikowany itp.
				print('|')

			line_count += 1
		
		print('|-')
		print('|}')

		print(f'\nPrzetworzone linie: {line_count}')

# Odczyanie pliku .CSV i wypisanie kodu tabeli dla wyników kwalifikacji
def print_quali_table(series: Series, filename: str) -> None:
	table_header = [
		'{| class="wikitable sortable" style="font-size: 90%;"',
		'! {{Tooltip|Poz.|Pozycja}}',
		'! class="unsortable" | Klasa',
		'! class="unsortable" | Zespół',
		'! class="unsortable" | Kierowca',
		'! class="unsortable" | Czas',
		'! class="unsortable" | Strata',
		'! {{Tooltip|Poz. s.|Pozycja startowa}}'
	]

	print('\nKod tabeli:')
	print('\n'.join(table_header))

	with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		class_polesitters = set()

		for row in csv_reader:
			category = row['CLASS']

			# Pogrubienie wierszy z zdobywcami pole position w klasach
			if category not in class_polesitters:
				print('|- style="font-weight: bold;"')
				class_polesitters.add(category)
			else:
				print('|-')
			
			# Wypisanie pozycji, organizatorzy niejednolicie używają nazwy kolumny z pozycją
			position = row['POSITION'] if 'POSITION' in row else row['POS']

			# Wypisanie klasy
			print(f'| align="center" | {category}')

			# Wypisanie nazwy zespołu z numerem samochodu i flagą
			team_data = get_team_data(f'#{row["NUMBER"]} {row["TEAM"]}', series.db_id)

			if team_data is not None:
				print('| {{Flaga|%s}} #%d %s' % (
					team_data['nationality'],
					int(team_data['car_number']),
					team_data['short_link']
				))
			else:
				print('| {{Flaga|?}} #%d [[%s]]' % (
					int(row['NUMBER']),
					row['TEAM']
				))
			
			drivers: list[dict[str, any]] = list()

			# Maksymalnie składy czteroosobowe
			for x in range(1, 5):
				if row[f'DRIVER{x}_FIRSTNAME'] is None or row[f'DRIVER{x}_FIRSTNAME'] == '':
					print(row[f'DRIVER{x}_FIRSTNAME'] is None)
					print(row[f'DRIVER{x}_FIRSTNAME'] == '')
					continue

				driver_name = '%s %s' % (
					row[f'DRIVER{x}_FIRSTNAME'].capitalize(),
					row[f'DRIVER{x}_SECONDNAME'].capitalize()
				)

				driver_data = get_driver_data(driver_name.lower())

				if driver_data is None:
					driver_data = {
						'short_link': driver_name,
						'long_link': '',
						'nationality': row[f'DRIVER{x}_COUNTRY']
					}
				
				if driver_data is not None:
					drivers.append(driver_data)

			# Wypisanie kierowców
			for x in range(0, len(drivers)):
				if x == 0:
					print('| {{Flaga|%s}} %s' % (
						drivers[x]['nationality'],
						drivers[x]['short_link']
					), end='')
				elif x == len(drivers) - 1:
					print('<br />{{Flaga|%s}} %s' % (
						drivers[x]['nationality'],
						drivers[x]['short_link']
					))
				else:
					print('<br />{{Flaga|%s}} %s' % (
						drivers[x]['nationality'],
						drivers[x]['short_link']
					), end='')

			# Wypisanie uzyskanego czasu i straty
			time = row['TIME']
			if time != '':
				time = time.replace('.',',')
				print(f'| {time}')
				
				gap = row['GAP_FIRST'].replace('.',',').replace('\'',':')

				gap = gap if gap.startswith('+') else f'+{gap}'
				
				if line_count > 0:
					print(f'| {gap}')
				else:
					# Zdobywca pole position w klasyfikacji ogólnej ma w tej komórce
					# myślnik zamiast straty
					print('| align="center" | —')
			# W razie braku czasu zostaje wypisany myślnik w komórkach dla czasu i straty
			else:
				print('| colspan="2" align="center" | —')

			# Wypisanie pozycji startowej, która jest taka sama jak zajęta pozycja,
			# chyba że lista z ustawieniem na starcie mówi inaczej
			print(f'! {position}')

			line_count += 1

		print('|-')
		print('! colspan="7" | Źródła')
		print('|-')
		print('|}')

		print(f'\nPrzetworzone linie: {line_count}')

# Odczyanie pliku .CSV i wypisanie kodu fragmentu tabeli dla wyników sesji treningowych
def print_fp_table(series: Series, filename: str) -> None:
	table_header = [
		'{| class="wikitable" style="font-size:95%"',
		'! Klasa',
		'! Zespół',
		'! Samochód',
		'! Czas',
		'! {{Tooltip|Okr.|Liczba pokonanych okrążeń}}',
		'|-',
		'! colspan="5" | Sesja<!--źródło-->'
	]

	print('\nKod tabeli:')
	print('\n'.join(table_header))
	
	with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		classes = set()

		for row in csv_reader:
			if row['CLASS'] not in classes:
				classes.add(row['CLASS'])

				print('|-')
				# Wypisanie nazwy klasy
				print(f'! {row['CLASS']}')

				# Wypisanie danych zespołu
				team_data = get_team_data(f'#{row["NUMBER"]} {row["TEAM"]}', series.db_id)

				if team_data is not None:
					print('| {{Flaga|%s}} #%d %s' % (
						team_data['nationality'],
						int(team_data['car_number']),
						team_data['short_link']
					))
				else:
					print('| {{Flaga|?}} #%d [[%s]]' % (
						int(row['NUMBER']),
						row['TEAM']
					))

				# Wypisanie auta
				car = get_car_link(row['VEHICLE'])

				if car is None:
					car = f'[[{row["VEHICLE"]}]]'

				print(f'| {car}')

				# Wypisanie czasu
				if row['TIME'] != '':
					time = row['TIME'].replace('.',',')
					print(f'| {time}')
				else:
					print(f'|')

				print(f'| align="center" | {row[" LAPS"]}')

			line_count += 1
		
		print('|-')
		print('|}')

		print(f'\nPrzetworzone linie: {line_count}')

# Odczytanie ścieżki do pliku
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

# Odczytanie sesji której wyniki zawiera plik
def read_session() -> Session:
	num = 0

	options = {
		1: {'text': 'Treningowa/testowa', 'enum': Session.FP},
		2: {'text': 'Kwalifikacyjna', 'enum': Session.QUALI},
		3: {'text': 'Wyścig', 'enum': Session.RACE}
	}

	print('\nWybierz sesję, która jest w podanym pliku .CSV:')

	while True:
		for o in options:
			print(f'{o}. {options[o]['text']}')

		try:
			num = int(input('Wybór: '))
		except ValueError:
			print(f'Podaj liczbę naturalną z przedziału 1-{len(options)}\n')

		if num in options:
			return options[num]['enum']
		else:
			print(f'Liczba musi być w przedziale 1-{len(options)}\n')

# Odczytanie serii wyścigowej, różne serie mogą inaczej nazywać kolumny w plikach .CSV
def read_series() -> Series:
	num = None

	series: dict[int, Series] = get_series()

	print('\nPodaj serię wyścigową, z której pochodzą dane:')

	while True:
		for s in series:
			print(f'{s}. {series[s].name}')
		try:
			num = int(input('Wybór: '))
		except ValueError:
			print(f'Podaj liczbę naturalną z przedziału 1-{len(series)}\n')
			continue

		if num in series.keys():
			return series[num]
		else:
			print(f'Liczba musi być w przedziale 1-{len(series)}\n')

# Główna funkcja skryptu
def main():
	file = read_csv_path()
	session = read_session()
	series = read_series()

	if session == Session.FP:
		print_fp_table(series, file)
	elif session == Session.QUALI:
		print_quali_table(series, file)
	elif session == Session.RACE:
		print_race_table(series, file)
	else:
		print('Typ sesji nieobsługiwany')

if __name__ == "__main__":
	main()