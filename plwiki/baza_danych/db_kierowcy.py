import sys

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True

import os
import csv
import re

from modele import Driver

# Zapisanie danych o kierowcach do pliku .csv
def write_drivers_csv(drivers: list[Driver]) -> None:
	from datetime import datetime
	timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
	filename = f'kierowcy_{timestamp}.csv'
	
	headers = ['codename','nationality','short_link','long_link']

	with open(filename, mode='w', encoding='utf-8-sig') as csv_file:
		csv_writer = csv.writer(
			csv_file,
			delimiter=',',
			quoting=csv.QUOTE_NONNUMERIC,
			lineterminator='\n'
		)

		csv_writer.writerow(headers)

		for d in drivers:
			csv_writer.writerow(list(d))
	
	print(f'\nDo pliku {filename} zapisano dane o {len(drivers)} kierowcach')

# Odczytanie danych o kierowcach kierowców z pliku zawierającego wyniki
def read_results_csv(file) -> list[Driver]:
	from db_zapytania import check_driver_exists

	drivers: list[Driver] = list()

	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0

		print('')

		for row in csv_reader:
			line_count += 1

			for x in range(1,5):
				if row[f'DRIVER{x}_FIRSTNAME'] != '':
					driver_codename='%s %s' % (
						row[f'DRIVER{x}_FIRSTNAME'].lower(),
						row[f'DRIVER{x}_SECONDNAME'].lower()
					)
					
					driver_nationality = row[f'DRIVER{x}_COUNTRY']

					if check_driver_exists(driver_codename, driver_nationality):
						print(f'{driver_codename} ({driver_nationality}) jest już w bazie.')
						continue

					driver_short_link='[[%s %s]]' % (
						row[f'DRIVER{x}_FIRSTNAME'].capitalize(),
						row[f'DRIVER{x}_SECONDNAME'].capitalize()
					)
					
					driver = Driver(
						codename=driver_codename,
						nationality=driver_nationality,
						short_link=driver_short_link
					)

					drivers.append(driver)

		print(f'\nPrzetworzne linie: {line_count}.\nZnalezioni kierowcy: {len(drivers)}')
	
	return drivers

# Sprwadzenie czy podany plik z wynikami ma wymagane nazwy kolumn
def verify_results_csv(file) -> bool:
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return (
			'DRIVER1_FIRSTNAME' in headers and
			'DRIVER1_SECONDNAME' in headers and
			'DRIVER1_COUNTRY' in headers and
			'DRIVER2_FIRSTNAME' in headers and
			'DRIVER2_SECONDNAME' in headers and
			'DRIVER2_COUNTRY' in headers
		)

# Odczytanie ścieżki do pliku z wynikami
def read_results_csv_path() -> str:
	text = ''

	while True:
		text = input('\nPodaj ścieżkę do pliku .CSV pobranego ze strony Alkamelsystems:\n')

		if not os.path.isfile(text):
			print('\nŚcieżka nieprawidłowa, spróbuj ponownie.')
			continue
		elif not verify_results_csv(text):
			print('\nPlik nie posiada wymaganych kolumn.')
			continue
		else:
			return text

# Tworzenie pliku .csv z danymi kierowców
def driver_data_to_csv_mode() -> None:
	path: str = read_results_csv_path()

	drivers: list[Driver] = read_results_csv(path)

	if len(drivers) == 0:
		return

	write_drivers_csv(drivers)

# Sprawdzenie czy podany plik z danymi kierowców ma wymagane kolumny
def verify_drivers_csv(path: str) -> bool:
	with open(path, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=',')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return (
			'codename' in headers and
			'nationality' in headers and
			'short_link' in headers and
			'long_link' in headers
		)

# Sprawdzenie katalogu czy zawiera pliki z danymi kierowców
def get_drivers_csv_files_in_dir() -> list[str]:
	csv_files: list[str] = []
	files = [f for f in os.listdir() if os.path.isfile(f)]

	for f in files:
		if re.search('kierowcy_.*\\.([Cc][Ss][Vv])', f) is not None:
			if verify_drivers_csv(f):
				csv_files.append(f)
	
	return csv_files

# Wybór pliku z danymi o kierowcach
def choose_drivers_csv_file() -> str:
	csv_files: list[str] = get_drivers_csv_files_in_dir()

	if len(csv_files) > 1:
		while True:
			for x in range(0, len(csv_files)):
				print(f'{x+1}. {csv_files[x]}')

			try:
				num = int(input(f'Wybór (1-{len(csv_files)}): '))
			except ValueError:
				print('\nPodaj liczbę widoczną przy nazwie pliku')
				continue

			if num-1 in range(0, len(csv_files)):
				return csv_files[num-1]
			else:
				print('\nBłędna liczba. Spróbuj ponownie.')
				continue
	elif len(csv_files) == 1:
		options = {
			1: 'Tak',
			2: 'Nie'
		}

		while True:
			print(f'\nJedyny znaleziony plik to {csv_files[0]}. Czy chcesz zapisać jego zawartość do bazy danych?')

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
		text = input('\nPodaj ścieżkę do pliku .csv zawierającego dane o kierowcach:\n')

		if not os.path.isfile(text):
			print('\nŚcieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if re.search('.*\\.([Cc][Ss][Vv])', text) is None:
			print('\nPodany plik nie posiada rozszerzenia csv.')
			continue
		if not verify_drivers_csv(text):
			print('\nPodany plik csv nie posiada wymaganych kolumn.')
			continue

		return text

# Odczytanie danych o kierowcach
def read_drivers_csv(path: str) -> list[Driver]:
	drivers: list[Driver] = list()
	
	with open(path, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=',')
		line_count = 0

		for row in csv_reader:
			try:
				codename = row['codename']
				nationality = row['nationality']
				short_link = row['short_link']
				long_link = row['long_link']
			except:
				line_count += 1
				continue

			drivers.append(Driver(codename, nationality, short_link, long_link))
			line_count += 1
		
		print(f'\nPrzetworzone linie: {line_count}.\nZnalezieni kierowcy: {len(drivers)}.')
	
	return drivers

# Zapisanie danych o kierowcach w bazie
def driver_data_to_db_mode() -> None:
	from db_zapytania import add_driver
	from db_zapytania import get_wiki_id
	from db_zapytania import get_entity_type_id

	chosen_file = choose_drivers_csv_file()

	drivers: list[Driver] = read_drivers_csv(chosen_file)

	if len(drivers) == 0:
		return

	wiki_id: int | None = get_wiki_id('plwiki')

	type_id: int | None = get_entity_type_id('driver')

	if wiki_id is None:
		print('\nW bazie nie znaleziono polskiej Wikipedii. Nie można dodać kierowców do bazy.')
		return
	
	if type_id is None:
		print('\nW bazie nie znaleziono typu kierowców. Nie można dodać kierowców do bazy.')
		return

	for driver in drivers:
		if add_driver(driver, wiki_id, type_id):
			print(f'{driver.codename} - dodano pomyślnie do bazy')

# Wybór trybu pracy skryptu
def choose_mode() -> None:
	options = {
		1: 'Wygenerować plik .csv z danymi o kierowcach',
		2: 'Zapisać dane o kierowcach w bazie',
		3: 'Zakończyć działanie'
	}
	
	while True:
		print('\nWybierz co ma zrobić skrypt.')

		for o in options:
			print(f'{o}. {options[o]}')

		try:
			num = int(input('Wybór: '))
		except ValueError:
			print(f'\nPodaj liczbę z przedziału 1-{len(options)}.')

		if num not in options:
			print('\nWybór spoza powyższej listy, spróbuj ponownie.')
			continue
		elif num == 1:
			driver_data_to_csv_mode()
			break
		elif num == 2:
			driver_data_to_db_mode()
			break
		elif num == 3:
			return

# Główna funkcja skryptu
def main() -> None:
	choose_mode()

if __name__ == "__main__":
	main()