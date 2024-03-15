import sqlite3
import os

from db_auta import Car
from db_kierowcy import Driver
from db_zespoły import Team

# Połączenie z bazą danych
def connect_db():
    db_relative = '../../common/database.db'
    db_absolute = os.path.abspath(db_relative)
    
    db = sqlite3.connect(db_absolute)
    return db

# Pobranie trzyliterowej nazwy kraju (ISO 3166-1 alpha-3) z bazy danych. Parametrem jest kod wykorzystywany przez ACO w plikach z wynikami.
def get_country_iso_alpha3(code: int) -> str:
	db = connect_db()
	
	with db:
		query = 'SELECT country FROM country_code WHERE code = :code;'
		params = {'code': code}

		result = db.execute(query, params).fetchone()

		if result is not None:
			return result[0]
		else:
			return '?'

# Pobieranie serii wyścigowych
def get_championships() -> list[dict[str, any]]:
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

		if result is not None:
			return int(result[0])
		else:
			return None

# Dodawanie auta do bazy danych, zwraca True jedynie w przypadku dodania zarówno auta jak i linku
def add_car(car: Car) -> bool:
	db = connect_db()

	wiki_id = get_wiki_id('plwiki')
	
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
				return False

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
				return False
		
			db.execute('COMMIT')
			return True
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

				print(f'{car.codename} - dodano link "{car.link}"')
				db.execute('COMMIT')
				return False
			else:
				db.execute('ROLLBACK')
				print('%s ma już w bazie link do artykułu na polskiej Wikipedii: %s' % (
					car.codename,
					result[0]
				))
				return False

# Dodawanie kierowcy do bazy danych, zwraca True jedynie w przypadku dodania zarówno kierowcy jak i linków
def add_driver(driver: Driver) -> bool:
	db = connect_db()

	wiki_id = get_wiki_id('plwiki')

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

		if result is None:
			# Dodanie kierowcy do tabeli driver
			query = '''
				INSERT INTO driver (codename, nationality)
				VALUES (:codename, :nationality)
			'''
			params = {
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
		
			# Sprawdzenie id dodanego kierowcy
			query = '''
				SELECT id
				FROM driver
				WHERE codename = :codename;
			'''
			params = {'codename': driver.codename}

			result = db.execute(query, params).fetchone()
			driver_id = result[0]

			# Dodanie linku/linków w tabeli driver_wikipedia
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
			return True
		else:
			# Czy dane o kierowcy są w tabeli driver_wikipedia
			query = '''
				SELECT short_link
				FROM driver_wikipedia
				WHERE driver_id = :driver_id
				AND wikipedia_id = :wikipedia_id;
			'''
			params = {
				'driver_id': result[0],
				'wikipedia_id': wiki_id
			}

			result = db.execute(query, params).fetchone()

			if result is None:
				# Dodanie linku/linków w tabeli driver_wikipedia
				driver_id = result[0]
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
				return False

			else:
				db.execute('ROLLBACK')
				print('%s ma już w bazie link do artykułu na polskiej Wikipedii: %s' % (
					driver.codename,
					result[0]
				))
				return False

# Dodawanie zespołu do bazy danych, zwraca True jedynie w przypadku dodania zarówno zespołu jak i linków
def add_team(team: Team, championship_id: int) -> bool:
	db = connect_db()

	wiki_id = get_wiki_id('plwiki')

	with db:
		db.execute('BEGIN')

		# Czy zespół jest już w tabeli team
		query = '''
			SELECT id
			FROM team
			WHERE codename = :codename
			AND nationality = :nationality
			AND car_number = :car_number
			AND championship_id = :championship_id;
		'''
		params = {
			'codename': team.codename,
			'nationality': team.nationality,
			'car_number': team.car_number,
			'championship_id': championship_id
		}

		result = db.execute(query, params).fetchone()

		if result is None:
			# Dodanie zespołu do tabeli team
			query = '''
				INSERT INTO team (codename, nationality, car_number, championship_id)
				VALUES (:codename, :nationality, :car_number, :championship_id)
			'''
			params = {
				'codename': team.codename,
				'nationality': team.nationality,
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
		
			# Sprawdzenie id dodanego zespołu
			query = '''
				SELECT id
				FROM team
				WHERE codename = :codename
				AND nationality = :nationality
				AND car_number = :car_number
				AND championship_id = :championship_id;
			'''
			params = {
				'codename': team.codename,
				'nationality': team.nationality,
				'car_number': team.car_number,
				'championship_id': championship_id
			}

			result = db.execute(query, params).fetchone()
			team_id = result[0]

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
			return True
		else:
			# Czy dane o zespole są w tabeli team_wikipedia
			query = '''
				SELECT short_link
				FROM team_wikipedia
				WHERE team_id = :team_id
				AND wikipedia_id = :wikipedia_id;
			'''
			params = {
				'team_id': result[0],
				'wikipedia_id': wiki_id
			}

			result = db.execute(query, params).fetchone()

			if result is None:
				# Dodanie linku/linków w tabeli team_wikipedia
				team_id = result[0]
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
		
				print(f'Dla istniejącego zespołu {team.codename} dodano link do wikipedii.')
				db.execute('COMMIT')
				return False

			else:
				db.execute('ROLLBACK')
				print('%s ma już w bazie link do artykułu na polskiej Wikipedii: %s' % (
					team.codename,
					result[0]
				))
				return False