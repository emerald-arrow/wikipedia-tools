from enum import Enum


class Session(Enum):
	PRACTICE = 1
	QUALIFYING = 2
	RACE = 3
	QUALIFYING_PRE_HP = 4
	QUALIFYING_POST_HP = 5


class DbSession:
	def __init__(self, db_id: int, name: str) -> None:
		self.db_id = db_id
		self.name = name
