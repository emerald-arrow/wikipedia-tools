import sys

# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True

if True:  # noqa: E402
	from sqlite3 import Connection
	from common.db_connect import db_connection


# Gets country's ISO 3166-1 alpha-3 code.
# Function's parameter is a number code used by ACO in its results files.
def get_country_iso_alpha3(code: int) -> str | None:
	db: Connection | None = db_connection()

	if db is None:
		return None

	with db:
		query = '''
			SELECT country
			FROM country_code
			WHERE code = :code;
		'''
		params = {'code': code}

		result = db.execute(query, params).fetchone()

		return '?' if result is None else '?' if result[0] is None else result[0]
