from dataclasses import dataclass

from models.seat import Seat


@dataclass
class Aircraft:
    id: str
    name: str
    seats: list[Seat]

    @property
    def total_seats(self):
        return len(self.seats)

    @property
    def total_rows(self):
        if not self.seats:
            return 0

        return max(
            seat.row
            for seat in self.seats
        )