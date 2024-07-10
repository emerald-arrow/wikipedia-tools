import sys
import os
import csv
import re
from pathlib import Path

project_path = str(Path(__file__).parent.parent.parent)
if project_path not in sys.path:
	sys.path.append(project_path)

from common.models.driver import Driver  # noqa: E402

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True


# Zapisanie danych o kierowcach do pliku .csv
def write_drivers_csv(drivers: list[Driver]) -> None:
	from datetime import datetime

	timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
	filename = f'kierowcy_{timestamp}.csv'

	headers = ['codename', 'nationality', 'short_link', 'long_link']

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

	print(f'\nKierowcy zapisani w pliku {filename}: {len(drivers)}')


# Odczytanie danych o kierowcach kierowców z pliku zawierającego wyniki
def read_results_csv(file: str, wiki_id: int) -> list[Driver]:
	from common.db_queries.driver_tables import check_driver_exists

	drivers: list[Driver] = list()

	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0

		print('')

		for row in csv_reader:  # type: dict
			line_count += 1

			for x in range(1, 5):  # type: int
				firstname = row.get(f'DRIVER{x}_FIRSTNAME')
				lastname = row.get(f'DRIVER{x}_SECONDNAME')

				if (
						firstname is not None and lastname is not None
						and firstname != '' and lastname != ''
				):
					driver_codename = '%s %s' % (
						firstname.lower(),
						lastname.lower()
					)

					driver_nationality = row.get(f'DRIVER{x}_COUNTRY')

					if driver_nationality is not None:
						if check_driver_exists(
							codename=driver_codename,
							wikipedia_id=wiki_id
						):
							print(f'{driver_codename} jest już w bazie.')
							continue

					driver_short_link = '[[%s %s]]' % (
						firstname.capitalize(),
						lastname.capitalize()
					)

					driver = Driver(
						codename=driver_codename,
						nationality=driver_nationality,
						short_link=driver_short_link
					)

					drivers.append(driver)

		print(f'\nPrzetworzone linie: {line_count}.\nZnalezieni kierowcy: {len(drivers)}')

	return drivers


# Sprawdzenie czy podany plik z wynikami ma wymagane nazwy kolumn
def verify_results_csv(file) -> bool:
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return (
			'DRIVER1_FIRSTNAME' in headers
			and 'DRIVER1_SECONDNAME' in headers
			and 'DRIVER1_COUNTRY' in headers
			and 'DRIVER2_FIRSTNAME' in headers
			and 'DRIVER2_SECONDNAME' in headers
			and 'DRIVER2_COUNTRY' in headers
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


# Tworzenie pliku .csv z danymi kierowców
def driver_data_to_csv_mode() -> None:
	from common.db_queries.wikipedia_table import get_wiki_id

	plwiki_id = get_wiki_id('plwiki')

	if plwiki_id is None:
		print('Nie znaleziono w bazie danych polskiej wersji Wikipedii')

	path: str = read_results_csv_path()

	drivers: list[Driver] = read_results_csv(path, plwiki_id)

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
			'codename' in headers
			and 'nationality' in headers
			and 'short_link' in headers
			and 'long_link' in headers
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
		text = input('\nPodaj ścieżkę do pliku .csv zawierającego dane o kierowcach:\n')

		if not os.path.isfile(text):
			print('\nŚcieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if not text.lower().endswith('.csv'):
			print('\nPodany plik nie posiada rozszerzenia .csv.')
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

		for row in csv_reader:  # type: dict
			line_count += 1

			codename = row.get('codename')
			flag = row.get('nationality')
			short_link = row.get('short_link')
			long_link = row.get('long_link')

			if (
				codename is not None
				and flag is not None
				and short_link is not None
				and long_link is not None
			):
				drivers.append(
					Driver(
						codename,
						flag,
						short_link,
						long_link
					)
				)

		print(f'\nPrzetworzone linie: {line_count}.\nZnalezieni kierowcy: {len(drivers)}.')

	return drivers


# Zapisanie danych o kierowcach w bazie
def driver_data_to_db_mode() -> None:
	from common.db_queries.driver_tables import add_driver
	from common.db_queries.wikipedia_table import get_wiki_id
	from common.db_queries.entity_table import get_entity_type_id

	wiki_id: int | None = get_wiki_id('plwiki')

	if wiki_id is None:
		print('\nW bazie nie znaleziono polskiej Wikipedii. Nie można dodać kierowców do bazy.')
		return

	type_id: int | None = get_entity_type_id('driver')

	if type_id is None:
		print('\nW bazie nie znaleziono typu kierowców. Nie można dodać kierowców do bazy.')
		return

	chosen_file: str = choose_drivers_csv_file()

	drivers: list[Driver] = read_drivers_csv(chosen_file)

	if len(drivers) == 0:
		return

	print()
	for driver in drivers:
		add_driver(driver, wiki_id, type_id)


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
			continue

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


if __name__ == "__main__":
	choose_mode()
