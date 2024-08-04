import sys
from common.db_connect import db_connection


# Prevents creating __pycache__ directory
sys.dont_write_bytecode = True


# Gets id of entity type
def get_entity_type_id(entity_name: str) -> int | None:
	db = db_connection()

	if db is None:
		return None

	with db:
		query = '''
			SELECT id
			FROM entity_type
			WHERE name = :name COLLATE NOCASE;
		'''
		params = {'name': entity_name}

		result = db.execute(query, params).fetchone()

		return -1 if result is None else int(result[0])
