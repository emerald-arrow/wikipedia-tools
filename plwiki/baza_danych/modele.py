type DriverList = list[dict[str, int | str | None]]

class Car:
	def __init__(self, codename: str, link: str) -> None:
		self.codename = codename
		self.link = link
	
	def __repr__(self) -> str:
		return f'{self.codename},{self.link}'

	def __eq__(self, other: object) -> bool:
		if isinstance(other, Car):
			return (
				self.codename == other.codename and
				self.link == other.link
			)
		else:
			return False
	
	def __hash__(self) -> int:
		return hash(self.__repr__())
	
	def __iter__(self) -> iter:
		return iter([self.codename, self.link])

class Classification:
    def __init__(self, id: int, name: str, championship_id: int) -> None:
        self.id = id
        self.name = name
        self.championship_id = championship_id

class Colour:
	def __init__(self, id: int, status: str) -> None:
		self.id = id
		self.status = status

class Driver:
	def __init__(self, codename: str, nationality: str, short_link: str, long_link: str='') -> None:
		self.codename = codename
		self.nationality = nationality
		self.short_link = short_link
		self.long_link = long_link
	
	def __repr__(self) -> str:
		return f'{self.codename},{self.nationality},{self.short_link},{self.long_link}'

	def __eq__(self, other: object) -> bool:
		if isinstance(other, Driver):
			return (
				self.codename == other.codename and
				self.nationality == other.nationality and
				self.short_link == other.short_link and
				self.long_link == other.long_link
			)
		else:
			return False
	
	def __hash__(self) -> int:
		return hash(self.__repr__())
	
	def __iter__(self) -> iter:
		return iter([self.codename, self.nationality, self.short_link, self.long_link])

class EligibleClassifications():
	def __init__(self, driver: Classification | None,
                  manufacturer: Classification | None,
                  team: Classification | None) -> None:
		self.driver = driver
		self.manufacturer = manufacturer
		self.team = team
	
	def __repr__(self) -> str:
		return f'[\n{self.driver}\n{self.manufacturer}\n{self.team}\n]'

class Manufacturer():
	def __init__(self, id: int, codename: str, flag: str) -> None:
		self.id = id
		self.codename = codename
		self.flag = flag

class ResultRow():
	def __init__(self, drivers: DriverList, category: str, status: str,
				 db_team_id: int, eligible_classifications:EligibleClassifications,
				 manufacturer: Manufacturer | None=None, position: int | None=None,
				 cat_position: int | None=None, result_style: int | None=None) -> None:
		self.drivers = drivers
		self.category = category
		self.status = status
		self.db_team_id = db_team_id
		self.eligible_classifications = eligible_classifications
		self.manufacturer = manufacturer
		self.position = position
		self.cat_position = cat_position
		self.result_style = result_style

class Team:
	def __init__(self, codename: str, nationality: str, car_number: str, short_link: str, long_link='') -> None:
		self.codename = codename
		self.nationality = nationality
		self.car_number = car_number
		self.short_link = short_link
		self.long_link = long_link
	
	def __repr__(self) -> str:
		return '%s,%s,%s,%s,%s' % (
			self.codename,
			self.nationality,
			self.car_number,
			self.short_link,
			self.long_link
		)
	
	def __eq__(self, other: object) -> bool:
		if isinstance(other, Team):
			return (
				self.codename == other.codename and
				self.nationality == other.nationality and
				self.car_number == other.car_number and
				self.short_link == other.short_link and
				self.long_link == other.long_link
			)
		else:
			return False
	
	def __hash__(self) -> int:
		return hash(self.__repr__())
	
	def __iter__(self) -> iter:
		return iter([self.codename, self.nationality, self.car_number,
			   self.short_link, self.long_link])