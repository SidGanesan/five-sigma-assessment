"""
At a concert, there are 100 seats numbered 1-100 and 100 tickets also numbered
1-100. Due to social distancing measures, members of the audience are only
allowed in one at a time, in ticket order starting from ticket 1, and must sit
in the seat with the same number as is on their ticket. However the first
member of the audience has had a few too many drinks and sits in a random seat.
Further audience members will sit in the seat on their ticket if it is free,
but if it is taken they will panic and also sit in a random seat

1. Write a function to simulate audience members taking their seats

2. Use monte carlo simulation to measure the probability (from e.g. 1000
simulations) that the person with the last ticket (ticket 100) gets to sit in
their own seat (seat 100).  (The true probability is 0.5 so make sure your
implementation matches up!)

3. For when we have our follow-up discussion/interview: think about the
computational complexity of your implementation (i.e. big O notation). Can you
think of any alternative algorithms that would significantly reduce
computational complexity? No additional code is needed for this step.
"""

import random

# TODO: Threading to improve performance of simulation
# import threading

from rich.console import Console
from rich.progress import track
from typing import Dict, Optional

CONCERT_SIZE = 100
SIMULATION_SIZE = 100_000


class Concert:
    def __init__(self, size: int) -> None:
        if not isinstance(size, int):
            raise TypeError("Please provide an integer size for the concert")

        # create a list of customers and assign them their seats while
        # retaining the order of customers as the key
        self._customers = {val: val for val in range(size)}

        # Initialise the actual seating
        self.seating: Dict[int, Optional[int]] = {
            val: None for val in range(size)
        }
        self._size = size

    def _seat_customer(self, distruption_idx: int) -> None:
        # Assign the random seat for the disruption index
        self._customers[distruption_idx] = random.randint(0, self._size - 1)
        available_seats = set(self.seating.keys())

        for customer, ticket in self._customers.items():
            position = ticket

            if not self.seating[position] is None:
                position = random.choice(tuple(available_seats))

            self.seating[position] = customer
            available_seats.remove(position)

    def _check_last_seat(self) -> bool:
        if any(val is None for val in self.seating.values()):
            raise ValueError("No customers have been seated")

        last_seat, last_customer = list(self.seating.items())[-1]
        return last_seat == last_customer

    def simulate_seating(self, distruption_idx: int = 0) -> bool:
        # TODO: Make this thread safe to improve the performance of multiple
        #       simulations
        assert (
            distruption_idx < self._size
        ), "Must give an index within the size of the concert"

        if any(val is not None for val in self.seating.values()):
            raise NotImplementedError("Can't resimulate")

        self._seat_customer(distruption_idx)
        return self._check_last_seat()


def simulate_concerts() -> None:
    console = Console()
    console.print(
        f"Preparing to simulate {SIMULATION_SIZE} concert"
        f"seatings for {CONCERT_SIZE} customers"
    )

    results = []
    for _ in track(
        range(SIMULATION_SIZE), description="Simulating concerts ..."
    ):
        results.append(Concert(CONCERT_SIZE).simulate_seating())

    true_cases = len([val for val in results if val])
    console.print(f"Probability: {true_cases/SIMULATION_SIZE:.4%}")


if __name__ == "__main__":
    simulate_concerts()
