import random


class PassengerService:

    def __init__(self, customer_service):

        self.customer_service = customer_service

        # 이번 비행기의 탑승 승객
        self.boarded_passengers = []

        # 이번 비행기의 예약 대기자
        self.waiting_passengers = []

    # ---------------------------------
    # 승객 랜덤 선정
    # ---------------------------------

    def select_random_passengers(self, count):

        customers = (
            self.customer_service.get_all_customers()
        )

        if count <= 0:
            return []

        if count > len(customers):
            count = len(customers)

        return random.sample(
            customers,
            count
        )

    # ---------------------------------
    # 승객 배치
    # ---------------------------------

    def create_passenger_list(
        self,
        requested_count,
        aircraft
    ):

        # 기존 데이터 초기화
        self.boarded_passengers = []
        self.waiting_passengers = []

        # 전체 고객 중 랜덤으로 선정
        selected_passengers = (
            self.select_random_passengers(
                requested_count
            )
        )

        # 좌석 목록
        seats = aircraft.seats

        # 좌석에 들어갈 수 있는 승객
        boarded_count = min(
            len(selected_passengers),
            len(seats)
        )

        # ---------------------------------
        # 좌석 배치
        # ---------------------------------

        boarded = selected_passengers[
            :boarded_count
        ]

        waiting = selected_passengers[
            boarded_count:
        ]

        # 좌석에 랜덤으로 배치하기 위해
        # 좌석 순서를 섞음
        shuffled_seats = seats.copy()

        random.shuffle(
            shuffled_seats
        )

        for customer, seat in zip(
            boarded,
            shuffled_seats
        ):

            seat.customer_number = (
                customer.number
            )

            self.boarded_passengers.append(
                customer
            )

        # ---------------------------------
        # 예약 대기자
        # ---------------------------------

        self.waiting_passengers = waiting

        return (
            self.boarded_passengers,
            self.waiting_passengers
        )

    # ---------------------------------
    # 탑승 리스트
    # ---------------------------------

    def get_boarded_passengers(self):

        return self.boarded_passengers

    # ---------------------------------
    # 예약 대기 리스트
    # ---------------------------------

    def get_waiting_passengers(self):

        return self.waiting_passengers