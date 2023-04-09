from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

from problem_b.tile import Caterpiller, Flower, Tile
from problem_b.utils import get_adjacent_units, matrix_dimensions


class Butterfly:
    x: int
    y: int
    age: int
    value: str
    mortality: float

    def __init__(
        self, x: int, y: int, *, age: int = 0, mortality: float = 0.1
    ) -> None:
        self.x = x
        self.y = y
        self.age = age
        self.value = "B"
        self.mortality = mortality

    def __repr__(self) -> str:
        return self.value

    @property
    def position(self) -> Tuple[int, int]:
        return (self.x, self.y)

    @property
    def rich_repr(self) -> str:
        return f"[cyan]{self.value}[/cyan]"

    @classmethod
    def create(
        cls,
        *,
        prev_board: List[List[Tile]],
        new_board: List[List[Tile]],
        spawn_probability: float = 0.01,
        mortality: float = 0.1,
    ) -> List[Butterfly]:
        """
        We need to check every tile that turned from Caterpiller to Field to
        see if we need to make a butterfly. This method is a brute force
        approach and could be improved. This feels like there has been an
        incorrect seperation of concerns
        """
        width, height = matrix_dimensions(prev_board)
        butterflies = []
        for y in range(height):
            for x in range(width):
                tile = prev_board[y][x]
                # Skip over everything that isn't a Caterpiller
                if not isinstance(tile, Caterpiller):
                    continue

                # the Caterpiller didn't die so continue
                new_tile = new_board[y][x]
                if isinstance(new_tile, Caterpiller):
                    continue

                assert not isinstance(
                    new_tile, Flower
                ), "This should never happen"

                probability = int(1 / spawn_probability)
                if random.randint(1, probability) == probability:
                    butterflies.append(cls(x, y, mortality=mortality))

        return butterflies

    def move(self, board: List[List[Tile]]) -> Optional[Butterfly]:
        x, y = self.position
        # Check for flower and create Caterpiller if true
        if isinstance(board[y][x], Flower):
            board[y][x] = Caterpiller(x, y)
            return None

        # Check if it dies
        if 1 >= self.mortality > 0:
            mortality = int(1 / self.mortality)
            if random.randint(1, mortality) == mortality:
                return None

        # otherwise move the butterfly
        available_positions = [
            tile.position for tile in get_adjacent_units(x, y, board)
        ]

        self.x, self.y = available_positions[
            random.randint(0, len(available_positions) - 1)
        ]

        return self

    @classmethod
    def simulate(
        cls,
        *,
        butterflies: List[Butterfly],
        board: List[List[Tile]],
    ) -> List[Butterfly]:
        new_butterflies: List[Butterfly] = []
        for butterfly in butterflies:
            updated_butterfly = butterfly.move(board)
            if updated_butterfly:
                new_butterflies.append(updated_butterfly)

        return new_butterflies
