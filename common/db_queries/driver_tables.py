import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	import sqlite3
	from common.db_connect import db_connection
	from common.models.driver import Driver


# Checks whether driver's data is in database
def check_driver_exists(codename: str, wikipedia_id: int) -> bool | None:
	db = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT EXISTS(
				SELECT 1
				FROM driver d
				JOIN driver_wikipedia dw
				ON d.id = dw.driver_id
				WHERE d.codename = :codename
				AND dw.wikipedia_id = :wiki_id
			);
		'''
		params = {'codename': codename, 'wiki_id': wikipedia_id}

		result = db.execute(query, params).fetchone()

		return False if result[0] is None else bool(result[0])


# Gets driver's links and flag from the database and refreshes driver's last used timestamp
def get_driver_flag_links(codename: str, wiki_id: int) -> Driver | None:
	db = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT short_link, long_link, d.flag, driver_id
			FROM driver_wikipedia dw
			JOIN driver d
			ON d.id = dw.driver_id
			WHERE d.codename = :codename
			AND wikipedia_id = :wikipedia_id;
		'''
		params = {
			'codename': codename,
			'wikipedia_id': wiki_id
		}

		try:
			result = db.execute(query, params).fetchone()
		except sqlite3.Error:
			return Driver()

		if result is None:
			return Driver()
		else:
			query = 'UPDATE driver SET last_used = CURRENT_TIMESTAMP WHERE id = :driver_id;'

			db.execute(query, {'driver_id': int(result[3])})

			return Driver(
				codename=codename,
				nationality=result[2],
				short_link=result[0],
				long_link=result[1]
			)


# Gets driver's id, link and flag by codename
def get_driver_by_codename(codename: str, wiki_id: int) -> Driver | None:
	db = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT d.flag, dw.short_link, d.id
			FROM driver d
			JOIN driver_wikipedia dw
			ON d.id = dw.driver_id
			WHERE codename = :codename
			AND wikipedia_id = :wiki_id;
		'''
		params = {'codename': codename, 'wiki_id': wiki_id}

		result = db.execute(query, params).fetchone()

		if result is None:
			return Driver()
		else:
			return Driver(
				db_id=int(result[2]),
				nationality=result[0],
				short_link=result[1],
				codename=codename
			)


# Adds drivers data to the database
def add_drivers(drivers: list[Driver], wiki_id: int, type_id: int) -> None:
	db = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return

	exists = False

	for driver in drivers:
		with db:
			db.execute('BEGIN')

			# Checking whether driver's data is in 'driver' table
			query = '''
				SELECT id
				FROM driver
				WHERE codename = :codename;
			'''
			params = {'codename': driver.codename}

			driver_id_db: tuple | None = db.execute(query, params).fetchone()

			# If driver's data is not in the 'driver' table
			if driver_id_db is None:
				# Adding driver into 'entity' table
				query = '''
					INSERT INTO entity (type_id)
					VALUES (:type_id)
				'''

				params = {'type_id': type_id}

				try:
					db.execute(query, params)
				except sqlite3.OperationalError as e:
					db.execute('ROLLBACK')
					print('An error occurred while adding {driver}: {error}'.format(
						driver=driver.codename,
						error=e
					))
					continue

				# Checking driver's id in the database
				query = '''
					SELECT MAX(id)
					FROM entity
					WHERE type_id = :type_id
				'''

				params = {'type_id': type_id}

				driver_id: int = int(db.execute(query, params).fetchone()[0])

				# Adding driver's data to 'driver' table
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
					print('An error occurred while adding {driver}: {error}'.format(
						driver=driver.codename,
						error=e
					))
					continue
			else:
				exists = True
				# Checking whether 'driver_wikipedia' table has links to articles about driver
				driver_id: int = driver_id_db[0]

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

				if result is not None:
					db.execute('ROLLBACK')
					print('{driver} already has links in database: "{short_link}", "{long_link}'.format(
						driver=driver.codename,
						short_link=result[0],
						long_link=result[1]
					))
					continue

			# Adding links into 'driver_wikipedia' table
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
				print('An error occurred while adding {driver}: {error}'.format(
					driver=driver.codename,
					error=e
				))
				continue

			db.execute('COMMIT')

			if exists:
				print(f'{driver.codename} - successfully added links to database')
			else:
				print(f'{driver.codename} - successfully added data to database')
