class Style:
	def __init__(self, background: str, bold: bool, text: str | None, db_id: int | None = None):
		self.db_id = db_id
		self.background = background
		self.text = text
		self.bold = bold

	def __eq__(self, other):
		if isinstance(other, Style):
			return (
				self.db_id == other.db_id
				and self.background == other.background
				and self.bold == other.bold
				and self.text == other.text
			)
		else:
			return False


class StyledStatus:
	def __init__(self, status: str, style: Style):
		self.status = status
		self.style = style


class StyledPosition:
	def __init__(self, db_id: int, position: int, points: float, style: Style):
		self.db_id = db_id
		self.position = position
		self.points = points
		self.style = style


class LocalisedAbbreviation:
	def __init__(self, status: str, abbr: str):
		self.status = status
		self.abbreviation = abbr
