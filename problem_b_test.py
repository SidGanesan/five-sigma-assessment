from io import StringIO
from typing import Tuple

import pytest
from problem_b import Board, Caterpiller, Field, Flower


def test_initialise_map() -> None:
    test_str = "~ ~   *~"
    board = Board.from_file(StringIO(test_str))

    assert board.width == 8
    assert board.height == 1

    assert isinstance(board.board[0][0], Caterpiller)
    assert isinstance(board.board[0][1], Field)
    assert isinstance(board.board[0][2], Caterpiller)
    assert isinstance(board.board[0][3], Field)
    assert isinstance(board.board[0][4], Field)
    assert isinstance(board.board[0][5], Field)
    assert isinstance(board.board[0][6], Flower)
    assert isinstance(board.board[0][7], Caterpiller)


@pytest.mark.parametrize(
    "test_str,expected_instance",
    [
        pytest.param("   \n   \n   ", " ", id="Field"),
        pytest.param("   \n * \n   ", "*", id="Flower"),
        pytest.param("   \n ~ \n   ", "~", id="Caterpiller"),
    ],
)
def test_simulate__board_init(test_str, expected_instance) -> None:
    board = Board.from_file(StringIO(test_str))

    assert board.height == board.width == 3
    assert all(isinstance(tile, Field) for tile in board.board[0])
    assert all(isinstance(tile, Field) for tile in board.board[2])
    assert str(board.board[1][1]) == expected_instance


@pytest.mark.parametrize(
    "test_str,expected_instance",
    [
        pytest.param("   \n   \n   ", "   \n   \n   ", id="field__static"),
        pytest.param(" * \n* *\n * ", " * \n***\n * ", id="field__mutate"),
        pytest.param("   \n * \n   ", "   \n * \n   ", id="flower__static"),
        pytest.param(" ~ \n~*~\n ~ ", " ~ \n~~~\n ~ ", id="flower__mutate"),
        pytest.param(
            "   \n*~~\n   ", "   \n*~ \n   ", id="caterpiller__static"
        ),
        pytest.param(
            "   \n ~ \n   ", "   \n   \n   ", id="caterpiller__mutate"
        ),
    ],
)
def test_simulate__center(test_str: str, expected_instance: str) -> None:
    board = Board.from_file(StringIO(test_str))

    board.simulate()

    assert board.step_count == 1
    assert str(board) == expected_instance


def test_get_neighbours() -> None:
    test_str = "   \n   \n   "
    board = Board.from_file(StringIO(test_str))

    neighbours = board.get_neighbours(1, 1)

    assert len(neighbours) == 8
    assert all(isinstance(tile, Field) for tile in neighbours)


@pytest.mark.parametrize(
    "test_str,position,expected_instance,expected_num",
    [
        pytest.param("*~ \n~**\n ~ ", (1, 0), "~", 5, id="1_0"),
        pytest.param("*~ \n~**\n ~ ", (2, 1), "*", 5, id="2_1"),
        pytest.param("*~ \n~**\n ~ ", (1, 2), "~", 5, id="1_2"),
        pytest.param("*~ \n~**\n ~ ", (0, 1), "~", 5, id="0_1"),
        pytest.param("*~ \n~**\n ~ ", (0, 0), "*", 3, id="0_0"),
        pytest.param("*~ \n~**\n ~ ", (2, 2), " ", 3, id="2_2"),
        pytest.param("*~ \n~**\n ~ ", (0, 2), " ", 3, id="1_2"),
        pytest.param("*~ \n~**\n ~ ", (2, 0), " ", 3, id="0_1"),
    ],
)
def test_get_neighbours__edges(
    test_str: str,
    position: Tuple[int, int],
    expected_instance: str,
    expected_num: int,
) -> None:
    board = Board.from_file(StringIO(test_str))

    x, y = position
    neighbours = board.get_neighbours(x, y)

    assert len(neighbours) == expected_num
    assert str(board.board[y][x]) == expected_instance


def test_spawn_butterflies() -> None:
    test_str = "   \n ~ \n   "
    board = Board.from_file(StringIO(test_str), with_butterflies=True)
    board._butterfly_chance = 1
    board._butterfly_mortality = 0

    board.simulate()
    assert "B" in str(board)

    board.simulate()
    assert "B" in str(board)
