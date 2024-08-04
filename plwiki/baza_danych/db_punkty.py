import sys
import os
import csv
import re
from pathlib import Path

project_path = str(Path(__file__).parent.parent.parent)
if project_path not in sys.path:
	sys.path.append(project_path)

if True:  # noqa: E402
	from common.models.classifications import Classification, EligibleClassifications, ClassificationScoring
	from common.models.manufacturer import Manufacturer, ManufacturerScoringCars
	from common.models.results import ResultRow
	from common.models.aliases import EntityDict
	from common.models.championships import ChampionshipExt
	from common.models.sessions import DbSession
	from common.models.styles import StyledStatus, StyledPosition
	from common.models.driver import Driver
	from common.models.teams import TeamEligibility

# Powstrzymanie Pythona od tworzenia dodatkowych plików i katalogów przy wykonywaniu skryptu
sys.dont_write_bytecode = True


# Odczytanie id serii, której klasyfikacje mają zostać wygenerowane
def read_championship() -> int | None:
	from common.db_queries.championship_table import get_championships_with_classifications

	championships: list[ChampionshipExt] | None = get_championships_with_classifications()

	if championships is None:
		return None

	if len(championships) == 0:
		print('Brak mistrzostw w bazie.')
		return None

	print('\nWybierz serię, której wyniki chcesz dodać do bazy:')

	while True:
		for x in range(0, len(championships)):
			print(f'{x + 1}. {championships[x].name}')

		try:
			num = int(input(f'Wybór (1-{len(championships)}): '))
		except (TypeError, ValueError):
			print(f'Podaj liczbę naturalną z przedziału 1-{len(championships)}')
			continue

		if num - 1 not in range(0, len(championships)):
			print(f'Podaj liczbę naturalną z zakresu 1-{len(championships)}')
			continue
		else:
			return championships[num - 1].db_id


# Pobranie liczby punktujących aut w klasyfikacjach producentów
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
					# Liczba 100 dla wartości 'ALL' z tabeli zawierającej dane o punktujących autach
					classifications_scoring_cars.append(
						ClassificationScoring(
							name=classification.name,
							scoring_entities=100
						)
					)
			elif cars == '':
				print(f'{classification.name}: nie znaleziono liczby punktujących aut w tej klasyfikacji')
				return None
			else:
				return None

	return classifications_scoring_cars


# Odczytanie skali punktowej
def read_points_scale(scales: list[float]) -> float:
	while True:
		print('\nWybierz skalę punktową tego wyniku:')
		try:
			for x in range(1, len(scales) + 1):
				print(f'{x}. {scales[x - 1]}')
			choice = int(input('Wybór: '))
		except ValueError:
			print(f'\nPodaj liczbę z przedziału 1-{len(scales)}')
			continue

		if choice in range(1, len(scales) + 1):
			return scales[choice - 1]
		else:
			print(f'\nPodaj liczbę z przedziału 1-{len(scales)}')
			continue


# Odczytanie sesji
def read_session(sessions: list[DbSession]) -> DbSession:
	while True:
		print('\nWybierz sesję:')
		try:
			for x in range(1, len(sessions) + 1):
				print(f'{x}. {sessions[x - 1].name}')
			choice = int(input('Wybór: '))
		except ValueError:
			print(f'\nPodaj liczbę z przedziału 1-{len(sessions)}')
			continue

		if choice in range(1, len(sessions) + 1):
			return sessions[choice - 1]
		else:
			print(f'\nPodaj liczbę z przedziału 1-{len(sessions)}')
			continue


# Odczytanie ścieżki do pliku z klasyfikacją wyścigu
def read_csv_path() -> str:
	while True:
		text = input('\nPodaj ścieżkę do pliku .CSV pobranego ze strony Alkamelsystems:\n')

		if not os.path.isfile(text):
			print('Ścieżka nieprawidłowa, spróbuj ponownie.')
			continue
		if not text.lower().endswith('.csv'):
			print('Ścieżka nie prowadzi do pliku z rozszerzeniem .CSV.')
			continue
		else:
			return text


# Wyszukiwanie odpowiednich klasyfikacji
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


# Odczytanie danych z pliku csv zawierającego wyniki
def read_results_csv(
	path: str, classifications: list[Classification], manufacturer_classifications_num: int,
	wiki_id: int
) -> list[ResultRow]:
	from common.db_queries.team_tables import get_id_and_scoring
	from common.db_queries.driver_tables import get_driver_by_codename
	from common.db_queries.manufacturer_table import get_manufacturers

	rows: list[ResultRow] = list()
	not_found: EntityDict = {'teams': [], 'drivers': []}
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
					'\nBłąd podczas czytania danych.',
					'W podanym pliku brakuje któregoś z nagłówków:',
					'NUMBER, TEAM, CLASS, STATUS lub VEHICLE.'
				]
				print(*error_text, sep=' ')
				return []

			codename = f'#{row_car_no} {row_team}'

			team_eligibility: TeamEligibility = get_id_and_scoring(
				codename,
				championship_id
			)

			if team_eligibility.team.db_id is None:
				not_found['teams'].append(codename)
				continue

			if team_eligibility.eligibility is None or not team_eligibility.eligibility:
				continue

			if 'DRIVER_1' in row:
				driver_columns: str = 'DRIVER_{0}'
			elif 'DRIVER1_FIRSTNAME' in row and 'DRIVER2_SECONDNAME' in row:
				driver_columns: list[str] = ['DRIVER{0}_FIRSTNAME', 'DRIVER{0}_SECONDNAME']
			else:
				msg: list[str] = [
					'\nBłąd podczas czytania danych.',
					'W podanym pliku brakuje kolumny z danymi kierowców.'
				]
				print(*msg, sep=' ')
				return list()

			for x in range(1, 5):
				if type(driver_columns) is list:
					driver = row[driver_columns[0].format(x)]
					driver += f' {row[driver_columns[1].format(x)]}'
				else:
					driver = row[driver_columns.format(x)]

				if len(driver) > 1:
					driver_data: Driver | None = get_driver_by_codename(driver.lower(), wiki_id)
					if driver_data is None:
						not_found['drivers'].append(driver)
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
				db_team_id=team_eligibility.team.db_id,
				manufacturer=row_manufacturer if eligible_cls.manufacturer_cl is not None else None,
				eligible_classifications=eligible_cls
			)

			rows.append(row_data)

		print(f'\nPrzetworzone linie: {line_count}')

		entity_not_found: bool = False

		if len(not_found['drivers']) > 0:
			entity_not_found = True
			print('\nW bazie danych nie znaleziono kierowców:')
			for driver in not_found['drivers']:
				print(driver)

		if len(not_found['teams']) > 0:
			entity_not_found = True
			print('\nW bazie danych nie znaleziono zespołów:')
			for team in not_found['teams']:
				print(team)

		return list() if entity_not_found else rows


# Wyszukanie stylu kolorowania dla wyniku
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
				# Niepunktowane pozycje w kwalifikacjach pozostaną bez stylu
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

			# Zdyskwalifikowani z kwalifikacji nie zostaną wzięci pod uwagę
			if session.upper() != 'QUALIFYING':
				style_id: int = next(
					(v.style.db_id for v in nonscoring_styles if v.status == "Disqualified")
				)

			return style_id, 0.0
		case _:
			return None


# Wyliczenie pozycji w klasyfikacjach i dobranie stylów kolorowania
def calculate_classifications_positions(
	rows: list[ResultRow], classifications: list[Classification],
	scoring_styles: list[StyledPosition], nonscoring_styles: list[StyledStatus],
	session: str, oem_classifications_scoring: list[ClassificationScoring]
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
			print('Lista producentów jest pusta.')
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

			# Dobieranie stylów i punktów
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
					row.eligible_classifications.team_points = found[1]

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

			# Jeśli auto(-a) producenta może(-gą) jeszcze punktować
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

				# Dobieranie stylów i punktów
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
						row.eligible_classifications.manufacturer_points = found[1]

						if row.status not in nonscoring_statuses:
							row.eligible_classifications.manufacturer_position = oem_position
						else:
							row.eligible_classifications.manufacturer_position = row.status
			positions[f'{row.eligible_classifications.manufacturer_cl.name}'] += 1
		if row.eligible_classifications.driver_cl is not None:
			driver_position = positions.get(row.eligible_classifications.driver_cl.name)

			# Dobieranie stylów i punktów
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
					row.eligible_classifications.driver_points = found[1]

					if row.status not in nonscoring_statuses:
						row.eligible_classifications.driver_position = driver_position
						positions[f'{row.eligible_classifications.driver_cl.name}'] += 1
					else:
						row.eligible_classifications.driver_position = row.status
	return rows


# Odczytanie numeru rundy
def read_round_number(classifications: list[Classification], session_id: int) -> int | None:
	from common.db_queries.classification_tables import check_round_session

	while True:
		try:
			num = int(input('\nPodaj numer rundy w sezonie, której wyniki są w pliku: '))
		except ValueError:
			print('Podaj liczbę naturalną.')
			continue

		if check_round_session(
			classification_id=classifications[0].db_id,
			round_number=num,
			session_id=session_id
		):
			while True:
				print('\nTa runda ma już wyniki tej sesji w bazie. Czy chcesz je zastąpić?')
				print('1. Tak\n2. Nie')
				try:
					ans = int(input('Wybór (1-2): '))
				except ValueError:
					print('\nPodaj liczbę 1 lub 2.')
					continue

				if ans == 1:
					from common.db_queries.classification_tables import remove_session_scores
					print('\nUsuwanie wyników...')

					results_removed: bool = remove_session_scores(
						classifications=classifications,
						round_number=num,
						session_id=session_id
					)

					if results_removed is None:
						return None

					if results_removed:
						print('\nWyniki tej sesji zostały usunięte z bazy danych.')
						return num
					else:
						print('\nUsuwanie wyników z bazy danych nie powiodło się.')
						return None
				elif ans == 2:
					print('\nSkrypt zakończy działanie.')
					return None
				else:
					print('\nPodaj liczbę 1 lub 2.')
		else:
			return num


# Dodanie wyników do bazy
def add_results_to_db(rows: list[ResultRow], round_number: int, session: DbSession) -> None:
	from common.db_queries.classification_tables import add_score

	for row in rows:
		# Zmienna potrzebna do niedodawania wyników kwalifikacji w klasyfikacjach zespołowych
		# nieprzyznających punktów za kwalifikacje
		drivers_result_added: bool = False

		if (
			row.eligible_classifications.driver_cl is not None
			and row.eligible_classifications.driver_style_id is not None
		):
			for driver in row.drivers:
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
			if row.manufacturer is not None:
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
			add_score(
				classification_id=row.eligible_classifications.team_cl.db_id,
				round_number=round_number,
				session_id=session.db_id,
				entity_id=row.db_team_id,
				place=row.eligible_classifications.team_position,
				points=row.eligible_classifications.team_points,
				style_id=row.eligible_classifications.team_style_id
			)
		print('------')


# Główna funkcja skryptu
def main() -> None:
	from common.db_queries.classification_tables import get_classifications_by_champ_id
	from common.db_queries.wikipedia_table import get_wiki_id
	from common.db_queries.points_tables import (
		get_points_scales,
		get_scoring_sessions,
		get_styled_nonscoring_statuses,
		get_styled_points_system
	)
	cannot_continue_error: str = '\nSkrypt nie może kontynuować działania.'

	# Pobranie id polskiej wersji Wikipedii z bazy danych
	plwiki_id = get_wiki_id('plwiki')

	if plwiki_id is None:
		print('Nie udało się pobrać id polskiej wersji Wikipedii z bazy danych.' + cannot_continue_error)
		return

	# Odczytanie id serii wyścigowej
	championship_id: int | None = read_championship()

	if championship_id is None:
		print(cannot_continue_error)
		return

	# Pobranie klasyfikacji punktowych z bazy danych
	classifications: list[Classification] = get_classifications_by_champ_id(
		championship_id
	)

	if len(classifications) == 0:
		print('\nBrak zdefiniowanych klasyfikacji w bazie dla wybranej serii.' + cannot_continue_error)
		return

	# Pobranie danych o punktujących autach w klasyfikacjach producentów (o ile takowe istnieją)
	oem_scoring_cars: list[ClassificationScoring] | None = get_oem_scoring_cars(classifications)

	if oem_scoring_cars is None:
		print(cannot_continue_error)
		return

	# Pobranie skali punktowych z bazy danych
	points_scales: list[float] | None = get_points_scales(championship_id)

	if points_scales is None:
		print(cannot_continue_error)
		return

	if len(points_scales) == 0:
		print('\nNie znaleziono skali punktowych tych mistrzostw.')
		return
	elif len(points_scales) == 1:
		scale: float = points_scales[0]
	else:
		scale: float = read_points_scale(points_scales)

	# Pobranie punktowanych sesji z bazy danych
	sessions: list[DbSession] | None = get_scoring_sessions(championship_id, scale)

	if sessions is None:
		print(cannot_continue_error)
		return

	if len(sessions) == 0:
		print('\nW żadnej z sesji nie są przyznawane punkty.')
		print(cannot_continue_error)
		return
	elif len(sessions) == 1:
		session: DbSession = sessions[0]
	else:
		session: DbSession = read_session(sessions)

	# Odczytanie numeru rundy
	round_num: int | None = read_round_number(classifications, session.db_id)

	if round_num is None:
		print(cannot_continue_error)
		return

	# Pobranie niepunktowanych statusów, takich jak niesklasyfikowany itp., razem ze stylami kolorowania tabeli
	nonscoring_statuses: list[StyledStatus] = get_styled_nonscoring_statuses()

	if len(nonscoring_statuses) == 0 and session.name == 'RACE':
		print('\nNie znaleziono styli wyników wyścigu.' + cannot_continue_error)
		return

	# Pobranie systemu punktowego razem ze stylami kolorowania tabeli
	styled_positions: list[StyledPosition] = get_styled_points_system(
		championship_id=championship_id,
		scale=scale,
		session_id=session.db_id
	)

	if len(styled_positions) == 0:
		print('\nNie znaleziono styli wyników.' + cannot_continue_error)
		return

	# Odczytanie ścieżki do pliku z wynikami
	path: str = read_csv_path()

	# Odczytanie zawartości pliku z wynikami
	rows: list[ResultRow] = read_results_csv(
		path=path,
		classifications=classifications,
		manufacturer_classifications_num=len(oem_scoring_cars),
		wiki_id=plwiki_id
	)

	if len(rows) == 0:
		print(cannot_continue_error)
		return

	# Wyliczenie zajętych pozycji w klasyfikacjach mistrzowskich i znalezienie styli wyników
	rows: list[ResultRow] = calculate_classifications_positions(
		rows=rows,
		classifications=classifications,
		scoring_styles=styled_positions,
		nonscoring_styles=nonscoring_statuses,
		session=session.name,
		oem_classifications_scoring=oem_scoring_cars
	)

	if len(rows) == 0:
		print(cannot_continue_error)
		return

	# Dodanie wyników do bazy danych
	add_results_to_db(rows, round_num, session)


if __name__ == '__main__':
	main()
