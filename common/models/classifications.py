class Classification:
    def __init__(self, db_id: int, name: str, championship_id: int, cl_type: str) -> None:
        self.db_id = db_id
        self.name = name
        self.championship_id = championship_id
        self.cl_type = cl_type


class EligibleClassifications:
    def __init__(
            self, driver_cl: Classification | None = None, manufacturer_cl: Classification | None = None,
            team_cl: Classification | None = None, driver_position: int | None = None,
            team_position: int | None = None, manufacturer_position: int | None = None,
            driver_points: float | None = None, team_points: float | None = None,
            manufacturer_points: float | None = None, driver_style_id: int | None = None,
            team_style_id: int | None = None, manufacturer_style_id: int | None = None
    ) -> None:
        self.driver_cl = driver_cl
        self.manufacturer_cl = manufacturer_cl
        self.team_cl = team_cl
        self.driver_position = driver_position
        self.team_position = team_position
        self.manufacturer_position = manufacturer_position
        self.driver_points = driver_points
        self.team_points = team_points
        self.manufacturer_points = manufacturer_points
        self.driver_style_id = driver_style_id
        self.team_style_id = team_style_id
        self.manufacturer_style_id = manufacturer_style_id
