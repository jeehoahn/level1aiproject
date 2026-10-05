from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)


class PassengerSetupDialog(QDialog):

    def __init__(self, max_customers, seat_count, parent=None):

        super().__init__(parent)

        self.max_customers = max_customers
        self.seat_count = seat_count

        self.passenger_count = None

        self.setWindowTitle(
            "항공편 승객 설정"
        )

        self.setFixedSize(
            400,
            220
        )

        self.create_ui()

    def create_ui(self):

        layout = QVBoxLayout(self)

        title = QLabel(
            "이번 비행기의 승객 수를 입력하세요."
        )

        title.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )

        layout.addWidget(title)

        info = QLabel(
            f"해당 항공기 좌석 수: {self.seat_count}석\n"
            f"현재 등록된 고객: {self.max_customers}명"
        )

        layout.addWidget(info)

        # -------------------------
        # 승객 수 입력
        # -------------------------

        input_layout = QHBoxLayout()

        input_label = QLabel(
            "승객 수:"
        )

        self.passenger_input = QLineEdit()

        self.passenger_input.setPlaceholderText(
            "예: 50"
        )

        self.passenger_input.setFixedWidth(
            150
        )

        input_layout.addWidget(
            input_label
        )

        input_layout.addWidget(
            self.passenger_input
        )

        input_layout.addStretch()

        layout.addLayout(
            input_layout
        )

        # -------------------------
        # 버튼
        # -------------------------

        button_layout = QHBoxLayout()

        start_button = QPushButton(
            "배치 시작"
        )

        cancel_button = QPushButton(
            "취소"
        )

        start_button.clicked.connect(
            self.start
        )

        cancel_button.clicked.connect(
            self.reject
        )

        button_layout.addStretch()

        button_layout.addWidget(
            start_button
        )

        button_layout.addWidget(
            cancel_button
        )

        layout.addLayout(
            button_layout
        )

    def start(self):

        text = (
            self.passenger_input
            .text()
            .strip()
        )

        if not text:

            QMessageBox.warning(
                self,
                "입력 오류",
                "승객 수를 입력해주세요."
            )

            return

        try:

            count = int(text)

        except ValueError:

            QMessageBox.warning(
                self,
                "입력 오류",
                "승객 수는 숫자로 입력해주세요."
            )

            return

        if count <= 0:

            QMessageBox.warning(
                self,
                "입력 오류",
                "승객 수는 1명 이상이어야 합니다."
            )

            return

        if count > self.max_customers:

            QMessageBox.warning(
                self,
                "입력 오류",
                (
                    f"현재 등록된 고객은 "
                    f"{self.max_customers}명입니다."
                )
            )

            return

        self.passenger_count = count

        self.accept()

    def get_passenger_count(self):

        return self.passenger_count
