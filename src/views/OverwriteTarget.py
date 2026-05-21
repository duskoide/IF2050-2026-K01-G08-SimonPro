import sys
import os

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGraphicsDropShadowEffect
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QPainter, QPainterPath,
    QLinearGradient, QColor, QBrush
)

import qtawesome as qta


# ── Gradient Base ──────────────────────────────────────────────────────────────
class GradientDialog(QDialog):
    RADIUS = 16
    GRADIENT_STOPS = [
        (0.00, "#F7F8F0"),
        (0.30, "#EEF4F6"),
        (1.00, "#D6ECFA"),
    ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(
            0, 0,
            self.width(), self.height(),
            self.RADIUS, self.RADIUS
        )

        painter.setClipPath(path)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        for pos, hex_color in self.GRADIENT_STOPS:
            gradient.setColorAt(pos, QColor(hex_color))

        painter.fillRect(self.rect(), QBrush(gradient))


# ── Target Popup ───────────────────────────────────────────────────────────────
class TargetPopup(GradientDialog):
    OVERWRITE = 1
    BATALKAN  = 0

    WIDTH  = 670
    HEIGHT = 220

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.WIDTH, self.HEIGHT)

        self._init_ui()
        self._init_shadow()
        self._center()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 36, 48, 36)
        layout.setSpacing(28)

        # ── Teks Pesan ───────────────────────────────────────────────────────
        self.lbl_message = QLabel(
            "Target untuk periode ini sudah diatur!"
        )
        self.lbl_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_message.setWordWrap(True)
        self.lbl_message.setStyleSheet("""
            QLabel {
                color: #355872;
                font-size: 26px;
                font-weight: 700;
                background: transparent;
                border: none;
                letter-spacing: 0.3px;
            }
        """)

        layout.addWidget(self.lbl_message, stretch=1)

        # ── Tombol ───────────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        # Overwrite Button
        self.btn_overwrite = QPushButton("Overwrite")
        self.btn_overwrite.setFixedSize(140, 44)
        self.btn_overwrite.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_overwrite.setStyleSheet("""
            QPushButton {
                background-color: #9CD5FF;
                color: #355872;
                font-size: 18px;
                font-weight: 700;
                border: 1.3px solid #355872;
                border-radius: 14px;
            }

            QPushButton:hover {
                background-color: #B8E2FF;
            }

            QPushButton:pressed {
                background-color: #7DC4F5;
            }
        """)
        self.btn_overwrite.clicked.connect(
            lambda: self.done(self.OVERWRITE)
        )

        # Batalkan Button
        self.btn_batalkan = QPushButton("  Batalkan")
        self.btn_batalkan.setFixedSize(140, 44)
        self.btn_batalkan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batalkan.setIcon(
            qta.icon("fa5s.times", color="#355872")
        )
        self.btn_batalkan.setStyleSheet("""
            QPushButton {
                background-color: #FF8B8B;
                color: #355872;
                font-size: 18px;
                font-weight: 700;
                border: 1.3px solid #355872;
                border-radius: 14px;
            }

            QPushButton:hover {
                background-color: #FFB1B1;
            }

            QPushButton:pressed {
                background-color: #F06060;
            }
        """)
        self.btn_batalkan.clicked.connect(
            lambda: self.done(self.BATALKAN)
        )

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_overwrite)
        btn_layout.addWidget(self.btn_batalkan)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

    # ── Drop Shadow ───────────────────────────────────────────────────────────
    def _init_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.setGraphicsEffect(shadow)

    # ── Centering ─────────────────────────────────────────────────────────────
    def _center(self):
        # Gunakan window() untuk mendapatkan jendela utama (top-level) agar posisi center akurat
        target_geo = None
        if self.parent():
            target_geo = self.parent().window().geometry()
        else:
            target_geo = QApplication.primaryScreen().availableGeometry()

        if target_geo:
            x = target_geo.x() + (target_geo.width() - self.WIDTH) // 2
            y = target_geo.y() + (target_geo.height() - self.HEIGHT) // 2
            self.move(x, y)

    # ── Public API ─────────────────────────────────────────────────────────────
    def show_message(self, message: str):
        """
        Ubah teks pesan sebelum ditampilkan.

        Contoh pemanggilan dari halaman lain:
            popup = TargetPopup(parent=self)
            popup.show_message("Target untuk periode ini sudah diatur!")
            result = popup.exec()

            if result == TargetPopup.OVERWRITE:
                # lanjut overwrite data
            elif result == TargetPopup.BATALKAN:
                # batalkan aksi
        """
        self.lbl_message.setText(message)


# ── Entry Point (demo / hardcode mockup) ──────────────────────────────────────
if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    popup = TargetPopup()
    popup.show_message("Target untuk periode ini sudah diatur!")
    result = popup.exec()

    if result == TargetPopup.OVERWRITE:
        print("User memilih: Overwrite")
    else:
        print("User memilih: Batalkan")

    sys.exit(0)