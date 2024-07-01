class Car:
    def __init__(self, codename: str, link: str) -> None:
        self.codename = codename
        self.link = link

    def __repr__(self) -> str:
        return f'{self.codename},{self.link}'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Car):
            return (
                self.codename == other.codename
                and self.link == other.link
            )
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.__repr__())

    def __iter__(self) -> iter:
        return iter([self.codename, self.link])
