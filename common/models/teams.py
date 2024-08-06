class Team:
    def __init__(self, codename: str = '', nationality: str = '', car_number: str = '',
                 short_link: str = '', long_link: str = '', db_id: int | None = None) -> None:
        self.codename = codename
        self.nationality = nationality
        self.car_number = car_number
        self.short_link = short_link
        self.long_link = long_link
        self.db_id = db_id

    def __repr__(self) -> str:
        return '%s,%s,%s,%s,%s,%s' % (
            self.codename,
            self.nationality,
            self.car_number,
            self.short_link,
            self.long_link,
            self.db_id
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

    # Returns True if codename, nationality, car_number and short_link are empty strings
    def empty_fields(self) -> bool:
        return all([
            len(self.codename) == 0,
            len(self.nationality) == 0,
            len(self.car_number) == 0,
            len(self.short_link) == 0
        ])


class TeamEligibility:
    def __init__(self, team: Team | None = None, eligibility: bool | None = None):
        self.team = team
        self.eligibility = eligibility
