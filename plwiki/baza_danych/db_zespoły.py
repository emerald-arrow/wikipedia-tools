import sys
import os
import csv
import re
from pathlib import Path

project_path = str(Path(__file__).parent.parent.parent)
if project_path not in sys.path:
	sys.path.append(project_path)

from common.models.team import Team  # noqa: E402

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True


# Zapisanie danych o zespołach do pliku .csv
def write_teams_csv(teams: list[Team]) -> None:
	from datetime import datetime

	timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
	filename = f'zespoły_{timestamp}.csv'

	headers = ['codename', 'nationality', 'car_number', 'short_link', 'long_link']

	with open(filename, mode='w', encoding='utf-8-sig') as csv_file:
		csv_writer = csv.writer(
			csv_file,
			delimiter=',',
			quoting=csv.QUOTE_NONNUMERIC,
			lineterminator='\n'
		)

		csv_writer.writerow(headers)

		for t in teams:
			csv_writer.writerow(list(t))

	print(f'\nZespoły zapisane w pliku {filename}: {len(teams)}')


# Odczytanie danych o zespołach z pliku zawierającego wyniki
def read_results_csv(file: str, wiki_id: int) -> list[Team]:
	from common.db_queries.country_code_table import get_country_iso_alpha3
	from common.db_queries.team_tables import check_team_exists

	teams = list()

	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0

		print('')

		for row in csv_reader:  # type: dict
			line_count += 1

			country_id: int = row.get('ECM Country Id')
			team_country: str | None = None

			if country_id is not None:
				team_country = get_country_iso_alpha3(country_id)

			if team_country is None:
				team_country = '?'

			team_codename = f'#{row.get("NUMBER")} {row.get("TEAM")}'
			team_car_no = row.get('NUMBER')
			team_short_link = f'[[{row.get("TEAM")}]]'

			if team_country != '?':
				check_team_db: bool = check_team_exists(
					team_codename,
					team_country,
					team_car_no,
					wiki_id
				)

				if check_team_db:
					print(f'{team_codename} ({team_country}) jest już w bazie.')
					continue

			team = Team(
				codename=team_codename,
				nationality=team_country,
				car_number=team_car_no,
				short_link=team_short_link
			)

			teams.append(team)

		print(f'\nPrzetworzone linie: {line_count}\nZnalezione zespoły: {len(teams)}')

	return teams


# Sprawdzenie czy podany plik z wynikami ma wymagane kolumny
def verify_results_csv(file: str) -> bool:
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return (
			'NUMBER' in headers and
			'TEAM' in headers
		)


# Odczytanie ścieżki do pliku z wynikami
def read_results_csv_path() -> str:
	while True:
		text = input('\nPodaj ścieżkę do pliku .CSV pobranego ze strony Alkamelsystems:\n')

		if not os.path.isfile(text):
			print('\nŚcieżka nieprawidłowa, spróbuj ponownie.')
			continue
		elif not text.lower().endswith('.csv'):
			print('\nPodany plik nie ma rozszerzenia .csv')
			continue
		elif not verify_results_csv(text):
			print('\nPlik nie posiada wymaganych kolumn.')
			continue
		else:
			return text


# Tworzenie pliku .csv z danymi zespołów
def team_data_to_csv_mode() -> None:
	from common.db_queries.wikipedia_table import get_wiki_id

	plwiki_id: int | None = get_wiki_id('plwiki')

	if plwiki_id is None:
		print('Nie znaleziono w bazie danych polskiej wersji Wikipedii.')
		return

	path: str = read_results_csv_path()

	teams: list[Team] = read_results_csv(path, plwiki_id)

	if len(teams) == 0:
		return

	write_teams_csv(teams)


# Sprawdzenie czy podany plik z danymi zespołów ma wymagane kolumny
def verify_teams_csv(path: str) -> bool:
	with open(path, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=',')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return (
			'codename' in headers
			and 'nationality' in headers
			and 'car_number' in headers
			and 'short_link' in headers
			and 'long_link' in headers
		)


# Sprawdzenie katalogu czy zawiera pliki z danymi zespołów
def get_teams_csv_files_in_dir() -> list[str]:
	csv_files: list[str] = []
	files = [f for f in os.listdir() if os.path.isfile(f)]

	for f in files:
		if re.search('zespoły_.*\\.([Cc][Ss][Vv])', f) is not None:
			if verify_teams_csv(f):
				csv_files.append(f)

	return csv_files


# Wybór pliku z danymi o zespołach
def choose_teams_csv_file() -> str:
	csv_files: list[str] = get_teams_csv_files_in_dir()

	if len(csv_files) > 1:
		for x in range(0, len(csv_files)):
			print(f'{x + 1}. {csv_files[x]}')

		while True:
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
			msg: list[str] = [
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
		text = input('\nPodaj ścieżkę do pliku .csv zawierającego dane o zespołach:\n')

		if not os.path.isfile(text):
			print('\nŚcieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if not text.lower().endswith('.csv'):
			print('\nPodany plik nie posiada rozszerzenia .csv.')
			continue
		if not verify_teams_csv(text):
			print('\nPodany plik csv nie posiada wymaganych kolumn.')
			continue

		return text


# Odczytanie danych o zespołach
def read_teams_csv(path: str) -> list[Team]:
	teams: list[Team] = list()

	with open(path, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=',')
		line_count = 0

		for row in csv_reader:  # type: dict
			line_count += 1

			codename = row.get('codename')
			nationality = row.get('nationality')
			car_number = row.get('car_number')
			short_link = row.get('short_link')
			long_link = row.get('long_link')

			if (
				codename is not None
				and nationality is not None
				and car_number is not None
				and short_link is not None
				and long_link is not None
			):
				teams.append(
					Team(
						codename,
						nationality,
						car_number,
						short_link,
						long_link
					)
				)

		print(f'\nPrzetworzone linie: {line_count}.\nLiczba znalezionych zespołów: {len(teams)}.')

	return teams


# Odczytanie id serii, w której startują zespoły
def read_championship() -> int:
	from common.db_queries.championship_table import get_championships

	championships = get_championships()

	while True:
		print('\nWybierz serię, w której startują zespoły z wczytanego pliku:')

		for x in range(0, len(championships)):
			print(f'{x + 1}. {championships[x].name}')

		try:
			num = int(input(f'Wybór (1-{len(championships)}): '))
		except (TypeError, ValueError):
			print(f'\nPodaj liczbę naturalną z przedziału 1-{len(championships)}')
			continue

		if num - 1 not in range(0, len(championships)):
			print(f'\nPodaj liczbę naturalną z zakresu 1-{len(championships)}')
			continue
		else:
			return championships[num - 1].db_id


# Zapisanie danych o zespołach w bazie
def team_data_to_db_mode() -> None:
	from common.db_queries.team_tables import add_team
	from common.db_queries.wikipedia_table import get_wiki_id
	from common.db_queries.entity_table import get_entity_type_id

	wiki_id: int | None = get_wiki_id('plwiki')

	if wiki_id is None:
		print('\nW bazie nie znaleziono polskiej Wikipedii. Nie można dodać zespołów do bazy.')
		return

	type_id: int | None = get_entity_type_id('team')

	if type_id is None:
		print('\nW bazie nie znaleziono typu zespołów. Nie można dodać zespołów do bazy.')
		return

	chosen_file: str = choose_teams_csv_file()

	teams: list[Team] = read_teams_csv(chosen_file)

	championship_id: int = read_championship()

	for team in teams:
		if add_team(team, championship_id, wiki_id, type_id):
			print(f'{team.codename} - dodano pomyślnie do bazy')


# Wybór trybu pracy skryptu
def choose_mode() -> None:
	options = {
		1: 'Wygenerować plik .csv z danymi o zespołach',
		2: 'Zapisać dane o zespołach w bazie',
		3: 'Zakończyć działanie'
	}

	while True:
		print('\nWybierz co ma zrobić skrypt.')

		for o in options:
			print(f'{o}. {options[o]}')

		try:
			num = int(input(f'Wybór 1-{len(options)}: '))
		except ValueError:
			print('\nWybór spoza powyższej listy, spróbuj ponownie.')
			continue

		if num not in options:
			print('\nWybór spoza powyższej listy, spróbuj ponownie.')
			continue
		elif num == 1:
			team_data_to_csv_mode()
			break
		elif num == 2:
			team_data_to_db_mode()
			break
		elif num == 3:
			return


if __name__ == '__main__':
	choose_mode()
