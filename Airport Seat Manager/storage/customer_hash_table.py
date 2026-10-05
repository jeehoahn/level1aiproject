class CustomerHashTable:

    def __init__(self, capacity=16):

        self.capacity = capacity
        self.size = 0

        self.buckets = [
            []
            for _ in range(self.capacity)
        ]

    # ---------------------------------
    # 해시 함수
    # ---------------------------------

    def _hash(self, key):

        return hash(key) % self.capacity

    # ---------------------------------
    # 데이터 추가
    # ---------------------------------

    def insert(self, customer):

        key = customer.number

        index = self._hash(key)

        bucket = self.buckets[index]

        # 이미 같은 접수번호가 존재하는 경우
        for i, existing_customer in enumerate(bucket):

            if existing_customer.number == key:

                bucket[i] = customer

                return

        bucket.append(customer)

        self.size += 1

        # 너무 많이 차면 크기 확장
        if self.size / self.capacity > 0.75:

            self._resize()

    # ---------------------------------
    # 접수번호로 검색
    # ---------------------------------

    def get(self, number):

        index = self._hash(number)

        bucket = self.buckets[index]

        for customer in bucket:

            if customer.number == number:

                return customer

        return None

    # ---------------------------------
    # 접수번호로 삭제
    # ---------------------------------

    def delete(self, number):

        index = self._hash(number)

        bucket = self.buckets[index]

        for i, customer in enumerate(bucket):

            if customer.number == number:

                del bucket[i]

                self.size -= 1

                return customer

        return None

    # ---------------------------------
    # 전체 고객 가져오기
    # ---------------------------------

    def values(self):

        customers = []

        for bucket in self.buckets:

            customers.extend(bucket)

        return customers

    # ---------------------------------
    # 이름 검색
    # ---------------------------------

    def search_by_name(self, keyword):

        keyword = str(keyword).strip()

        result = []

        for bucket in self.buckets:

            for customer in bucket:

                if keyword in customer.name:

                    result.append(customer)

        return result

    # ---------------------------------
    # 해시 테이블 크기 확장
    # ---------------------------------

    def _resize(self):

        old_customers = self.values()

        self.capacity *= 2

        self.buckets = [
            []
            for _ in range(self.capacity)
        ]

        self.size = 0

        for customer in old_customers:

            self.insert(customer)