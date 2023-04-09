import pytest
from .main import Concert


@pytest.mark.parametrize("size", [(5), (10), (15)])
def test_simulate_concert__happy_path(size):
    concert = Concert(size=size)

    assert len(concert._customers) == size

    concert.simulate_seating()

    assert all(val is not None for val in concert.seating.values())
    assert set(concert.seating.keys()) == set(range(size))
    assert set(concert.seating.values()) == set(range(size))


def test_simulate_concert__big():
    size = 1_000
    concert = Concert(size=size)

    assert len(concert._customers) == size

    concert.simulate_seating()

    assert all(val is not None for val in concert.seating.values())
    assert set(concert.seating.keys()) == set(range(size))
    assert set(concert.seating.values()) == set(range(size))
