from dataclasses import dataclass


@dataclass
class Seat:
    number: str
    seat_class: int
    row: int
    section: str
    customer_number: int | None = None