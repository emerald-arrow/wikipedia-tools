import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	import sqlite3
	from sqlite3 import Connection
	from common.db_connect import db_connection
	from common.models.classifications import Classification
	from common.models.results import EntityResults, RoundResult
	from common.models.styles import Style


# Gets all classifications of a championship
def get_classifications_by_champ_id(championship_id: int) -> list[Classification] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	classifications: list[Classification] = list()

	with db:
		query = '''
			SELECT cl.id, t.name, ct.name, cl.season
			FROM classification cl
			JOIN title t
			ON t.id = cl.title_id
			JOIN classification_type ct
			ON ct.id = t.type_id
			WHERE t.championship_id = :ch_id
			AND cl.active = 1;
		'''
		params = {'ch_id': championship_id}

		result = db.execute(query, params).fetchall()

		if result is not None:
			for r in result:
				classifications.append(
					Classification(
						db_id=int(r[0]),
						name=r[1],
						championship_id=championship_id,
						cl_type=r[2],
						season=r[3]
					)
				)

		return classifications


# Gets classification's results
def get_classification_results(classification: Classification, wiki_id: int) -> list[EntityResults] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	entities: list[EntityResults] = list()

	with db:
		query = '''
			SELECT DISTINCT entity_id, {entity_table}.flag, {wikipedia_table}.{link_column} {car_no}
			FROM score
			JOIN {entity_table}
			ON {entity_table}.id = score.entity_id
			JOIN {wikipedia_table}
			ON {entity_table}.id = {wikipedia_table}.{entity_id}
			WHERE score.classification_id = :cl_id
			AND {wikipedia_table}.wikipedia_id = :wiki;
		'''
		params = {
			'cl_id': classification.db_id,
			'wiki': wiki_id
		}
		match classification.cl_type:
			case 'DRIVERS':
				query = query.format(
					entity_table='driver',
					wikipedia_table='driver_wikipedia',
					link_column='short_link',
					entity_id='driver_id',
					car_no=''
				)
			case 'TEAMS':
				query = query.format(
					entity_table='team',
					wikipedia_table='team_wikipedia',
					link_column='short_link',
					entity_id='team_id',
					car_no=', team.car_number'
				)
			case 'MANUFACTURERS':
				query = query.format(
					entity_table='manufacturer',
					wikipedia_table='manufacturer_wikipedia',
					link_column='link',
					entity_id='manufacturer_id',
					car_no=''
				)
			case _:
				return None

		result = db.execute(query, params).fetchall()

		for entity_data in result:
			car_number: int | None = None

			try:
				car_number = int(entity_data[3])
			except IndexError:
				car_number = None

			new_entity = EntityResults(
						db_id=int(entity_data[0]),
						flag=entity_data[1],
						link=entity_data[2],
						car_no=car_number,
						points=0
					)

			query = '''
				SELECT round_number, ses.name, place, points, rs.background_hex, rs.text_colour_hex, rs.bold 
				FROM score sc
				JOIN "session" ses
				ON ses.id = sc.session_id
				JOIN result_styling rs
				ON rs.id = sc.style_id
				WHERE classification_id = :cl_id
				AND sc.entity_id = :e_id;
			'''
			params = {
				'cl_id': classification.db_id,
				'e_id': new_entity.db_id
			}

			round_results = db.execute(query, params).fetchall()

			scores: list[RoundResult] = list()

			prev_score: RoundResult | None = None

			for res in round_results:
				new_entity.points += int(res[3])

				score: RoundResult = RoundResult(
										number=int(res[0]),
										session=res[1],
										place=res[2],
										style=Style(
											background=res[4],
											text=res[5],
											bold=bool(res[6])
										)
				)

				if prev_score is not None:
					if prev_score.number == score.number and prev_score.session == 'QUALIFYING':
						score.style.bold = prev_score.style.bold
						scores.remove(prev_score)

				scores.append(score)
				prev_score = score

			new_entity.results = scores

			entities.append(new_entity)

		entities.sort(key=lambda x: x.points, reverse=True)

		return entities


# Gets how many cars score in manufacturer's classification (returns number values or 'ALL')
def get_manufacturer_scoring_cars(classification_id: int) -> str | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT scoring_cars
			FROM manufacturer_classification
			WHERE manufacturer_classification_id = :id;
		'''

		result = db.execute(query, {'id': classification_id}).fetchone()

		return '' if result is None else result[0]


# Gets number of all races in classification's season
def get_races_number(classification_id: int) -> int | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT races_number
			FROM classification
			WHERE id = :cl_id;
		'''

		result = db.execute(query, {'cl_id': classification_id}).fetchone()

		return -1 if result is None else int(result[0])


# Checks whether entity under given id can score in given classification
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


# Removes results of round's session
def remove_session_scores(
	classifications: list[Classification], round_number: int, session_id: int
) -> bool | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			DELETE FROM score
			WHERE classification_id = :classification
			AND round_number = :round
			AND session_id = :session;
		'''

		results: list[bool] = list()

		for cl in classifications:
			params = {
				'classification': cl.db_id,
				'round': round_number,
				'session': session_id
			}

			try:
				db.execute(query, params)
			except sqlite3.Error as e:
				print(e.__str__())
				results.append(False)
				return all(results)

			results.append(True)

		return all(results)
