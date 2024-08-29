import sys

# Prevents creating __pycache__ directory
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
	from common.db_queries.tyre_table import get_tyre_manufacturer_name


# Prints race results table from given .csv file
def print_race_table(championship: Championship, filepath: str, wiki_id: int) -> None:
	table_header = [
		'{| class="wikitable" style="font-size:95%;"',
		'|+ Classification',
		'! {{Tooltip|Pos|Position}}',
		'! Class',
		'! {{Tooltip|No|Car number}}',
		'! Team',
		'! Drivers',
		'! Car',
		'! Tyres',
		'! Laps',
		'! Time/Gap'
	]

	print("\nTable's code:\n")
	print(*table_header, sep='\n')

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader[str] = DictReader(csv_file, delimiter=';')
		line_count: int = 0
		class_winners: set[str] = set()
		statuses: set[str] = set()

		for row in csv_reader:  # type: dict[str]
			status: str = row['STATUS']

			# Dividing table into parts with "Not classified" and other statuses
			if status != 'Classified' and status not in statuses:
				statuses.add(status)
				print('|-')
				print(f'! colspan="9" | {status}')

			category: str = row['CLASS']

			# Bolding rows of class winners
			if category not in class_winners:
				print('|- style="font-weight: bold;"')
				class_winners.add(category)
			else:
				print('|-')

			# Printing overall position
			if status == 'Classified':
				print(f'! {row['POSITION']}')
			else:
				print('!')

			# Printing class with optional additional subgroup like Pro/Am etc.
			if 'GROUP' in row and row['GROUP'] != '':
				print(f'| align="center" | {category}<br />{row['GROUP']}')
			else:
				print(f'| align="center" | {category}')

			# Obtaining and printing team's data
			team_data: Team | None = get_team_data(
				codename=f'#{row["NUMBER"]} {row["TEAM"]}',
				championship_id=championship.db_id,
				wiki_id=wiki_id
			)

			if team_data is not None and not team_data.empty_fields():
				print(f'| align="center" | {team_data.car_number}')
				print('| {{{{flagicon|{country}}}}} {team_link}'.format(
					country=team_data.nationality,
					team_link=team_data.long_link if team_data.long_link != '' else team_data.short_link
				))
			else:
				print('| align="center" | %s' % row['NUMBER'])
				print('| {{flagicon|?}} %s' % row['TEAM'])

			# Obtaining and printing team's drivers with their data
			drivers: list[Driver] = list()

			# Finding correct header(s) with drivers' data
			if 'DRIVER_1' in row:
				driver_columns: list[str] = ['DRIVER_{number}']
			elif 'DRIVER1_FIRSTNAME' in row and 'DRIVER1_SECONDNAME' in row:
				driver_columns: list[str] = ['DRIVER{number}_FIRSTNAME', 'DRIVER{number}_SECONDNAME']
			else:
				print("| Drivers' names aren't in columns expected by this script.")

			# Up to 4 driver per car at maximum
			for x in range(1, 5):  # type: int
				driver_codename: str = ''

				for column in driver_columns:  # type: str
					driver_codename += f' {row[column.format(number=x)]}'

				driver_codename = driver_codename.lstrip()

				if len(driver_codename) > 1:
					driver_data: Driver | None = get_driver_data_by_codename(driver_codename.lower(), wiki_id)

					if driver_data is None or driver_data.empty_fields():
						driver_name = driver_codename.split(' ', 1)
						driver_data = Driver(
							nationality='?',
							short_link=f'{driver_name[0]} {driver_name[1].capitalize()}'
						)

					drivers.append(driver_data)

			for x in range(0, len(drivers)):  # type: int
				if x == 0:
					start: str = '| '
					end: str = ''
				elif 0 < x < len(drivers) - 1:
					start: str = '<br/>'
					end: str = ''
				else:
					start: str = '<br/>'
					end: str = '\n'

				print('{start}{{{{flagicon|{flag}}}}} {link}'.format(
					start=start,
					flag=drivers[x].nationality,
					link=drivers[x].long_link if drivers[x].long_link != '' else drivers[x].short_link
				), end=end)

			# Printing car's link
			car: str | None = get_car_link(row['VEHICLE'], wiki_id)

			if car is None or car == '':
				car = f'{row["VEHICLE"]}'

			print(f'| {car}')

			# Printing tyres' manufacturer
			tyre_oem_letter: str = row['TYRES'] if 'TYRES' in row else row['TIRES']

			tyre_oem_name: str | None = get_tyre_manufacturer_name(tyre_oem_letter)

			if tyre_oem_name is not None or tyre_oem_letter != '':
				print('| align="center" | {{%s}}' % tyre_oem_name)
			else:
				print('| align="center" | Tyre=%s' % tyre_oem_letter)

			# Printing number of laps
			print(f'| align="center" | {row["LAPS"]}')

			# Printing race time/gap
			if status == 'Classified':
				# Printing time/lap gap
				if line_count > 0:
					gap: str = row['GAP_FIRST'].replace('\'', ':')

					gap = gap if gap.startswith('+') else f'+{gap}'

					print(f'| {gap}')
				# Printing winner's race time
				elif line_count == 0:
					total_time: str = row['TOTAL_TIME'].replace('\'', ':')
					print(f'| align="center" | {total_time}')
			else:
				# Printing empty cell for not classified etc.
				print('|')

			line_count += 1

		print('|-')
		print('|}')

		print(f'\nProcessed lines: {line_count}')


# Prints qualifying results table from given .csv file
def print_qualifying_table(championship: Championship, filepath: str, wiki_id: int) -> None:
	table_header = [
		'{| class="wikitable sortable" style="font-size: 90%;"',
		'! {{Tooltip|Pos|Position}}',
		'! class="unsortable" | Class',
		'! class="unsortable" | {{Tooltip|No.|Car number}}',
		'! class="unsortable" | Team',
		'! class="unsortable" | Driver',
		'! class="unsortable" | Time',
		'! class="unsortable" | Gap',
		'! {{Tooltip|Grid|Grid position}}'
	]

	print("\nTable's code:\n")
	print(*table_header, sep='\n')

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader[str] = DictReader(csv_file, delimiter=';')
		line_count: int = 0
		class_polesitters: set[str] = set()

		for row in csv_reader:  # type: dict[str]
			category: str = row['CLASS']

			# Bolding rows of class pole-sitters
			if category not in class_polesitters:
				print('|- style="font-weight: bold;"')
				class_polesitters.add(category)
			else:
				print('|-')

			# Printing overall position, organisers use different headers for this value
			position: str = row['POSITION'] if 'POSITION' in row else row['POS']
			print(f'! {position}')

			# Printing class
			print(f'| align="center" | {category}')

			# Obtaining and printing team's data
			team_data: Team | None = get_team_data(
				codename=f'#{row["NUMBER"]} {row["TEAM"]}',
				championship_id=championship.db_id,
				wiki_id=wiki_id
			)

			print(f'| align="center" | {row["NUMBER"]}')

			if team_data is not None and not team_data.empty_fields():
				print('| {{{{flagicon|{country}}}}} {team_link}'.format(
					country=team_data.nationality,
					team_link=team_data.short_link
				))
			else:
				print('| {{{{flagicon|?}}}} [[{team_link}]]'.format(
					team_link=row['TEAM']
				))

			# Obtaining and printing team's drivers with their data
			drivers: list[Driver] = list()

			# Up to 4 driver per car at maximum
			for x in range(1, 5):  # type: int
				if (
					row[f'DRIVER{x}_FIRSTNAME'] is None
					or row[f'DRIVER{x}_FIRSTNAME'] == ''
				):
					continue

				driver_name = '{name} {lastname}'.format(
					name=row[f'DRIVER{x}_FIRSTNAME'].capitalize(),
					lastname=row[f'DRIVER{x}_SECONDNAME'].capitalize()
				)

				driver_data: Driver | None = get_driver_data_by_codename(driver_name.lower(), wiki_id)

				if driver_data is None or driver_data.empty_fields():
					driver_data = Driver(
						short_link=driver_name,
						nationality=row[f'DRIVER{x}_COUNTRY']
					)

				drivers.append(driver_data)

			for x in range(0, len(drivers)):  # type: int
				if x == 0:
					start: str = '| '
					end: str = ''
				elif 0 < x < len(drivers) - 1:
					start: str = '<br />'
					end: str = ''
				else:
					start: str = '<br />'
					end: str = '\n'

				print('{start}{{{{flagicon|{flag}}}}} {link}'.format(
					start=start,
					flag=drivers[x].nationality,
					link=drivers[x].long_link if drivers[x].long_link != '' else drivers[x].short_link
				), end=end)

			# Printing time and gap
			time: str = row['TIME']
			if time != '':
				print(f'| align="center" | {time}')

				gap: str = row['GAP_FIRST'].replace('.', ',').replace('\'', ':')

				gap = gap if gap.startswith('+') else f'+{gap}'

				if line_count > 0:
					print(f'| {gap}')
				else:
					# Pole-sitter has a dash instead of gap
					print('| align="center" | —')
			# Printing dash in case of a time not being set
			else:
				print('| colspan="2" align="center" | —')

			# Printing starting grid place that should be the same as qualifying overall result
			# unless a starting grid document says otherwise
			print(f'! {position}')

			line_count += 1

		print('|-')
		print('! colspan="8" | Sources:')
		print('|-')
		print('|}')

		print(f'\nProcessed lines: {line_count}')


# Prints WEC qualifying final results table from given .csv file
def print_qualifying_post_hp_table(championship: Championship, filepath: str, wiki_id: int) -> None:
	table_header = [
		'{| class="wikitable sortable" style="font-size:90%;"',
		'! {{Tooltip|Pos|Position}}',
		'! Class',
		'! {{Tooltip|No.|Number}}',
		'! Entrant',
		'! Qualifying',
		'! Hyperpole',
		'! {{Tooltip|Grid|Final grid position}}'
	]

	print("\nTable's code:\n")
	print(*table_header, sep='\n')

	# Reading headers that contain qualifying sessions results
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

			# Printing overall position, organisers use different headers for this value
			position: str = row['POSITION'] if 'POSITION' in row else row['POS']
			print(f'! {position}')

			category: str = row['CLASS']

			# Printing class and bolding for class pole-sitters
			if category not in class_polesitters:
				print(f"| align=\"center\" | '''{category}'''")
			else:
				print(f'| align="center" | {category}')

			# Obtaining and printing team's data
			team_data: Team | None = get_team_data(
				codename=f'#{row["NUMBER"]} {row["TEAM"]}',
				championship_id=championship.db_id,
				wiki_id=wiki_id
			)

			if team_data is not None and not team_data.empty_fields():
				row_team: str = '{{{{flagicon|{country}}}}} {team_link}'.format(
					country=team_data.nationality,
					team_link=team_data.short_link
				)
			else:
				row_team: str = '{{{{flagicon|?}}}} [[{team_link}]]'.format(
					team_link=row['TEAM']
				)

			if category in class_polesitters:
				print(f'| align="center" | {row["NUMBER"]}')
				print(f"| {row_team}")
			else:
				print(f"| align=\"center\" | '''{row['NUMBER']}'''")
				print(f"| '''{row_team}'''")

			# Obtaining Q1 and Hyperpole lap times
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

			# Printing times
			if q1_time != '':
				print(f'| align="center" | {q1_time}')

				if hp_time != '':
					hp_time = hp_time.replace('.', ',')
					if category in class_polesitters:
						print(f'| align="center" | {hp_time}')
					else:
						print(f"| align=\"center\" | '''{hp_time}'''")
						class_polesitters.add(category)
				else:
					print('!')
			else:
				# Printing a dash in case of a Q1 time not being set
				# and empty cell for Hyperpole session
				print('| align="center" | —')
				print('!')

			# Printing starting grid place that should be the same as qualifying overall result
			# unless a starting grid document says otherwise
			print(f'! {position}')

			line_count += 1

		print('|-')
		print('! colspan="7" | Sources:')
		print('|-')
		print('|}')

		print(f'\nProcessed lines: {line_count}')


# Prints WEC qualifying results table before Hyperpole from given .csv file
def print_qualifying_pre_hp_table(championship: Championship, filepath: str, wiki_id: int) -> None:
	table_header = [
		'{| class="wikitable sortable" style="font-size:90%;"',
		'! {{Tooltip|Pos|Position}}',
		'! Class',
		'! {{Tooltip|No.|Number}}',
		'! Entrant',
		'! Qualifying',
		'! Hyperpole',
		'! {{Tooltip|Grid|Final grid position}}'
	]

	print("\nTable's code:\n")
	print(*table_header, sep='\n')

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader = DictReader(csv_file, delimiter=';')
		line_count: int = 0
		class_fastest: set[str] = set()

		for row in csv_reader:  # type: dict[str]
			print('|-')

			# Printing overall position, organisers use different headers for this value
			position = row['POSITION'] if 'POSITION' in row else row['POS']
			print(f'! {position}')

			# Printing class
			print(f'| align="center" | {row["CLASS"]}')

			# Obtaining and printing team's data
			team_data: Team | None = get_team_data(
				codename=f'#{row["NUMBER"]} {row["TEAM"]}',
				championship_id=championship.db_id,
				wiki_id=wiki_id
			)

			print(f'| align="center" | {row["NUMBER"]}')

			if team_data is not None and not team_data.empty_fields():
				print('| {{{{flagicon|{country}}}}} {team_link}'.format(
					country=team_data.nationality,
					team_link=team_data.short_link
				))
			else:
				print('| {{{{flagicon|?}}}} [[{team_link}]]'.format(
					team_link=row['TEAM']
				))

			# Printing Q1 time
			time: str = row['TIME']
			if time != '':
				if row['CLASS'] in class_fastest:
					print(f'| align="center" | {time}')
				else:
					class_fastest.add(row['CLASS'])
					print(f"| align=\"center\" | '''{time}'''")
				print('|')
			# Printing a dash in case of a Q1 time not being set
			# and empty cell for Hyperpole session
			else:
				print('| align="center" | —')
				print('|')

			# Printing starting grid place that should be the same as qualifying overall result
			# unless a starting grid document says otherwise
			print(f'! {position}')

			line_count += 1

		print('|-')
		print('! colspan="7" | Sources')
		print('|-')
		print('|}')

		print(f'\nProcessed lines: {line_count}')


# Prints free practice results table from given .csv file
def print_fp_table(championship: Championship, filepath: str, wiki_id: int) -> None:
	table_header = [
		'{| class="wikitable" style="font-size:90%;"',
		'|-',
		'! rowspan="5" | Practice Session',
		'! Class',
		'! {{Tooltip|No.|Number}}',
		'! Entrant',
		'! Time'
	]

	print("\nTable's code:\n")
	print(*table_header, sep='\n')

	with open(filepath, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader: DictReader = DictReader(csv_file, delimiter=';')
		line_count: int = 0
		classes: set[str] = set()

		for row in csv_reader:  # type: dict[str]
			if row['CLASS'] not in classes:
				classes.add(row['CLASS'])

				print('|-')
				# Printing class
				print(f'! {row['CLASS']}')

				# Obtaining and printing team's data
				team_data: Team | None = get_team_data(
					codename=f'#{row["NUMBER"]} {row["TEAM"]}',
					championship_id=championship.db_id,
					wiki_id=wiki_id
				)

				print(f'| align="center" | {row['NUMBER']}')

				if team_data is not None and not team_data.empty_fields():
					print('| {{{{flagicon|{country}}}}} {team_link}'.format(
						country=team_data.nationality,
						team_link=team_data.short_link
					))
				else:
					print('| {{{{flagicon|?}}}} [[{team_link}]]'.format(
						team_link=row['TEAM']
					))

				# Printing time
				time: str = row['TIME']

				if time != '':
					print(f'| {time}')
				else:
					print(f'|')

			line_count += 1

		print('|-')
		print('|}')

		print(f'\nProcessed lines: {line_count}')


# Reads path to results .csv file
def read_csv_path() -> str:
	while True:
		text = input('\nPlease enter path to a results .csv file downloaded from an Alkamelsystems website:\n').strip()

		if not os.path.isfile(text):
			print('\nInvalid path, please try again.')
			continue
		elif not text.lower().endswith('.csv'):
			print("\nFile under given path doesn't have .csv extension")
			continue
		else:
			return text


# Reads what session results are in a file
def read_session(championship: Championship) -> Session:
	if championship.name == 'FIA World Endurance Championship':
		options: list[dict[str, any]] = [
			{'name': 'Test/Free Practice', 'enum': Session.PRACTICE},
			{'name': 'Qualifying (before Hyperpole)', 'enum': Session.QUALIFYING_PRE_HP},
			{'name': 'Qualifying (after Hyperpole)', 'enum': Session.QUALIFYING_POST_HP},
			{'name': 'Race', 'enum': Session.RACE}
		]
	else:
		options: list[dict[str, any]] = [
			{'name': 'Test/Free Practice', 'enum': Session.PRACTICE},
			{'name': 'Qualifying', 'enum': Session.QUALIFYING},
			{'name': 'Race', 'enum': Session.RACE}
		]

	print('\nPlease pick session whose results are in .csv file:')

	while True:
		for x in range(0, len(options)):
			print(f'{x + 1}. {options[x]['name']}')

		try:
			num: int = int(input(f'Choice (1-{len(options)}): ').strip())
		except ValueError:
			print(f'\nPlease enter a natural number from 1-{len(options)} range')
			continue

		if num in range(1, len(options) + 1):
			return options[num - 1]['enum']
		else:
			print(f'\nPlease enter a natural number from 1-{len(options)} range')


# Reads championship (series) whose results are in a .csv file
def read_series(championships: list[Championship]) -> Championship | None:
	print('\nPlease choose a championship from below list:')

	while True:
		if len(championships) == 1:
			print(f'\nThe only series found was {championships[0].name}. Would you like to proceed with it?')
			print('1. Yes\2. No')

			try:
				num: int = int(input('Choice (1-2): ').strip())
			except ValueError:
				print('\nPlease enter 1 or 2.')
				continue

			if num == 1:
				return championships[0]
			elif num == 2:
				return None
			else:
				print('\nPlease enter 1 or 2.')
				continue
		else:
			for x in range(0, len(championships)):
				print(f'{x + 1}. {championships[x].name}')
			try:
				num: int = int(input(f'Choice (1-{len(championships)}): ').strip())
			except ValueError:
				print(f'\nPlease enter a natural number from 1-{len(championships)} range')
				continue

			if num in range(1, len(championships) + 1):
				return championships[num - 1]
			else:
				print(f'\nPlease enter a natural number from 1-{len(championships)} range')


# Script's main function
def main() -> None:
	script_cannot_continue: str = "Script can't continue and is going to end its execution."

	championship_list: list[Championship] | None = get_championships()

	if championship_list is None:
		print(f'\n{script_cannot_continue}')
		return

	if len(championship_list) == 0:
		print(f"\nCouldn't find any championship in database. {script_cannot_continue}")
		return

	enwiki_id: int | None = get_wiki_id('enwiki')

	if enwiki_id is None:
		print(f'\n{script_cannot_continue}')
		return

	if enwiki_id == -1:
		msg: list[str] = [
			"\nCouldn't find English Wikipedia in database.",
			'Data about teams, drivers etc. will be taken only from results file.'
		]
		print(*msg, sep=' ')

	championship_data: Championship | None = read_series(championship_list)

	if championship_data is None:
		print(f'\n{script_cannot_continue}')
		return

	session: Session = read_session(championship_data)

	path: str = read_csv_path()

	match session:
		case Session.PRACTICE:
			print_fp_table(
				championship=championship_data,
				filepath=path,
				wiki_id=enwiki_id
			)
		case Session.QUALIFYING:
			print_qualifying_table(
				championship=championship_data,
				filepath=path,
				wiki_id=enwiki_id
			)
		case Session.QUALIFYING_PRE_HP:
			print_qualifying_pre_hp_table(
				championship=championship_data,
				filepath=path,
				wiki_id=enwiki_id
			)
		case Session.QUALIFYING_POST_HP:
			print_qualifying_post_hp_table(
				championship=championship_data,
				filepath=path,
				wiki_id=enwiki_id
			)
		case Session.RACE:
			print_race_table(
				championship=championship_data,
				filepath=path,
				wiki_id=enwiki_id
			)
		case _:
			print('\nUnsupported session.')


# Runs main function
if __name__ == "__main__":
	main()
