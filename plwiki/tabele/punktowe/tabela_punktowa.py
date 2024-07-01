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
			print(f'{x+1}. {classifications[x].name}')

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
def print_classification(entities: list[EntityResults], rounds_held: int, season_rounds: int, wiki_id: int) -> None:
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

		print(f'! {position}')

		if entity.car_no is not None:
			print(f'| align="left" | {{{{Flaga|{entity.flag}}}}} #{entity.car_no} {entity.link}')
		else:
			print(f'| align="left" | {{{{Flaga|{entity.flag}}}}} {entity.link}')

		for x in range(season_rounds):
			if x + 1 <= rounds_held:
				round_result: RoundResult | None = next((el for el in entity.results if el.number == x + 1), None)

				if round_result is not None:
					style = f'background:#{round_result.style.background}'

					if round_result.style.text is not None:
						style += f'; color:#{round_result.style.text}'

					try:
						place = int(round_result.place)
					except (ValueError, TypeError):
						place = next(
							(abbr.abbreviation for abbr in abbr_list if abbr.status == round_result.place),
							None
						)

					if round_result.style.bold:
						print(f'| style="{style}" | \'\'\'{place}\'\'\'')
					else:
						print(f'| style="{style}" | {place}')
				else:
					print('| –')
			else:
				print('|')

		print(f'! {entity.points}')
		print('|-')

		prev_entity = entity


# Główna funkcja skryptu
def main() -> None:
	from common.db_queries.wikipedia_table import get_wiki_id
	from common.db_queries.classification_tables import get_classification_results

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

	# Pobranie listy kierowców/producentów/zespołów z wynikami
	results: list[EntityResults] = get_classification_results(classification, plwiki_id)

	# Odczytanie liczby rozegranych rund i rund w całym sezonie
	race_numbers: tuple[int, int] = read_round_numbers()

	# Wypisanie klasyfikacji punktowej
	print_classification(
		entities=results,
		rounds_held=race_numbers[0],
		season_rounds=race_numbers[1],
		wiki_id=plwiki_id
	)


if __name__ == '__main__':
	main()
