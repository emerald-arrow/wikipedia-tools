import sqlite3
import os

from modele import Car, Colour, Driver, Team, Manufacturer, Classification

# Połączenie z bazą danych
def connect_db() -> sqlite3.Connection | None:
    db_relative = '../../common/database.db'
    db_absolute = os.path.abspath(db_relative)
    
    try:
        db = sqlite3.connect(db_absolute)
    except sqlite3.OperationalError:
        return None
    return db

# Pobranie trzyliterowej nazwy kraju (ISO 3166-1 alpha-3) z bazy danych. Parametrem jest kod wykorzystywany przez ACO w plikach z wynikami.
def get_country_iso_alpha3(code: int) -> str:
	db = connect_db()
	
	with db:
		query = 'SELECT country FROM country_code WHERE code = :code;'
		params = {'code': code}

		result = db.execute(query, params).fetchone()

		return '?' if result is None else result[0]

# Pobieranie serii wyścigowych
def get_championships() -> list[dict[str, int | str]]:
	championships: list[dict[str, any]] = []

	db = connect_db()

	with db:
		query = 'SELECT id, name FROM championship'

		result = db.execute(query).fetchall()

		if result is not None:
			for r in result:
				championships.append({'id': r[0], 'name': r[1]})
	
	return championships

# Pobieranie wersji językowych wikipedii
def get_wiki_versions() -> list[dict[str, str]]:
	db = connect_db()
	
	with db:
		version_list: list[dict[str, str]] = []

		query = 'SELECT id, version FROM wikipedia'

		result = db.execute(query).fetchall()

		if result is not None:
			for v in result:
				version_list.append({'id': v[0], 'version': v[1]})

		return version_list

# Pobieranie id wybranej wersji wikipedii
def get_wiki_id(version: str) -> int | None:
	db = connect_db()
	
	with db:
		query = 'SELECT id FROM wikipedia WHERE version = :version'
		params = {'version': version}

		result = db.execute(query, params).fetchone()

		return None if result is None else int(result[0])

def get_entity_type_id(entity_name: str) -> int | None:
	db = connect_db()

	with db:
		query = '''
			SELECT id
			FROM entity_type
			WHERE name = :name COLLATE NOCASE
		'''
		params = {'name': entity_name}

		result = db.execute(query, params).fetchone()

		return None if result is None else int(result[0])

# Pobranie wszystkich klasyfikacji danej serii
def get_classifications_by_championship_id(championship_id: int) -> list[Classification]:
	db = connect_db()
	classifications: list[Classification] = []

	with db:
		query = '''
			SELECT id, name
			FROM classification
			WHERE championship_id = :ch_id
		'''
		params = {'ch_id': championship_id}

		result = db.execute(query, params).fetchall()

		if result is not None:
			for r in result:
				classifications.append(Classification(int(r[0]), r[1], championship_id))
		
		return classifications

# Sprawdzenie czy numer rundy jest już w klasyfikacji
def check_round_number_in_classification(classification_id: int, round_number: int) -> bool:
	db = connect_db()

	with db:
		query = '''
			SELECT EXISTS(
				SELECT 1
				FROM classification_point
				WHERE classification_id = :cl_id
				AND round = :round_num
			)
		'''
		params = {'cl_id': classification_id, 'round_num': round_number}

		result = db.execute(query, params).fetchone()

		return False if result is None else bool(result[0])

# Sprawdzenie czy zespół/kierowca może punktować w danej klasyfikacji
def check_classification_eligibility(classification_id: int, test_id: int) -> bool:
	db = connect_db()

	with db:
		# Jeśli jest w tej tabeli to nie może
		query = '''
			SELECT EXISTS(
				SELECT 1
				FROM classification_ineligible
				WHERE classification_id = :c_id
				AND entity_id = :e_id
			)
		'''
		params = {'c_id': classification_id, 'e_id': test_id}

		result = db.execute(query, params).fetchone()

		return True if result is None else bool(not result[0])

# Pobieranie id zespołu i czy może on punktować
def get_team_id_and_scoring_by_codename(codename: str, championship_id: str) -> tuple[int | None, bool | None]:
	db = connect_db()

	with db:
		query = '''
			SELECT id, points_eligible
			FROM team
			WHERE codename = :codename
			AND championship_id = :c_id;
		'''
		params = {'codename': codename, 'c_id': championship_id}

		result = db.execute(query, params).fetchone()

		return (None, None) if result is None else (int(result[0]), bool(result[1]))

# Pobieranie danych kierowcy przy użyciu codename
def get_driver_by_codename(codename: str) -> dict[str, int | str] | None:
	db = connect_db()

	with db:
		query = '''
			SELECT d.flag, dw.short_link, d.id
			FROM driver d
			JOIN driver_wikipedia dw
			ON d.id = dw.driver_id
			WHERE codename = :codename;
		'''
		params = {'codename': codename}

		result = db.execute(query, params).fetchone()

		return None if result is None else {'id': result[2], 'flag': result[0], 'link': result[1]}

# Pobranie wszystkich producentów
def get_manufacturers() -> list[Manufacturer]:
	db = connect_db()

	with db:
		query = '''
			SELECT id, codename, flag
			FROM manufacturer
		'''

		result = db.execute(query).fetchall()

		manufacturers = list()

		if result is not None:
			for r in result:
				manufacturers.append(Manufacturer(r[0], r[1], r[2]))
		
		return manufacturers

# Pobieranie styli kolorowania wyników
def get_colours() -> list[Colour]:
	db = connect_db()

	with db:
		query = '''
			SELECT id, status
			FROM bg_colour
		'''

		result = db.execute(query).fetchall()

		colours = []

		if result is not None:
			for r in result:
				colours.append(Colour(r[0], r[1]))
		
		return colours

# Dodawanie auta do bazy danych, zwraca True jedynie w przypadku dodania zarówno auta jak i linku
def add_car(car: Car, wiki_id: int) -> None:
	db = connect_db()
	
	with db:
		db.execute('BEGIN')

		# Czy samochód jest już w tabeli car
		query = 'SELECT id FROM car WHERE codename = :codename;'
		params = {'codename': car.codename}

		result = db.execute(query, params).fetchone()

		if result is None:
			# Dodanie auta do tabeli car
			query = 'INSERT INTO car (codename) VALUES (:codename);'
			params = {'codename': car.codename}

			try:
				db.execute(query, params)
			except sqlite3.OperationalError as e:
				db.execute('ROLLBACK')
				print('Błąd przy dodawaniu %s do bazy - %s' % (
					car.codename,
					e
				))
				return

			# Sprawdzenie id dodanego auta
			query = 'SELECT id FROM car WHERE codename = :codename'
			params = {'codename': car.codename}

			result = db.execute(query, params).fetchone()
			car_id = result[0]

			# Dodanie linku do tabeli car_wikipedia
			query = '''
				INSERT INTO car_wikipedia (wikipedia_id, car_id, link)
				VALUES (:wikipedia_id, :car_id, :link);
			'''
			params = {
				'wikipedia_id': wiki_id,
				'car_id': car_id,
				'link': car.link
			}

			try:
				db.execute(query, params)
			except sqlite3.OperationalError as e:
				db.execute('ROLLBACK')
				print('Błąd przy dodawaniu %s do bazy - %s' % (
					car.codename,
					e
				))
				return

			# Wszystko dobrze
			db.execute('COMMIT')
			print(f'Dodanie {car.codename} do bazy zakończyło się powodzeniem.')
		else:
			# Czy w tabeli car_wikipedia jest już link do artykułu z autem na polskiej wikipedii
			car_id = result[0]

			query = '''
				SELECT link
				FROM car_wikipedia
				WHERE car_id = :car_id
				AND wikipedia_id = :wikipedia_id;
			'''
			params = {'car_id': car_id, 'wikipedia_id': wiki_id}

			result = db.execute(query, params).fetchone()

			if result is None:
				# Dodanie linku do tabeli car_wikipedia
				query = '''
					INSERT INTO car_wikipedia (wikipedia_id, car_id, link)
					VALUES (:wikipedia_id, :car_id, :link);
				'''
				params = {
					'wikipedia_id': wiki_id,
					'car_id': car_id,
					'link': car.link
				}

				try:
					db.execute(query, params)
				except sqlite3.OperationalError as e:
					db.execute('ROLLBACK')
					print('Błąd przy dodawaniu %s do bazy - %s' % (
						car.codename,
						e
					))
					return False

				print(f'{car.codename} - z powodzeniem dodano link: "{car.link}"')
				db.execute('COMMIT')
			else:
				db.execute('ROLLBACK')
				print('%s ma już w bazie link do artykułu na polskiej Wikipedii: %s' % (
					car.codename,
					result[0]
				))

# Dodawanie kierowcy do bazy danych, zwraca True jedynie w przypadku dodania zarówno kierowcy jak i linków
def add_driver(driver: Driver, wiki_id: int, type_id: int) -> bool:
	db = connect_db()

	driver_id = None
	exists = False

	with db:
		db.execute('BEGIN')

		# Czy kierowca jest już w tabeli driver
		query = '''
			SELECT id
			FROM driver
			WHERE codename = :codename;
		'''
		params = {'codename': driver.codename}

		result = db.execute(query, params).fetchone()

		# Jeśli nie ma kierowcy w tabeli driver
		if result is None:
			# Dodanie kierowcy do tabeli entity
			query = '''
				INSERT INTO entity (type_id)
				VALUES (:type_id)
			'''

			params = {'type_id': type_id}

			try:
				db.execute(query, params)
			except sqlite3.OperationalError as e:
				db.execute('ROLLBACK')
				print('Błąd przy dodawaniu %s do bazy - %s' % (
					driver.codename,
					e
				))
				return False
			
			# Sprawdzenie id dodanego kierowcy
			query = '''
				SELECT MAX(id)
				FROM entity
				WHERE type_id = :type_id
			'''

			params = {'type_id': type_id}

			driver_id = int(db.execute(query, params).fetchone()[0])

			# Dodanie kierowcy do tabeli driver
			query = '''
				INSERT INTO driver (id, codename, flag)
				VALUES (:id, :codename, :nationality)
			'''
			params = {
				'id': driver_id,
				'codename': driver.codename,
				'nationality': driver.nationality
			}

			try:
				db.execute(query, params)
			except sqlite3.OperationalError as e:
				db.execute('ROLLBACK')
				print('Błąd przy dodawaniu %s do bazy - %s' % (
					driver.codename,
					e
				))
				return False
		else:
			exists = True
			# Czy dane o kierowcy są w tabeli driver_wikipedia
			driver_id = result[0]

			query = '''
				SELECT short_link, long_link
				FROM driver_wikipedia
				WHERE driver_id = :driver_id
				AND wikipedia_id = :wikipedia_id;
			'''
			params = {
				'driver_id': driver_id,
				'wikipedia_id': wiki_id
			}

			result = db.execute(query, params).fetchone()
			
			# Jeśli dane są w tabeli driver_wikipedia
			if result is not None:
				db.execute('ROLLBACK')
				print('%s ma już w bazie link do artykułu na polskiej Wikipedii: "%s", "%s"' % (
					driver.codename,
					result[0],
					result[1]
				))

				return False
		
		# Dodanie linków do tabeli driver_wikipedia
		query = '''
			INSERT INTO driver_wikipedia (wikipedia_id, driver_id, short_link, long_link)
			VALUES (:wikipedia_id, :driver_id, :short_link, :long_link);
		'''
		params = {
			'wikipedia_id': wiki_id,
			'driver_id': driver_id,
			'short_link': driver.short_link,
			'long_link': driver.long_link
		}

		try:
			db.execute(query, params)
		except sqlite3.OperationalError as e:
			db.execute('ROLLBACK')
			print('Błąd przy dodawaniu %s do bazy - %s' % (
				driver.codename,
				e
			))
			return False

		db.execute('COMMIT')

		if exists:
			print('%s - dodano linki do artykułów na polskiej Wikipedii' % (driver.codename))
			return False
		else:
			return True

# Dodawanie zespołu do bazy danych, zwraca True jedynie w przypadku dodania zarówno zespołu jak i linków
def add_team(team: Team, championship_id: int, wiki_id: int, type_id: int) -> bool:
	db = connect_db()

	team_id = None
	exists = False

	with db:
		db.execute('BEGIN')

		# Czy zespół jest już w tabeli team
		query = '''
			SELECT id
			FROM team
			WHERE codename = :codename
			AND flag = :flag
			AND car_number = :car_number
			AND championship_id = :championship_id;
		'''
		params = {
			'codename': team.codename,
			'flag': team.nationality,
			'car_number': team.car_number,
			'championship_id': championship_id
		}

		result = db.execute(query, params).fetchone()

		# Jeśli zespołu nie ma w tabeli team
		if result is None:
			# Dodanie zespołu do tabeli entity
			query = '''
				INSERT INTO entity (type_id)
				VALUES (:type_id)
			'''

			params = {'type_id': type_id}

			try:
				db.execute(query, params)
			except sqlite3.OperationalError as e:
				db.execute('ROLLBACK')
				print('Błąd przy dodawaniu %s do bazy - %s' % (
					team.codename,
					e
				))
				return False
			
			# Sprawdzenie id dodanego zespołu
			query = '''
				SELECT MAX(id)
				FROM entity
				WHERE type_id = :type_id
			'''

			params = {'type_id': type_id}

			team_id = int(db.execute(query, params).fetchone()[0])

			# Dodanie zespołu do tabeli team
			query = '''
				INSERT INTO team (id, codename, flag, car_number, championship_id)
				VALUES (:id, :codename, :flag, :car_number, :championship_id)
			'''
			params = {
				'id': team_id,
				'codename': team.codename,
				'flag': team.nationality,
				'car_number': team.car_number,
				'championship_id': championship_id
			}

			try:
				db.execute(query, params)
			except sqlite3.OperationalError as e:
				db.execute('ROLLBACK')
				print('Błąd przy dodawaniu %s do bazy - %s' % (
					team.codename,
					e
				))
				return False
		else:
			exists = True
			# Czy dane o zespole są w tabeli team_wikipedia
			team_id = result[0]

			query = '''
				SELECT short_link, long_link
				FROM team_wikipedia
				WHERE team_id = :team_id
				AND wikipedia_id = :wikipedia_id;
			'''
			params = {
				'team_id': team_id,
				'wikipedia_id': wiki_id
			}

			result = db.execute(query, params).fetchone()

			# Jeśli dane są w tabeli team_wikipedia
			if result is not None:
				db.execute('ROLLBACK')
				print('%s ma już w bazie link do artykułu na polskiej Wikipedii: "%s", "%s"' % (
					team.codename,
					result[0],
					result[1]
				))

				return False
		
		# Dodanie linku/linków w tabeli team_wikipedia
		query = '''
			INSERT INTO team_wikipedia (wikipedia_id, team_id, short_link, long_link)
			VALUES (:wikipedia_id, :team_id, :short_link, :long_link);
		'''
		
		params = {
			'wikipedia_id': wiki_id,
			'team_id': team_id,
			'short_link': team.short_link,
			'long_link': team.long_link
		}

		try:
			db.execute(query, params)
		except sqlite3.OperationalError as e:
			db.execute('ROLLBACK')
			print('Błąd przy dodawaniu %s do bazy - %s' % (
				team.codename,
				e
			))
			return False

		db.execute('COMMIT')
		if exists:
			print('%s - dodano linki do artykułów na polskiej Wikipedii' % (team.codename))
			return False
		else:
			return True

# Dodanie wyniku do bazy danych
def add_score(classification_id: int, entity_id: int, colour_id: int,
			  position: int, points: int, pole_position: bool,
			  round_number: int) -> bool:
	db = connect_db()

	print(locals())

	# with db:
	# 	db.execute('BEGIN')