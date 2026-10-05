import json
from pathlib import Path

from models.aircraft import Aircraft
from models.seat import Seat


class AircraftService:

    def __init__(self, file_path=None):

        if file_path is None:
            file_path = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "aircraft"
                / "TEST-001.json"
            )

        self.file_path = Path(file_path)

    def load_aircraft(self):

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"항공기 JSON 파일을 찾을 수 없습니다:\n"
                f"{self.file_path}"
            )

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        aircraft_data = data["aircraft"]
        layout_data = data["seat_layout"]

        aircraft_id = aircraft_data["id"]
        aircraft_name = aircraft_data["name"]

        row_count = layout_data["row_count"]
        rows = layout_data["rows"]

        seats = []

        # 좌석 번호에 사용할 알파벳
        seat_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        for row_data in rows:

            row_number = row_data["row"]

            # JSON에 있는 순서 그대로
            sections = [
                ("left", row_data.get("left", [])),
                ("middle", row_data.get("middle", [])),
                ("right", row_data.get("right", []))
            ]

            seat_index = 0

            for section_name, section_data in sections:

                for class_data in section_data:

                    count = class_data["count"]
                    seat_class = class_data["class"]

                    for _ in range(count):

                        if seat_index >= len(seat_letters):
                            raise ValueError(
                                f"{row_number}번 줄의 좌석 수가 "
                                f"26개를 초과했습니다."
                            )

                        seat_number = (
                            f"{row_number}"
                            f"{seat_letters[seat_index]}"
                        )

                        seat = Seat(
                            number=seat_number,
                            seat_class=seat_class,
                            row=row_number,
                            section=section_name
                        )

                        seats.append(seat)

                        seat_index += 1

        # JSON의 row_count와 실제 rows 개수 확인
        if row_count != len(rows):
            raise ValueError(
                f"row_count({row_count})와 "
                f"실제 rows 개수({len(rows)})가 다릅니다."
            )

        return Aircraft(
            id=aircraft_id,
            name=aircraft_name,
            seats=seats
        )

    def get_aircraft_name(self):

        aircraft = self.load_aircraft()

        return aircraft.name