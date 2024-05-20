from sqlite3 import Connection
from common.db_connect import db_connection
from common.models.championship import Championship


# Pobieranie serii wyścigowych
def get_championships() -> list[Championship] | None:
	db: Connection | None = db_connection()

	if db is None:
		return None

	championships: list[Championship] = []

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
					Championship(
						db_id=int(r[0]),
						name=r[1],
						organiser=r[2]
					)
				)

	return championships
