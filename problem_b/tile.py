from __future__ import annotations

from abc import ABC, abstractmethod
from operator import and_
from typing import Dict, List, Tuple, Type


class Tile(ABC):
    x: int
    y: int
    value: str
    age: int

    def __init__(self, x: int, y: int, value: str, age: int = 0) -> None:
        self.x = x
        self.y = y
        self.value = value
        self.age = age

    def __repr__(self) -> str:
        return self.value

    @property
    def position(self) -> Tuple[int, int]:
        return self.x, self.y

    @property
    @abstractmethod
    def rich_repr(self) -> str:
        pass

    @abstractmethod
    def simulate(self, neighbours: List[Tile]) -> Tuple[Tile, int]:
        pass


class Field(Tile):
    def __init__(self, x: int, y: int, age: int = 0) -> None:
        super().__init__(x, y, " ", age)

    @property
    def rich_repr(self) -> str:
        return " "

    def simulate(self, neighbours: List[Tile]) -> Tuple[Tile, int]:
        if sum(isinstance(tile, Flower) for tile in neighbours) >= 3:
            return Flower(self.x, self.y), 0

        self.age += 1
        return self, 0


class Flower(Tile):
    def __init__(self, x: int, y: int, age: int = 0) -> None:
        super().__init__(x, y, "*", age)

    @property
    def rich_repr(self) -> str:
        return f"[magenta]{self.value}[/magenta]"

    def simulate(self, neighbours: List[Tile]) -> Tuple[Tile, int]:
        if sum(isinstance(tile, Caterpiller) for tile in neighbours) >= 3:
            return Caterpiller(self.x, self.y), 0

        self.age += 1
        return self, self.age


class Caterpiller(Tile):
    def __init__(self, x: int, y: int, age: int = 0) -> None:
        super().__init__(x, y, "~", age)

    @property
    def rich_repr(self) -> str:
        return f"[green]{self.value}[/green]"

    def simulate(self, neighbours: List[Tile]) -> Tuple[Tile, int]:
        if and_(
            any(isinstance(tile, Caterpiller) for tile in neighbours),
            any(isinstance(tile, Flower) for tile in neighbours),
        ):
            self.age += 1
            return self, -1

        # TODO: Too coupled
        # board._create_butterfly(self.x, self.y)

        return Field(self.x, self.y), 0


TILE_VALUE_TYPES_MAP: Dict[str, Type] = {
    " ": Field,
    "*": Flower,
    "~": Caterpiller,
}
