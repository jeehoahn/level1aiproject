from pathlib import Path

from models.customer import Customer
from storage.customer_hash_table import CustomerHashTable

import json

class CustomerService:

    def __init__(self, file_path=None):

        if file_path is None:

            file_path = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "레벨1-3_대기자명단1.txt"
            )

        self.file_path = Path(file_path)

        # 고객 등급 기준 JSON
        self.grade_file_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "customer_grade.json"
        )

        # 고객 데이터를 저장하는 해시 테이블
        self.customer_table = CustomerHashTable()

        # 프로그램 시작 시 파일을 한 번 읽음
        self.load_customers()

    # ---------------------------------
    # 고객 등급 기준 불러오기
    # ---------------------------------

    def load_customer_grades(self):

        if not self.grade_file_path.exists():

            raise FileNotFoundError(
                f"고객 등급 JSON 파일을 찾을 수 없습니다:\n"
                f"{self.grade_file_path}"
            )

        with open(
            self.grade_file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data["grades"]

    # ---------------------------------
    # 마일리지 → 고객 등급
    # ---------------------------------

    def get_customer_grade(self, mileage):

        grades = self.load_customer_grades()

        current_grade = "일반"

        for grade in grades:

            if mileage >= grade["minMileage"]:

                current_grade = grade["name"]

        return current_grade

    # ---------------------------------
    # 파일 → 해시 테이블
    # ---------------------------------

    def load_customers(self):

        if not self.file_path.exists():

            print(
                f"고객 파일을 찾을 수 없습니다: "
                f"{self.file_path}"
            )

            return

        with open(
            self.file_path,
            "r",
            encoding="utf-8-sig"
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                # 헤더 제거
                if line.startswith("접수번호"):
                    continue

                parts = line.split("\t")

                if len(parts) < 4:
                    continue

                try:

                    number = int(parts[0])
                    name = parts[1]
                    mileage = int(parts[2])
                    membership_days = int(parts[3])

                    customer = Customer(
                        number=number,
                        name=name,
                        mileage=mileage,
                        membership_days=membership_days,
                        grade=self.get_customer_grade(mileage)
                    )

                    self.customer_table.insert(
                        customer
                    )

                except ValueError:

                    continue

        return self.get_all_customers()

    # ---------------------------------
    # 전체 고객
    # ---------------------------------

    def get_all_customers(self):

        return self.customer_table.values()

    # ---------------------------------
    # 접수번호 검색
    # ---------------------------------

    def find_by_number(self, number):

        try:

            number = int(number)

        except (ValueError, TypeError):

            return None

        return self.customer_table.get(
            number
        )

    # ---------------------------------
    # 검색
    # ---------------------------------

    def search(self, keyword):

        keyword = str(keyword).strip()

        if not keyword:

            return self.get_all_customers()

        # 숫자라면 접수번호 검색
        if keyword.isdigit():

            customer = self.find_by_number(
                int(keyword)
            )

            if customer is None:
                return []

            return [customer]

        # 숫자가 아니라면 이름 검색
        return self.customer_table.search_by_name(
            keyword
        )

    # ---------------------------------
    # 고객 추가
    # ---------------------------------

    def add_customer(self, customer):

        existing = self.find_by_number(
            customer.number
        )

        if existing is not None:

            return False

        self.customer_table.insert(
            customer
        )

        return True

    # ---------------------------------
    # 고객 수정
    # ---------------------------------

    def update_customer(self, customer):

        existing = self.find_by_number(
            customer.number
        )

        if existing is None:

            return False

        self.customer_table.insert(
            customer
        )

        return True

    # ---------------------------------
    # 고객 삭제
    # ---------------------------------

    def delete_customer(self, number):

        return self.customer_table.delete(
            number
        )