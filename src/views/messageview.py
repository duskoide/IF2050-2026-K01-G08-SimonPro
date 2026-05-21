import os
import sys

os.environ['QT_API'] = 'pyqt6'

import qtawesome as qta
from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath
from PyQt6.QtWidgets import (QApplication, QGraphicsDropShadowEffect,
                             QGraphicsOpacityEffect, QHBoxLayout, QLabel,
                             QWidget)


# Success Popup Widget 
class SuccessPopup(QWidget):
    MIN_WIDTH = 320
    MAX_WIDTH = 500
    HEIGHT  = 60
    RADIUS  = 16
    BG      = "#99F9D7"

    def __init__(self, parent=None):
        super().__init__(parent)

        # Window flags 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMaximumWidth(self.MAX_WIDTH)
        self.setFixedHeight(self.HEIGHT)
        
        self.bg_color = "#99F9D7"
        self.text_color = "#2D6A55"
        self.icon_color = "#2D6A55"

        self._init_ui()
        self._init_timer()
        self._init_animation()
        self.hide()

    # Build UI 
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 5, 12, 5)
        layout.setSpacing(12)

        # Teks pesan
        self.lbl_message = QLabel("")
        self.lbl_message.setWordWrap(True)
        self.lbl_message.setStyleSheet(f"""
            QLabel {{
                color: {self.text_color};
                font-size: 16px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        self.lbl_message.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # Icon 
        self.lbl_icon = QLabel()
        icon_pixmap = qta.icon(
            "fa5s.check-circle",
            color=self.icon_color
        ).pixmap(24, 24)
        self.lbl_icon.setPixmap(icon_pixmap)
        self.lbl_icon.setFixedSize(28, 28)
        self.lbl_icon.setStyleSheet(
            "background: transparent; border: none;"
        )

        layout.addWidget(self.lbl_message, stretch=1)
        layout.addWidget(
            self.lbl_icon,
            alignment=Qt.AlignmentFlag.AlignVCenter
        )
        
    def _refresh_styles(self):

        # Update text color
        self.lbl_message.setStyleSheet(f"""
            QLabel {{
                color: {self.text_color};
                font-size: 16px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)

        # Update icon color
        icon_pixmap = qta.icon(
            "fa5s.check-circle",
            color=self.icon_color
        ).pixmap(24, 24)

        self.lbl_icon.setPixmap(icon_pixmap)

    # Drop Shadow 
    # def _init_shadow(self):
    #     shadow = QGraphicsDropShadowEffect(self)
    #     shadow.setBlurRadius(24)
    #     shadow.setOffset(0, 4)
    #     shadow.setColor(QColor(0, 0, 0, 60))
    #     self.setGraphicsEffect(shadow)

    # ── Fade Animation ──────────────────────────────────────────────────────
    def _init_animation(self):
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)
        self._anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._anim.setDuration(300)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def _init_timer(self):
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fade_out)

    # Rounded Background 
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
        painter.fillRect(
            self.rect(),
            QBrush(QColor(self.bg_color))
        )
    # Public API 
    def show_message(
        self, 
        message: str = "", 
        bg_color: str = "#99F9D7",
        text_color: str = "#2D6A55",
        icon_color: str = "#2D6A55",
        duration_ms: int = 2000

    ):

        self.lbl_message.setText(message)

        self.bg_color = bg_color
        self.text_color = text_color
        self.icon_color = icon_color
        self._refresh_styles()
        
        # Adjust size based on content
        self.adjustSize()
        if self.width() < self.MIN_WIDTH:
            self.setFixedWidth(self.MIN_WIDTH)
        elif self.width() > self.MAX_WIDTH:
            self.setFixedWidth(self.MAX_WIDTH)
            self.adjustSize() # Recalculate height for wrapped text
        else:
            self.setFixedWidth(self.width())
            
        self.update()
        self._opacity_effect.setOpacity(0.0)
        self.show()
        self.raise_()

        QTimer.singleShot(0, self._reposition)

        self._anim.stop()
        self._anim.setStartValue(self._opacity_effect.opacity())
        self._anim.setEndValue(1.0)
        self._anim.start()

        if duration_ms and duration_ms > 0:
            self._timer.stop()
            self._timer.start(duration_ms)

    def _fade_out(self):
        self._anim.stop()
        self._anim.setStartValue(self._opacity_effect.opacity())
        self._anim.setEndValue(0.0)
        self._anim.finished.connect(self.hide)
        self._anim.start()

    # Positioning 
    def _reposition(self):
        margin = 20
        parent_widget = self.parent() if self.parent() else None
        if parent_widget:
            x = parent_widget.width() - self.width() - margin
            y = parent_widget.height() - self.height() - margin
            self.move(x, y)
            return

        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.width() - self.width() - margin
        y = screen.height() - self.height() - margin
        self.move(x, y)


# ── Entry Point (demo) ─────────────────────────────────────────────────────────
if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Demo: tampilkan popup mandiri
    popup = SuccessPopup()
    popup.show_message("produk berhasil disimpan")

    sys.exit(app.exec())
