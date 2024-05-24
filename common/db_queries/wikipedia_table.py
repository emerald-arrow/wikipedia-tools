from sqlite3 import Connection
from common.db_connect import db_connection


# Gets all Wikipedia versions
def get_wiki_versions() -> list[dict[str, str]] | None:
	db: Connection | None = db_connection()

	if db is None:
		return None

	with db:
		version_list: list[dict[str, str]] = []

		query = 'SELECT id, version FROM wikipedia'

		result = db.execute(query).fetchall()

		if result is not None:
			for v in result:
				version_list.append({'id': v[0], 'version': v[1]})

		return version_list


# Gets Wikipedia's id by version name (plwiki, enwiki and so on)
def get_wiki_id(name: str) -> int | None:
	db: Connection | None = db_connection()

	if db is None:
		return None

	with db:
		query = 'SELECT id FROM wikipedia WHERE version = :version'
		params = {'version': name}

		result = db.execute(query, params).fetchone()

		return None if result is None else int(result[0])
