import sqlite3
from sqlite3 import Connection
from common.db_connect import db_connection
from common.models.classifications import Classification


# Gets all classifications of a championship
def get_classifications_by_champ_id(championship_id: int) -> list[Classification] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	classifications: list[Classification] = list()

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
				classifications.append(
					Classification(
						db_id=int(r[0]),
						name=r[1],
						championship_id=championship_id
					)
				)

		return classifications


# Checking whether entity under given id can score in given classification
def check_points_eligibility(classification_id: int, entity_id: int) -> bool | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		# If entity is in this table then it cannot score
		query = '''
			SELECT EXISTS(
				SELECT 1
				FROM classification_ineligible
				WHERE classification_id = :c_id
				AND entity_id = :e_id
			);
		'''
		params = {'c_id': classification_id, 'e_id': entity_id}

		result = db.execute(query, params).fetchone()

		return False if result is None else bool(not result[0])


# Checks whether given round and session are in the database
def check_round_session(classification_id: int, round_number: int, session_id: int) -> bool | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT EXISTS(
				SELECT 1
				FROM score s
				WHERE classification_id = :cl_id
				AND round_number = :round
				AND session_id = :s_id
			);
		'''
		params = {
			'cl_id': classification_id,
			'round': round_number,
			's_id': session_id
		}

		result = db.execute(query, params).fetchone()

		return False if result is None else bool(result[0])


# Adds a score to the database
def add_score(
	classification_id: int, round_number: int, session_id: int,
	entity_id: int, place: int, points: float, style_id: int
) -> None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			INSERT INTO score
			VALUES (:cl_id, :rnd_num, :s_id, :e_id, :place, :points, :style_id);
		'''
		params = {
			'cl_id': classification_id,
			'rnd_num': round_number,
			's_id': session_id,
			'e_id': entity_id,
			'place': place,
			'points': points,
			'style_id': style_id
		}

		try:
			db.execute('BEGIN')
			db.execute(query, params)
		except sqlite3.OperationalError as e:
			db.execute('ROLLBACK')
			print(f'An error occurred while adding score to the database - {e.__str__()}')
			return

		db.execute('COMMIT')
		print('Successfully added score to the database.')
