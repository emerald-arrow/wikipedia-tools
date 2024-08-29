import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	import sqlite3
	from sqlite3 import Connection
	from common.db_connect import db_connection


#
def get_tyre_manufacturer_name(letter_code: str) -> str | None:
	db: Connection | None = db_connection()

	if db is None:
		print("Couldn't connect to the database.")
		return None

	with db:
		query: str = '''
			SELECT manufacturer_name
			FROM tyre
			WHERE codename = :letter;
		'''

		result = db.execute(query, {'letter': letter_code}).fetchone()

		return '' if result is None else result[0]
