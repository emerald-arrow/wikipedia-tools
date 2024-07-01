class Championship:
	def __init__(self, db_id: int, name: str):
		self.db_id = db_id
		self.name = name


class ChampionshipExt:
	def __init__(self, db_id: int, name: str, organiser: str | None = None):
		self.db_id = db_id
		self.name = name
		self.organiser = organiser
