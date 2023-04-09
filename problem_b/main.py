from __future__ import annotations

from io import StringIO
from pathlib import Path
from rich.console import Console
from rich.columns import Columns
from typer import Typer, Argument, Option

from problem_b.board import Board


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
