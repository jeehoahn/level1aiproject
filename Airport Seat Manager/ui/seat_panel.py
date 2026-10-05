from PySide6.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QPushButton
)


class SeatButton(QPushButton):

    def __init__(
        self,
        seat,
        customer=None,
        clicked_callback=None
    ):
        super().__init__()

        self.seat = seat
        self.customer = customer
        self.selected = False

        self.setText(
            f"{seat.number}\n-"
        )

        if clicked_callback:
            self.clicked.connect(
                lambda checked=False:
                clicked_callback(self)
            )

        self.update_style()

    def set_selected(self, selected):
        self.selected = selected
        self.update_style()

    def set_customer(self, customer):

        self.customer = customer

        if customer is None:
            self.setText(
                f"{self.seat.number}\n-"
            )
        else:
            self.setText(
                f"{self.seat.number}\n"
                f"{customer.name}"
            )

        self.update_style()

    def update_style(self):
        if self.selected:
            border = "3px solid #000000"
        else:
            border = "1px solid"

        # First
        if self.seat.seat_class == 1:

            if self.selected:
                border = "3px solid #000000"
            else:
                border = "1px solid #D6B656"

            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFF3CD;
                    color: #795548;
                    border: {border};
                    border-radius: 5px;
                    font-size: 9px;
                    font-weight: bold;
                }}

                QPushButton:hover {{
                    background-color: #FFE69C;
                }}
            """)

        # Business
        elif self.seat.seat_class == 2:

            if self.selected:
                border = "3px solid #000000"
            else:
                border = "1px solid #7986CB"

            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #E8EAF6;
                    color: #283593;
                    border: {border};
                    border-radius: 5px;
                    font-size: 9px;
                    font-weight: bold;
                }}

                QPushButton:hover {{
                    background-color: #C5CAE9;
                }}
            """)

        # Premium Economy
        elif self.seat.seat_class == 3:

            if self.selected:
                border = "3px solid #000000"
            else:
                border = "1px solid #4DB6AC"

            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #E0F2F1;
                    color: #00695C;
                    border: {border};
                    border-radius: 5px;
                    font-size: 9px;
                }}

                QPushButton:hover {{
                    background-color: #B2DFDB;
                }}
            """)

        # Economy
        else:

            if self.selected:
                border = "3px solid #000000"
            else:
                border = "1px solid #BDBDBD"

            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #F5F5F5;
                    color: #333333;
                    border: {border};
                    border-radius: 5px;
                    font-size: 9px;
                }}

                QPushButton:hover {{
                    background-color: #E0E0E0;
                }}
            """)
class SeatPanel(QGroupBox):

    def __init__(
        self,
        aircraft,
        seat_selected_callback=None
    ):
        super().__init__("좌석 배치")

        self.aircraft = aircraft

        self.seat_buttons = {}

        self.selected_button = None

        self.seat_selected_callback = (
            seat_selected_callback
        )

        self.create_panel()

    def create_panel(self):

        layout = QGridLayout(self)

        # 패널 내부 여백
        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        # 좌석 사이 간격
        layout.setHorizontalSpacing(4)
        layout.setVerticalSpacing(4)

        # ---------------------------------
        # 각 구역의 최대 좌석 수 계산
        # ---------------------------------

        max_left = self.get_max_section_count("left")
        max_middle = self.get_max_section_count("middle")
        max_right = self.get_max_section_count("right")

        # ---------------------------------
        # 좌석 배치
        # ---------------------------------

        for seat in self.aircraft.seats:

            button = SeatButton(
                seat=seat,
                clicked_callback=self.select_seat
            )

            self.seat_buttons[
                seat.number
            ] = button

            row = seat.row - 1

            section_seats = [
                s
                for s in self.aircraft.seats
                if (
                    s.row == seat.row
                    and s.section == seat.section
                )
            ]

            seat_index = section_seats.index(seat)

            # 좌측
            if seat.section == "left":

                column = seat_index

            # 중간
            elif seat.section == "middle":

                column = (
                    max_left
                    + 1
                    + seat_index
                )

            # 우측
            else:

                column = (
                    max_left
                    + 1
                    + max_middle
                    + 1
                    + seat_index
                )

            layout.addWidget(
                button,
                row,
                column
            )

        # ---------------------------------
        # 좌석 크기 비율
        # ---------------------------------

        total_columns = (
            max_left
            + max_middle
            + max_right
            + 2
        )

        # 좌석이 없는 부분도 일정한 공간을 차지하도록 설정
        for column in range(total_columns):

            # 두 개의 통로
            if (
                column == max_left
                or
                column == max_left + max_middle + 1
            ):

                layout.setColumnStretch(
                    column,
                    1
                )

            else:

                layout.setColumnStretch(
                    column,
                    3
                )

        # 모든 행의 높이를 동일하게
        for row in range(
            self.aircraft.total_rows
        ):

            layout.setRowStretch(
                row,
                1
            )

    # ---------------------------------
    # 특정 구역의 최대 좌석 수
    # ---------------------------------

    def get_max_section_count(
        self,
        section
    ):

        max_count = 0

        for row in range(
            1,
            self.aircraft.total_rows + 1
        ):

            count = len([
                seat
                for seat in self.aircraft.seats
                if (
                    seat.row == row
                    and seat.section == section
                )
            ])

            max_count = max(
                max_count,
                count
            )

        return max_count

    # ---------------------------------
    # 좌석 클릭
    # ---------------------------------

    def select_seat(self, button):

        # 기존에 선택된 좌석 해제
        if self.selected_button is not None:

            self.selected_button.set_selected(
                False
            )

        # 새 좌석 선택
        self.selected_button = button

        self.selected_button.set_selected(
            True
        )

        # 기존 콜백 호출
        if self.seat_selected_callback:

            self.seat_selected_callback(
                button.seat
            )

    # ---------------------------------
    # 좌석 번호로 버튼 가져오기
    # ---------------------------------

    def get_button(
        self,
        seat_number
    ):

        return self.seat_buttons.get(
            seat_number
        )