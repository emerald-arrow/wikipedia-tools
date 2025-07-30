import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

if True:  # noqa: E402
	import os
	from csv import DictReader
	from pathlib import Path

	project_path = str(Path(__file__).parent.parent.parent.parent)
	if project_path not in sys.path:
		sys.path.append(project_path)

	from common.models.sessions import Session
	from common.models.championship import Championship
	from common.models.driver import Driver
	from common.models.teams import Team
	from common.db_queries.wikipedia_table import get_wiki_id
	from common.db_queries.team_tables import get_team_data
	from common.db_queries.driver_tables import get_driver_data_by_codename
	from common.db_queries.car_tables import get_car_link
	from common.db_queries.championship_table import get_championships


# Odczytanie pliku .CSV i wypisanie kodu tabeli dla wyników wyścigu
def print_race_table(championship: Championship, filepath: str, wiki_id: int) -> None:
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
	print(*table_header, sep='\n')

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader[str] = DictReader(csv_file, delimiter=';')
		line_count: int = 0
		class_winners: set[str] = set()
		statuses: set[str] = set()

		for row in csv_reader:  # type: dict[str]
			status: str = row['STATUS']

			if status != 'Classified' and status not in statuses:
				statuses.add(status)
				print('|-')
				print(f'! colspan="8" | {status}')

			category: str = row['CLASS']

			# Pogrubienie wierszy ze zwycięzcami klas
			if category not in class_winners:
				print('|- style="font-weight: bold;"')
				class_winners.add(category)
			else:
				print('|-')

			# Pozycja zajęta w klasyfikacji ogólnej wyścigu
			if status == 'Classified':
				print(f'! {row['POSITION']}')
			else:
				print('!')

			# Wypisanie klasy z ewentualną dodatkową grupą (np. Pro/Am)
			if 'GROUP' in row and row['GROUP'] != '':
				print(f'| align="center" | {category}<br>{row['GROUP']}')
			else:
				print(f'| align="center" | {category}')

			# Wypisanie nazwy zespołu, numeru auta i odpowiedniej flagi
			team_data: Team | None = get_team_data(
				codename=f'#{row["NUMBER"]} {row["TEAM"]}',
				championship_id=championship.db_id,
				wiki_id=wiki_id
			)

			if team_data is not None and not team_data.empty_fields():
				print('| {{{{Flaga|{country}}}}} #{number} {team_link}'.format(
					country=team_data.nationality,
					number=team_data.car_number,
					team_link=team_data.long_link if team_data.long_link != '' else team_data.short_link
				))
			else:
				print('| {{{{Flaga|?}}}} #{number} [[{team_link}]]'.format(
					number=row['NUMBER'],
					team_link=row['TEAM']
				))

			# Wypisanie listy kierowców z flagami
			drivers: list[Driver] = list()

			if 'DRIVER_1' in row:
				driver_columns: list[str] = ['DRIVER_{number}']
			elif 'DRIVER1_FIRSTNAME' in row and 'DRIVER1_SECONDNAME' in row:
				driver_columns: list[str] = ['DRIVER{number}_FIRSTNAME', 'DRIVER{number}_SECONDNAME']
			else:
				print('| Imiona i nazwiska kierowców znajdują się w innych kolumnach niż przewiduje skrypt.')

			# Składy są co najwyżej czteroosobowe
			for x in range(1, 5):  # type: int
				driver_codename: str = ''

				for column in driver_columns:  # type: str
					driver_codename += f' {row[column.format(number=x)]}'

				driver_codename = driver_codename.lstrip()

				if len(driver_codename) > 1:
					driver_data: Driver | None = get_driver_data_by_codename(driver_codename.lower(), wiki_id)

					if driver_data is None or driver_data.empty_fields():
						driver_name = driver_codename.split(' ', 1)

						driver_short_link = driver_name[0]

						if len(driver_name) > 1:
							driver_short_link += f' {driver_name[1].capitalize()}'

						driver_data = Driver(
							nationality='?',
							short_link=driver_short_link
						)

					drivers.append(driver_data)

			for x in range(0, len(drivers)):  # type: int
				if x == 0:
					start: str = '| '
					end: str = ''
				elif 0 < x < len(drivers) - 1:
					start: str = '<br>'
					end: str = ''
				else:
					start: str = '<br>'
					end: str = '\n'

				print('{start}{{{{Flaga|{flag}}}}} {link}'.format(
					start=start,
					flag=drivers[x].nationality,
					link=drivers[x].long_link if drivers[x].long_link != '' else drivers[x].short_link
				), end=end)

			# Wypisanie auta
			car: str | None = get_car_link(row['VEHICLE'], wiki_id)

			if car is None or car == '':
				car = f'[[{row["VEHICLE"]}]]'

			print(f'| {car}')

			# Wypisanie opon
			tyre_oem: str = row['TYRES'] if 'TYRES' in row else row['TIRES']

			print('| align="center" | {{Opony|%s}}' % tyre_oem)

			# Wypisanie liczby okrążeń
			print(f'| align="center" | {row["LAPS"]}')

			# Wypisanie czasu wyścigu/straty/statusu
			if status == 'Classified':
				# Wypisanie straty czasowej/liczby okrążeń
				if line_count > 0:
					gap: str = row['GAP_FIRST'].replace('.', ',').replace('\'', ':')

					gap = gap.replace('Laps', 'okr.')

					gap = gap if gap.startswith('+') else f'+{gap}'

					print(f'| {gap}')
				# Wypisanie czasu wyścigu u zwycięzcy
				elif line_count == 0:
					total_time: str = row['TOTAL_TIME'].replace('.', ',').replace('\'', ':')
					print(f'| align="center" | {total_time}')
			else:
				# Wypisanie pustej komórki, jeśli nieklasyfikowany, zdyskwalifikowany itp.
				print('|')

			line_count += 1

		print('|-')
		print('|}')

		print(f'\nPrzetworzone linie: {line_count}')


# Odczytanie pliku .CSV i wypisanie kodu tabeli dla wyników kwalifikacji
def print_qualifying_table(championship: Championship, filepath: str, wiki_id: int) -> None:
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
	print(*table_header, sep='\n')

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader[str] = DictReader(csv_file, delimiter=';')
		line_count: int = 0
		class_polesitters: set[str] = set()

		for row in csv_reader:  # type: dict[str]
			category: str = row['CLASS']

			# Pogrubienie wierszy ze zdobywcami pole position w klasach
			if category not in class_polesitters:
				print('|- style="font-weight: bold;"')
				class_polesitters.add(category)
			else:
				print('|-')

			# Wypisanie pozycji, organizatorzy niejednolicie używają nazwy kolumny z pozycją
			position: str = row['POSITION'] if 'POSITION' in row else row['POS']
			print(f'! {position}')

			# Wypisanie klasy
			print(f'| align="center" | {category}')

			# Wypisanie nazwy zespołu z numerem samochodu i flagą
			team_data: Team | None = get_team_data(
				codename=f'#{row["NUMBER"]} {row["TEAM"]}',
				championship_id=championship.db_id,
				wiki_id=wiki_id
			)

			if team_data is not None and not team_data.empty_fields():
				print('| {{{{Flaga|{country}}}}} #{number} {team_link}'.format(
					country=team_data.nationality,
					number=team_data.car_number,
					team_link=team_data.short_link
				))
			else:
				print('| {{{{Flaga|?}}}} #{number} [[{team_link}]]'.format(
					number=row['NUMBER'],
					team_link=row['TEAM']
				))

			drivers: list[Driver] = list()

			# Zebranie danych o kierowcach, maksymalnie składy czteroosobowe
			for x in range(1, 5):  # type: int
				if (
					row[f'DRIVER{x}_FIRSTNAME'] is None
					or row[f'DRIVER{x}_FIRSTNAME'] == '' and row[f'DRIVER{x}_SECONDNAME'] == ''
				):
					continue

				driver_name = '{name} {lastname}'.format(
					name=row[f'DRIVER{x}_FIRSTNAME'].capitalize(),
					lastname=row[f'DRIVER{x}_SECONDNAME'].capitalize()
				)

				driver_data: Driver | None = get_driver_data_by_codename(driver_name.lower(), wiki_id)

				if driver_data is None or driver_data.empty_fields():
					driver_data = Driver(
						short_link=driver_name.strip(),
						nationality=row[f'DRIVER{x}_COUNTRY']
					)

				drivers.append(driver_data)

			# Wypisanie kierowców
			for x in range(0, len(drivers)):  # type: int
				if x == 0:
					start: str = '| '
					end: str = ''
				elif 0 < x < len(drivers) - 1:
					start: str = '<br>'
					end: str = ''
				else:
					start: str = '<br>'
					end: str = '\n'

				print('{start}{{{{Flaga|{flag}}}}} {link}'.format(
					start=start,
					flag=drivers[x].nationality,
					link=drivers[x].short_link
				), end=end)

			# Wypisanie uzyskanego czasu i straty
			time: str = row['TIME']
			if time != '':
				time = time.replace('.', ',')
				print(f'| align="center" | {time}')

				gap: str = row['GAP_FIRST'].replace('.', ',').replace('\'', ':')

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
def print_qualifying_post_hp_table(championship: Championship, filepath: str, wiki_id: int) -> None:
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
	print(*table_header, sep='\n')

	# Odczytanie nagłówków kolumn zawierających czasy sesji kwalifikacyjnych
	session_headers: dict[str, list[str]] = dict()

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_header_reader: DictReader[str] = DictReader(csv_file, delimiter=';')
		csv_headers: list[str] = list(dict(list(csv_header_reader)[0]).keys())
		q1_headers: list[str] = [x for x in csv_headers if x.startswith('QP')]
		hp_headers: list[str] = [x for x in csv_headers if x.startswith('HP')]

	if len(q1_headers) > 0:
		session_headers.update({'QP': q1_headers})

	if len(hp_headers) > 0:
		session_headers.update({'HP': hp_headers})

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader[str] = DictReader(csv_file, delimiter=';')
		line_count: int = 0

		class_polesitters: set[str] = set()

		for row in csv_reader:  # type: dict[str]
			print('|-')

			# Wypisanie pozycji, organizatorzy niejednolicie używają nazwy kolumny z pozycją
			position: str = row['POSITION'] if 'POSITION' in row else row['POS']
			print(f'! {position}')

			category: str = row['CLASS']

			# Pogrubienie nazwy klasy dla zdobywcy pole position w klasie
			if category not in class_polesitters:
				category = f"'''{category}'''"

			# Wypisanie klasy
			print(f'| align="center" | {category}')

			# Wypisanie nazwy zespołu z numerem samochodu i flagą
			team_data: Team | None = get_team_data(
				codename=f'#{row["NUMBER"]} {row["TEAM"]}',
				championship_id=championship.db_id,
				wiki_id=wiki_id
			)

			if team_data is not None and not team_data.empty_fields():
				row_team: str = '{{{{Flaga|{country}}}}} #{number} {team_link}'.format(
					country=team_data.nationality,
					number=team_data.car_number,
					team_link=team_data.short_link
				)
			else:
				row_team: str = '{{{{Flaga|?}}}} #{number} [[{team_link}]]'.format(
					number=row['NUMBER'],
					team_link=row['TEAM']
				)

			if category in class_polesitters:
				print(f"| {row_team}")
			else:
				print(f"| '''{row_team}'''")

			q1_time: str = ''
			for q1 in session_headers.get('QP'):
				if row.get(q1) != '':
					q1_time = row.get(q1)
					break

			hp_time: str = ''
			for hp in session_headers.get('HP'):
				if row.get(hp) != '':
					hp_time = row.get(hp)
					break

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

			# Wypisanie pozycji startowej, która jest taka sama jak zajęta pozycja w kwalifikacjach,
			# chyba że lista z ustawieniem na starcie mówi inaczej
			print(f'! {position}')

			line_count += 1

		print('|-')
		print('! colspan="7" | Źródła')
		print('|-')
		print('|}')

		print(f'\nPrzetworzone linie: {line_count}')


# Odczytanie pliku .CSV i wypisanie kodu tabeli dla wyników sesji kwalifikacyjnej przed Hyperpole
def print_qualifying_pre_hp_table(championship: Championship, filepath: str, wiki_id: int) -> None:
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
	print(*table_header, sep='\n')

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader = DictReader(csv_file, delimiter=';')
		line_count: int = 0
		class_fastest: set[str] = set()

		for row in csv_reader:  # type: dict[str]
			print('|-')

			# Wypisanie pozycji, organizatorzy niejednolicie używają nazwy kolumny z pozycją
			position = row['POSITION'] if 'POSITION' in row else row['POS']
			print(f'! {position}')

			# Wypisanie klasy
			print(f'| align="center" | {row["CLASS"]}')

			# Wypisanie nazwy zespołu z numerem samochodu i flagą
			team_data: Team | None = get_team_data(
				codename=f'#{row["NUMBER"]} {row["TEAM"]}',
				championship_id=championship.db_id,
				wiki_id=wiki_id
			)

			if team_data is not None and not team_data.empty_fields():
				print('| {{{{Flaga|{country}}}}} #{number} {team_link}'.format(
					country=team_data.nationality,
					number=team_data.car_number,
					team_link=team_data.short_link
				))
			else:
				print('| {{{{Flaga|?}}}} #{number} [[{team_link}]]'.format(
					number=row['NUMBER'],
					team_link=row['TEAM']
				))

			# Wypisanie uzyskanego czasu
			time: str = row['TIME']
			if time != '':
				time = time.replace('.', ',')
				if row['CLASS'] in class_fastest:
					print(f'| align="center" | {time}')
				else:
					class_fastest.add(row['CLASS'])
					print(f'| align="center" | \'\'\'{time}\'\'\'')
				print('|')
			# W razie braku czasu zostaje wypisany myślnik w komórkach dla czasu i straty
			else:
				print('| align="center" | —')
				print('|')

			# Wypisanie pozycji startowej, która jest taka sama jak zajęta pozycja w kwalifikacjach,
			# chyba że lista z ustawieniem na starcie mówi inaczej
			print(f'! {position}')

			line_count += 1

		print('|-')
		print('! colspan="6" | Źródła')
		print('|-')
		print('|}')

		print(f'\nPrzetworzone linie: {line_count}')


# Odczytanie pliku .CSV i wypisanie kodu fragmentu tabeli dla wyników sesji treningowych
def print_fp_table(championship: Championship, filepath: str, wiki_id: int) -> None:
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
	print(*table_header, sep='\n')

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader = DictReader(csv_file, delimiter=';')
		line_count: int = 0
		classes: set[str] = set()

		for row in csv_reader:  # type: dict[str]
			if row['CLASS'] not in classes:
				classes.add(row['CLASS'])

				print('|-')
				# Wypisanie nazwy klasy
				print(f'! {row['CLASS']}')

				# Wypisanie danych zespołu
				team_data: Team | None = get_team_data(
					codename=f'#{row["NUMBER"]} {row["TEAM"]}',
					championship_id=championship.db_id,
					wiki_id=wiki_id
				)

				if team_data is not None and not team_data.empty_fields():
					print('| {{{{Flaga|{country}}}}} #{number} {team_link}'.format(
						country=team_data.nationality,
						number=team_data.car_number,
						team_link=team_data.short_link
					))
				else:
					print('| {{{{Flaga|?}}}} #{number} [[{team_link}]]'.format(
						number=row['NUMBER'],
						team_link=row['TEAM']
					))

				# Wypisanie auta
				car: str | None = get_car_link(row['VEHICLE'], wiki_id)

				if car is None or car == '':
					car = f'[[{row["VEHICLE"]}]]'

				print(f'| {car}')

				# Wypisanie czasu
				time: str = row['TIME']

				if time != '':
					time = time.replace('.', ',')
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
		text: str = input('\nPodaj ścieżkę do pliku .CSV pobranego ze strony Alkamelsystems:\n').strip()

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if not text.lower().endswith('.csv'):
			print('Ścieżka nie prowadzi do pliku z rozszerzeniem .csv.')
			continue
		else:
			return text


# Odczytanie sesji, której wyniki zawiera plik
def read_session(championship: Championship) -> Session:
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

	print('\nWybierz sesję, której wyniki są w podanym pliku .CSV:')

	while True:
		for x in range(0, len(options)):
			print(f'{x + 1}. {options[x]['name']}')

		try:
			num: int = int(input('Wybór: ').strip())
		except ValueError:
			print(f'Podaj liczbę naturalną z przedziału 1-{len(options)}\n')
			continue

		if num in range(1, len(options) + 1):
			return options[num - 1]['enum']
		else:
			print(f'Liczba musi być w przedziale 1-{len(options)}\n')


# Odczytanie serii wyścigowej, różne serie mogą inaczej nazywać kolumny w plikach .CSV
def read_series(championships: list[Championship]) -> Championship:
	print('\nPodaj serię wyścigową, z której pochodzą dane:')

	while True:
		for x in range(0, len(championships)):
			print(f'{x + 1}. {championships[x].name}')
		try:
			num: int = int(input('Wybór: ').strip())
		except ValueError:
			print(f'Podaj liczbę naturalną z przedziału 1-{len(championships)}\n')
			continue

		if num in range(1, len(championships) + 1):
			return championships[num - 1]
		else:
			print(f'Liczba musi być w przedziale 1-{len(championships)}\n')


# Główna funkcja skryptu
def main() -> None:
	script_cannot_continue: str = 'Skrypt nie może kontynuować i zakończy swoje działanie.'

	championship_list: list[Championship] | None = get_championships()

	if championship_list is None:
		print(f'\n{script_cannot_continue}')
		return

	if len(championship_list) == 0:
		print(f'\nNie znaleziono w bazie żadnych serii wyścigowych. {script_cannot_continue}')
		return

	plwiki_id: int | None = get_wiki_id('plwiki')

	if plwiki_id is None:
		print(f'\n{script_cannot_continue}')
		return

	if plwiki_id == -1:
		msg: list[str] = [
			'\nNie znaleziono w bazie polskiej wersji językowej Wikipedii.',
			'Dane m.in. kierowców będą pobrane jedynie z pliku.'
		]
		print(*msg, sep=' ')

	championship_data: Championship = read_series(championship_list)

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
