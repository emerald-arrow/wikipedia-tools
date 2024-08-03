class Driver:
    def __init__(
            self, codename: str = '', nationality: str = '',
            short_link: str = '', long_link: str = '', db_id: int = -1
    ) -> None:
        self.codename = codename
        self.nationality = nationality
        self.short_link = short_link
        self.long_link = long_link
        self.db_id = db_id

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
        return iter([
            self.codename,
            self.nationality,
            self.short_link,
            self.long_link
        ])

    # Returns True if codename, short_link and nationality are empty strings
    def empty_fields(self) -> bool:
        return all([
            len(self.codename) == 0,
            len(self.short_link) == 0,
            len(self.nationality) == 0
        ])
