import sys
from sqlite3 import Connection
from common.db_connect import db_connection
from common.models.championships import Championship, ChampionshipExt

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True


# Gets championships data with organiser names
def get_championships() -> list[ChampionshipExt] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	championships: list[ChampionshipExt] = list()

	with db:
		query = '''
			SELECT c.id, c.name, o.name
			FROM championship c
			JOIN organiser o
			ON c.organiser_id = o.id;
		'''

		result = db.execute(query).fetchall()

		if result is not None:
			for r in result:
				championships.append(
					ChampionshipExt(
						db_id=int(r[0]),
						name=r[1],
						organiser=r[2]
					)
				)

	return championships


# Gets list of championships that have results saved in the database
def get_championships_with_results() -> list[Championship] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	championships: list[Championship] = list()

	with db:
		query = '''
			SELECT DISTINCT ch.id, ch.name
			FROM championship ch
			JOIN title t
			ON t.championship_id = ch.id
			JOIN classification cl
			ON cl.title_id = t.id
			JOIN score s
			ON s.classification_id = cl.id;
		'''

		result = db.execute(query).fetchall()

		if result is not None:
			for r in result:
				championships.append(
					Championship(
						db_id=int(r[0]),
						name=r[1],
					)
				)

	return championships


# Gets list of championships that have defined classifications in the database
def get_championships_with_classifications() -> list[Championship] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	championships: list[Championship] = list()

	with db:
		query = '''
			SELECT DISTINCT ch.id, ch.name
			FROM championship ch
			JOIN title t
			ON t.championship_id = ch.id;
		'''

		result = db.execute(query).fetchall()

		if result is not None:
			for r in result:
				championships.append(
					Championship(
						db_id=int(r[0]),
						name=r[1],
					)
				)

	return championships
