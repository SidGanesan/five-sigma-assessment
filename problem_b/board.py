from __future__ import annotations

from io import StringIO
from rich.panel import Panel
from typing import List, Optional
from problem_b.butterfly import Butterfly

from problem_b.tile import (
    TILE_VALUE_TYPES_MAP,
    Tile,
)
from problem_b.utils import get_adjacent_units, matrix_dimensions


class Board:
    step_count: int
    score: int
    height: int
    width: int
    board: List[List[Tile]]

    # Internal properties for use within the class only
    _simulation_limit: int
    _with_butterflies: bool
    _butterfly_chance: float
    _butterfly_mortality: float
    _butterflies: List[Butterfly]

    def __init__(
        self,
        board: List[List[Tile]],
        with_butterflies: bool = False,
    ) -> None:
        width, height = matrix_dimensions(board)

        self.step_count = 0
        self.score = 0
        self.height = height
        self.width = width
        self.board = board

        self._simulation_limit = 1_000
        self._with_butterflies = with_butterflies

        # Setting the probability here so we can change it for unit testing
        self._butterfly_chance = 0.01
        self._butterfly_mortality = 0.1

        # We simulate butterflys above the tiles as what is below them is
        # important to know how they behave
        self._butterflies = []

    def __repr__(self) -> str:
        """
        We define a repr method here so that comparing board states and
        displaying them in the terminal is easier. We ant to be able to quickly
        check if two board states are the same for both tests and finding the
        stopping point for a steady state
        """
        rows = []
        butterflies = {b.position: b for b in self._butterflies}
        for idx, row in enumerate(self.board):
            str_row = ""
            for tile in row:
                str_repr = str(tile)

                # Add in butterflies
                if tile.position in butterflies.keys():
                    str_repr = str(butterflies[tile.position])

                str_row = str_row + str_repr

            # New line marker for every line except the last
            if idx != self.height - 1:
                str_row = str_row + "\n"

            rows.append(str_row)

        return "".join(rows)

    @property
    def rich_repr(self) -> str:
        """
        The purpose of this property is to make calling the enriched text
        version of the board easy. This is done so that we can print out
        the board quickly and neatly for a user and be able to see what each
        value is
        """
        rows = []
        butterflies = {b.position: b for b in self._butterflies}
        for idx, row in enumerate(self.board):
            str_row = ""
            for tile in row:
                str_repr = tile.rich_repr

                # Add in butterflies
                if tile.position in butterflies.keys():
                    str_repr = butterflies[tile.position].rich_repr

                str_row = str_row + str_repr

            # New line marker for every line except the last
            if idx != self.height - 1:
                str_row = str_row + "\n"

            rows.append(str_row)

        return "".join(rows)

    @property
    def rich_panel(self) -> Panel:
        return Panel(
            self.rich_repr,
            title=f"Board ({self.step_count})",
            subtitle=f"Score:{self.score}",
            border_style="blue",
        )

    @staticmethod
    def _initialise_row(row_str: str, row_num: int = 0) -> List[Tile]:
        row = []
        for idx, char in enumerate(row_str):
            # initialise a tile type for our row
            tile_type = TILE_VALUE_TYPES_MAP.get(char, None)
            if not tile_type:
                continue

            tile = tile_type(idx, row_num)
            row.append(tile)
        return row

    @classmethod
    def from_file(
        cls, buffer: StringIO, *, with_butterflies: bool = False
    ) -> Board:
        board = []
        with buffer as file:
            for idx, row_str in enumerate(file):
                board.append(cls._initialise_row(row_str, idx))

        return cls(board, with_butterflies)

    def simulate(self) -> None:
        new_board: List[List[Optional[Tile]]] = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

        # Iterate through the existing board and simulate a new step
        for y in range(self.height):
            for x in range(self.width):
                tmp = self.board[y][x]
                neighbours = get_adjacent_units(x, y, self.board)
                new_board[y][x], score = tmp.simulate(neighbours)
                self.score += score

        assert all(
            all([tile for tile in row]) for row in new_board
        ), "empty tiles found in the board"

        if self._with_butterflies:
            new_butterflies = Butterfly.create(
                prev_board=self.board,
                new_board=new_board,  # type: ignore
                spawn_probability=self._butterfly_chance,
                mortality=self._butterfly_mortality,
            )
            self._butterflies = Butterfly.simulate(
                butterflies=self._butterflies + new_butterflies,
                board=self.board,
            )

        self.board = new_board  # type: ignore
        self.step_count += 1

    def simulate_till_steady(self) -> int:
        loop = True
        board_str = ""
        count = 0
        previous_sims = {str(self): count}
        while loop and self.step_count < self._simulation_limit:
            self.simulate()
            board_str = str(self)
            if board_str in previous_sims.keys():
                count += 1
                loop = False
            else:
                count += 1
                previous_sims[board_str] = count

        return count - previous_sims[board_str]
