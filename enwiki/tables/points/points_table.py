import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	from pathlib import Path

	project_path = str(Path(__file__).parent.parent.parent.parent)
	if project_path not in sys.path:
		sys.path.append(project_path)

	from common.db_queries.championship_table import get_championships_with_results
	from common.db_queries.classification_tables import get_classifications_by_champ_id
	from common.models.championship import Championship
	from common.models.classifications import Classification
	from common.models.results import EntityResults, RoundResult
	from common.models.styles import LocalisedAbbreviation

# Message when script must stop its execution
script_cannot_continue = "Script cannot continue and it's going to stop its execution."


# Reads championship (series) choice
def read_championship() -> Championship | None:
	from common.db_queries.championship_table import get_championships_with_results
	global script_cannot_continue

	championships: list[Championship] | None = get_championships_with_results()

	if championships is None:
		print(f'\n{script_cannot_continue}')
		return

	if len(championships) == 0:
		print("\nNo championship with saved results was found. Script's going to stop its execution.")
		return
	elif len(championships) == 1:
		options: list[str] = ['Yes', 'No']

		while True:
			print(f'\nThe only found championship was {championships[0].name}. Would you like to choose it?')

			for x in range(0, len(options)):
				print(f'{x+1}. {options[x]}')

			try:
				num: int = int(input('Choice (1-2): ').strip())
			except (TypeError, ValueError):
				print(f'\nPlease enter 1 or 2')
				continue

			if num not in range(1, 3):
				print(f'\nPlease enter 1 or 2')
				continue
			else:
				return championships[0] if num == 1 else None
	else:
		while True:
			print('\nPlease choose a championship from below list:')

			for x in range(0, len(championships)):
				print(f'{x+1}. {championships[x].name}')

			try:
				num: int = int(input(f'Choice (1-{len(championships)}): ').strip())
			except (TypeError, ValueError):
				print(f'\nPlease enter a natural number from 1-{len(championships)} range')
				continue

			if num - 1 not in range(0, len(championships)):
				print(f'\nPlease enter a natural number from 1-{len(championships)} range')
				continue
			else:
				return championships[num - 1]


# Reads classification to be printed
def read_classification(championship_id: int) -> Classification | None:
	global script_cannot_continue

	classifications: list[Classification] | None = get_classifications_by_champ_id(championship_id)

	if classifications is None:
		print(f'\n{script_cannot_continue}')
		return None

	if len(classifications) == 0:
		print('\nNo classification was found in database')
		return None

	while True:
		print('\nPlease choose a classification from below list:')

		for x in range(0, len(classifications)):
			print(f'{x+1}. {classifications[x].season} {classifications[x].name}')

		try:
			num: int = int(input(f'Choice (1-{len(classifications)}): ').strip())
		except (TypeError, ValueError):
			print(f'Please enter a natural number from 1-{len(classifications)} range')
			continue

		if num - 1 not in range(0, len(classifications)):
			print(f'Please enter a natural number from 1-{len(classifications)} range')
			continue
		else:
			return classifications[num - 1]


# Reads number of races that already took place and number of all races in season
def get_round_numbers(classification_id: int) -> tuple[int, int] | None:
	from common.db_queries.classification_tables import get_races_number
	from common.db_queries.points_tables import get_races_held
	global script_cannot_continue

	season_rounds: int | None = get_races_number(classification_id)
	rounds_held: int | None = get_races_held(classification_id)

	if season_rounds is None or rounds_held is None:
		print(script_cannot_continue)
		return None

	if season_rounds == -1:
		while True:
			try:
				season_rounds: int = int(input('\nPlease enter the number of races in season: ').strip())
			except (TypeError, ValueError):
				print('\nPlease enter natural number')
				continue

			if season_rounds <= 0:
				print('\nPlease enter natural number')
				continue
			else:
				break

	if rounds_held == -1:
		while True:
			try:
				rounds_held: int = int(input('\nPlease enter the number of races that took place: ').strip())
			except (TypeError, ValueError):
				print('\nPlease enter natural number')
				continue

			if rounds_held <= 0:
				print('\nPlease enter natural number')
				continue
			elif rounds_held > season_rounds:
				print('\nThe number of races that took place cannot be bigger than the number of races in season')
				continue
			else:
				break

	return rounds_held, season_rounds


# Prints chosen classification
def print_classification(
	entities: list[EntityResults], rounds_held: int,
	season_rounds: int, wiki_id: int, rowspan: int
) -> None:
	from common.db_queries.points_tables import get_nonscoring_abbreviations

	abbr_list: list[LocalisedAbbreviation] = get_nonscoring_abbreviations(wiki_id)

	print('\n|-')

	position: int = 1

	prev_entity: EntityResults | None = None

	for entity in entities:
		if prev_entity is not None and prev_entity.points != entity.points:
			position += 1
		elif prev_entity is not None and prev_entity.results != entity.results:
			position += 1

		name_cell: list[str] = list()

		if rowspan == 1:
			print(f'! {position}')
			name_cell.append('| align="left"')
		else:
			print(f'! rowspan="{rowspan}" | {position}')
			name_cell.append(f'| align="left" rowspan="{rowspan}"')

		if entity.car_no is not None:
			print(f'| align="center" | {entity.car_no}')

		name_cell.append('| {{{{flagicon|{flag}}}}} {link}'.format(
			flag=entity.flag,
			link=entity.link
		))

		print(*name_cell, sep=' ')

		result_cells: list[list[str]] = list()

		cars_range: range = range(rowspan)

		for i in cars_range:
			result_cells.insert(i, list())

		for x in range(1, season_rounds + 1):
			if x <= rounds_held:
				round_results: list[RoundResult] = [
					el for el in entity.results if el.number == x
				]

				if len(round_results) == 0:
					for j in cars_range:
						result_cells[j].append('| –')
				else:
					retrieved_num: int = 0

					for result in round_results:
						style: str = f'background:#{result.style.background}'

						if result.style.text is not None:
							style += f'; color:#{result.style.text}'

						try:
							place: int | None = int(result.place)
						except (ValueError, TypeError):
							place = next(
								(abbr.abbreviation for abbr in abbr_list if abbr.status == result.place),
								None
							)

						if result.style.bold is not None and result.style.bold is not False:
							cell: str = f'| style="{style}" | \'\'\'{place}\'\'\''
						else:
							cell: str = f'| style="{style}" | {place}'

						result_cells[retrieved_num].append(cell)

						retrieved_num += 1

					while retrieved_num != rowspan:
						result_cells[retrieved_num].append('| –')

						retrieved_num += 1
			else:
				for a in cars_range:
					result_cells[a].append('|')

		if rowspan == 1:
			print(*result_cells[0], sep='\n')
			print(f'! {entity.points:g}')
			print('|-')
		else:
			for k in cars_range:
				print(*result_cells[k], sep='\n')
				if k == 0:
					print(f'! rowspan="{rowspan}" | {entity.points:g}')
				print('|-')

		prev_entity = entity


# Script's main function
def main() -> None:
	from common.db_queries.wikipedia_table import get_wiki_id
	from common.db_queries.classification_tables import (
		get_classification_results,
		get_manufacturer_scoring_cars,
		check_classification_entities
	)
	global script_cannot_continue

	# Finding id of English Wikipedia
	enwiki_id: int | None = get_wiki_id('enwiki')

	if enwiki_id is None:
		print(f'\n{script_cannot_continue}')
		return

	if enwiki_id == -1:
		print(f"\nEnglish Wikipedia's id wasn't found in database. {script_cannot_continue}")
		return

	# Choosing championship
	championship: Championship | None = read_championship()

	if championship is None:
		print(f'\n{script_cannot_continue}')
		return

	# Choosing classification
	classification: Classification | None = read_classification(championship.db_id)

	if classification is None:
		print(f'\n{script_cannot_continue}')
		return

	# Sprawdzenie, czy w bazie są dane potrzebne do wygenerowania kodu tabeli
	# Checking whether database has all needed data to generate classification table's code
	check_db_data: bool | None = check_classification_entities(classification, enwiki_id)

	if check_db_data is None:
		return

	if not check_db_data:
		print("\nData about some entities is missing. Cannot generate classification table without it.", end=' ')
		print(f'{script_cannot_continue}')
		return

	# Setting how many results rows will be printed, needed for manufacturers' classifications
	result_rows: int = 1

	if classification.cl_type == 'MANUFACTURERS':
		cars: str = get_manufacturer_scoring_cars(classification.db_id)

		if cars != '' and cars != 'ALL':
			result_rows = int(cars)
		elif cars == 'ALL':
			result_rows = 10

	# Getting drivers/manufacturers/teams results
	results: list[EntityResults] = get_classification_results(classification, enwiki_id)

	# Reading number of races that already took part and number of races in whole season
	race_numbers: tuple[int, int] | None = get_round_numbers(classification.db_id)

	if race_numbers is None:
		print(f'\n{script_cannot_continue}')
		return

	# Printing warning about pole position in case when more than one car score in manufacturer's classification
	if result_rows > 1 and classification.cl_type == 'MANUFACTURERS':
		import time

		msg: list[str] = [
			"\nIn case of manufacturer scoring pole position, manufacturer's highest classified",
			'car in the race will have its result bolded.'
		]
		print(*msg, sep=' ')

		time.sleep(3)

	# Printing points classification
	print_classification(
		entities=results,
		rounds_held=race_numbers[0],
		season_rounds=race_numbers[1],
		wiki_id=enwiki_id,
		rowspan=result_rows
	)


if __name__ == '__main__':
	main()
