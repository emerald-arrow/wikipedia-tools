import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
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

		if len(result) > 0:
			for r in result:
				manufacturers.append(
					Manufacturer(
						db_id=int(r[0]),
						codename=r[1],
						flag=r[2]
					)
				)

		return manufacturers


# Refreshes manufacturers timestamps
def refresh_manufacturers_timestamps(ids: list[int]) -> None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	for i in ids:  # type: int
		with db:
			query = 'UPDATE manufacturer SET last_used = CURRENT_TIMESTAMP WHERE id = id;'

			db.execute(query, {'id': i})
