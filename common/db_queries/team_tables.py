import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	import sqlite3
	from sqlite3 import Connection
	from common.db_connect import db_connection
	from common.models.teams import Team, TeamEligibility


# Checks whether a team is in database
def check_team_exists(
	codename: str, championship_id: int, flag: str, car_number: str, wikipedia_id: int
) -> bool | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT EXISTS(
				SELECT 1
				FROM team t
				JOIN team_wikipedia tw
				ON t.id = tw.team_id
				WHERE t.codename = :codename
				AND t.championship_id = :ch_id
				AND t.flag = :flag
				AND t.car_number = :car_number
				AND tw.wikipedia_id = :wiki_id
			);
		'''
		params = {
			'codename': codename,
			'ch_id': championship_id,
			'flag': flag,
			'car_number': car_number,
			'wiki_id': wikipedia_id
		}

		result = db.execute(query, params).fetchone()

		return bool(result[0])


# Gets team's data from the database and refreshes team's timestamp
def get_team_data(codename: str, championship_id: int, wiki_id) -> Team | None:
	db = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT short_link, long_link, t.flag, t.car_number, team_id
			FROM team_wikipedia tw
			JOIN team t
			ON t.id = tw.team_id
			WHERE t.codename = :codename
			AND t.championship_id = :championship_id
			AND wikipedia_id = :wikipedia_id;
		'''
		params = {
			'codename': codename,
			'championship_id': championship_id,
			'wikipedia_id': wiki_id
		}

		result = db.execute(query, params).fetchone()

		if result is None:
			return Team()
		else:
			query = '''
				UPDATE team
				SET last_used = CURRENT_TIMESTAMP
				WHERE id = :team_id;
			'''
			params = {'team_id': int(result[4])}

			db.execute(query, params)

			return Team(
				codename=codename,
				nationality=result[2],
				car_number=result[3],
				short_link=result[0],
				long_link=result[1]
			)


# Gets team's id and points eligibility
def get_id_and_scoring(codename: str, championship_id: int) -> TeamEligibility | None:
	db = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT id, points_eligible
			FROM team
			WHERE codename = :codename
			AND championship_id = :c_id;
		'''
		params = {'codename': codename, 'c_id': championship_id}

		result = db.execute(query, params).fetchone()

		if result is None:
			return TeamEligibility()
		else:
			refresh_query = '''
				UPDATE team
				SET last_used = CURRENT_TIMESTAMP
				WHERE id = :team_id;
			'''

			db.execute(refresh_query, {'team_id': int(result[0])})

			return TeamEligibility(
				team=Team(
					db_id=int(result[0]),
					codename=codename
				),
				eligibility=bool(result[1])
			)


# Adds teams data to the database
def add_teams(teams: list[Team], championship_id: int, wiki_id: int, type_id: int) -> None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return

	team_id: int | None = None
	exists: bool = False

	for team in teams:
		with db:
			db.execute('BEGIN')

			# Checking whether team is in 'team' table
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

			if result is None:
				# Adding team to 'entity' table
				query = '''
					INSERT INTO entity (type_id)
					VALUES (:type_id)
				'''

				params = {'type_id': type_id}

				try:
					db.execute(query, params)
				except sqlite3.OperationalError as e:
					db.execute('ROLLBACK')
					print('An error occurred while adding {team}: {error}'.format(
						team=team.codename,
						error=e
					))
					continue

				# Checking id of added team
				query = '''
					SELECT MAX(id)
					FROM entity
					WHERE type_id = :type_id
				'''

				params = {'type_id': type_id}

				team_id = int(db.execute(query, params).fetchone()[0])

				# Adding team's data to 'team' table
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
					print('An error occurred while adding {team}: {error}'.format(
						team=team.codename,
						error=e
					))
					continue
			else:
				exists = True
				# Checking whether team's data is in 'team_wikipedia' table
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

				# If team's data is in 'team_wikipedia' table
				if result is not None:
					db.execute('ROLLBACK')
					print('{team} already has links in database: "{short_link}", "{long_link}"'.format(
						team=team.codename,
						short_link=result[0],
						long_link=result[1]
					))
					continue

			# Adding links to 'team_wikipedia' table
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
				print('An error occurred while adding {team}: {error}'.format(
					team=team.codename,
					error=e
				))
				continue

			db.execute('COMMIT')

			if exists:
				print(f'{team.codename} - successfully added links to database')
			else:
				print(f'{team.codename} - successfully added data to database')
