class Style:
	def __init__(self, db_id: int, background: str, bold: bool, text: str | None):
		self.db_id = db_id
		self.background = background
		self.text = text
		self.bold = bold


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
