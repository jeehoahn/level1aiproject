import sys

from PySide6.QtWidgets import QApplication

from services.customer_service import CustomerService
from services.aircraft_service import AircraftService
from services.passenger_service import PassengerService

from ui.passenger_setup_dialog import PassengerSetupDialog
from ui.main_window import MainWindow

from PySide6.QtWidgets import QApplication, QDialog

def main():

    app = QApplication(sys.argv)

    # -------------------------
    # 데이터 준비
    # -------------------------

    customer_service = CustomerService()

    # -------------------------
    # 메인 화면
    # -------------------------

    # 메인 화면 먼저 생성
    window = MainWindow()

    passenger_service = PassengerService(
        customer_service
    )

    # 승객 설정 창
    setup_dialog = PassengerSetupDialog(
        max_customers=len(
            customer_service.get_all_customers()
        ),
        seat_count=len(window.aircraft.seats),
        parent=window
    )

    result = setup_dialog.exec()

    if result != QDialog.Accepted:
        sys.exit(0)

    passenger_count = setup_dialog.get_passenger_count()

    # 승객 배치
    (
        boarded_passengers,
        waiting_passengers
    ) = passenger_service.create_passenger_list(
        passenger_count,
        window.aircraft
    )

    # 메인 화면에 결과 전달
    window.boarded_passengers = boarded_passengers
    window.waiting_passengers = waiting_passengers

    window.update_seat_panel()
    window.update_passenger_table()
    window.update_waiting_table(
        waiting_passengers
    )
    window.update_status_info()
    window.update_customer_statistics()

    # 메인 화면 표시
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

def select_passenger_customer(self):

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

            상태: 탑승

            좌석: {assigned_seat.number if assigned_seat else "미배정"}

            패널티: 없음
            """
    )