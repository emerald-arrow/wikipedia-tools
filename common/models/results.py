from common.models.classifications import EligibleClassifications
from common.models.manufacturer import Manufacturer
from common.models.driver import DbDriver
from common.models.styles import Style


class ResultRow:
    def __init__(
        self, drivers: list[DbDriver], status: str, db_team_id: int,
        eligible_classifications: EligibleClassifications,
        manufacturer: Manufacturer | None = None,
    ) -> None:
        self.drivers = drivers
        self.status = status
        self.db_team_id = db_team_id
        self.eligible_classifications = eligible_classifications
        self.manufacturer = manufacturer


class RoundResult:
    def __init__(
        self, number: int, session: str, place: int | None, style: Style
    ):
        self.number = number
        self.session = session
        self.place = place
        self.style = style

    def __eq__(self, other):
        if isinstance(other, RoundResult):
            return (
                self.number == other.number
                and self.session == other.session
                and self.place == other.place
                and self.style == other.style
            )
        else:
            return False


class EntityResults:
    def __init__(
        self, db_id: int, link: str, flag: str, points: int, car_no: int | None, results: list[RoundResult] | None = None
    ):
        self.db_id = db_id
        self.link = link
        self.flag = flag
        self.points = points
        self.car_no = car_no
        self.results = results
