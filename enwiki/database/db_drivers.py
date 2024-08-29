import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	import os
	import csv
	from csv import DictReader, writer as CsvWriter
	import re
	from pathlib import Path

	project_path = str(Path(__file__).parent.parent.parent)
	if project_path not in sys.path:
		sys.path.append(project_path)

	from common.models.driver import Driver
	from common.db_queries.wikipedia_table import get_wiki_id

# Message when script must stop its execution
script_cannot_continue = "Script cannot continue and it's going to stop its execution."


# Saves drivers data into .csv file
def write_drivers_csv(drivers: list[Driver]) -> None:
	from datetime import datetime

	timestamp: str = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
	filename: str = f'drivers_{timestamp}.csv'

	headers: list[str] = ['codename', 'nationality', 'short_link', 'long_link']

	with open(filename, mode='w', encoding='utf-8-sig') as csv_file:
		csv_writer: CsvWriter = CsvWriter(
			csv_file,
			delimiter=',',
			quoting=csv.QUOTE_NONNUMERIC,
			lineterminator='\n'
		)

		csv_writer.writerow(headers)

		for d in drivers:  # type: Driver
			csv_writer.writerow(list(d))

	print(f'\nNumer of drivers saved into {filename}: {len(drivers)}')


# Reads drivers data from results .csv file
def read_results_csv(file: str, wiki_id: int) -> list[Driver]:
	from common.db_queries.driver_tables import check_driver_exists

	drivers: list[Driver] = list()

	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader[str] = DictReader(csv_file, delimiter=';')
		line_count: int = 0

		print('')

		for row in csv_reader:  # type: dict[str]
			line_count += 1

			for x in range(1, 5):  # type: int
				firstname: str | None = row.get(f'DRIVER{x}_FIRSTNAME')
				lastname: str | None = row.get(f'DRIVER{x}_SECONDNAME')

				if (
					firstname is not None
					and firstname != ''
					and lastname is not None
					and lastname != ''
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
							print(f'{driver_codename} is already in database')
							continue

					driver_short_link = '%s %s' % (
						firstname.capitalize(),
						lastname.capitalize()
					)

					driver = Driver(
						codename=driver_codename,
						nationality=driver_nationality,
						short_link=driver_short_link
					)

					drivers.append(driver)

		print(f'\nProcessed lines: {line_count}\nNumber of new drivers found: {len(drivers)}')

	return drivers


# Checks header of results .csv file
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


# Reads path to results .csv file
def read_results_csv_path() -> str:
	while True:
		text = input('\nPlease enter path to a results .csv file downloaded from an Alkamelsystems website:\n').strip()

		if not os.path.isfile(text):
			print('\nInvalid path, please try again.')
			continue
		elif not text.lower().endswith('.csv'):
			print("\nFile under given path doesn't have .csv extension.")
			continue
		elif not verify_results_csv(text):
			print("\nFile under given path doesn't have required columns in its header.")
			continue
		else:
			return text


# Saves drivers data into .csv file
def dump_drivers_data_to_csv() -> None:
	global script_cannot_continue

	enwiki_id: int | None = get_wiki_id('enwiki')

	if enwiki_id is None:
		print(f'\n{script_cannot_continue}')
		return

	if enwiki_id == -1:
		print(f"\nCouldn't find English Wikipedia in database. {script_cannot_continue}")
		return

	path: str = read_results_csv_path()

	drivers: list[Driver] = read_results_csv(path, enwiki_id)

	if len(drivers) == 0:
		print("\nNo new drivers found. Script's going to stop its execution.")
		return

	write_drivers_csv(drivers)


# Checks headers in drivers data .csv file
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


# Searches this directory for drivers data .csv files
def get_drivers_csv_files_in_dir() -> list[str]:
	csv_files: list[str] = []
	files = [f for f in os.listdir() if os.path.isfile(f)]

	for f in files:
		if re.search('drivers_.*\\.([Cc][Ss][Vv])', f) is not None:
			if verify_drivers_csv(f):
				csv_files.append(f)

	return csv_files


# Chooses drivers data .csv file
def choose_drivers_csv_file() -> str:
	csv_files: list[str] = get_drivers_csv_files_in_dir()

	if len(csv_files) > 1:
		while True:
			for x in range(0, len(csv_files)):
				print(f'{x + 1}. {csv_files[x]}')

			try:
				num = int(input(f'Choice (1-{len(csv_files)}): ').strip())
			except ValueError:
				print('\nPlease enter a number shown before file name')
				continue

			if num - 1 in range(0, len(csv_files)):
				return csv_files[num - 1]
			else:
				print('\nWrong number, please try again')
				continue
	elif len(csv_files) == 1:
		options = {
			1: 'Yes',
			2: 'No'
		}

		while True:
			msg: list[str] = [
				f'\nThe only found file was {csv_files[0]}.',
				'Do you want to save its contents into database?'
			]
			print(*msg, sep=' ')

			for x in options:
				print(f'{x}. {options[x]}')

			try:
				num = int(input('Choice (1-2): ').strip())
			except ValueError:
				print('\nPlease enter number 1 or 2.')
				continue

			if num == 1:
				return csv_files[0]
			elif num == 2:
				return ''
			else:
				print('\nPlease enter number 1 or 2.')
				continue

	while True:
		text = input('\nPlease enter path to drivers data .csv file:\n').strip()

		if not os.path.isfile(text):
			print('\nInvalid path, please try again.')
			continue
		if not text.lower().endswith('.csv'):
			print("\nFile under given path doesn't have .csv extension.")
			continue
		if not verify_drivers_csv(text):
			print("\nFile under given path doesn't have required columns.")
			continue

		return text


# Reads drivers data .csv file
def read_drivers_csv(path: str) -> list[Driver]:
	drivers: list[Driver] = list()

	with open(path, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader[str] = DictReader(csv_file, delimiter=',')
		line_count: int = 0

		for row in csv_reader:  # type: dict[str]
			line_count += 1

			codename: str | None = row.get('codename')
			flag: str | None = row.get('nationality')
			short_link: str | None = row.get('short_link')
			long_link: str | None = row.get('long_link')

			if (
				codename is not None
				and flag is not None
				and short_link is not None
				and long_link is not None
			):
				drivers.append(
					Driver(
						codename=codename,
						nationality=flag,
						short_link=short_link,
						long_link=long_link
					)
				)

		print(f'\nProcessed lines: {line_count}\nNumber of drivers found: {len(drivers)}')

	return drivers


# Saves drivers data into database
def save_drivers_data_to_db() -> None:
	from common.db_queries.driver_tables import add_drivers
	from common.db_queries.entity_table import get_entity_type_id
	global script_cannot_continue

	enwiki_id: int | None = get_wiki_id('enwiki')

	if enwiki_id is None:
		print(f'\n{script_cannot_continue}')
		return

	if enwiki_id == -1:
		print(f"\nCouldn't find English Wikipedia in database. {script_cannot_continue}")
		return

	driver_type_id: int | None = get_entity_type_id('driver')

	if driver_type_id is None:
		print(f'\n{script_cannot_continue}')
		return

	if driver_type_id == -1:
		print(f"\nCouldn't find drivers type in database. {script_cannot_continue}")
		return

	chosen_file: str = choose_drivers_csv_file()

	if chosen_file == '':
		print(f'\n{script_cannot_continue}')
		return

	drivers: list[Driver] = read_drivers_csv(chosen_file)

	if len(drivers) == 0:
		print("\nNo drivers found. Script's going to stop its execution.")
		return

	print()

	add_drivers(drivers, enwiki_id, driver_type_id)


# Chooses script's working mode
def choose_mode() -> None:
	options = {
		1: 'Generate drivers data .csv file',
		2: 'Save drivers data into database',
		3: 'Exit'
	}

	while True:
		print('\nWhat would you like to do?')

		for o in options:
			print(f'{o}. {options[o]}')

		try:
			num = int(input(f'Choice (1-{len(options)}): ').strip())
		except ValueError:
			print('\nPlease enter a natural number between 1 and 3.')
			continue

		if num in options:
			match num:
				case 1:
					dump_drivers_data_to_csv()
					break
				case 2:
					save_drivers_data_to_db()
					break
				case 3:
					return
		else:
			print('\nPlease enter a natural number between 1 and 3.')
			continue


if __name__ == "__main__":
	choose_mode()
