import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

import os
import csv
import re

from modele import Car

# Zapisanie nazw samochodów do pliku .csv
def write_cars_csv(cars: set[Car]) -> None:
	from datetime import datetime
	
	timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
	filename = f'auta_{timestamp}.csv'

	headers = ['codename','link']

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
	
	print(f'Do pliku {filename} zapisano {len(cars)} aut')

# Odczytanie samochodów z pliku zawierającego wyniki
def read_results_csv(path: str) -> set[Car]:
	cars: set[Car] = set()
	
	with open(path, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0

		for row in csv_reader:
			try:
				codename = row["VEHICLE"]
			except:
				line_count += 1
				continue

			cars.add(Car(codename, f'[[{codename}]]'))
			line_count += 1
		
		print(f'Przetworzone linie: {line_count}')
	
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
		text = input('Podaj ścieżkę do pliku .CSV pobranego ze strony Alkamelsystems:\n')

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if not verify_results_csv(text):
			print('Plik nie posiada wymaganych kolumn.')
			continue
		else:
			return text

# Tworzenie pliku .csv z danymi aut
def car_data_to_csv_mode() -> None:
	path: str = read_path_to_results_csv()

	cars: set[Car] = read_results_csv(path)

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

# Sprawdzenie katalogu czy zawiera pliki z danymi aut
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
		text = input('Podaj ścieżkę do pliku .csv zawierającego dane o autach:\n')

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if re.search('.*\\.([Cc][Ss][Vv])', text) is None:
			print('Podany plik nie posiada rozszerzenia csv.')
			continue
		if not verify_cars_csv(text):
			print('Podany plik csv nie posiada wymaganych kolumn.')
			continue

		return text

# Odczytanie danych o autach z pliku zawierającego dane o nich
def read_cars_csv(path: str) -> set[Car]:
	cars: set[Car] = set()
	
	with open(path, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=',')
		line_count = 0

		for row in csv_reader:
			try:
				codename = row['codename']
				link = row['link']
			except:
				line_count += 1
				continue

			cars.add(Car(codename, link))
			line_count += 1
		
		print(f'Przetworzone linie: {line_count}.\nLiczba znalezionych aut: {len(cars)}.')
	
	return cars

# Zapisanie danych o autach w bazie
def car_data_to_db_mode() -> None:
	from db_zapytania import add_car
	from db_zapytania import get_wiki_id
	
	chosen_file: str = choose_car_csv_file()

	cars: set[Car] = read_cars_csv(chosen_file)

	if len(cars) == 0:
		return

	plwiki_id: int | None  = get_wiki_id('plwiki')

	if plwiki_id is None:
		print('Nie znaleziono id polskiej Wikipedii w bazie danych. Nie można rozpocząć dodawania danych do bazy danych.')
		return

	for car in cars:
		add_car(car, plwiki_id)	

# Wybór trybu pracy skryptu
def choose_mode() -> None:
	options = {
		'1': 'Wygenerować plik .csv z danymi o autach',
		'2': 'Zapisać dane o autach w bazie',
		'3': 'Zakończyć działanie'
	}

	print('Wybierz co ma zrobić skrypt.')

	for o in options:
		print(f'{o}. {options[o]}')

	while True:
		try:
			num = int(input('Wybór: '))
		except ValueError:
			print('Podaj liczbę między 1 a 3.')
			continue

		if num not in options:
			print('Wybór spoza powyższej listy, spróbuj ponownie.')
			continue
		elif num == 1:
			car_data_to_csv_mode()
			break
		elif num == 2:
			car_data_to_db_mode()
			break
		elif num == 3:
			return

# Główna funkcja skryptu
def main() -> None:
	choose_mode()

if __name__ == "__main__":
	main()