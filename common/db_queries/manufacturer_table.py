from sqlite3 import Connection
from common.models.manufacturer import Manufacturer
from common.db_connect import db_connection


# Gets all manufacturers with their id's, codenames and flags
def get_manufacturers() -> list[Manufacturer] | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query = '''
			SELECT id, codename, flag
			FROM manufacturer
		'''

		result = db.execute(query).fetchall()

		manufacturers = list()

		if result is not None:
			for r in result:
				manufacturers.append(Manufacturer(r[0], r[1], r[2]))

		return manufacturers
