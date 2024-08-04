import sys
from sqlite3 import Connection
from common.db_connect import db_connection
from common.models.wikipedia import Wikipedia

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True


# Gets all Wikipedia versions
def get_wiki_versions() -> list[Wikipedia] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		version_list: list[Wikipedia] = list()

		query = 'SELECT id, version FROM wikipedia'

		result = db.execute(query).fetchall()

		if len(result) > 0:
			for r in result:
				version_list.append(
					Wikipedia(
						db_id=int(r[0]),
						name=r[1]
					)
				)

		return version_list


# Gets Wikipedia's id by version name (plwiki, enwiki and so on)
def get_wiki_id(name: str) -> int | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = 'SELECT id FROM wikipedia WHERE version = :version'
		params = {'version': name}

		result = db.execute(query, params).fetchone()

		return -1 if result is None else int(result[0])
