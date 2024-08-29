from enum import Enum


class AwardedPoints(Enum):
	FULL = 1.00,
	HALF = 0.50

	def __init__(self, multiplier: float):
		self.multiplier = multiplier
