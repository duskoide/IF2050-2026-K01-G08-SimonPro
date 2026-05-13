import sys
import os

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout,
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

        gradient = QLinearGradient(
            0, 0,
            self.width(), self.height()
        )

        for pos, hex_color in self.GRADIENT_STOPS:
            gradient.setColorAt(pos, QColor(hex_color))

        painter.fillRect(self.rect(), QBrush(gradient))


# ── Owner Popup ────────────────────────────────────────────────────────────────
class OwnerPopup(GradientDialog):
    WIDTH  = 670
    HEIGHT = 200

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

    # ── Build UI ─────────────────────────────────────────────────────────────
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 36, 48, 36)
        layout.setSpacing(28)

        # ── Teks Pesan ───────────────────────────────────────────────────────
        self.lbl_message = QLabel(
            "Owner tidak memiliki akses untuk mengedit!"
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

        # ── Tombol OK ────────────────────────────────────────────────────────
        self.btn_ok = QPushButton("OK")
        self.btn_ok.setFixedSize(140, 44)
        self.btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #9CD5FF;
                color: #355872;
                font-size: 15px;
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
        self.btn_ok.clicked.connect(self.accept)

        layout.addWidget(
            self.btn_ok,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

    # ── Drop Shadow ───────────────────────────────────────────────────────────
    def _init_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.setGraphicsEffect(shadow)

    # ── Centering ─────────────────────────────────────────────────────────────
    def _center(self):
        if self.parent():
            pr = self.parent().geometry()
            x  = pr.x() + (pr.width()  - self.WIDTH)  // 2
            y  = pr.y() + (pr.height() - self.HEIGHT) // 2
        else:
            screen = QApplication.primaryScreen().availableGeometry()
            x = (screen.width()  - self.WIDTH)  // 2
            y = (screen.height() - self.HEIGHT) // 2
        self.move(x, y)

    # ── Public API ─────────────────────────────────────────────────────────────
    def show_message(self, message: str):
        self.lbl_message.setText(message)


# ── Entry Point (demo / hardcode mockup) ──────────────────────────────────────
if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    popup = OwnerPopup()
    popup.show_message("Owner tidak memiliki akses untuk mengedit!")
    popup.exec()

    sys.exit(0)