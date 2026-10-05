from dataclasses import dataclass


@dataclass
class PriorityFormula:

    # -------------------------
    # 마일리지
    # -------------------------
    b_reference: str = "B_AVERAGE"
    b_weight: float = 5.0
    # -------------------------
    # 가입기간
    # -------------------------
    c_reference: str = "C_MAX"
    c_weight: float = 10.0
    # -------------------------
    # 고객 등급
    # -------------------------
    d_weight: float = 0.0
    # -------------------------
    # 동점자 처리
    # -------------------------
    tie_breaker: str = "A_DESC"