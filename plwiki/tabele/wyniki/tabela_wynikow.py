import sys
import os
import csv
from pathlib import Path

project_path = str(Path(__file__).parent.parent.parent.parent)
if project_path not in sys.path:
	sys.path.append(project_path)

if True:  # noqa: E402
	from common.models.sessions import Session
	from common.models.championships import ChampionshipExt
	from common.db_queries.wikipedia_table import get_wiki_id
	from common.db_queries.team_tables import get_team_data
	from common.db_queries.driver_tables import get_driver_flag_links
	from common.db_queries.car_tables import get_car_link
	from common.db_queries.championship_table import get_championships

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True


# Odczytanie pliku .CSV i wypisanie kodu tabeli dla wyników wyścigu
def print_race_table(championship: ChampionshipExt, filepath: str, wiki_id: int) -> None:
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

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		class_winners = set()
		statuses = set()

		for row in csv_reader:  # type: dict
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

			# Pozycja zajęta w klasyfikacji ogólnej wyścigu
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
				championship_id=championship.db_id,
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

				if (
						row.get(f'DRIVER_{x}') is not None
						and row.get(f'DRIVER_{x}') != ''
				):
					driver_data = get_driver_flag_links(row[f'DRIVER_{x}'].lower(), wiki_id)
					if driver_data is None:
						driver_name = row[f'DRIVER_{x}'].split(" ", 1)
						driver_data = {
							'short_link': f'[[{driver_name[0]} {driver_name[1].capitalize()}]]',
							'long_link': '',
							'nationality': '?'
						}
				elif (
						row.get(f'DRIVER{x}_FIRSTNAME') is not None
						and row.get(f'DRIVER{x}_FIRSTNAME') != ''
				):
					codename = '%s %s' % (
						row[f'DRIVER{x}_FIRSTNAME'],
						row[f'DRIVER{x}_SECONDNAME'].capitalize()
					)
					driver_data = get_driver_flag_links(codename.lower(), wiki_id)
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
						drivers[x]['long_link'] if drivers[x]['long_link'] != ''
						else drivers[x]['short_link']
					), end='')
				elif x == len(drivers) - 1:
					print('<br />{{Flaga|%s}} %s' % (
						drivers[x]['nationality'],
						drivers[x]['long_link'] if drivers[x]['long_link'] != ''
						else drivers[x]['short_link']
					))
				else:
					print('<br />{{Flaga|%s}} %s' % (
						drivers[x]['nationality'],
						drivers[x]['long_link'] if drivers[x]['long_link'] != ''
						else drivers[x]['short_link']
					), end='')

			# Wypisanie auta
			car = get_car_link(row['VEHICLE'], wiki_id)

			if car is None:
				car = f'[[{row["VEHICLE"]}]]'

			print(f'| {car}')

			# Wypisanie opon
			tyre_oem = row['TYRES'] if 'TYRES' in row else row['TIRES']

			print('| align="center" | {{Opony|%s}}' % tyre_oem)

			# Wypisanie liczby okrążeń
			print(f'| align="center" | {row["LAPS"]}')

			# Wypisanie czasu wyścigu/straty/statusu
			if status == 'Classified':
				# Wypisanie straty czasowej/liczby okrążeń
				if line_count > 0:
					gap = row['GAP_FIRST'].replace('.', ',').replace('\'', ':')

					gap = gap if gap.startswith('+') else f'+{gap}'

					print(f'| {gap}')
				# Wypisanie czasu wyścigu u zwycięzcy
				elif line_count == 0:
					total_time = row['TOTAL_TIME'].replace('.', ',').replace('\'', ':')
					print(f'| align="center" | {total_time}')
			else:
				# Wypisanie pustej komórki jeśli nieklasyfikowany, zdyskwalifikowany itp.
				print('|')

			line_count += 1

		print('|-')
		print('|}')

		print(f'\nPrzetworzone linie: {line_count}')


# Odczytanie pliku .CSV i wypisanie kodu tabeli dla wyników kwalifikacji
def print_qualifying_table(championship: ChampionshipExt, filepath: str, wiki_id: int) -> None:
	table_header = [
		'{| class="wikitable sortable" style="font-size: 90%;"',
		'! {{Tooltip|Poz.|Pozycja}}',
		'! class="unsortable" | Klasa',
		'! class="unsortable" | Zespół',
		'! class="unsortable" | Kierowca',
		'! class="unsortable" | Czas',
		'! class="unsortable" | Strata',
		'! {{Tooltip|Poz. s.|Pozycja startowa}}',
	]

	print('\nKod tabeli:\n')
	print('\n'.join(table_header))

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		class_polesitters = set()

		for row in csv_reader:  # type: dict
			category = row['CLASS']

			# Pogrubienie wierszy ze zdobywcami pole position w klasach
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
			team_data = get_team_data(
				codename=f'#{row["NUMBER"]} {row["TEAM"]}',
				championship_id=championship.db_id,
				wiki_id=wiki_id
			)

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
				if (
						row[f'DRIVER{x}_FIRSTNAME'] is None
						or row[f'DRIVER{x}_FIRSTNAME'] == ''
				):
					continue

				driver_name = '%s %s' % (
					row[f'DRIVER{x}_FIRSTNAME'].capitalize(),
					row[f'DRIVER{x}_SECONDNAME'].capitalize()
				)

				driver_data = get_driver_flag_links(driver_name.lower(), wiki_id)

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
				time = time.replace('.', ',')
				print(f'| align="center" | {time}')

				gap = row['GAP_FIRST'].replace('.', ',').replace('\'', ':')

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


# Odczytanie pliku .CSV i wypisanie kodu tabeli dla wyników sesji kwalifikacyjnej z Hyperpole
def print_qualifying_post_hp_table(championship: ChampionshipExt, filepath: str, wiki_id: int) -> None:
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

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_header_reader = csv.DictReader(csv_file, delimiter=';')
		csv_headers = list(dict(list(csv_header_reader)[0]).keys())
		q1_headers = [x for x in csv_headers if x.startswith('QP')]
		hp_headers = [x for x in csv_headers if x.startswith('HP')]

	if len(q1_headers) > 0:
		session_headers.update({'QP': q1_headers})

	if len(hp_headers) > 0:
		session_headers.update({'HP': hp_headers})

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0

		class_polesitters = set()

		for row in csv_reader:  # type: dict
			print('|-')

			# Wypisanie pozycji, organizatorzy niejednolicie używają nazwy kolumny z pozycją
			position = row['POSITION'] if 'POSITION' in row else row['POS']
			print(f'! {position}')

			category = row['CLASS']

			# Pogrubienie nazwy klasy dla zdobywcy pole position w klasie
			if category not in class_polesitters:
				category = f"'''{category}'''"

			# Wypisanie klasy
			print(f'| align="center" | {category}')

			# Wypisanie nazwy zespołu z numerem samochodu i flagą
			team_data = get_team_data(
				codename=f'#{row["NUMBER"]} {row["TEAM"]}',
				championship_id=championship.db_id,
				wiki_id=wiki_id
			)

			if team_data is not None:
				row_team: str = '{{Flaga|%s}} #%s %s' % (
					team_data['nationality'],
					team_data['car_number'],
					team_data['short_link']
				)
			else:
				row_team: str = '{{Flaga|?}} #%s [[%s]]' % (
					row['NUMBER'],
					row['TEAM']
				)

			if category in class_polesitters:
				print(f"| {row_team}")
			else:
				print(f"| '''{row_team}'''")

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
				q1_time = q1_time.replace('.', ',')
				print(f'| align="center" | {q1_time}')

				if hp_time != '':
					hp_time = hp_time.replace('.', ',')
					if category in class_polesitters:
						print(f'| align="center" | {hp_time}')
					else:
						print(f"| align=\"center\" | '''{hp_time}'''")
						class_polesitters.add(row['CLASS'])
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


# Odczytanie pliku .CSV i wypisanie kodu tabeli dla wyników sesji kwalifikacyjnej przed Hyperpole
def print_qualifying_pre_hp_table(championship: ChampionshipExt, filepath: str, wiki_id: int) -> None:
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

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		class_fastest: set[str] = set()

		for row in csv_reader:  # type: dict
			print('|-')

			# Wypisanie pozycji, organizatorzy niejednolicie używają nazwy kolumny z pozycją
			position = row['POSITION'] if 'POSITION' in row else row['POS']
			print(f'! {position}')

			# Wypisanie klasy
			print(f'| align="center" | {row["CLASS"]}')

			# Wypisanie nazwy zespołu z numerem samochodu i flagą
			team_data = get_team_data(
				codename=f'#{row["NUMBER"]} {row["TEAM"]}',
				championship_id=championship.db_id,
				wiki_id=wiki_id
			)

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

			# Wypisanie uzyskanego czasu
			time = row['TIME']
			if time != '':
				time = time.replace('.', ',')
				if row["CLASS"] in class_fastest:
					print(f'| align="center" | {time}')
				else:
					class_fastest.add(row["CLASS"])
					print(f'| align="center" | \'\'\'{time}\'\'\'')
				print('|')
			# W razie braku czasu zostaje wypisany myślnik w komórkach dla czasu i straty
			else:
				print('| align="center" | —')
				print('|')

			# Wypisanie pozycji startowej, która jest taka sama jak zajęta pozycja,
			# chyba że lista z ustawieniem na starcie mówi inaczej
			print(f'! {position}')

			line_count += 1

		print('|-')
		print('! colspan="6" | Źródła')
		print('|-')
		print('|}')

		print(f'\nPrzetworzone linie: {line_count}')


# Odczytanie pliku .CSV i wypisanie kodu fragmentu tabeli dla wyników sesji treningowych
def print_fp_table(championship: ChampionshipExt, filepath: str, wiki_id: int) -> None:
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

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0
		classes = set()

		for row in csv_reader:  # type: dict
			if row['CLASS'] not in classes:
				classes.add(row['CLASS'])

				print('|-')
				# Wypisanie nazwy klasy
				print(f'! {row['CLASS']}')

				# Wypisanie danych zespołu
				team_data = get_team_data(
					codename=f'#{row["NUMBER"]} {row["TEAM"]}',
					championship_id=championship.db_id,
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
					time = row['TIME'].replace('.', ',')
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


# Odczytanie sesji, której wyniki zawiera plik
def read_session(championship: ChampionshipExt) -> Session:
	if championship.name == 'FIA World Endurance Championship':
		options: list[dict[str, any]] = [
			{'name': 'Treningowa/testowa', 'enum': Session.PRACTICE},
			{'name': 'Kwalifikacyjna (przed Hyperpole)', 'enum': Session.QUALIFYING_PRE_HP},
			{'name': 'Kwalifikacyjna (po Hyperpole)', 'enum': Session.QUALIFYING_POST_HP},
			{'name': 'Wyścig', 'enum': Session.RACE}
		]
	else:
		options: list[dict[str, any]] = [
			{'name': 'Treningowa/testowa', 'enum': Session.PRACTICE},
			{'name': 'Kwalifikacyjna', 'enum': Session.QUALIFYING},
			{'name': 'Wyścig', 'enum': Session.RACE}
		]

	print('\nWybierz sesję, która jest w podanym pliku .CSV:')

	while True:
		for x in range(0, len(options)):
			print(f'{x + 1}. {options[x]['name']}')

		try:
			num = int(input('Wybór: '))
		except ValueError:
			print(f'Podaj liczbę naturalną z przedziału 1-{len(options)}\n')
			continue

		if num in range(1, len(options) + 1):
			return options[num - 1]['enum']
		else:
			print(f'Liczba musi być w przedziale 1-{len(options)}\n')


# Odczytanie serii wyścigowej, różne serie mogą inaczej nazywać kolumny w plikach .CSV
def read_series(championships: list[ChampionshipExt]) -> ChampionshipExt:
	print('\nPodaj serię wyścigową, z której pochodzą dane:')

	while True:
		for x in range(0, len(championships)):
			print(f'{x + 1}. {championships[x].name}')
		try:
			num = int(input('Wybór: '))
		except ValueError:
			print(f'Podaj liczbę naturalną z przedziału 1-{len(championships)}\n')
			continue

		if num in range(1, len(championships) + 1):
			return championships[num - 1]
		else:
			print(f'Liczba musi być w przedziale 1-{len(championships)}\n')


# Główna funkcja skryptu
def main() -> None:
	championship_list: list[ChampionshipExt] = get_championships()

	if len(championship_list) == 0:
		print('Nie znaleziono w bazie żadnych serii wyścigowych.')
		return

	plwiki_id = get_wiki_id('plwiki')

	if plwiki_id is None:
		msg: list[str] = [
			'\nNie znaleziono w bazie polskiej wersji językowej Wikipedii.',
			'Dane m.in. kierowców będą pobrane jedynie z pliku.'
		]
		print(' '.join(msg))

	championship_data: ChampionshipExt = read_series(championship_list)

	session: Session = read_session(championship_data)

	path: str = read_csv_path()

	match session:
		case Session.PRACTICE:
			print_fp_table(
				championship=championship_data,
				filepath=path,
				wiki_id=plwiki_id
			)
		case Session.QUALIFYING:
			print_qualifying_table(
				championship=championship_data,
				filepath=path,
				wiki_id=plwiki_id
			)
		case Session.QUALIFYING_PRE_HP:
			print_qualifying_pre_hp_table(
				championship=championship_data,
				filepath=path,
				wiki_id=plwiki_id
			)
		case Session.QUALIFYING_POST_HP:
			print_qualifying_post_hp_table(
				championship=championship_data,
				filepath=path,
				wiki_id=plwiki_id
			)
		case Session.RACE:
			print_race_table(
				championship=championship_data,
				filepath=path,
				wiki_id=plwiki_id
			)
		case _:
			print('Nieobsługiwany typ sesji')


# Automatyczne uruchamianie głównej funkcji skryptu
if __name__ == "__main__":
	main()
