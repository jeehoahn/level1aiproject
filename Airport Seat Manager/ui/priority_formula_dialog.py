from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QGroupBox,
    QSpinBox
)

from models.priority_formula import PriorityFormula
from services.priority_service import PriorityService


class PriorityFormulaDialog(QDialog):

    def __init__(
        self,
        waiting_passengers,
        current_formula=None,
        parent=None
    ):

        super().__init__(parent)

        self.setWindowTitle(
            "우선순위식 변경"
        )

        self.resize(
            950,
            700
        )

        self.waiting_passengers = (
            waiting_passengers
        )

        self.priority_service = (
            PriorityService()
        )

        if current_formula is None:

            self.formula = (
                PriorityFormula()
            )

        else:

            self.formula = (
                current_formula
            )

        self.create_ui()

        self.update_preview()

    # =========================
    # UI 생성
    # =========================

    def create_ui(self):

        layout = QVBoxLayout(
            self
        )

        # =========================
        # 우선순위식 설정
        # =========================

        formula_group = QGroupBox(
            "우선순위식 설정"
        )

        formula_layout = QVBoxLayout(
            formula_group
        )

        # -------------------------
        # A
        # -------------------------

        a_layout = QHBoxLayout()

        a_layout.addWidget(
            QLabel(
                "A = 접수번호"
            )
        )

        formula_layout.addLayout(
            a_layout
        )

        # -------------------------
        # B
        # -------------------------

        b_layout = QHBoxLayout()

        b_layout.addWidget(
            QLabel(
                "B 기준값:"
            )
        )

        self.b_reference_combo = (
            QComboBox()
        )

        self.b_reference_combo.addItems([
            "B_MAX",
            "B_AVERAGE",
            "B_MIN"
        ])

        self.b_reference_combo.setCurrentText(
            self.formula.b_reference
        )

        b_layout.addWidget(
            self.b_reference_combo
        )

        b_layout.addWidget(
            QLabel(
                "× 가중치:"
            )
        )

        self.b_weight_spin = (
            QDoubleSpinBox()
        )

        self.b_weight_spin.setRange(
            -1000,
            1000
        )

        self.b_weight_spin.setDecimals(
            2
        )

        self.b_weight_spin.setValue(
            self.formula.b_weight
        )

        b_layout.addWidget(
            self.b_weight_spin
        )

        formula_layout.addLayout(
            b_layout
        )

        # -------------------------
        # C
        # -------------------------

        c_layout = QHBoxLayout()

        c_layout.addWidget(
            QLabel(
                "C 기준값:"
            )
        )

        self.c_reference_combo = (
            QComboBox()
        )

        self.c_reference_combo.addItems([
            "C_MAX",
            "C_AVERAGE",
            "C_MIN"
        ])

        self.c_reference_combo.setCurrentText(
            self.formula.c_reference
        )

        c_layout.addWidget(
            self.c_reference_combo
        )

        c_layout.addWidget(
            QLabel(
                "× 가중치:"
            )
        )

        self.c_weight_spin = (
            QDoubleSpinBox()
        )

        self.c_weight_spin.setRange(
            -1000,
            1000
        )

        self.c_weight_spin.setDecimals(
            2
        )

        self.c_weight_spin.setValue(
            self.formula.c_weight
        )

        c_layout.addWidget(
            self.c_weight_spin
        )

        formula_layout.addLayout(
            c_layout
        )

        # -------------------------
        # D = 등급
        # -------------------------

        d_layout = QHBoxLayout()

        d_layout.addWidget(
            QLabel(
                "D = 고객 등급"
            )
        )

        d_layout.addWidget(
            QLabel(
                "(일반 1 / Silver 2 / Gold 3 / VIP 4)"
            )
        )

        d_layout.addWidget(
            QLabel(
                "× 가중치:"
            )
        )

        self.d_weight_spin = (
            QDoubleSpinBox()
        )

        self.d_weight_spin.setRange(
            -1000,
            1000
        )

        self.d_weight_spin.setDecimals(
            2
        )

        self.d_weight_spin.setValue(
            self.formula.d_weight
        )

        d_layout.addWidget(
            self.d_weight_spin
        )

        formula_layout.addLayout(
            d_layout
        )

        # -------------------------
        # 동점자 기준
        # -------------------------

        tie_layout = QHBoxLayout()

        tie_layout.addWidget(
            QLabel(
                "우선순위가 같을 경우:"
            )
        )

        self.tie_breaker_combo = (
            QComboBox()
        )

        self.tie_breaker_combo.addItem(
            "접수번호가 낮은 사람 우선",
            "A_ASC"
        )

        self.tie_breaker_combo.addItem(
            "접수번호가 높은 사람 우선",
            "A_DESC"
        )

        self.tie_breaker_combo.addItem(
            "마일리지가 낮은 사람 우선",
            "B_ASC"
        )

        self.tie_breaker_combo.addItem(
            "마일리지가 높은 사람 우선",
            "B_DESC"
        )

        self.tie_breaker_combo.addItem(
            "가입기간이 짧은 사람 우선",
            "C_ASC"
        )

        self.tie_breaker_combo.addItem(
            "가입기간이 긴 사람 우선",
            "C_DESC"
        )

        self.tie_breaker_combo.addItem(
            "등급이 낮은 사람 우선",
            "D_ASC"
        )

        self.tie_breaker_combo.addItem(
            "등급이 높은 사람 우선",
            "D_DESC"
        )

        index = (
            self.tie_breaker_combo.findData(
                self.formula.tie_breaker
            )
        )

        if index >= 0:

            self.tie_breaker_combo.setCurrentIndex(
                index
            )

        tie_layout.addWidget(
            self.tie_breaker_combo
        )

        formula_layout.addLayout(
            tie_layout
        )

        layout.addWidget(
            formula_group
        )

        # =========================
        # 실제 공식 표시
        # =========================

        self.formula_label = QLabel()

        self.formula_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)

        layout.addWidget(
            self.formula_label
        )

        # =========================
        # Top-K
        # =========================

        top_k_layout = QHBoxLayout()

        top_k_layout.addWidget(
            QLabel(
                "미리보기 Top-K:"
            )
        )

        self.top_k_spin = (
            QSpinBox()
        )

        self.top_k_spin.setRange(
            1,
            max(
                1,
                len(self.waiting_passengers)
            )
        )

        self.top_k_spin.setValue(
            min(
                10,
                max(
                    1,
                    len(self.waiting_passengers)
                )
            )
        )

        top_k_layout.addWidget(
            self.top_k_spin
        )

        top_k_layout.addWidget(
            QLabel(
                "명"
            )
        )

        top_k_layout.addStretch()

        layout.addLayout(
            top_k_layout
        )

        # =========================
        # 미리보기
        # =========================

        preview_group = QGroupBox(
            "대기자 우선순위 미리보기"
        )

        preview_layout = QVBoxLayout(
            preview_group
        )

        self.preview_table = (
            QTableWidget()
        )

        self.preview_table.setColumnCount(
            6
        )

        self.preview_table.setHorizontalHeaderLabels([
            "순위",
            "접수번호",
            "이름",
            "마일리지",
            "가입기간",
            "우선순위"
        ])

        self.preview_table.setSortingEnabled(
            False
        )

        preview_layout.addWidget(
            self.preview_table
        )

        layout.addWidget(
            preview_group
        )

        # =========================
        # 버튼
        # =========================

        button_layout = QHBoxLayout()

        cancel_button = QPushButton(
            "취소"
        )

        apply_button = QPushButton(
            "변경"
        )

        cancel_button.clicked.connect(
            self.reject
        )

        apply_button.clicked.connect(
            self.apply_formula
        )

        button_layout.addStretch()

        button_layout.addWidget(
            apply_button
        )

        button_layout.addWidget(
            cancel_button
        )

        layout.addLayout(
            button_layout
        )

        # =========================
        # 변경 시 미리보기 갱신
        # =========================

        self.b_reference_combo.currentTextChanged.connect(
            self.update_preview
        )

        self.c_reference_combo.currentTextChanged.connect(
            self.update_preview
        )

        self.b_weight_spin.valueChanged.connect(
            self.update_preview
        )

        self.c_weight_spin.valueChanged.connect(
            self.update_preview
        )

        self.d_weight_spin.valueChanged.connect(
            self.update_preview
        )

        self.tie_breaker_combo.currentIndexChanged.connect(
            self.update_preview
        )

        self.top_k_spin.valueChanged.connect(
            self.update_preview
        )

    # =========================
    # 현재 설정 가져오기
    # =========================

    def get_current_formula(self):

        return PriorityFormula(

            b_reference=(
                self.b_reference_combo.currentText()
            ),

            c_reference=(
                self.c_reference_combo.currentText()
            ),

            b_weight=(
                self.b_weight_spin.value()
            ),

            c_weight=(
                self.c_weight_spin.value()
            ),

            d_weight=(
                self.d_weight_spin.value()
            ),

            tie_breaker=(
                self.tie_breaker_combo.currentData()
            )
        )

    # =========================
    # 미리보기 갱신
    # =========================

    def update_preview(self):

        formula = (
            self.get_current_formula()
        )

        self.formula_label.setText(
            "A - "
            f"B/{formula.b_reference} × "
            f"{formula.b_weight:g}"
            " - "
            f"C/{formula.c_reference} × "
            f"{formula.c_weight:g}"
            " - "
            f"D/4 × "
            f"{formula.d_weight:g}"
        )

        preview = (
            self.priority_service
            .calculate_preview(
                self.waiting_passengers,
                formula
            )
        )

        # =========================
        # Top-K 적용
        # =========================

        top_k = (
            self.top_k_spin.value()
        )

        preview = preview[
            :top_k
        ]

        self.preview_table.setRowCount(
            len(preview)
        )

        for row, item in enumerate(
            preview
        ):

            customer = item[
                "customer"
            ]

            priority = item[
                "priority"
            ]

            values = [
                str(row + 1),
                str(item["A"]),
                customer.name,
                f"{customer.mileage:,}",
                f"{customer.membership_days:,}",
                f"{priority:.2f}"
            ]

            for column, value in enumerate(
                values
            ):

                self.preview_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        value
                    )
                )

        self.preview_table.resizeColumnsToContents()

    # =========================
    # 적용
    # =========================

    def apply_formula(self):

        self.formula = (
            self.get_current_formula()
        )

        self.accept()

    # =========================
    # 결과 가져오기
    # =========================

    def get_formula(self):

        return self.formula