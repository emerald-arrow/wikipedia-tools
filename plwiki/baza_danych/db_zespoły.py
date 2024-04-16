import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

import os
import csv
import re

from modele import Team

# Zapisanie danych o zespołach do pliku .csv
def write_drivers_csv(teams: list[Team]) -> None:
	from datetime import datetime
	timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
	filename = f'zespoły_{timestamp}.csv'

	headers = ['codename','nationality','car_number','short_link','long_link']

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
	
	print(f'Do pliku {filename} zapisano dane o {len(teams)} zespołach')

# Odczytanie danych o zespołach z pliku zawierającego wyniki
def read_results_csv(file: str) -> list[Team]:
	teams = list()

	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		from db_zapytania import get_country_iso_alpha3
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0

		for row in csv_reader:
			try:
				country_id: int = row["ECM Country Id"]
				team_country = get_country_iso_alpha3(country_id)
			except KeyError:
				team_country = '?'

			team_codename = f'#{row["NUMBER"]} {row["TEAM"]}'
			team_car_no = int(row['NUMBER'])
			team_short_link = f'[[{row["TEAM"]}]]'

			team = Team(
				codename=team_codename,
				nationality=team_country,
				car_number=team_car_no,
				short_link=team_short_link
			)

			teams.append(team)

			line_count += 1

		print(f'Przetworzone linie: {line_count}\nZnalezione zespoły: {len(teams)}')
	
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
		text = input('Podaj ścieżkę do pliku .CSV pobranego ze strony Alkamelsystems:\n')

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		elif not verify_results_csv(text):
			print('Plik nie posiada wymaganych kolumn.')
			continue
		else:
			return text

# Tworzenie pliku .csv z danymi zespołów
def team_data_to_csv_mode() -> None:
	path: str = read_results_csv_path()

	teams: list[Team] = read_results_csv(path)

	write_drivers_csv(teams)

# Sprawdzenie czy podany plik z danymi zespołów ma wymagane kolumny
def verify_teams_csv(path: str) -> bool:
	with open(path, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=',')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return (
			'codename' in headers and
			'nationality' in headers and
			'car_number' in headers and
			'short_link' in headers and
			'long_link' in headers
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
			print(f'{x+1}. {csv_files[x]}')
	
		while True:
			try:
				num = int(input(f'Wybór (1-{len(csv_files)}): '))
			except ValueError:
				print('Podaj liczbę widoczną przy nazwie pliku')
				continue

			if num-1 in range(0, len(csv_files)):
				return csv_files[num-1]
			else:
				print('Błędna liczba. Spróbuj ponownie.')
				continue
	elif len(csv_files) == 1:
		options = {
			1: 'Tak',
			2: 'Nie'
		}

		print(f'Jedyny znaleziony plik to {csv_files[0]}. Czy chcesz zapisać jego zawartość do bazy danych?')

		for x in options:
			print(f'{x}. {options[x]}')

		while True:
			try:
				num = int(input('Wybór (1-2): '))
			except ValueError:
				print('Podaj liczbę 1 lub 2.')
				continue
			
			if num in options:
				if num == 1:
					return csv_files[0]
				else:
					break
			else:
				print('Podaj liczbę 1 lub 2.')
				continue
	
	while True:
		text = input('Podaj ścieżkę do pliku .csv zawierającego dane o zespołach:\n')

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if re.search('.*\\.([Cc][Ss][Vv])', text) is None:
			print('Podany plik nie posiada rozszerzenia csv.')
			continue
		if not verify_teams_csv(text):
			print('Podany plik csv nie posiada wymaganych kolumn.')
			continue

		return text

# Odczytanie danych o zespołach
def read_teams_csv(path: str) -> list[Team]:
	teams: list[Team] = list()
	
	with open(path, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=',')
		line_count = 0

		for row in csv_reader:
			try:
				codename = row['codename']
				nationality = row['nationality']
				car_number = row['car_number']
				short_link = row['short_link']
				long_link = row['long_link']
			except:
				line_count += 1
				continue

			teams.append(Team(codename, nationality, int(car_number), short_link, long_link))
			line_count += 1
		
		print(f'Przetworzone linie: {line_count}.\nLiczba znalezionych zespołów: {len(teams)}.')
	
	return teams

# Odczytanie id serii, w której startują zespoły
def read_championship() -> int:
	from db_zapytania import get_championships

	championships = get_championships()

	num: int = None

	print('Wybierz serię w której startują zespoły z wczytanego pliku:')

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

# Zapisanie danych o zespołach w bazie
def team_data_to_db_mode() -> None:
	from db_zapytania import add_team
	from db_zapytania import get_wiki_id
	from db_zapytania import get_entity_type_id

	chosen_file = choose_teams_csv_file()

	teams: list[Team] = read_teams_csv(chosen_file)

	championship_id = read_championship()

	wiki_id: int | None = get_wiki_id('plwiki')

	type_id: int | None = get_entity_type_id('team')

	if wiki_id is None:
		print('W bazie nie znaleziono polskiej Wikipedii. Nie można dodać zespołów do bazy.')
		return
	
	if type_id is None:
		print('W bazie nie znaleziono typu zespołów. Nie można dodać zespołów do bazy.')
		return

	for team in teams:
		if add_team(team, championship_id, wiki_id, type_id):
			print(f'{team.codename} - dodano pomyślnie do bazy')

# Wybór trybu pracy skryptu
def choose_mode() -> None:
	options = {
		'1': 'Wygenerować plik .csv z danymi o zespołach',
		'2': 'Zapisać dane o zespołach w bazie',
		'3': 'Zakończyć działanie'
	}

	print('Wybierz co ma zrobić skrypt.')

	for o in options:
		print(f'{o}. {options[o]}')
	
	while True:
		text = input('Wybór: ')

		if text not in options:
			print('Wybór spoza powyższej listy, spróbuj ponownie.')
			continue
		elif text == '1':
			team_data_to_csv_mode()
			break
		elif text == '2':
			team_data_to_db_mode()
			break
		elif text == '3':
			return

# Główna funkcja skryptu
def main() -> None:
	choose_mode()

if __name__ == '__main__':
	main()