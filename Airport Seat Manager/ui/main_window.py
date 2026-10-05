from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QDialog,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
    QInputDialog,
    QDialog,
    QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime

from services.customer_service import CustomerService
from services.aircraft_service import AircraftService
from services.passenger_service import PassengerService
from ui.seat_panel import SeatPanel
from models.priority_formula import PriorityFormula
from ui.priority_formula_dialog import PriorityFormulaDialog
from services.priority_service import PriorityService

import random
from datetime import datetime

class NumericTableWidgetItem(QTableWidgetItem):

    def __lt__(
        self,
        other
    ):

        return (
            self.data(Qt.UserRole)
            <
            other.data(Qt.UserRole)
        )

class CustomerSearchDialog(QDialog):

    def __init__(
        self,
        customers,
        boarded_passengers,
        waiting_passengers,
        parent=None
    ):

        super().__init__(parent)

        self.setWindowTitle(
            "전체 고객 검색"
        )

        self.resize(
            850,
            600
        )

        self.customers = customers
        self.boarded_passengers = boarded_passengers
        self.waiting_passengers = waiting_passengers

        self.selected_customer = None
        self.waiting_changed = False

        # =========================
        # 전체 레이아웃
        # =========================

        layout = QVBoxLayout(
            self
        )

        # =========================
        # 검색
        # =========================

        search_layout = QHBoxLayout()

        search_label = QLabel(
            "검색:"
        )

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "이름 검색"
        )

        search_button = QPushButton(
            "검색"
        )

        search_button.clicked.connect(
            self.search_customers
        )

        search_layout.addWidget(
            search_label
        )

        search_layout.addWidget(
            self.search_input
        )

        search_layout.addWidget(
            search_button
        )

        layout.addLayout(
            search_layout
        )

        # =========================
        # 고객 리스트
        # =========================

        self.table = QTableWidget()

        self.table.setColumnCount(
            4
        )

        self.table.setHorizontalHeaderLabels([
            "이름",
            "마일리지",
            "가입경과일",
            "상태"
        ])

        # 헤더 클릭으로 정렬
        self.table.setSortingEnabled(
            True
        )

        # 한 번에 한 명 선택
        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.table.itemSelectionChanged.connect(
            self.select_customer
        )

        layout.addWidget(
            self.table
        )

        # =========================
        # 하단 고객 정보
        # =========================

        info_group = QGroupBox(
            "고객 정보"
        )

        info_layout = QVBoxLayout(
            info_group
        )

        info_layout.setContentsMargins(
            10, 10, 10, 10
        )

        self.info_label = QLabel(
            "고객을 선택해주세요."
        )

        self.info_label.setAlignment(
            Qt.AlignLeft | Qt.AlignTop
        )

        self.info_label.setWordWrap(
            True
        )

        info_layout.addWidget(
            self.info_label
        )

        self.waiting_button = QPushButton(
            "예약 대기"
        )

        self.waiting_button.setEnabled(
            False
        )

        self.waiting_button.clicked.connect(
            self.add_to_waiting
        )

        info_layout.addWidget(
            self.waiting_button
        )

        layout.addWidget(
            info_group
        )

        # =========================
        # 닫기
        # =========================

        close_button = QPushButton(
            "닫기"
        )

        close_button.clicked.connect(
            self.accept
        )

        layout.addWidget(
            close_button
        )

        # =========================
        # 최초 표시
        # =========================

        self.show_customers(
            self.customers
        )

    # =================================
    # 고객 상태
    # =================================

    def get_customer_status(
        self,
        customer
    ):

        for boarded in self.boarded_passengers:

            if boarded.number == customer.number:
                return "탑승"

        for waiting in self.waiting_passengers:

            if waiting.number == customer.number:
                return "대기"

        return "미예약"

    # =================================
    # 고객 목록 표시
    # =================================

    def show_customers(
        self,
        customers
    ):

        self.table.setSortingEnabled(
            False
        )

        self.table.setRowCount(
            len(customers)
        )

        for row, customer in enumerate(
            customers
        ):

            name_item = QTableWidgetItem(
                customer.name
            )

            mileage_item = QTableWidgetItem(
                f"{customer.mileage:,}"
            )

            membership_item = QTableWidgetItem(
                f"{customer.membership_days:,}"
            )

            status_item = QTableWidgetItem(
                self.get_customer_status(
                    customer
                )
            )

            # -------------------------
            # 숫자 정렬용 데이터
            # -------------------------

            mileage_item.setData(
                Qt.UserRole,
                customer.mileage
            )

            membership_item.setData(
                Qt.UserRole,
                customer.membership_days
            )

            # -------------------------
            # 고객 번호는 숨겨진 데이터로 저장
            # -------------------------

            name_item.setData(
                Qt.UserRole + 1,
                customer.number
            )

            self.table.setItem(
                row,
                0,
                name_item
            )

            self.table.setItem(
                row,
                1,
                mileage_item
            )

            self.table.setItem(
                row,
                2,
                membership_item
            )

            self.table.setItem(
                row,
                3,
                status_item
            )

        self.table.resizeColumnsToContents()

        self.table.setSortingEnabled(
            True
        )

    # =================================
    # 검색
    # =================================

    def search_customers(self):

        keyword = (
            self.search_input
            .text()
            .strip()
        )

        if not keyword:

            self.show_customers(
                self.customers
            )

            return

        result = []

        for customer in self.customers:

            if (
                keyword in customer.name
                or keyword in str(customer.number)
            ):

                result.append(
                    customer
                )

        self.show_customers(
            result
        )

    # =================================
    # 고객 선택
    # =================================

    def select_customer(self):

        row = (
            self.table.currentRow()
        )

        if row < 0:
            return

        name_item = (
            self.table.item(
                row,
                0
            )
        )

        if name_item is None:
            return

        customer_number = name_item.data(
            Qt.UserRole + 1
        )

        if customer_number is None:
            return

        customer = None

        for item in self.customers:

            if item.number == customer_number:

                customer = item
                break

        if customer is None:
            return

        self.selected_customer = customer

        status = self.get_customer_status(
            customer
        )

        self.info_label.setText(
            f"""접수번호: {customer.number}\n이름: {customer.name}

        마일리지: {customer.mileage:,}

        가입경과일: {customer.membership_days:,}일

        상태: {status}"""
        )

        if status == "미예약":

            self.waiting_button.setEnabled(
                True
            )

            self.waiting_button.setText(
                "예약 대기"
            )

        else:

            self.waiting_button.setEnabled(
                False
            )

            self.waiting_button.setText(
                f"{status} 중"
            )

    # =================================
    # 예약 대기
    # =================================

    def add_to_waiting(self):

        if self.selected_customer is None:
            return

        customer = self.selected_customer

        # 이미 탑승한 고객인지 확인
        for boarded in self.boarded_passengers:

            if boarded.number == customer.number:

                QMessageBox.information(
                    self,
                    "알림",
                    "이미 탑승 승객입니다."
                )

                return

        # 이미 대기자인지 확인
        for waiting in self.waiting_passengers:

            if waiting.number == customer.number:

                QMessageBox.information(
                    self,
                    "알림",
                    "이미 예약 대기자입니다."
                )

                return

        reply = QMessageBox.question(
            self,
            "예약 대기",
            f"{customer.name} 고객을 예약 대기자 목록에 추가하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # 대기자 추가
        self.waiting_passengers.append(
            customer
        )

        # 메인 화면에서 갱신하도록 표시
        self.waiting_changed = True

        QMessageBox.information(
            self,
            "예약 대기",
            f"{customer.name} 고객이 예약 대기자 목록에 추가되었습니다."
        )

        # 검색창 내부 상태도 즉시 갱신
        self.show_customers(
            self.customers
        )

        # 추가된 고객 다시 선택
        for row in range(
            self.table.rowCount()
        ):

            item = self.table.item(
                row,
                0
            )

            if item is None:
                continue

            number = item.data(
                Qt.UserRole + 1
            )

            if number == customer.number:

                self.table.selectRow(
                    row
                )

                break

class SortableTableWidgetItem(QTableWidgetItem):

    SORT_ROLE = Qt.UserRole + 1

    def __init__(self, text, sort_value=None):
        super().__init__(text)

        if sort_value is not None:
            self.setData(
                self.SORT_ROLE,
                sort_value
            )

    def __lt__(self, other):

        self_value = self.data(
            self.SORT_ROLE
        )

        other_value = other.data(
            self.SORT_ROLE
        )

        if (
            self_value is not None
            and other_value is not None
        ):
            try:
                return self_value < other_value
            except TypeError:
                pass

        return super().__lt__(other)

    
class MainWindow(QMainWindow):

    def __init__(
        self,
        aircraft=None,
        boarded_passengers=None,
        waiting_passengers=None
    ):

        super().__init__()

        self.setWindowTitle(
            "항공사 좌석 배정 시스템"
        )

        self.resize(1500, 900)

        # -------------------------
        # 데이터
        # -------------------------

        self.customer_service = (
            CustomerService()
        )

        self.aircraft_service = (
            AircraftService()
        )

        self.customers = (
            self.customer_service
            .get_all_customers()
        )

        self.passenger_service = (
            PassengerService(
                self.customer_service
            )
        )
        self.boarded_passengers = (
            boarded_passengers or []
        )

        self.waiting_passengers = (
            waiting_passengers or []
        )

        try:
            if aircraft is None:
                self.aircraft = (
                    self.aircraft_service
                    .load_aircraft()
                )
            else:
                self.aircraft = aircraft

        except Exception as e:

            QMessageBox.critical(
                self,
                "항공기 오류",
                str(e)
            )

            raise

        self.selected_customer = None
        self.selected_seat = None

        self.priority_service = (
            PriorityService()
        )

        self.priority_formula = (
            PriorityFormula()
        )
        
        self.priority_formula = (
                    PriorityFormula()
                )

        # -------------------------
        # UI
        # -------------------------

        self.create_ui()

        self.update_seat_panel()

        self.update_passenger_table()

        self.update_waiting_table(
            self.waiting_passengers
        )
        self.update_status_info()

    def create_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QVBoxLayout(
            central
        )

        # =========================
        # 상단
        # =========================

        top_layout = QHBoxLayout()

        title = QLabel(
            "KE123"
        )

        title.setFont(
            QFont("", 16, QFont.Bold)
        )

        priority_button = QPushButton(
            "우선순위식 변경"
        )

        priority_button.clicked.connect(
            self.open_priority_formula
        )

        customer_search_button = QPushButton(
            "전체 고객 검색"
        )

        customer_search_button.clicked.connect(
            self.open_customer_search
        )

        top_layout.addWidget(title)

        top_layout.addStretch()

        top_layout.addWidget(
            customer_search_button
        )
        top_layout.addWidget(
            priority_button
        )

        main_layout.addLayout(
            top_layout
        )

        # =========================
        # 현황 정보
        # =========================

        status_group = QGroupBox(
            "비행 현황"
        )

        status_layout = QHBoxLayout(
            status_group
        )

        self.boarded_count_label = QLabel(
            "탑승자: 0명"
        )

        self.waiting_count_label = QLabel(
            "대기자: 0명"
        )

        self.total_seat_label = QLabel(
            "전체 좌석: 0석"
        )

        self.remaining_seat_label = QLabel(
            "남은 좌석: 0석"
        )

        self.first_class_label = QLabel(
            "First: 0 / 0"
        )

        self.business_class_label = QLabel(
            "Business: 0 / 0"
        )

        self.premium_class_label = QLabel(
            "Premium: 0 / 0"
        )

        self.economy_class_label = QLabel(
            "Economy: 0 / 0"
        )

        status_layout.addWidget(
            self.boarded_count_label
        )

        status_layout.addWidget(
            self.waiting_count_label
        )

        status_layout.addWidget(
            self.total_seat_label
        )

        status_layout.addWidget(
            self.remaining_seat_label
        )

        status_layout.addStretch()

        status_layout.addWidget(
            self.first_class_label
        )

        status_layout.addWidget(
            self.business_class_label
        )

        status_layout.addWidget(
            self.premium_class_label
        )

        status_layout.addWidget(
            self.economy_class_label
        )

        main_layout.addWidget(
            status_group
        )

        # =========================
        # 고객 통계
        # =========================
    
        statistics_group = QGroupBox(
            "고객 통계"
        )

        statistics_layout = QHBoxLayout(
            statistics_group
        )

        statistics_layout.setSpacing(10)

        # -------------------------
        # 탑승자 통계
        # -------------------------

        boarded_statistics_group = QGroupBox(
            "탑승 승객"
        )

        boarded_statistics_layout = QGridLayout(
            boarded_statistics_group
        )

        boarded_statistics_layout.setHorizontalSpacing(15)
        boarded_statistics_layout.setVerticalSpacing(3)

        self.boarded_average_mileage_label = QLabel(
            "평균 마일리지: 0"
        )

        self.boarded_max_mileage_label = QLabel(
            "최고 마일리지: 0"
        )

        self.boarded_min_mileage_label = QLabel(
            "최저 마일리지: 0"
        )

        self.boarded_average_membership_label = QLabel(
            "평균 가입기간: 0일"
        )

        self.boarded_max_membership_label = QLabel(
            "최장 가입기간: 0일"
        )

        self.boarded_grade_label = QLabel(
            "등급별 고객: 없음"
        )

        # 3열 × 2행
        boarded_statistics_layout.addWidget(
            self.boarded_average_mileage_label,
            0,
            0
        )

        boarded_statistics_layout.addWidget(
            self.boarded_max_mileage_label,
            0,
            1
        )

        boarded_statistics_layout.addWidget(
            self.boarded_min_mileage_label,
            0,
            2
        )

        boarded_statistics_layout.addWidget(
            self.boarded_average_membership_label,
            1,
            0
        )

        boarded_statistics_layout.addWidget(
            self.boarded_max_membership_label,
            1,
            1
        )

        boarded_statistics_layout.addWidget(
            self.boarded_grade_label,
            1,
            2
        )


        # -------------------------
        # 대기자 통계
        # -------------------------

        waiting_statistics_group = QGroupBox(
            "예약 대기자"
        )

        waiting_statistics_layout = QGridLayout(
            waiting_statistics_group
        )

        waiting_statistics_layout.setHorizontalSpacing(15)
        waiting_statistics_layout.setVerticalSpacing(3)

        self.waiting_average_mileage_label = QLabel(
            "평균 마일리지: 0"
        )

        self.waiting_max_mileage_label = QLabel(
            "최고 마일리지: 0"
        )

        self.waiting_min_mileage_label = QLabel(
            "최저 마일리지: 0"
        )

        self.waiting_average_membership_label = QLabel(
            "평균 가입기간: 0일"
        )

        self.waiting_max_membership_label = QLabel(
            "최장 가입기간: 0일"
        )

        self.waiting_grade_label = QLabel(
            "등급별 고객: 없음"
        )

        # 3열 × 2행
        waiting_statistics_layout.addWidget(
            self.waiting_average_mileage_label,
            0,
            0
        )

        waiting_statistics_layout.addWidget(
            self.waiting_max_mileage_label,
            0,
            1
        )

        waiting_statistics_layout.addWidget(
            self.waiting_min_mileage_label,
            0,
            2
        )

        waiting_statistics_layout.addWidget(
            self.waiting_average_membership_label,
            1,
            0
        )

        waiting_statistics_layout.addWidget(
            self.waiting_max_membership_label,
            1,
            1
        )

        waiting_statistics_layout.addWidget(
            self.waiting_grade_label,
            1,
            2
        )


        # -------------------------
        # 전체 통계 영역에 추가
        # -------------------------

        statistics_layout.addWidget(
            boarded_statistics_group
        )

        statistics_layout.addWidget(
            waiting_statistics_group
        )

        main_layout.addWidget(
            statistics_group
        )

        # =========================
        # 가운데
        # =========================

        center_layout = QHBoxLayout()

        # 좌석
        self.seat_panel = SeatPanel(
            self.aircraft,
            self.select_seat
        )

        center_layout.addWidget(
            self.seat_panel,
            4
        )

        # 승객
        passenger_group = QGroupBox(
            "탑승 승객"
        )

        passenger_layout = QVBoxLayout(
            passenger_group
        )

        self.passenger_search = QLineEdit()
        self.passenger_search.setPlaceholderText(
            "이름 검색"
        )

        self.passenger_search.textChanged.connect(
            self.search_passengers
        )

        passenger_layout.addWidget(
            self.passenger_search
        )

        passenger_filter_layout = QHBoxLayout()

        self.passenger_min_mileage = QLineEdit()
        self.passenger_min_mileage.setPlaceholderText(
            "최소 마일리지"
        )

        self.passenger_max_mileage = QLineEdit()
        self.passenger_max_mileage.setPlaceholderText(
            "최대 마일리지"
        )

        passenger_filter_layout.addWidget(
            self.passenger_min_mileage
        )

        passenger_filter_layout.addWidget(
            self.passenger_max_mileage
        )

        passenger_layout.addLayout(
            passenger_filter_layout
        )

        self.passenger_min_mileage.textChanged.connect(
            self.search_passengers
        )

        self.passenger_max_mileage.textChanged.connect(
            self.search_passengers
        )

        self.passenger_table = QTableWidget()

        self.passenger_table.setSortingEnabled(True)

        self.passenger_table.setColumnCount(6)

        self.passenger_table.setHorizontalHeaderLabels([
            "좌석",
            "등급",
            "이름",
            "마일리지",
            "가입일",
            "고객등급"
        ])
        self.passenger_table.itemSelectionChanged.connect(
            self.select_passenger_customer
        )

        passenger_layout.addWidget(
            self.passenger_table
        )

        center_layout.addWidget(
            passenger_group,
            2
        )
        self.passenger_table.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        self.passenger_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.passenger_table.setSortingEnabled(True)

        # 대기자
        waiting_group = QGroupBox(
            "예약 대기자"
        )

        waiting_layout = QVBoxLayout(
            waiting_group
        )

        self.waiting_search = QLineEdit()

        self.waiting_search.setPlaceholderText(
            "이름 검색"
        )

        self.waiting_search.textChanged.connect(
            self.search_waiting
        )

        waiting_layout.addWidget(
            self.waiting_search
        )

        waiting_filter_layout = QHBoxLayout()

        self.waiting_min_mileage = QLineEdit()
        self.waiting_min_mileage.setPlaceholderText(
            "최소 마일리지"
        )

        self.waiting_max_mileage = QLineEdit()
        self.waiting_max_mileage.setPlaceholderText(
            "최대 마일리지"
        )

        waiting_filter_layout.addWidget(
            self.waiting_min_mileage
        )

        waiting_filter_layout.addWidget(
            self.waiting_max_mileage
        )

        waiting_layout.addLayout(
            waiting_filter_layout
        )

        self.waiting_min_mileage.textChanged.connect(
            self.search_waiting
        )

        self.waiting_max_mileage.textChanged.connect(
            self.search_waiting
        )

        self.waiting_table = QTableWidget()
    

        self.waiting_table.setSortingEnabled(True)

        self.waiting_table.setColumnCount(5)

        self.waiting_table.setHorizontalHeaderLabels([
            "접수번호",
            "이름",
            "마일리지",
            "가입일",
            "고객등급"
        ])

        self.waiting_table.itemSelectionChanged.connect(
            self.select_waiting_customer
        )

        waiting_layout.addWidget(
            self.waiting_table
        )

        center_layout.addWidget(
            waiting_group,
            2
        )

        self.waiting_table.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )

        self.waiting_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.waiting_table.setSortingEnabled(True)

        # 고객 정보
        customer_group = QGroupBox(
            "고객 정보"
        )

        customer_layout = QVBoxLayout(
            customer_group
        )

        self.customer_info = QLabel(
            "고객을 선택해주세요."
        )

        self.customer_info.setAlignment(
            Qt.AlignLeft | Qt.AlignTop
        )

        self.customer_info.setWordWrap(
            True
        )

        customer_layout.addWidget(
            self.customer_info
        )

        assign_button = QPushButton(
            "좌석 배정"
        )

        exclude_button = QPushButton(
            "제외"
        )
        random_assign_button = QPushButton(
            "랜덤 좌석 배정"
        )

        assign_button.clicked.connect(
            self.assign_selected_customer
        )

        exclude_button.clicked.connect(
            self.exclude_selected_customer
        )

        random_assign_button.clicked.connect(
            self.random_assign_selected_customers
        )

        customer_layout.addWidget(
            assign_button
        )

        customer_layout.addWidget(
            exclude_button
        )
        customer_layout.addWidget(
            random_assign_button
        )

        customer_layout.addStretch()

        center_layout.addWidget(
            customer_group,
            1
        )

        main_layout.addLayout(
            center_layout
        )

    # =================================
    # 좌석
    # =================================

    def select_seat(self, seat):

        self.selected_seat = seat

        seat_class_names = {
            1: "First",
            2: "Business",
            3: "Premium",
            4: "Economy"
        }

        seat_class_name = seat_class_names.get(
            seat.seat_class,
            "알 수 없음"
        )

        # 좌석에 배정된 고객 찾기
        customer = None

        if seat.customer_number is not None:

            for passenger in self.boarded_passengers:

                if (
                    passenger.number
                    == seat.customer_number
                ):
                    customer = passenger
                    break

        if customer is not None:
            self.selected_customer = customer
        else:
            self.selected_customer = None

        # 고객이 없는 좌석
        if customer is None:

            self.customer_info.setText(
                f"""좌석: {seat.number}

등급: {seat_class_name}

줄: {seat.row}

구역: {seat.section}

고객: 없음""")

            return

        # 고객이 있는 좌석
        self.customer_info.setText(
            f"""
            접수번호: {customer.number}

            이름: {customer.name}

            마일리지: {customer.mileage:,}

            가입경과일:
            {customer.membership_days:,}일

            고객 등급: {customer.grade}

            상태: 탑승 승객

            좌석: {seat.number}

            좌석 등급: {seat_class_name}

            줄: {seat.row}

            구역: {seat.section}
            """
        )

    def update_waiting_table(self, customers):

        self.current_waiting_customers = customers

        self.waiting_table.setSortingEnabled(False)

        preview = (
            self.priority_service
            .calculate_preview(
                customers,
                self.priority_formula
            )
        )

        self.waiting_table.setRowCount(len(preview))
        self.waiting_table.setColumnCount(6)

        self.waiting_table.setHorizontalHeaderLabels([
            "우선순위",
            "접수번호",
            "이름",
            "마일리지",
            "가입일",
            "고객등급"
        ])

        for row, item in enumerate(preview):

            customer = item["customer"]
            A = item["A"]

            # =========================
            # 우선순위 = 정렬된 순번
            # =========================

            priority_item = SortableTableWidgetItem(
                str(row + 1),
                row + 1
            )

            priority_item.setData(
                Qt.UserRole,
                row + 1
            )

            # =========================
            # 접수번호 = 원래 대기 순서 A
            # =========================

            number_item = SortableTableWidgetItem(
                str(A),
                A
            )

            # 실제 고객 고유번호 저장
            number_item.setData(
                Qt.UserRole,
                customer.number
            )

            name_item = QTableWidgetItem(
                customer.name
            )

            mileage_item = SortableTableWidgetItem(
                f"{customer.mileage:,}",
                customer.mileage
            )

            membership_item = SortableTableWidgetItem(
                f"{customer.membership_days:,}",
                customer.membership_days
            )

            grade_item = QTableWidgetItem(
                customer.grade
            )

            items = [
                priority_item,
                number_item,
                name_item,
                mileage_item,
                membership_item,
                grade_item
            ]

            for column, item_widget in enumerate(items):
                self.waiting_table.setItem(
                    row,
                    column,
                    item_widget
                )

        self.waiting_table.resizeColumnsToContents()

        self.waiting_table.setSortingEnabled(True)

        # 우선순위 순으로 정렬
        self.waiting_table.sortItems(
            0,
            Qt.AscendingOrder
        )

    def search_waiting(self):

        keyword = (
            self.waiting_search
            .text()
            .strip()
        )

        min_text = (
            self.waiting_min_mileage
            .text()
            .strip()
        )

        max_text = (
            self.waiting_max_mileage
            .text()
            .strip()
        )

        try:
            min_mileage = (
                int(min_text)
                if min_text
                else None
            )
        except ValueError:
            min_mileage = None

        try:
            max_mileage = (
                int(max_text)
                if max_text
                else None
            )
        except ValueError:
            max_mileage = None

        result = []

        for customer in self.waiting_passengers:

            if keyword:
                if not (
                    keyword in customer.name
                    or keyword == str(customer.number)
                ):
                    continue

            if (
                min_mileage is not None
                and customer.mileage < min_mileage
            ):
                continue

            if (
                max_mileage is not None
                and customer.mileage > max_mileage
            ):
                continue

            result.append(customer)

        self.update_waiting_table(result)
        self.waiting_table.resizeColumnsToContents()

    def select_waiting_customer(self):

        self.passenger_table.blockSignals(True)

        self.passenger_table.clearSelection()

        self.passenger_table.blockSignals(False)

        row = self.waiting_table.currentRow()

        if row < 0:
            return

        number_item = self.waiting_table.item(
            row,
            1
        )

        if number_item is None:
            return

        customer_number = number_item.data(
            Qt.UserRole
        )

        if customer_number is None:
            return

        customer = None

        for waiting_customer in self.current_waiting_customers:

            if waiting_customer.number == customer_number:

                customer = waiting_customer

                break

        if customer is None:
            return

        self.selected_customer = customer

        # 현재 화면에서 표시되고 있는 접수번호
        display_receipt_number = number_item.text()

        self.customer_info.setText(
            f"""
                접수번호: {display_receipt_number}

                이름: {customer.name}

                마일리지: {customer.mileage:,}

                가입경과일:
                {customer.membership_days:,}일

                고객 등급 : {customer.grade}

                상태: 대기 중

                좌석: 미배정

                패널티: 없음
                """
        )
    def select_passenger_customer(self):

        # 대기자 리스트 선택 해제
        self.waiting_table.blockSignals(True)
        self.waiting_table.clearSelection()
        self.waiting_table.blockSignals(False)

        row = self.passenger_table.currentRow()

        if row < 0:
            return

        item = self.passenger_table.item(
            row,
            0
        )

        if item is None:
            return

        number = item.data(
            Qt.UserRole
        )

        if number is None:
            return

        customer = (
            self.customer_service
            .find_by_number(number)
        )

        if customer is None:
            return

        assigned_seat = None

        for seat in self.aircraft.seats:

            if seat.customer_number == customer.number:
                assigned_seat = seat
                break

        self.selected_customer = customer

        self.customer_info.setText(
            f"""
                접수번호: {row + 1}

                이름: {customer.name}

                마일리지: {customer.mileage:,}

                가입경과일:
                {customer.membership_days:,}일

                고객 등급 : {customer.grade}

                상태: 탑승

                좌석: {assigned_seat.number if assigned_seat else "미배정"}

                패널티: 없음
            """
        )

        self.waiting_table.blockSignals(True)
        self.waiting_table.clearSelection()
        self.waiting_table.blockSignals(False)

        row = self.passenger_table.currentRow()

        if row < 0:
            return

        item = self.passenger_table.item(
            row,
            2
        )

        if item is None:
            return

        try:
            number = int(item.text())
        except ValueError:
            return

        customer = (
            self.customer_service
            .find_by_number(number)
        )

        if customer is None:
            return

        assigned_seat = None

        for seat in self.aircraft.seats:

            if seat.customer_number == customer.number:
                assigned_seat = seat
                break

        self.selected_customer = customer

        self.customer_info.setText(
            f"""
                접수번호: {customer.number}

                이름: {customer.name}

                마일리지: {customer.mileage:,}

                가입경과일:
                {customer.membership_days:,}일

                고객 등급 : {customer.grade}

                상태: 탑승

                좌석: {assigned_seat.number if assigned_seat else "미배정"}

                패널티: 없음
            """
        )

    # =================================
    # 좌석 배정
    # =================================

    def assign_selected_customer(self):

        if self.selected_customer is None:

            QMessageBox.warning(
                self,
                "알림",
                "고객을 먼저 선택해주세요."
            )

            return

        if self.selected_seat is None:

            QMessageBox.warning(
                self,
                "알림",
                "좌석을 먼저 선택해주세요."
            )

            return

        # 이미 사람이 앉아있는 좌석인지 확인
        if self.selected_seat.customer_number is not None:

            QMessageBox.warning(
                self,
                "알림",
                "이미 배정된 좌석입니다."
            )

            return

        # 대기자만 좌석 배정 가능
        if self.selected_customer not in self.waiting_passengers:

            QMessageBox.warning(
                self,
                "알림",
                "예약 대기자만 좌석을 배정할 수 있습니다."
            )

            return

        # 좌석 배정 확인
        reply = QMessageBox.question(
            self,
            "좌석 배정 확인",
            (
                f"{self.selected_customer.name} 고객을 "
                f"{self.selected_seat.number} 좌석에 "
                f"배정하시겠습니까?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # 좌석에 고객 번호 저장
        self.selected_seat.customer_number = (
            self.selected_customer.number
        )

        # 좌석 버튼에 고객 표시
        seat_button = (
            self.seat_panel.get_button(
                self.selected_seat.number
            )
        )

        if seat_button is not None:

            seat_button.set_customer(
                self.selected_customer
            )

        # 대기자 → 탑승자로 이동
        self.waiting_passengers.remove(
            self.selected_customer
        )

        self.boarded_passengers.append(
            self.selected_customer
        )

        # 화면 갱신
        self.update_waiting_table(
            self.waiting_passengers
        )

        self.update_passenger_table()

        # 고객 정보 갱신
        self.customer_info.setText(
            f"""
            접수번호: {self.selected_customer.number}

            이름: {self.selected_customer.name}

            마일리지: {self.selected_customer.mileage:,}

            가입경과일:
            {self.selected_customer.membership_days:,}일

            고객 등급: {self.selected_customer.grade}

            상태: 탑승 승객

            좌석: {self.selected_seat.number}
            """
        )

        QMessageBox.information(
            self,
            "좌석 배정 완료",
            (
                f"{self.selected_customer.name} 고객에게 "
                f"{self.selected_seat.number} 좌석을 "
                f"배정했습니다."
            )
        )

        # 선택 상태 초기화
        self.selected_customer = None
        self.selected_seat = None
        self.update_status_info()

    def random_assign_selected_customers(self):

        # 선택된 대기자 행 가져오기
        selected_rows = sorted(
            set(
                index.row()
                for index
                in self.waiting_table.selectedIndexes()
            )
        )

        if not selected_rows:

            QMessageBox.warning(
                self,
                "알림",
                "대기자를 먼저 선택해주세요."
            )

            return

        # 선택된 행에서 고객 가져오기
        selected_customers = []

        for row in selected_rows:

            number_item = self.waiting_table.item(
                row,
                0
            )

            if number_item is None:
                continue

            customer_number = number_item.data(
                Qt.UserRole
            )

            for customer in self.waiting_passengers:

                if customer.number == customer_number:

                    selected_customers.append(
                        customer
                    )

                    break

        # 현재 빈 좌석 가져오기
        empty_seats = [
            seat
            for seat in self.aircraft.seats
            if seat.customer_number is None
        ]

        # 좌석이 부족하면 취소
        if len(selected_customers) > len(empty_seats):

            QMessageBox.warning(
                self,
                "랜덤 좌석 배정",
                (
                    f"선택한 대기자는 "
                    f"{len(selected_customers)}명입니다.\n"
                    f"현재 빈 좌석은 "
                    f"{len(empty_seats)}개입니다.\n\n"
                    f"좌석이 부족하여 "
                    f"배정을 취소합니다."
                )
            )

            return

        # 랜덤 좌석 배정 확인
        reply = QMessageBox.question(
            self,
            "랜덤 좌석 배정 확인",
            (
                f"선택한 {len(selected_customers)}명의 "
                f"대기자를 랜덤 좌석에 배정하시겠습니까?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # 빈 좌석을 랜덤하게 섞기
        random.shuffle(
            empty_seats
        )

        # 고객마다 랜덤 좌석 배정
        for customer, seat in zip(
            selected_customers,
            empty_seats
        ):

            seat.customer_number = (
                customer.number
            )

            button = (
                self.seat_panel.get_button(
                    seat.number
                )
            )

            if button is not None:

                button.set_customer(
                    customer
                )

            self.waiting_passengers.remove(
                customer
            )

            self.boarded_passengers.append(
                customer
            )

        # 화면 갱신
        self.update_waiting_table(
            self.waiting_passengers,
        )
        self.update_status_info()

        self.update_passenger_table()

        QMessageBox.information(
            self,
            "랜덤 좌석 배정 완료",
            (
                f"{len(selected_customers)}명의 "
                f"대기자를 랜덤 좌석에 배정했습니다."
            )
            
        )

        # 선택 초기화
        self.selected_customer = None
        self.selected_seat = None

    def exclude_selected_customer(self):

        if self.selected_customer is None:

            QMessageBox.warning(
                self,
                "알림",
                "고객을 먼저 선택해주세요."
            )

            return

        reasons = [
            "잦은 신고 대상",
            "사기",
            "항공사 실수",
            "기타"
        ]

        reason, ok = QInputDialog.getItem(
            self,
            "고객 제외 사유",
            (
                f"{self.selected_customer.name} "
                f"고객을 제외하는 사유를 선택해주세요."
            ),
            reasons,
            0,
            False
        )

        if not ok:
            return

        if reason == "기타":

            memo, ok = QInputDialog.getMultiLineText(
                self,
                "제외 사유 입력",
                "제외 사유를 입력해주세요:"
            )

            if not ok:
                return

            if not memo.strip():

                QMessageBox.warning(
                    self,
                    "알림",
                    "기타 사유를 입력해주세요."
                )

                return

            reason = memo.strip()

        # =================================
        # 대기자 제외
        # =================================

        if self.selected_customer in self.waiting_passengers:

            # 대기자 목록에서 제거
            self.waiting_passengers.remove(
                self.selected_customer
            )

            # 혹시 해당 고객이 좌석에 표시되어 있다면 제거
            for seat in self.aircraft.seats:

                if seat.customer_number is not None:

                    customer = (
                        self.customer_service
                        .find_by_number(
                            seat.customer_number
                        )
                    )

                    if (
                        customer is not None
                        and
                        customer.number
                        == self.selected_customer.number
                    ):

                        seat.customer_number = None

                        button = (
                            self.seat_panel.get_button(
                                seat.number
                            )
                        )

                        if button is not None:
                            button.set_customer(None)

                        break

            self.update_waiting_table(
                self.waiting_passengers
            )

            QMessageBox.information(
                self,
                "고객 제외",
                (
                    f"고객: {self.selected_customer.name}\n"
                    f"사유: {reason}\n\n"
                    f"대기자 목록에서 제외되었습니다."
                )
            )
            self.update_status_info()

        # =================================
        # 탑승자 제외
        # =================================

        elif self.selected_customer in self.boarded_passengers:

            # 탑승자의 좌석 찾기
            for seat in self.aircraft.seats:

                if (
                    seat.customer_number
                    == self.selected_customer.number
                ):

                    seat.customer_number = None

                    button = (
                        self.seat_panel.get_button(
                            seat.number
                        )
                    )

                    if button is not None:
                        button.set_customer(None)

                    break

            # 탑승자 목록에서 제거
            self.boarded_passengers.remove(
                self.selected_customer
            )

            self.update_passenger_table()

            QMessageBox.information(
                self,
                "고객 제외",
                (
                    f"고객: {self.selected_customer.name}\n"
                    f"사유: {reason}\n\n"
                    f"탑승자 목록에서 제외되었습니다."
                )
            )
            self.update_status_info()

        # =================================
        # 해당 없음
        # =================================

        else:

            QMessageBox.information(
                self,
                "고객 제외",
                (
                    f"고객: {self.selected_customer.name}\n"
                    f"사유: {reason}\n\n"
                    f"현재 대기자 또는 탑승자가 아닙니다."
                )
            )

        # =================================
        # 선택 해제
        # =================================

        self.selected_customer = None

        self.customer_info.setText(
            "고객을 선택해주세요."
        )
        
   
    # =================================
    # 전체 고객 검색
    # =================================

    def open_customer_search(self):
        dialog = CustomerSearchDialog(
            self.customers,
            self.boarded_passengers,
            self.waiting_passengers,
            self
        )

        result = dialog.exec()

        # 전체 고객 검색에서 대기자가 추가되었으면
        # 메인 화면을 즉시 갱신
        if dialog.waiting_changed:
            self.update_waiting_table(
                self.waiting_passengers
            )

            self.update_passenger_table()

    def update_seat_panel(self):

        for seat in self.aircraft.seats:

            button = self.seat_panel.get_button(
                seat.number
            )

            if button is None:
                continue

            customer = None

            if seat.customer_number is not None:

                customer = (
                    self.customer_service
                    .find_by_number(
                        seat.customer_number
                    )
                )

            button.set_customer(
                customer
            )

    def update_passenger_table(self):

        self.current_boarded_customers = (
            self.boarded_passengers
        )

        self.refresh_passenger_table(
            self.boarded_passengers
        )
        self.passenger_table.resizeColumnsToContents()

    def refresh_passenger_table(self, customers):

        self.passenger_table.setSortingEnabled(False)

        self.passenger_table.setRowCount(
            len(customers)
        )

        seat_class_names = {
            1: "First",
            2: "Business",
            3: "Premium",
            4: "Economy"
        }

        for row, customer in enumerate(customers):

            assigned_seat = None

            for seat in self.aircraft.seats:

                if (
                    seat.customer_number
                    == customer.number
                ):
                    assigned_seat = seat
                    break

            if assigned_seat is None:
                continue

            seat_class_name = seat_class_names.get(
                assigned_seat.seat_class,
                "Unknown"
            )

            # 좌석
            seat_number = assigned_seat.number
            seat_sort_value = (
                int("".join(
                    char
                    for char in seat_number
                    if char.isdigit()
                )),
                "".join(
                    char
                    for char in seat_number
                    if char.isalpha()
                )
            )

            seat_item = SortableTableWidgetItem(
                seat_number,
                seat_sort_value
            )

            # 좌석등급
            class_item = SortableTableWidgetItem(
                seat_class_name,
                assigned_seat.seat_class
            )

            # 이름
            name_item = QTableWidgetItem(
                customer.name
            )

            # 마일리지
            mileage_item = SortableTableWidgetItem(
                f"{customer.mileage:,}",
                customer.mileage
            )

            # 가입일
            membership_item = SortableTableWidgetItem(
                f"{customer.membership_days:,}",
                customer.membership_days
            )

            # 고객등급
            grade_item = QTableWidgetItem(
                customer.grade
            )

            items = [
                seat_item,
                class_item,
                name_item,
                mileage_item,
                membership_item,
                grade_item
            ]

            for column, item in enumerate(items):

                self.passenger_table.setItem(
                    row,
                    column,
                    item
                )

            # 화면에는 표시하지 않는 접수번호 저장
            self.passenger_table.item(
                row,
                0
            ).setData(
                Qt.UserRole,
                customer.number
            )

        self.passenger_table.resizeColumnsToContents()

        self.passenger_table.setSortingEnabled(True)

    def search_passengers(self):

        keyword = (
            self.passenger_search
            .text()
            .strip()
        )

        min_text = (
            self.passenger_min_mileage
            .text()
            .strip()
        )

        max_text = (
            self.passenger_max_mileage
            .text()
            .strip()
        )

        try:
            min_mileage = (
                int(min_text)
                if min_text
                else None
            )
        except ValueError:
            min_mileage = None

        try:
            max_mileage = (
                int(max_text)
                if max_text
                else None
            )
        except ValueError:
            max_mileage = None

        result = []

        for customer in self.boarded_passengers:

            if keyword:

                if not (
                    keyword in customer.name
                    or keyword == str(customer.number)
                ):
                    continue

            if (
                min_mileage is not None
                and customer.mileage < min_mileage
            ):
                continue

            if (
                max_mileage is not None
                and customer.mileage > max_mileage
            ):
                continue

            result.append(customer)

        self.refresh_passenger_table(result)

    def update_status_info(self):

        # =========================
        # 좌석 현황
        # =========================

        total_seats = len(
            self.aircraft.seats
        )

        occupied_seats = [
            seat
            for seat in self.aircraft.seats
            if seat.customer_number is not None
        ]

        empty_seats = [
            seat
            for seat in self.aircraft.seats
            if seat.customer_number is None
        ]

        boarded_count = len(
            occupied_seats
        )

        remaining_seats = len(
            empty_seats
        )

        # =========================
        # 대기자
        # =========================

        waiting_count = len(
            self.waiting_passengers
        )

        # =========================
        # 좌석 등급별
        # =========================

        first_total = 0
        first_used = 0

        business_total = 0
        business_used = 0

        premium_total = 0
        premium_used = 0

        economy_total = 0
        economy_used = 0

        for seat in self.aircraft.seats:

            if seat.seat_class == 1:

                first_total += 1

                if seat.customer_number is not None:
                    first_used += 1

            elif seat.seat_class == 2:

                business_total += 1

                if seat.customer_number is not None:
                    business_used += 1

            elif seat.seat_class == 3:

                premium_total += 1

                if seat.customer_number is not None:
                    premium_used += 1

            else:

                economy_total += 1

                if seat.customer_number is not None:
                    economy_used += 1

        # =========================
        # 화면 갱신
        # =========================

        self.boarded_count_label.setText(
            f"탑승자: {boarded_count}명"
        )

        self.waiting_count_label.setText(
            f"대기자: {waiting_count}명"
        )

        self.total_seat_label.setText(
            f"전체 좌석: {total_seats}석"
        )

        self.remaining_seat_label.setText(
            f"남은 좌석: {remaining_seats}석"
        )

        self.first_class_label.setText(
            f"First: {first_used} / {first_total}"
        )

        self.business_class_label.setText(
            f"Business: {business_used} / {business_total}"
        )

        self.premium_class_label.setText(
            f"Premium Economy: "
            f"{premium_used} / {premium_total}"
        )

        self.economy_class_label.setText(
            f"Economy: {economy_used} / {economy_total}"
        )
    def update_customer_statistics(self):

        # =========================
        # 내부 통계 계산 함수
        # =========================

        def calculate_statistics(customers):

            if not customers:
                return {
                    "average_mileage": 0,
                    "max_mileage": 0,
                    "min_mileage": 0,
                    "average_membership": 0,
                    "max_membership": 0,
                    "grades": {}
                }

            mileages = [
                customer.mileage
                for customer in customers
            ]

            memberships = [
                customer.membership_days
                for customer in customers
            ]

            grades = {}

            for customer in customers:

                grade = customer.grade

                grades[grade] = (
                    grades.get(grade, 0) + 1
                )

            return {
                "average_mileage":
                    sum(mileages) / len(mileages),

                "max_mileage":
                    max(mileages),

                "min_mileage":
                    min(mileages),

                "average_membership":
                    sum(memberships) / len(memberships),

                "max_membership":
                    max(memberships),

                "grades":
                    grades
            }

        # =========================
        # 탑승자
        # =========================

        boarded_statistics = calculate_statistics(
            self.boarded_passengers
        )

        # =========================
        # 대기자
        # =========================

        waiting_statistics = calculate_statistics(
            self.waiting_passengers
        )

        # =========================
        # 등급 문자열
        # =========================

        def format_grades(grades):

            if not grades:
                return "등급별 고객: 없음"

            grade_text = ", ".join(
                f"{grade}: {count}명"
                for grade, count
                in sorted(grades.items())
            )

            return (
                f"등급별 고객: {grade_text}"
            )

        # =========================
        # 탑승자 화면
        # =========================

        self.boarded_average_mileage_label.setText(
            f"평균 마일리지: "
            f"{boarded_statistics['average_mileage']:,.0f}"
        )

        self.boarded_max_mileage_label.setText(
            f"최고 마일리지: "
            f"{boarded_statistics['max_mileage']:,}"
        )

        self.boarded_min_mileage_label.setText(
            f"최저 마일리지: "
            f"{boarded_statistics['min_mileage']:,}"
        )

        self.boarded_average_membership_label.setText(
            f"평균 가입기간: "
            f"{boarded_statistics['average_membership']:,.0f}일"
        )

        self.boarded_max_membership_label.setText(
            f"최장 가입기간: "
            f"{boarded_statistics['max_membership']:,}일"
        )

        self.boarded_grade_label.setText(
            format_grades(
                boarded_statistics["grades"]
            )
        )

        # =========================
        # 대기자 화면
        # =========================

        self.waiting_average_mileage_label.setText(
            f"평균 마일리지: "
            f"{waiting_statistics['average_mileage']:,.0f}"
        )

        self.waiting_max_mileage_label.setText(
            f"최고 마일리지: "
            f"{waiting_statistics['max_mileage']:,}"
        )

        self.waiting_min_mileage_label.setText(
            f"최저 마일리지: "
            f"{waiting_statistics['min_mileage']:,}"
        )

        self.waiting_average_membership_label.setText(
            f"평균 가입기간: "
            f"{waiting_statistics['average_membership']:,.0f}일"
        )

        self.waiting_max_membership_label.setText(
            f"최장 가입기간: "
            f"{waiting_statistics['max_membership']:,}일"
        )

        self.waiting_grade_label.setText(
            format_grades(
                waiting_statistics["grades"]
            )
        )
    def open_priority_formula(self):

        dialog = PriorityFormulaDialog(
            waiting_passengers=self.waiting_passengers,
            current_formula=self.priority_formula,
            parent=self
        )

        result = dialog.exec()

        if result != QDialog.Accepted:
            return

        # 새 우선순위식 저장
        self.priority_formula = (
            dialog.get_formula()
        )

        # 대기자 리스트 우선순위 재계산
        self.update_waiting_table(
            self.waiting_passengers
        )

        # 상단 통계도 갱신
        self.update_customer_statistics()

    def closeEvent(self, event):

        try:
            self.save_waiting_list()
        except Exception as e:
            print(
                f"대기자 목록 저장 중 오류 발생: {e}"
            )

        event.accept()

    def save_waiting_list(self):

        file_name = "waiting_list.txt"

        with open(
            file_name,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "항공편: KE123\n"
            )

            file.write(
                "저장 시간: "
                + datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                + "\n\n"
            )

            file.write(
                "[예약 대기자 최종 순위]\n\n"
            )

            file.write(
                "순위 | 접수번호 | 이름 | "
                "마일리지 | 가입기간 | 고객등급\n"
            )

            file.write(
                "-" * 70
                + "\n"
            )

            # 현재 대기자 테이블의 화면 순서 그대로 저장
            for row in range(
                self.waiting_table.rowCount()
            ):

                priority_item = (
                    self.waiting_table.item(
                        row,
                        0
                    )
                )

                number_item = (
                    self.waiting_table.item(
                        row,
                        1
                    )
                )

                name_item = (
                    self.waiting_table.item(
                        row,
                        2
                    )
                )

                mileage_item = (
                    self.waiting_table.item(
                        row,
                        3
                    )
                )

                membership_item = (
                    self.waiting_table.item(
                        row,
                        4
                    )
                )

                grade_item = (
                    self.waiting_table.item(
                        row,
                        5
                    )
                )

                if (
                    priority_item is None
                    or number_item is None
                    or name_item is None
                    or mileage_item is None
                    or membership_item is None
                    or grade_item is None
                ):
                    continue

                file.write(
                    f"{priority_item.text()} | "
                    f"{number_item.text()} | "
                    f"{name_item.text()} | "
                    f"{mileage_item.text()} | "
                    f"{membership_item.text()} | "
                    f"{grade_item.text()}\n"
                )