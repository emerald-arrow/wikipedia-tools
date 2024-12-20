import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	import sqlite3
	from sqlite3 import Connection
	from common.db_connect import db_connection
	from common.models.car import Car


# Checks whether car's data exists in database
def check_car_exists(codename: str, wikipedia_id: int) -> bool | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT EXISTS(
				SELECT 1
				FROM car c
				JOIN car_wikipedia cw
				ON c.id = cw.car_id
				WHERE codename = :codename
				AND cw.wikipedia_id = :wiki_id
			);
		'''
		params = {'codename': codename, 'wiki_id': wikipedia_id}

		result = db.execute(query, params).fetchone()

		return False if result[0] is None else bool(result[0])


# Gets car's link from the database and refreshes car's timestamp
def get_car_link(codename: str, wiki_id: int) -> str | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT link, car_id
			FROM car_wikipedia cw
			JOIN car c
			ON c.id = cw.car_id
			WHERE c.codename = :codename
			AND wikipedia_id = :wikipedia_id;
		'''
		params = {'codename': codename, 'wikipedia_id': wiki_id}

		try:
			result = db.execute(query, params).fetchone()
		except sqlite3.Error:
			return ''

		if result is None:
			return ''
		else:
			query = '''
				UPDATE car
				SET last_used = CURRENT_TIMESTAMP
				WHERE id = :car_id;
			'''

			db.execute(query, {'car_id': result[1]})

			return result[0]


# Adds cars data to the database
def add_cars(cars: list[Car], wiki_id: int) -> None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	for car in cars:
		with db:
			exists: bool = False

			db.execute('BEGIN')

			# Checking whether car's data is in 'car' table
			query = 'SELECT id FROM car WHERE codename = :codename;'
			params = {'codename': car.codename}

			car_id_db: tuple | None = db.execute(query, params).fetchone()

			if car_id_db is None:
				# Adding car's data to 'car' table
				query = 'INSERT INTO car (codename) VALUES (:codename);'
				params = {'codename': car.codename}

				try:
					db.execute(query, params)
				except sqlite3.OperationalError as e:
					db.execute('ROLLBACK')
					print('An error occurred while adding {car}: {error}'.format(
						car=car.codename,
						error=e
					))
					continue

				# Checking car's id in the database
				query = 'SELECT id FROM car WHERE codename = :codename'
				params = {'codename': car.codename}

				result = db.execute(query, params).fetchone()
				car_id = result[0]
			else:
				exists = True
				car_id: int = car_id_db[0]
				# Checking whether 'car_wikipedia' table has links to the article about the car
				query = '''
					SELECT link
					FROM car_wikipedia
					WHERE car_id = :car_id
					AND wikipedia_id = :wikipedia_id;
				'''
				params = {'car_id': car_id, 'wikipedia_id': wiki_id}

				result = db.execute(query, params).fetchone()

				if result is not None:
					db.execute('ROLLBACK')
					print('{car} already has a link in database: {link}'.format(
						car=car.codename,
						link=result[0]
					))
					continue

			# Adding link into 'car_wikipedia' table
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
				print('An error occurred while adding {car}: {error}'.format(
					car=car.codename,
					error=e
				))
				continue

			db.execute('COMMIT')

			if exists:
				print(f'{car.codename} - successfully added link: "{car.link}"')
			else:
				print(f'{car.codename} - successfully added to the database')
