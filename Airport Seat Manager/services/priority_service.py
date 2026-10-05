class PriorityService:

    # =========================
    # 등급 점수
    # =========================

    GRADE_SCORES = {
        "일반": 1,
        "Silver": 2,
        "Gold": 3,
        "VIP": 4
    }

    # =========================
    # 통계
    # =========================

    def get_statistics(self, customers):

        if not customers:
            return {
                "B_MAX": 0,
                "B_AVERAGE": 0,
                "B_MIN": 0,
                "C_MAX": 0,
                "C_AVERAGE": 0,
                "C_MIN": 0
            }

        mileages = [
            customer.mileage
            for customer in customers
        ]

        memberships = [
            customer.membership_days
            for customer in customers
        ]

        return {
            "B_MAX": max(mileages),
            "B_AVERAGE": sum(mileages) / len(mileages),
            "B_MIN": min(mileages),

            "C_MAX": max(memberships),
            "C_AVERAGE": sum(memberships) / len(memberships),
            "C_MIN": min(memberships)
        }

    # =========================
    # 우선순위 계산
    # =========================

    def calculate_priority(
        self,
        customer,
        statistics,
        formula,
        A
    ):

        # -------------------------
        # B = 마일리지
        # -------------------------

        B = customer.mileage

        B_reference = statistics.get(
            formula.b_reference,
            0
        )

        if B_reference == 0:
            b_score = 0
        else:
            b_score = (
                B
                / B_reference
                * formula.b_weight
            )

        # -------------------------
        # C = 가입기간
        # -------------------------

        C = customer.membership_days

        C_reference = statistics.get(
            formula.c_reference,
            0
        )

        if C_reference == 0:
            c_score = 0
        else:
            c_score = (
                C
                / C_reference
                * formula.c_weight
            )

        # -------------------------
        # D = 고객 등급
        # -------------------------

        D = self.GRADE_SCORES.get(
            customer.grade,
            1
        )

        D_MAX = 4

        d_score = (
            D
            / D_MAX
            * formula.d_weight
        )

        # -------------------------
        # 최종 우선순위
        # -------------------------

        return (
            A
            - b_score
            - c_score
            - d_score
        )

    # =========================
    # 동점자 정렬값
    # =========================

    def get_tie_breaker_value(
        self,
        item,
        formula
    ):

        customer = item["customer"]

        if formula.tie_breaker == "A_ASC":
            return item["A"]

        if formula.tie_breaker == "A_DESC":
            return -item["A"]

        if formula.tie_breaker == "B_ASC":
            return customer.mileage

        if formula.tie_breaker == "B_DESC":
            return -customer.mileage

        if formula.tie_breaker == "C_ASC":
            return customer.membership_days

        if formula.tie_breaker == "C_DESC":
            return -customer.membership_days

        if formula.tie_breaker == "D_ASC":
            return self.GRADE_SCORES.get(
                customer.grade,
                1
            )

        if formula.tie_breaker == "D_DESC":
            return -self.GRADE_SCORES.get(
                customer.grade,
                1
            )

        return item["A"]

    # =========================
    # 미리보기 계산
    # =========================

    def calculate_preview(
        self,
        customers,
        formula
    ):

        statistics = self.get_statistics(
            customers
        )

        result = []

        # -------------------------
        # A = 정렬 전 대기 순서
        # -------------------------

        for index, customer in enumerate(
            customers,
            start=1
        ):

            A = index

            priority = self.calculate_priority(
                customer,
                statistics,
                formula,
                A
            )

            result.append({
                "customer": customer,
                "A": A,
                "priority": priority
            })

        # -------------------------
        # 우선순위 → 동점자 기준
        # -------------------------

        result.sort(
            key=lambda item: (
                item["priority"],
                self.get_tie_breaker_value(
                    item,
                    formula
                )
            )
        )

        return result