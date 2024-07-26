import sqlite3
import sys
from sqlite3 import Connection
from pathlib import Path

# Stops Python from creating __pycache__
sys.dont_write_bytecode = True

# Establishing database's path
current_dir = Path(__file__)
project_dir = next(p for p in current_dir.parents if p.name == "wikipedia-tools")
common_dir = Path.joinpath(project_dir, 'common')
db_absolute = Path.joinpath(common_dir, 'database.db')


# Returns the connection to the database
def db_connection() -> Connection | None:
	global db_absolute

	try:
		db: Connection = sqlite3.connect(f'file:{db_absolute}?mode=rw', uri=True)
	except sqlite3.Error as err:
		return None
	return db
