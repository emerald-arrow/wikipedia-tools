import sys
from pathlib import Path

project_path = str(Path(__file__).parent.parent.parent.parent)
if project_path not in sys.path:
	sys.path.append(project_path)

if True:  # noqa: E402
	from common.db_queries.championship_table import get_championships_with_results
	from common.db_queries.classification_tables import get_classifications_by_champ_id
	from common.models.championships import Championship
	from common.models.classifications import Classification
	from common.models.results import EntityResults, RoundResult
	from common.models.styles import LocalisedAbbreviation

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True


# Wybór serii wyścigowej
def read_championship() -> Championship | None:
	from common.db_queries.championship_table import get_championships_with_results

	championships: list[Championship] | None = get_championships_with_results()

	if championships is None:
		return

	if len(championships) == 0:
		print('\nNie znaleziono w bazie danych żadnej serii wyścigowej z zapisanymi wynikami.')
		return
	elif len(championships) == 1:
		options: list[str] = ['Tak', 'Nie']

		while True:
			print(f'\nJedyna znaleziona seria to {championships[0].name}. Kontynuować?')

			for x in range(0, len(options)):
				print(f'{x+1}. {options[x]}')

			try:
				num = int(input('Wybór (1-2): '))
			except (TypeError, ValueError):
				print(f'\nPodaj liczbę 1 lub 2')
				continue

			if num not in range(1, 3):
				print('\nPodaj liczbę 1 lub 2')
				continue
			else:
				return championships[0] if num == 1 else None
	else:
		while True:
			print('Wybierz serię z poniższej listy:')

			for x in range(0, len(championships)):
				print(f'{x+1}. {championships[x].name}')

			try:
				num = int(input(f'Wybór (1-{len(championships)}): '))
			except (TypeError, ValueError):
				print(f'Podaj liczbę naturalną z przedziału 1-{len(championships)}')
				continue

			if num - 1 not in range(0, len(championships)):
				print(f'Podaj liczbę naturalną z zakresu 1-{len(championships)}')
				continue
			else:
				return championships[num - 1]


# Wybór klasyfikacji
def read_classification(championship_id: int) -> Classification | None:
	classifications: list[Classification] | None = get_classifications_by_champ_id(championship_id)

	if classifications is None:
		return

	while True:
		print('\nWybierz klasyfikację z poniższej listy:')

		for x in range(0, len(classifications)):
			print(f'{x+1}. {classifications[x].season} {classifications[x].name}')

		try:
			num = int(input(f'Wybór (1-{len(classifications)}): '))
		except (TypeError, ValueError):
			print(f'Podaj liczbę naturalną z przedziału 1-{len(classifications)}')
			continue

		if num - 1 not in range(0, len(classifications)):
			print(f'Podaj liczbę naturalną z zakresu 1-{len(classifications)}')
			continue
		else:
			return classifications[num - 1]


# Odczytanie liczby rund w sezonie oraz rozegranych rund
def read_round_numbers() -> tuple[int, int]:
	season_rounds: int | None = None
	rounds_held: int | None = None

	while True:
		try:
			season_rounds = int(input('\nLiczba wyścigów w sezonie: '))
		except (TypeError, ValueError):
			print('\nPodaj liczbę naturalną.')
			continue
		else:
			if season_rounds <= 0:
				print('\nPodaj liczbę naturalną.')
				continue
			else:
				break

	while True:
		try:
			rounds_held: int = int(input('\nLiczba rozegranych wyścigów: '))
		except (TypeError, ValueError):
			print('\nPodaj liczbę naturalną.')
			continue

		if rounds_held <= 0:
			print('\nPodaj liczbę naturalną.')
			continue
		elif rounds_held > season_rounds:
			print('\nLiczba rozegranych wyścigów nie może być większa od liczby wyścigów w sezonie.')
			continue
		else:
			break

	return rounds_held, season_rounds


# Wypisanie klasyfikacji
def print_classification(
	entities: list[EntityResults], rounds_held: int, season_rounds: int, wiki_id: int,
	rowspan: int
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
			name_cell.append(f' | {{{{Flaga|{entity.flag}}}}} #{entity.car_no} {entity.link}')
		else:
			name_cell.append(f' | {{{{Flaga|{entity.flag}}}}} {entity.link}')

		print(*name_cell, sep='')

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
			print(f'! {entity.points}')
			print('|-')
		else:
			for k in cars_range:
				print(*result_cells[k], sep='\n')
				if k == 0:
					print(f'! rowspan="{rowspan}" | {entity.points}')
				print('|-')

		prev_entity = entity


# Główna funkcja skryptu
def main() -> None:
	from common.db_queries.wikipedia_table import get_wiki_id
	from common.db_queries.classification_tables import (
		get_classification_results,
		get_manufacturer_scoring_cars
	)

	# Znalezienie id polskiej wersji Wikipedii
	plwiki_id: int | None = get_wiki_id('plwiki')

	if plwiki_id is None:
		print('Nie znaleziono w bazie danych id polskiej wersji Wikipedii.')
		return

	# Wybór serii wyścigowej
	championship: Championship | None = read_championship()

	if championship is None:
		return

	# Wybór klasyfikacji
	classification: Classification | None = read_classification(championship.db_id)

	if classification is None:
		return

	rowspan: int = 1

	if classification.cl_type == 'MANUFACTURERS':
		cars: str = get_manufacturer_scoring_cars(classification.db_id)

		if cars != '' and cars != 'ALL':
			rowspan = int(cars)
		elif cars == 'ALL':
			rowspan = 10

	# Pobranie listy kierowców/producentów/zespołów z wynikami
	results: list[EntityResults] = get_classification_results(classification, plwiki_id)

	# Odczytanie liczby rozegranych rund i rund w całym sezonie
	# TODO:
	# Do zastąpienia odczytywaniem liczby rozegranych rund i ogółem w sezonie z bazy danych
	race_numbers: tuple[int, int] = read_round_numbers()

	if rowspan > 1 and classification.cl_type == 'MANUFACTURERS':
		import time

		msg: list[str] = [
			'\nW przypadku zdobycia pole position przez producenta',
			'pogrubiony zostanie wynik auta najwyżej sklasyfikowanego na mecie wyścigu.'
		]
		print(*msg, sep=' ')

		time.sleep(3)

	# Wypisanie klasyfikacji punktowej
	print_classification(
		entities=results,
		rounds_held=race_numbers[0],
		season_rounds=race_numbers[1],
		wiki_id=plwiki_id,
		rowspan=rowspan
	)


if __name__ == '__main__':
	main()
