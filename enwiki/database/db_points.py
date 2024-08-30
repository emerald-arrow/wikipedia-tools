import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	import os
	import csv
	import re
	from pathlib import Path

	project_path = str(Path(__file__).parent.parent.parent)
	if project_path not in sys.path:
		sys.path.append(project_path)

	from common.models.classifications import Classification, EligibleClassifications, ClassificationScoring
	from common.models.manufacturer import Manufacturer, ManufacturerScoringCars
	from common.models.results import ResultRow
	from common.models.championship import Championship
	from common.models.sessions import DbSession
	from common.models.styles import StyledStatus, StyledPosition
	from common.models.driver import Driver
	from common.models.teams import Team, TeamEligibility
	from common.models.points import AwardedPoints

# Message when script must stop its execution
script_cannot_continue = "Script cannot continue and it's going to stop its execution."


# Reads id of championship
def read_championship() -> int | None:
	from common.db_queries.championship_table import get_championships_with_classifications

	championships: list[Championship] | None = get_championships_with_classifications()

	if championships is None:
		print(f'{script_cannot_continue}')

	if len(championships) == 0:
		print(f'No championships found in database. {script_cannot_continue}')
		return None

	print('\nChoose championship which results you want to add to database:')

	while True:
		for x in range(0, len(championships)):
			print(f'{x + 1}. {championships[x].name}')

		try:
			num = int(input(f'Choice (1-{len(championships)}): ').strip())
		except (TypeError, ValueError):
			print(f'\nPlease enter natural number from 1-{len(championships)} range')
			continue

		if num not in range(1, len(championships) + 1):
			print(f'\nPlease enter natural number from 1-{len(championships)} range')
			continue
		else:
			return championships[num - 1].db_id


# Reads season from which the results will be added
def read_season(championship_id: int) -> str | None:
	from common.db_queries.classification_tables import get_active_classifications_seasons

	seasons: list[str] | None = get_active_classifications_seasons(championship_id)

	if seasons is None:
		return None

	if len(seasons) == 0:
		print('\nNo active classifications of this series in database.')
		return None

	if len(seasons) == 1:
		while True:
			print(f'\nThe only available season is {seasons[0]}. Would you like to continue?')
			print('1. Yes\n2. No')

			try:
				ans = int(input('Choice (1-2): ').strip())
			except ValueError:
				print('\nPlease enter 1 or 2.')
				continue

			if ans == 1:
				return seasons[0]
			elif ans == 2:
				return ''
			else:
				print('\nPlease enter 1 or 2.')

	while True:
		print('\nPlease choose a season from which results the results will be added:')
		for x in range(0, len(seasons)):
			print(f'{x + 1}. {seasons[x]}')

		try:
			num = int(input(f'Choice (1-{len(seasons)}): ').strip())
		except (TypeError, ValueError):
			print(f'\nPlease enter a natural number from 1-{len(seasons)} range.')
			continue

		if num not in range(1, len(seasons) + 1):
			print(f'\nPlease enter a natural number from 1-{len(seasons)} range.')
			continue
		else:
			return seasons[num - 1]


# Gets numbers of scoring cars in manufacturers' classifications
def get_oem_scoring_cars(classifications: list[Classification]) -> list[ClassificationScoring] | None:
	from common.db_queries.classification_tables import get_manufacturer_scoring_cars

	classifications_scoring_cars: list[ClassificationScoring] = list()

	for classification in classifications:
		if classification.cl_type == 'MANUFACTURERS':
			cars = get_manufacturer_scoring_cars(classification.db_id)

			if cars is not None and cars != '':
				try:
					classifications_scoring_cars.append(
						ClassificationScoring(
							name=classification.name,
							scoring_entities=int(cars)
						)
					)
				except ValueError:
					# 100 for 'ALL' value in database table
					classifications_scoring_cars.append(
						ClassificationScoring(
							name=classification.name,
							scoring_entities=100
						)
					)
			elif cars == '':
				print(f"{classification.name}: didn't find number of scoring cars in this classification.")
				return None
			else:
				return None

	return classifications_scoring_cars


# Reads points scale
def read_points_scale(scales: list[float]) -> float:
	while True:
		print('\nPlease choose points scale of these results:')
		try:
			for x in range(1, len(scales) + 1):
				print(f'{x}. {scales[x - 1]}')
			choice = int(input(f'Choice (1-{len(scales)}): ').strip())
		except ValueError:
			print(f'\nPlease enter number in 1-{len(scales)} range.')
			continue

		if choice not in range(1, len(scales) + 1):
			print(f'\nPlease enter number in 1-{len(scales)} range.')
			continue

		else:
			return scales[choice - 1]


# Reads session type
def read_session(sessions: list[DbSession]) -> DbSession:
	while True:
		print('\nPlease choose session:')

		for x in range(1, len(sessions) + 1):
			print(f'{x}. {sessions[x - 1].name}')

		try:
			choice = int(input(f'Choice (1-{len(sessions)}): ').strip())
		except ValueError:
			print(f'\nPlease enter number in 1-{len(sessions)} range.')
			continue

		if choice not in range(1, len(sessions) + 1):
			print(f'\nPlease enter number in 1-{len(sessions)} range.')
			continue
		else:
			return sessions[choice - 1]


# Reads path to file with session's results
def read_csv_path() -> str:
	while True:
		text = input('\nPlease enter path to a results .csv file downloaded from an Alkamelsystems website:\n').strip()

		if not os.path.isfile(text):
			print('\nInvalid path, please try again.')
			continue
		if not text.lower().endswith('.csv'):
			print("\nFile under given path doesn't have .csv extension.")
			continue
		else:
			return text


# Searches for right classifications
def find_classifications(
	category: str, team_id: int, driver_ids: list[int],
	manufacturer_id: int | None, classifications: list[Classification],
) -> EligibleClassifications:
	from common.db_queries.classification_tables import check_points_eligibility

	eligible_cl = EligibleClassifications(driver_cl=None, team_cl=None, manufacturer_cl=None)

	for cl in classifications:
		if re.search(f'{category}', cl.name, re.IGNORECASE):
			if re.search('driver', cl.name, re.IGNORECASE):
				checks: list[bool] = list()

				for drv_id in driver_ids:
					checks.append(check_points_eligibility(cl.db_id, drv_id))

				if all(checks) is True:
					eligible_cl.driver_cl = cl

			if (
				manufacturer_id is not None
				and re.search('manufacturer', cl.name, re.IGNORECASE)
				and check_points_eligibility(cl.db_id, team_id)
			):
				eligible_cl.manufacturer_cl = cl
			if (
				re.search('team', cl.name, re.IGNORECASE)
				and check_points_eligibility(cl.db_id, team_id)
			):
				eligible_cl.team_cl = cl

	return eligible_cl


# Reads data from results file
def read_results_csv(
	path: str, classifications: list[Classification], manufacturer_classifications_num: int,
	wiki_id: int
) -> list[ResultRow]:
	from common.db_queries.team_tables import get_id_and_scoring
	from common.db_queries.driver_tables import get_driver_data_by_codename
	from common.db_queries.manufacturer_table import get_manufacturers

	rows: list[ResultRow] = list()
	not_found: dict[str, list[str]] = {'teams': [], 'drivers': []}
	manufacturers: list[Manufacturer] | None = None

	if manufacturer_classifications_num > 0:
		manufacturers = get_manufacturers()

	championship_id: int = classifications[0].championship_id

	with open(path, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=';')
		line_count = 0

		for row in csv_reader:  # type: dict
			line_count += 1
			row_drivers: list[Driver] = list()

			try:
				row_car_no = row['NUMBER']
				row_team = row['TEAM']
				row_category = row['CLASS']
				row_status = row['STATUS']
				row_vehicle = row['VEHICLE']
			except KeyError:
				error_text = [
					'\nAn error occurred while reading data.',
					"Given file doesn't have one of these headers:",
					'NUMBER, TEAM, CLASS, STATUS lub VEHICLE.'
				]
				print(*error_text, sep=' ')
				return list()

			team_codename: str = f'#{row_car_no} {row_team}'

			team_eligibility: TeamEligibility = get_id_and_scoring(
				team_codename,
				championship_id
			)

			if team_eligibility.team.db_id is None:
				not_found['teams'].append(team_codename)
				continue

			if team_eligibility.eligibility is None or not team_eligibility.eligibility:
				continue

			if 'DRIVER_1' in row:
				driver_columns: list[str] = ['DRIVER_{number}']
			elif 'DRIVER1_FIRSTNAME' in row and 'DRIVER1_SECONDNAME' in row:
				driver_columns: list[str] = ['DRIVER{number}_FIRSTNAME', 'DRIVER{number}_SECONDNAME']
			else:
				msg: list[str] = [
					'\nAn error occurred while reading data.',
					"Given file doesn't have columns with drivers' data."
				]
				print(*msg, sep=' ')
				return list()

			for x in range(1, 5):
				driver_codename: str = ''

				for column in driver_columns:
					driver_codename += f' {row[column.format(number=x)]}'

				driver_codename = driver_codename.lstrip()

				if len(driver_codename) > 1:
					driver_data: Driver | None = get_driver_data_by_codename(driver_codename.lower(), wiki_id)
					if driver_data is None or driver_data.empty_fields():
						not_found['drivers'].append(driver_codename)
					else:
						row_drivers.append(driver_data)

			row_manufacturer: Manufacturer | None = None

			if manufacturers is not None and len(manufacturers) > 0:
				for m in manufacturers:
					if re.search(m.codename, row_vehicle, re.IGNORECASE):
						row_manufacturer = m
						break

			eligible_cls = find_classifications(
				category=row_category,
				team_id=team_eligibility.team.db_id,
				driver_ids=[x.db_id for x in row_drivers],
				manufacturer_id=row_manufacturer.db_id if row_manufacturer is not None else None,
				classifications=classifications
			)

			row_data = ResultRow(
				drivers=row_drivers,
				status=row_status,
				team=Team(codename=team_codename, db_id=team_eligibility.team.db_id),
				manufacturer=row_manufacturer if eligible_cls.manufacturer_cl is not None else None,
				eligible_classifications=eligible_cls
			)

			rows.append(row_data)

		print(f'\nProcessed lines: {line_count}')

		entity_not_found: bool = False

		if len(not_found['drivers']) > 0:
			entity_not_found = True
			print("\nCouldn't find these drivers in database:")
			for driver_codename in not_found['drivers']:
				print(driver_codename)

		if len(not_found['teams']) > 0:
			entity_not_found = True
			print("\nCouldn't find these drivers in database::")
			for team in not_found['teams']:
				print(team)

		return list() if entity_not_found else rows


# Finds right colouring for result
def find_result_style(
	status: str, position: int, scoring_styles: list[StyledPosition],
	nonscoring_styles: list[StyledStatus], session: str
) -> tuple[int | None, float] | None:
	match status:
		case 'Classified':
			style_id: int = next(
				(v.style.db_id for v in scoring_styles if v.position == position),
				None
			)
			points: float = next(
				(v.points for v in scoring_styles if v.position == position),
				None
			)

			if style_id is None:
				# Nonscoring positions in qualifying sessions won't get any style
				if session.upper() != 'QUALIFYING':
					style_id = next(
						(v.style.db_id for v in nonscoring_styles if v.status == "Classified, nonscoring")
					)
				points = 0.0

			return style_id, points
		case 'Not classified':
			style_id: int = next(
				(v.style.db_id for v in nonscoring_styles if v.status == "Not classified")
			)

			return style_id, 0.0
		case 'Retired':
			style_id = next(
				(v.style.db_id for v in nonscoring_styles if v.status == "Retired")
			)

			return style_id, 0.0
		case 'Disqualified':
			style_id: int | None = None

			# Entries disqualified from qualifying sessions will be ignored
			if session.upper() != 'QUALIFYING':
				style_id: int = next(
					(v.style.db_id for v in nonscoring_styles if v.status == "Disqualified")
				)

			return style_id, 0.0
		case _:
			return None


# Reads whether full points were awarded for race
def read_full_points() -> AwardedPoints:
	while True:
		print('\nWere full points awarded for this race?')
		print('1. Yes\n2. No')

		try:
			ans = int(input('Choice (1-2): ').strip())
		except ValueError:
			print('\nPlease enter 1 or 2.')
			continue

		if ans == 1:
			return AwardedPoints.FULL
		elif ans == 2:
			return AwardedPoints.HALF
		else:
			print('\nPlease enter 1 or 2.')


# Calculates positions in classifications
def calculate_classifications_positions(
	rows: list[ResultRow], classifications: list[Classification],
	scoring_styles: list[StyledPosition], nonscoring_styles: list[StyledStatus],
	session: str, oem_classifications_scoring: list[ClassificationScoring],
	awarded_points: AwardedPoints
) -> list[ResultRow]:
	from common.db_queries.manufacturer_table import get_manufacturers

	positions: dict[str, int] = dict()
	nonscoring_statuses: list[str] = [x.status for x in nonscoring_styles]

	manufacturers_scoring_cars: list[ManufacturerScoringCars] = list()

	if len(oem_classifications_scoring) > 0:
		manufacturers: list[Manufacturer] | None = get_manufacturers()

		if manufacturers is None:
			return list()

		if len(manufacturers) == 0:
			print("\nManufacturers' list is empty")
			return list()

		for oem in manufacturers:  # type: Manufacturer
			manufacturers_scoring_cars.append(ManufacturerScoringCars(
				manufacturer=oem,
				classifications=oem_classifications_scoring
			))

	for cl in classifications:
		positions.update({f'{cl.name}': 1})

	for row in rows:  # type: ResultRow
		if row.eligible_classifications.team_cl is not None:
			team_position = positions.get(row.eligible_classifications.team_cl.name)

			# Finding styles and points
			found: tuple[int | None, float] | None = find_result_style(
				status=row.status,
				position=team_position,
				scoring_styles=scoring_styles,
				nonscoring_styles=nonscoring_styles,
				session=session
			)

			if found is not None:
				if found[0] is not None:
					row.eligible_classifications.team_style_id = found[0]
					row.eligible_classifications.team_points = found[1] * awarded_points.multiplier

					if row.status not in nonscoring_statuses:
						row.eligible_classifications.team_position = team_position
						positions[f'{row.eligible_classifications.team_cl.name}'] += 1
					else:
						row.eligible_classifications.team_position = row.status
		if row.eligible_classifications.manufacturer_cl is not None:
			oem_position = positions.get(row.eligible_classifications.manufacturer_cl.name)

			oem_scoring: ManufacturerScoringCars = next(
				(x for x in manufacturers_scoring_cars if x.manufacturer.db_id == row.manufacturer.db_id)
			)

			scoring_found: ClassificationScoring = next(
				(x for x in oem_scoring.classifications if x.name == row.eligible_classifications.manufacturer_cl.name)
			)

			# If manufacturer's car(s) can still score
			if scoring_found.scoring_entities > 0:
				manufacturers_scoring_cars.pop(
					manufacturers_scoring_cars.index(oem_scoring)
				)

				oem_scoring.classifications.pop(
					oem_scoring.classifications.index(scoring_found)
				)

				scoring_found.scoring_entities -= 1

				oem_scoring.classifications.append(scoring_found)

				manufacturers_scoring_cars.append(oem_scoring)

				# Finding styles and points
				found: tuple[int | None, float] | None = find_result_style(
					status=row.status,
					position=oem_position,
					scoring_styles=scoring_styles,
					nonscoring_styles=nonscoring_styles,
					session=session
				)

				if found is not None:
					if found[0] is not None:
						row.eligible_classifications.manufacturer_style_id = found[0]
						row.eligible_classifications.manufacturer_points = found[1] * awarded_points.multiplier

						if row.status not in nonscoring_statuses:
							row.eligible_classifications.manufacturer_position = oem_position
						else:
							row.eligible_classifications.manufacturer_position = row.status
			positions[f'{row.eligible_classifications.manufacturer_cl.name}'] += 1
		if row.eligible_classifications.driver_cl is not None:
			driver_position = positions.get(row.eligible_classifications.driver_cl.name)

			# Finding styles and points
			found: tuple[int | None, float] | None = find_result_style(
				status=row.status,
				position=driver_position,
				scoring_styles=scoring_styles,
				nonscoring_styles=nonscoring_styles,
				session=session
			)

			if found is not None:
				if found[0] is not None:
					row.eligible_classifications.driver_style_id = found[0]
					row.eligible_classifications.driver_points = found[1] * awarded_points.multiplier

					if row.status not in nonscoring_statuses:
						row.eligible_classifications.driver_position = driver_position
						positions[f'{row.eligible_classifications.driver_cl.name}'] += 1
					else:
						row.eligible_classifications.driver_position = row.status
	return rows


# Reads round's number
def read_round_number(classifications: list[Classification], session_id: int) -> int | None:
	from common.db_queries.classification_tables import check_round_session

	while True:
		try:
			num: int = int(input('\nPlease enter number of round whose results are in the file: ').strip())
		except ValueError:
			print('\nPlease enter natural number.')
			continue

		if check_round_session(
			classification_id=classifications[0].db_id,
			round_number=num,
			session_id=session_id
		):
			while True:
				print('\nThis round-session pairing already has results in database. Do you want to replace them?')
				print('1. Yes\n2. No')
				try:
					ans = int(input('Choice (1-2): ').strip())
				except ValueError:
					print('\nPlease enter 1 or 2.')
					continue

				if ans == 1:
					from common.db_queries.classification_tables import remove_session_scores
					print('\nDeleting results...')

					results_removed: bool = remove_session_scores(
						classifications=classifications,
						round_number=num,
						session_id=session_id
					)

					if results_removed is None:
						return None

					if results_removed:
						print("\nResults of this round's session were removed from database")
						return num
					else:
						print("\nRemoving results of this round's sessions failed.")
						return None
				elif ans == 2:
					print("\nScript's going to stop its execution.")
					return None
				else:
					print('\nPlease enter 1 or 2.')
		else:
			return num


# Adds results to database
def add_results_to_db(rows: list[ResultRow], round_number: int, session: DbSession) -> None:
	from common.db_queries.classification_tables import add_score

	print('')

	for row in rows:
		# Variable needed to prevent adding qualifying results in team's classifications that
		# don't grant points for qualifying
		drivers_result_added: bool = False

		if (
			row.eligible_classifications.driver_cl is not None
			and row.eligible_classifications.driver_style_id is not None
		):
			print('{season} {classification_name}'.format(
				season=row.eligible_classifications.driver_cl.season,
				classification_name=row.eligible_classifications.driver_cl.name
			))

			for driver in row.drivers:
				print(f'{driver.codename}:', end=' ')
				add_score(
					classification_id=row.eligible_classifications.driver_cl.db_id,
					round_number=round_number,
					session_id=session.db_id,
					entity_id=driver.db_id,
					place=row.eligible_classifications.driver_position,
					points=row.eligible_classifications.driver_points,
					style_id=row.eligible_classifications.driver_style_id
				)
				drivers_result_added = True
		if (
			row.eligible_classifications.manufacturer_cl is not None
			and row.eligible_classifications.manufacturer_style_id is not None
		):
			print('{season} {classification_name}'.format(
				season=row.eligible_classifications.manufacturer_cl.season,
				classification_name=row.eligible_classifications.manufacturer_cl.name
			))

			if row.manufacturer is not None:
				print(f'{row.manufacturer.codename}:', end=' ')
				add_score(
					classification_id=row.eligible_classifications.manufacturer_cl.db_id,
					round_number=round_number,
					session_id=session.db_id,
					entity_id=row.manufacturer.db_id,
					place=row.eligible_classifications.manufacturer_position,
					points=row.eligible_classifications.manufacturer_points,
					style_id=row.eligible_classifications.manufacturer_style_id
				)
		if (
			row.eligible_classifications.team_cl is not None
			and row.eligible_classifications.team_style_id is not None
			and drivers_result_added is True
		):
			print('{season} {classification_name}'.format(
				season=row.eligible_classifications.team_cl.season,
				classification_name=row.eligible_classifications.team_cl.name
			))

			print(f'{row.team.codename}:', end=' ')
			add_score(
				classification_id=row.eligible_classifications.team_cl.db_id,
				round_number=round_number,
				session_id=session.db_id,
				entity_id=row.team.db_id,
				place=row.eligible_classifications.team_position,
				points=row.eligible_classifications.team_points,
				style_id=row.eligible_classifications.team_style_id
			)
		print('-' * 50)


# Script's main function
def main() -> None:
	from common.db_queries.classification_tables import get_champ_classifications_by_season
	from common.db_queries.wikipedia_table import get_wiki_id
	from common.db_queries.points_tables import (
		get_points_scales,
		get_scoring_sessions,
		get_styled_nonscoring_statuses,
		get_styled_points_system
	)
	from common.db_queries.manufacturer_table import refresh_manufacturers_timestamps

	global script_cannot_continue

	# Getting English Wikipedia's id from database
	enwiki_id: int | None = get_wiki_id('enwiki')

	if enwiki_id is None:
		print(f'\n{script_cannot_continue}')
		return

	if enwiki_id == -1:
		print("\nCouldn't find English Wikipedia in database." + script_cannot_continue)
		return

	# Reading id of championship (series)
	championship_id: int | None = read_championship()

	if championship_id is None:
		print(script_cannot_continue)
		return

	# Reading season from which results will be added
	season: str | None = read_season(championship_id)

	if season is None or season == '':
		return

	# Getting classifications of chosen championship (series)
	classifications: list[Classification] = get_champ_classifications_by_season(
		championship_id,
		season
	)

	if len(classifications) == 0:
		print("\nNo classification in database for chosen championship." + script_cannot_continue)
		return

	# Getting data about scoring in manufacturer's classifications (if there are any)
	oem_scoring_cars: list[ClassificationScoring] | None = get_oem_scoring_cars(classifications)

	if oem_scoring_cars is None:
		print(script_cannot_continue)
		return

	# Getting points scales from database
	points_scales: list[float] | None = get_points_scales(championship_id)

	if points_scales is None:
		print(script_cannot_continue)
		return

	if len(points_scales) == 0:
		print("\nThis championship doesn't hav any points scales in database")
		return
	elif len(points_scales) == 1:
		scale: float = points_scales[0]
	else:
		scale: float = read_points_scale(points_scales)

	# Getting points awarding sessions from database
	sessions: list[DbSession] | None = get_scoring_sessions(championship_id, scale)

	if sessions is None:
		print(script_cannot_continue)
		return

	if len(sessions) == 0:
		print(f'\nNo session awards points. {script_cannot_continue}')
		return
	elif len(sessions) == 1:
		session: DbSession = sessions[0]
	else:
		session: DbSession = read_session(sessions)

	# Reading round number
	round_num: int | None = read_round_number(classifications, session.db_id)

	if round_num is None:
		print(script_cannot_continue)
		return

	# Gets nonscoring statuses (not classified etc.) with their styles in Wikipedia tables
	nonscoring_statuses: list[StyledStatus] = get_styled_nonscoring_statuses()

	if len(nonscoring_statuses) == 0 and session.name == 'RACE':
		print('\nNo styling of race results found.' + script_cannot_continue)
		return

	# Checking whether race's results are being added, if so reads awarded points
	if session.name == 'RACE':
		awarded_points: AwardedPoints = read_full_points()
	else:
		awarded_points: AwardedPoints = AwardedPoints.FULL

	# Getting points system with styles in Wikipedia tables
	styled_positions: list[StyledPosition] = get_styled_points_system(
		championship_id=championship_id,
		scale=scale,
		session_id=session.db_id
	)

	if len(styled_positions) == 0:
		print('\nNo results styles found.' + script_cannot_continue)
		return

	# Reading results .csv file path
	path: str = read_csv_path()

	# Reading data from given .csv file
	rows: list[ResultRow] = read_results_csv(
		path=path,
		classifications=classifications,
		manufacturer_classifications_num=len(oem_scoring_cars),
		wiki_id=enwiki_id
	)

	if len(rows) == 0:
		print(script_cannot_continue)
		return

	# Calculating positions in classifications and finding correct result styles
	rows: list[ResultRow] = calculate_classifications_positions(
		rows=rows,
		classifications=classifications,
		scoring_styles=styled_positions,
		nonscoring_styles=nonscoring_statuses,
		session=session.name,
		oem_classifications_scoring=oem_scoring_cars,
		awarded_points=awarded_points
	)

	if len(rows) == 0:
		print(script_cannot_continue)
		return

	# Adding results to database
	add_results_to_db(rows, round_num, session)

	# Refreshing timestamps of manufacturers that took part in the race meeting
	manufacturers_ids: list[int] = list()

	for row in rows:  # type: ResultRow
		if row.manufacturer is not None:
			manufacturers_ids.append(row.manufacturer.db_id)

	refresh_manufacturers_timestamps(manufacturers_ids)


if __name__ == '__main__':
	main()
