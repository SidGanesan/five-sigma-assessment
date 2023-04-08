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
from typer import Typer, Argument


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

        return Field(self.x, self.y)


class Butterfly(Tile):
    def __init__(self, x: int, y: int, age: int = 0) -> None:
        super().__init__(x, y, "B", age)

    @property
    def rich_repr(self) -> str:
        return f"[cyan]{self.value}[/cyan]"

    def simulate(self, board: Board) -> Tile:
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

    _simulation_limit: int

    def __init__(
        self, board: List[List[Tile]], with_butterflies: bool = False
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

        # We simulate butterflys above the tiles as what is below
        # them is important to how they behave
        self._butterflies = dict()

    def __repr__(self) -> str:
        rows = []
        for idx, row in enumerate(self.board):
            str_row = "".join([str(tile) for tile in row])

            # We need to append a new line delimiter for all
            # but the last line
            if idx != self.height - 1:
                str_row = str_row + "\n"

            rows.append(str_row)

        return "".join(rows)

    @property
    def rich_repr(self) -> str:
        rows = []
        for row in self.board:
            str_row = "".join([tile.rich_repr for tile in row]) + "\n"
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
    def from_file(cls, buffer: StringIO) -> Board:
        board = []
        with buffer as file:
            for idx, row_str in enumerate(file):
                board.append(cls._initialise_row(row_str, idx))

        return cls(board)

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
        self.step_count += 1

    def _simulate_butterflies(self) -> None:
        # butterfly = (
        #     Butterfly(self.x, self.y)
        #     if random.randint(1, 100) == 100
        #     else Field(self.x, self.y)
        # )
        pass

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
    file_path: str = Argument(None), generations: int = Argument(10)
) -> None:
    console = Console()

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError("File does not exist")

    buffer = StringIO(path.read_bytes().decode("utf-8"))
    board = Board.from_file(buffer)
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
def simulate_till_steady(file_path: str = Argument(None)) -> None:
    console = Console()

    console.print("Simulating Steady state:")
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError("File does not exist")

    buffer = StringIO(path.read_bytes().decode("utf-8"))
    board = Board.from_file(buffer)

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
