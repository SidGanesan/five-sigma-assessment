from __future__ import annotations

from typing import Any, List, Tuple, TypeVar

T = TypeVar("T")


def matrix_dimensions(matrix: List[List[Any]]) -> Tuple[int, int]:
    height = len(matrix)
    width = len(matrix[0])

    assert all(
        len(row) == width for row in matrix
    ), "matrix must be a valid quadrilateral"
    return (width, height)


def get_adjacent_units(x: int, y: int, matrix: List[List[T]]) -> List[T]:
    """
    Helper function to get all of the adjacent units in a matrix, including the
    diagonals we use a set to deduplicate any points for points at the edge of
    the matrix
    """
    width, height = matrix_dimensions(matrix)

    points = set(
        [
            (min(x + 1, width - 1), y),  # right
            (max(x - 1, 0), y),  # left
            (x, min(y + 1, height - 1)),  # up
            (x, max(y - 1, 0)),  # down
            (
                min(x + 1, width - 1),
                min(y + 1, height - 1),
            ),  # right up
            (min(x + 1, width - 1), max(y - 1, 0)),  # right down
            (max(x - 1, 0), min(y + 1, height - 1)),  # left up
            (max(x - 1, 0), max(y - 1, 0)),  # left down
        ]
    )
    # We need to remove the center point if it is in the set
    # this can happen because of the max and min used to define
    # the points we are looking for
    points.discard((x, y))

    # Return the tiles
    return [matrix[y][x] for x, y in points]
