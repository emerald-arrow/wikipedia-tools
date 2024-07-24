from common.models.classifications import ClassificationScoring


class Manufacturer:
    def __init__(self, db_id: int, codename: str, flag: str) -> None:
        self.db_id = db_id
        self.codename = codename
        self.flag = flag

    def __eq__(self, other):
        if type(other) is type(self):
            return (
                self.db_id == other.db_id
                and self.codename == other.codename
                and self.flag == other.flag
            )


class ManufacturerScoringCars:
    def __init__(self, manufacturer: Manufacturer, classifications: list[ClassificationScoring]):
        self.manufacturer = manufacturer
        self.classifications = [ClassificationScoring(x.name, x.scoring_entities) for x in classifications]

    def __eq__(self, other):
        if type(other) is type(self):
            return self.manufacturer == other.manufacturer
