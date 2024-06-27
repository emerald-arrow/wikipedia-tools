from common.models.classifications import EligibleClassifications
from common.models.manufacturer import Manufacturer
from common.models.driver import DbDriver


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
