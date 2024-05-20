from classification import Classification


class EligibleClassifications:
    def __init__(self, driver: Classification | None,
                 manufacturer: Classification | None,
                 team: Classification | None) -> None:
        self.driver = driver
        self.manufacturer = manufacturer
        self.team = team

    def __repr__(self) -> str:
        return f'[\n{self.driver}\n{self.manufacturer}\n{self.team}\n]'
