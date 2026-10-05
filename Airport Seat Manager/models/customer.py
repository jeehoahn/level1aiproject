from dataclasses import dataclass


@dataclass
class Customer:
    number: int
    name: str
    mileage: int
    membership_days: int
    grade: str = ""