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

	from common.models.teams import Team
	from common.db_queries.wikipedia_table import get_wiki_id

# Message when script must stop its execution
script_cannot_continue = "Script cannot continue and it's going to stop its execution."


# Saves teams data into .csv file
def write_teams_csv(teams: list[Team]) -> None:
	from datetime import datetime

	timestamp: str = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
	filename: str = f'teams_{timestamp}.csv'

	headers: list[str] = ['codename', 'nationality', 'car_number', 'short_link', 'long_link']

	with open(filename, mode='w', encoding='utf-8-sig') as csv_file:
		csv_writer: CsvWriter = CsvWriter(
			csv_file,
			delimiter=',',
			quoting=csv.QUOTE_NONNUMERIC,
			lineterminator='\n'
		)

		csv_writer.writerow(headers)

		for t in teams:
			csv_writer.writerow(list(t))

	print(f'\nNumer of team saved into {filename}: {len(teams)}')


# Reads teams data from results .csv file
def read_results_csv(file: str, wiki_id: int, championship_id: int) -> list[Team]:
	from common.db_queries.country_code_table import get_country_iso_alpha3
	from common.db_queries.team_tables import check_team_exists

	teams: list[Team] = list()

	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader[str] = DictReader(csv_file, delimiter=';')
		line_count: int = 0

		print('')

		for row in csv_reader:  # type: dict[str]
			line_count += 1

			country_id: int = row.get('ECM Country Id')
			team_country: str | None = None

			if country_id is not None:
				team_country = get_country_iso_alpha3(country_id)

			if team_country is None:
				team_country = '?'

			team_codename: str = f'#{row.get("NUMBER")} {row.get("TEAM")}'
			team_car_no: str = row.get('NUMBER')
			team_short_link: str = f'[[{row.get("TEAM")}]]'

			if team_country != '?':
				check_team_db: bool = check_team_exists(
					codename=team_codename,
					championship_id=championship_id,
					flag=team_country,
					car_number=team_car_no,
					wikipedia_id=wiki_id
				)

				if check_team_db:
					print(f'{team_codename} ({team_country}) is already in database')
					continue

			team = Team(
				codename=team_codename,
				nationality=team_country,
				car_number=team_car_no,
				short_link=team_short_link
			)

			teams.append(team)

		print(f'\nProcessed lines: {line_count}\nNumber of new teams found: {len(teams)}')

	return teams


# Checks header of results .csv file
def verify_results_csv(file: str) -> bool:
	with open(file, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		csv_dict = dict(list(csv_reader)[0])
		headers = list(csv_dict.keys())

		return (
			'NUMBER' in headers and
			'TEAM' in headers
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


# Saves teams data into .csv file
def dump_teams_data_to_csv() -> None:
	global script_cannot_continue

	enwiki_id: int | None = get_wiki_id('enwiki')

	if enwiki_id is None:
		print(f'\n{script_cannot_continue}')
		return

	if enwiki_id == -1:
		print(f"\nCouldn't find English Wikipedia in database. {script_cannot_continue}")
		return

	path: str = read_results_csv_path()

	champ_id: int = read_championship()

	teams: list[Team] = read_results_csv(path, enwiki_id, champ_id)

	if len(teams) == 0:
		print("\nNo new teams found. Script's going to stop its execution.")
		return

	write_teams_csv(teams)


# Checks headers in teams data .csv file
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


# Searches this directory for drivers data .csv files
def get_teams_csv_files_in_dir() -> list[str]:
	csv_files: list[str] = []
	files = [f for f in os.listdir() if os.path.isfile(f)]

	for f in files:
		if re.search('teams_.*\\.([Cc][Ss][Vv])', f) is not None:
			if verify_teams_csv(f):
				csv_files.append(f)

	return csv_files


# Chooses teams data .csv file
def choose_teams_csv_file() -> str:
	csv_files: list[str] = get_teams_csv_files_in_dir()

	if len(csv_files) > 1:
		for x in range(0, len(csv_files)):
			print(f'{x + 1}. {csv_files[x]}')

		while True:
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
		text = input('\nPlease enter path to teams data .csv file:\n').strip()

		if not os.path.isfile(text):
			print('\nInvalid path, please try again.')
			continue
		if not text.lower().endswith('.csv'):
			print("\nFile under given path doesn't have .csv extension.")
			continue
		if not verify_teams_csv(text):
			print("\nFile under given path doesn't have required columns.")
			continue

		return text


# Reads teams data .csv file
def read_teams_csv(path: str) -> list[Team]:
	teams: list[Team] = list()

	with open(path, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader[str] = DictReader(csv_file, delimiter=',')
		line_count: int = 0

		for row in csv_reader:  # type: dict[str]
			line_count += 1

			codename: str | None = row.get('codename')
			nationality: str | None = row.get('nationality')
			car_number: str | None = row.get('car_number')
			short_link: str | None = row.get('short_link')
			long_link: str | None = row.get('long_link')

			if (
				codename is not None
				and nationality is not None
				and car_number is not None
				and short_link is not None
				and long_link is not None
			):
				teams.append(
					Team(
						codename=codename,
						nationality=nationality,
						car_number=car_number,
						short_link=short_link,
						long_link=long_link
					)
				)

		print(f'\nProcessed lines: {line_count}\nNumber of teams found: {len(teams)}.')

	return teams


# Reads championship's (series') id where teams race
def read_championship() -> int:
	from common.db_queries.championship_table import get_championships

	championships = get_championships()

	while True:
		print('\nPlease choose championship where teams from the file race in:')

		for x in range(0, len(championships)):
			print(f'{x + 1}. {championships[x].name}')

		try:
			num = int(input(f'Choice (1-{len(championships)}): ').strip())
		except (TypeError, ValueError):
			print(f'\nPlease choose number from 1-{len(championships)} range')
			continue

		if num - 1 not in range(0, len(championships)):
			print(f'\nPlease choose number from 1-{len(championships)} range')
			continue
		else:
			return championships[num - 1].db_id


# Saves teams data into database
def save_teams_data_to_db() -> None:
	from common.db_queries.team_tables import add_teams
	from common.db_queries.entity_table import get_entity_type_id
	global script_cannot_continue

	enwiki_id: int | None = get_wiki_id('enwiki')

	if enwiki_id is None:
		print(f'\n{script_cannot_continue}')
		return

	if enwiki_id == -1:
		print(f"\nCouldn't find English Wikipedia in database. {script_cannot_continue}")
		return

	team_type_id: int | None = get_entity_type_id('team')

	if team_type_id is None:
		print(f'\n{script_cannot_continue}')
		return

	if team_type_id == -1:
		print(f"\nCouldn't find teams type in database. {script_cannot_continue}")
		return

	chosen_file: str = choose_teams_csv_file()

	if chosen_file == '':
		print(f'\n{script_cannot_continue}')
		return

	teams: list[Team] = read_teams_csv(chosen_file)

	if len(teams) == 0:
		print("\nNo teams found. Script's going to stop its execution.")
		return

	championship_id: int = read_championship()

	print()

	add_teams(teams, championship_id, enwiki_id, team_type_id)


# Chooses script's working mode
def choose_mode() -> None:
	options = {
		1: 'Generate teams data .csv file',
		2: 'Save teams data into database',
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
					dump_teams_data_to_csv()
					break
				case 2:
					save_teams_data_to_db()
					break
				case 3:
					return
		else:
			print('\nPlease enter a natural number between 1 and 3.')
			continue


if __name__ == '__main__':
	choose_mode()
