from __future__ import annotations

import random

from abc import ABC, abstractmethod
from io import StringIO
from operator import and_
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from typing import Dict, List, Optional, Tuple, Type
from typer import Typer, Argument, Option


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
    def simulate(self, board: Board) -> Tile:
        # TODO: Decouple this, the tile should not depend on the board or be
        #       responsible for incrementing the score
        pass


class Field(Tile):
    def __init__(self, x: int, y: int, age: int = 0) -> None:
        super().__init__(x, y, " ", age)

    @property
    def rich_repr(self) -> str:
        return " "

    def simulate(self, board: Board) -> Tile:
        neighbours = board.get_neighbours(self.x, self.y)
        if sum(isinstance(tile, Flower) for tile in neighbours) >= 3:
            return Flower(self.x, self.y)

        self.age += 1
        return self


class Flower(Tile):
    def __init__(self, x: int, y: int, age: int = 0) -> None:
        super().__init__(x, y, "*", age)

    @property
    def rich_repr(self) -> str:
        return f"[magenta]{self.value}[/magenta]"

    def simulate(self, board: Board) -> Tile:
        neighbours = board.get_neighbours(self.x, self.y)
        if sum(isinstance(tile, Caterpiller) for tile in neighbours) >= 3:
            return Caterpiller(self.x, self.y)

        self.age += 1
        board.score += self.age
        return self


class Caterpiller(Tile):
    def __init__(self, x: int, y: int, age: int = 0) -> None:
        super().__init__(x, y, "~", age)

    @property
    def rich_repr(self) -> str:
        return f"[green]{self.value}[/green]"

    def simulate(self, board: Board) -> Tile:
        neighbours = board.get_neighbours(self.x, self.y)
        if and_(
            any(isinstance(tile, Caterpiller) for tile in neighbours),
            any(isinstance(tile, Flower) for tile in neighbours),
        ):
            self.age += 1
            board.score -= 1
            return self

        # TODO: Too coupled
        board._create_butterfly(self.x, self.y)

        return Field(self.x, self.y)


class Butterfly(Tile):
    def __init__(self, x: int, y: int, age: int = 0) -> None:
        super().__init__(x, y, "B", age)

    @property
    def rich_repr(self) -> str:
        return f"[cyan]{self.value}[/cyan]"

    def simulate(self, board: Board) -> Tile:
        """
        Butterflies are a special case because they move after the simulation
        is
        """
        return self


TILE_VALUE_TYPES_MAP: Dict[str, Type] = {
    " ": Field,
    "*": Flower,
    "~": Caterpiller,
    "B": Butterfly,
}


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
    _butterflies: Dict[Tuple[int, int], Butterfly]

    def __init__(
        self,
        board: List[List[Tile]],
        with_butterflies: bool = False,
    ) -> None:
        height = len(board)
        width = len(board[0])

        assert all(
            len(row) == width for row in board
        ), "Board must be a valid quadrilateral"

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
        # important to how they behave
        self._butterflies = dict()

    def __repr__(self) -> str:
        """
        We define a repr method here so that comparing board states and
        displaying them in the terminal is easier. We ant to be able to quickly
        check if two board states are the same for both tests and finding the
        stopping point for a steady state
        """
        rows = []
        for idx, row in enumerate(self.board):
            str_row = ""
            for tile in row:
                str_repr = str(tile)

                # Add in butterflies
                if tile.position in self._butterflies.keys():
                    str_repr = str(self._butterflies[tile.position])

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
        for idx, row in enumerate(self.board):
            str_row = ""
            for tile in row:
                str_repr = tile.rich_repr

                # Add in butterflies
                if tile.position in self._butterflies.keys():
                    str_repr = self._butterflies[tile.position].rich_repr

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

    def get_neighbours(self, x: int, y: int) -> List[Tile]:
        # get the diagonals, we use a set to deduplicate any points for
        # points at the edge of the board
        points = set(
            [
                (min(x + 1, self.width - 1), y),  # right
                (max(x - 1, 0), y),  # left
                (x, min(y + 1, self.height - 1)),  # up
                (x, max(y - 1, 0)),  # down
                (
                    min(x + 1, self.width - 1),
                    min(y + 1, self.height - 1),
                ),  # right up
                (min(x + 1, self.width - 1), max(y - 1, 0)),  # right down
                (max(x - 1, 0), min(y + 1, self.height - 1)),  # left up
                (max(x - 1, 0), max(y - 1, 0)),  # left down
            ]
        )
        # We need to remove the center point if it is in the set
        points.discard((x, y))

        # Return the tiles
        return [self.board[y][x] for x, y in points]

    def simulate(self) -> None:
        new_board = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

        # Iterate through the existing board and simulate a new step
        for y in range(self.height):
            for x in range(self.width):
                tmp = self.board[y][x]
                new_board[y][x] = tmp.simulate(self)  # type: ignore

        self.board = new_board  # type: ignore

        if self._with_butterflies:
            self._simulate_butterflies()

        self.step_count += 1

    def _create_butterfly(self, x: int, y: int) -> None:
        if not self._with_butterflies:
            return

        # This method is slightly imperfect due to rounding but its close
        # enough that it should not affect the simulation too much
        probability = int(1 / self._butterfly_chance)
        if random.randint(1, probability) == probability:
            self._butterflies[(x, y)] = Butterfly(x, y)

    def _simulate_butterflies(self) -> None:
        # TODO: This method is too coupled, need to address how the board
        #       interacts with Tiles and specifically butterflies
        new_butterflies = dict()
        for position, butterfly in self._butterflies.items():
            x, y = position
            # Check for flower and create Caterpiller if true
            if isinstance(self.board[y][x], Flower):
                self.board[y][x] = Caterpiller(x, y)
                continue

            # Check if it dies
            if 1 >= self._butterfly_mortality > 0:
                mortality = int(1 / self._butterfly_mortality)
                if random.randint(1, mortality) == mortality:
                    continue

            # otherwise move the butterfly
            available_positions = [
                tile.position for tile in self.get_neighbours(x, y)
            ]
            new_position = available_positions[
                random.randint(0, len(available_positions) - 1)
            ]
            new_butterflies[new_position] = butterfly

        self._butterflies = new_butterflies

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


app = Typer()


@app.command("simulate_garden")
def simulate_garden(
    file_path: str = Argument(None),
    generations: int = Argument(10),
    butterflies: bool = Option(
        False, is_flag=True, help="Enable butterflies in the simulation"
    ),
) -> None:
    console = Console()

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError("File does not exist")

    buffer = StringIO(path.read_bytes().decode("utf-8"))
    board = Board.from_file(buffer, with_butterflies=butterflies)
    console.print(f"Simulating Map over {generations} steps:")

    with console.status(
        "[green]Simulating gardens ...[/green]", spinner="dots"
    ):
        columns = Columns(expand=True, padding=1)
        columns.add_renderable(board.rich_panel)

        while board.step_count < generations:
            board.simulate()
            columns.add_renderable(board.rich_panel)

    console.print(columns)


@app.command("simulate_till_steady")
def simulate_till_steady(
    file_path: str = Argument(None),
    butterflies: bool = Option(
        False, is_flag=True, help="Enable butterflies in the simulation"
    ),
) -> None:
    console = Console()

    console.print("Simulating Steady state:")
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError("File does not exist")

    buffer = StringIO(path.read_bytes().decode("utf-8"))
    board = Board.from_file(buffer, with_butterflies=butterflies)

    with console.status(
        "[green]Simulating gardens ...[/green]", spinner="dots"
    ):
        simulation_loops = board.simulate_till_steady()

    console.print(f"Steady state found after {board.step_count} iterations")
    console.print(board.rich_panel)

    if simulation_loops != 1:
        console.print(
            f"Steady state is a loop of {simulation_loops} simulation steps"
        )


if __name__ == "__main__":
    app()
