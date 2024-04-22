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
	QUALI_HP = 4

# Organizatorzy
class Organiser(Enum):
	ACO = 1
	IMSA = 2

# Serie wyścigowe
class Series:
	def __init__(self, name: str, organiser: Organiser, db_id: int | None=None) -> None:
		self.name = name
		self.organiser = organiser
		self.db_id = db_id

# Połączenie z bazą danych
def connect_db() -> sqlite3.Connection | None:
	db_relative = '../../../common/database.db'
	db_absolute = os.path.abspath(db_relative)
    
	try:
		db = sqlite3.connect(f'file:{db_absolute}?mode=rw', uri=True)
	except sqlite3.Error:
		return None
	return db

# Pobieranie id wybranej wersji wikipedii
def get_wiki_id(version: str) -> int | None:
	db = connect_db()

	if db is None:
		return None
	
	with db:
		query = 'SELECT id FROM wikipedia WHERE version = :version;'
		params = {'version': version}

		try:
			result = db.execute(query, params).fetchone()
		except sqlite3.Error:
			return None

		return None if result is None else int(result[0])

# Pobieranie danych zespołu
def get_team_data(codename: str, championship_id: int, wiki_id) -> dict[str, any] | None:
	db = connect_db()

	if db is None:
		return None

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

		try:
			result = db.execute(query, params).fetchone()
		except sqlite3.Error:
			return None

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
				'car_number': result[3]
			}

# Pobieranie danych kierowcy
def get_driver_data(codename: str, wiki_id: int) -> dict[str, any] | None:
	db = connect_db()

	if db is None:
		return None

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

		try:
			result = db.execute(query, params).fetchone()
		except sqlite3.Error:
			return None

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
def get_car_link(codename: str, wiki_id: int) -> str | None:
	db = connect_db()

	if db is None:
		return None

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

		try:
			result = db.execute(query, params).fetchone()
		except sqlite3.Error:
			return None

		if result is None:
			return None
		else:
			query = 'UPDATE car SET last_used = CURRENT_TIMESTAMP WHERE id = :car_id;'

			db.execute(query, {'car_id': result[1]})

			return result[0]

# Pobranie id serii wyścigowej
def get_series_id_by_name(series_name: str) -> int | None:
	db = connect_db()

	if db is None:
		return None
	
	with db:
		query = '''
			SELECT id
			FROM championship
			WHERE name = :series_name;
		'''
		params = {'series_name': series_name}

		try:
			result = db.execute(query, params).fetchone()
		except sqlite3.Error:
			return None

		return None if result is None else int(result[0])

# Odczytanie pliku .CSV i wypisanie kodu tabeli dla wyników wyścigu
def print_race_table(series: Series, filename: str, wiki_id: int) -> None:
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

	print('\nKod tabeli:\n')
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
			team_data = get_team_data(
							codename=f'#{row["NUMBER"]} {row["TEAM"]}',
							championship_id=series.db_id,
							wiki_id=wiki_id
						)

			if team_data is None:
				print(f'| {{{{Flaga|?}}}} #{row["NUMBER"]} [[{row["TEAM"]}]]')
			else:
				if team_data['long_link'] != '':
					print('| {{Flaga|%s}} #%s %s' % (
						team_data['nationality'],
						team_data['car_number'],
						team_data['long_link']
					))
				else:
					print('| {{Flaga|%s}} #%s %s' % (
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
					driver_data = get_driver_data(row[f'DRIVER_{x}'].lower(), wiki_id)
					if driver_data is None:
						driver_name = row[f'DRIVER_{x}'].split(" ", 1)
						driver_data = {
							'short_link': f'[[{driver_name[0]} {driver_name[1].capitalize()}]]',
							'long_link': '',
							'nationality': '?'
						}
				elif series.organiser == Organiser.IMSA and row[f'DRIVER{x}_FIRSTNAME'] != '':
					codename = '%s %s' % (
						row[f'DRIVER{x}_FIRSTNAME'],
						row[f'DRIVER{x}_SECONDNAME'].capitalize()
					)
					driver_data = get_driver_data(codename.lower(), wiki_id)
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
			car = get_car_link(row['VEHICLE'], wiki_id)

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
def print_quali_table(series: Series, filename: str, wiki_id: int) -> None:
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

	print('\nKod tabeli:\n')
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
			print(f'! {position}')

			# Wypisanie klasy
			print(f'| align="center" | {category}')

			# Wypisanie nazwy zespołu z numerem samochodu i flagą
			team_data = get_team_data(f'#{row["NUMBER"]} {row["TEAM"]}', series.db_id, wiki_id)

			if team_data is not None:
				print('| {{Flaga|%s}} #%s %s' % (
					team_data['nationality'],
					team_data['car_number'],
					team_data['short_link']
				))
			else:
				print('| {{Flaga|?}} #%d [[%s]]' % (
					int(row['NUMBER']),
					row['TEAM']
				))
			
			drivers: list[dict[str, any]] = list()

			# Zebranie danych o kierowcach, maksymalnie składy czteroosobowe
			for x in range(1, 5):
				if row[f'DRIVER{x}_FIRSTNAME'] is None or row[f'DRIVER{x}_FIRSTNAME'] == '':
					continue

				driver_name = '%s %s' % (
					row[f'DRIVER{x}_FIRSTNAME'].capitalize(),
					row[f'DRIVER{x}_SECONDNAME'].capitalize()
				)

				driver_data = get_driver_data(driver_name.lower(), wiki_id)

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

# Odczyanie pliku .CSV i wypisanie kodu tabeli dla wyników dwusesyjnej sesji kwalifikacyjnej
def print_quali_and_hyperpole_table(series: Series, filename: str, wiki_id: int) -> None:
	table_header = [
		'{| class="wikitable sortable" style="font-size: 90%;"',
		'! {{Tooltip|Poz.|Pozycja}}',
		'! class="unsortable" | Klasa',
		'! class="unsortable" | Zespół',
		'! Kwalifikacje',
		'! Hyperpole',
		'! {{Tooltip|Poz. s.|Pozycja startowa}}'
	]

	print('\nKod tabeli:\n')
	print('\n'.join(table_header))

	# Odczytanie nagłówków kolumn zawierających czasy sesji kwalifikacyjnych
	session_headers: dict[str, list[str]] = dict()

	with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
		csv_header_reader = csv.DictReader(csv_file, delimiter=';')
		csv_headers = list(dict(list(csv_header_reader)[0]).keys())
		q1_headers = [x for x in csv_headers if x.startswith('QP_')]
		hp_headers = [x for x in csv_headers if x.startswith('HP_')]

	if len(q1_headers) > 0:
		session_headers.update({'QP': q1_headers})

	if len(hp_headers) > 0:
		session_headers.update({'HP': hp_headers})

	with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0

		class_polesitters = set()

		for row in csv_reader:
			print('|-')
			
			# Wypisanie pozycji, organizatorzy niejednolicie używają nazwy kolumny z pozycją
			position = row['POSITION'] if 'POSITION' in row else row['POS']
			print(f'! {position}')

			category = row['CLASS']
			
			# Pogrubienie nazwy klasy dla zdobywcy pole position w klasie
			if category not in class_polesitters:
				class_polesitters.add(category)
				category = f"'''{category}'''"
			
			# Wypisanie klasy
			print(f'| align="center" | {category}')

			# Wypisanie nazwy zespołu z numerem samochodu i flagą
			team_data = get_team_data(f'#{row["NUMBER"]} {row["TEAM"]}', series.db_id, wiki_id)

			if team_data is not None:
				print('| {{Flaga|%s}} #%s %s' % (
					team_data['nationality'],
					team_data['car_number'],
					team_data['short_link']
				))
			else:
				print('| {{Flaga|?}} #%d [[%s]]' % (
					int(row['NUMBER']),
					row['TEAM']
				))

			q1_time = ''
			for q1 in session_headers.get('QP'):
				if row.get(q1) != '':
					q1_time = row.get(q1)
			
			hp_time = ''
			for hp in session_headers.get('HP'):
				if row.get(hp) != '':
					hp_time = row.get(hp)

			# Wypisanie uzyskanych czasów
			if q1_time != '':
				q1_time = q1_time.replace('.',',')
				print(f'| align="center" | {q1_time}')

				if hp_time != '':
					hp_time = hp_time.replace('.',',')
					print(f'| align="center" | {hp_time}')
				else:
					print('!')
			else:
				print('| align="center" | —')
				print('!')

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
def print_fp_table(series: Series, filename: str, wiki_id: int) -> None:
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

	print('\nKod tabeli:\n')
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
				team_data = get_team_data(
								codename=f'#{row["NUMBER"]} {row["TEAM"]}',
								championship_id=series.db_id,
								wiki_id=wiki_id
							)

				if team_data is not None:
					print('| {{Flaga|%s}} #%s %s' % (
						team_data['nationality'],
						team_data['car_number'],
						team_data['short_link']
					))
				else:
					print('| {{Flaga|?}} #%s [[%s]]' % (
						row['NUMBER'],
						row['TEAM']
					))

				# Wypisanie auta
				car = get_car_link(row['VEHICLE'], wiki_id)

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
def read_session(series: Series) -> Session:
	if series.name == 'FIA World Endurance Championship':
		options: list[dict[str, any]] = [
			{'name': 'Treningowa/testowa', 'enum': Session.FP},
			{'name': 'Kwalifikacyjna z Hyperpole', 'enum': Session.QUALI_HP},
			{'name': 'Wyścig', 'enum': Session.RACE}
		]
	else:
		options: list[dict[str, any]] = [
			{'name': 'Treningowa/testowa', 'enum': Session.FP},
			{'name': 'Kwalifikacyjna', 'enum': Session.QUALI},
			{'name': 'Wyścig', 'enum': Session.RACE}
		]

	print('\nWybierz sesję, która jest w podanym pliku .CSV:')

	while True:
		for x in range(0, len(options)):
			print(f'{x+1}. {options[x]['name']}')

		try:
			num = int(input('Wybór: '))
		except ValueError:
			print(f'Podaj liczbę naturalną z przedziału 1-{len(options)}\n')

		if num in range(1, len(options)+1):
			return options[num-1]['enum']
		else:
			print(f'Liczba musi być w przedziale 1-{len(options)}\n')

# Odczytanie serii wyścigowej, różne serie mogą inaczej nazywać kolumny w plikach .CSV
def read_series() -> Series:
	series: list[Series] = [
		Series(name='FIA World Endurance Championship', organiser=Organiser.ACO),
		Series(name='European Le Mans Series', organiser=Organiser.ACO),
		Series(name='IMSA SportsCar Championship', organiser=Organiser.IMSA)
	]

	print('\nPodaj serię wyścigową, z której pochodzą dane:')

	while True:
		for x in range(0, len(series)):
			print(f'{x+1}. {series[x].name}')
		try:
			num = int(input('Wybór: '))
		except ValueError:
			print(f'Podaj liczbę naturalną z przedziału 1-{len(series)}\n')
			continue

		if num in range(1, len(series)+1):
			series_id = get_series_id_by_name(series[num-1].name)

			if series_id is not None:
				series[num-1].db_id = series_id
			
			return series[num-1]
		else:
			print(f'Liczba musi być w przedziale 1-{len(series)}\n')

# Główna funkcja skryptu
def main():
	file: str = read_csv_path()
	series: Series = read_series()
	session: Session = read_session(series)

	if series.db_id is None:
		msg: list[str] = [
			'\nNie znaleziono serii w bazie danych.',
			'Dane zespołów w tabeli będą pobrane jedynie z pliku.'
		]
		print(' '.join(msg))

	plwiki_id = get_wiki_id('plwiki')

	if plwiki_id is None:
		msg: list[str] = [
			'\nNie znaleziono w bazie polskiej wersji językowej Wikipedii.',
			'Dane m.in. kierowców będą pobrane jedynie z pliku.'
		]
		print(' '.join(msg))

	if session == Session.FP:
		print_fp_table(series, file, plwiki_id)
	elif session == Session.QUALI:
		print_quali_table(series, file, plwiki_id)
	elif session == Session.QUALI_HP:
		print_quali_and_hyperpole_table(series, file, plwiki_id)
	elif session == Session.RACE:
		print_race_table(series, file, plwiki_id)
	else:
		print('Typ sesji nieobsługiwany')

if __name__ == "__main__":
	main()