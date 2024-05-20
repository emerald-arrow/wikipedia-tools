from eligible_classifications import EligibleClassifications
from manufacturer import Manufacturer
from aliases import DriverList


class ResultRow:
    def __init__(self, drivers: DriverList, category: str, status: str,
                 db_team_id: int, eligible_classifications: EligibleClassifications,
                 manufacturer: Manufacturer | None = None, position: int | None = None,
                 cat_position: int | None = None, result_style: int | None = None) -> None:
        self.drivers = drivers
        self.category = category
        self.status = status
        self.db_team_id = db_team_id
        self.eligible_classifications = eligible_classifications
        self.manufacturer = manufacturer
        self.position = position
        self.cat_position = cat_position
        self.result_style = result_style
