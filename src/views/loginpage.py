import sys
import os

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt6.QtGui import (
    QPainter, QRadialGradient, QColor, QBrush, QPixmap
)
from PyQt6.QtCore import Qt, QSize
import qtawesome as qta


class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        # PyQt6: RenderHint pakai namespace lengkap
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QRadialGradient(
            self.width() / 2,
            self.height() / 2,
            self.width()
        )
        gradient.setColorAt(0.0, QColor("#9CD5FF"))
        gradient.setColorAt(0.3, QColor("#CDEBFF"))
        gradient.setColorAt(0.5, QColor("#EAF6FF"))
        gradient.setColorAt(1.0, QColor("#F7F8F0"))

        painter.fillRect(self.rect(), QBrush(gradient))


class RoundedInputField(QFrame):
    def __init__(self, placeholder, icon_name, is_password=False, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setMinimumWidth(300)

        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 1.5px solid #355872;
                border-radius: 15px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(10)

        # Ikon qtawesome
        icon_label = QLabel()
        icon_pixmap = qta.icon(icon_name, color="#355872").pixmap(24, 24)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(30, 30)
        # PyQt6: AlignmentFlag
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("border: none; background: transparent;")

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #3A4A5C;
                font-size: 18px;
            }
        """)
        self.input.setFrame(False)

        layout.addWidget(icon_label)
        layout.addWidget(self.input)

        if is_password:
            # PyQt6: EchoMode pakai namespace lengkap
            self.input.setEchoMode(QLineEdit.EchoMode.Password)

            self.toggle_btn = QPushButton()
            self.toggle_btn.setFixedSize(28, 28)
            # PyQt6: CursorShape
            self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.toggle_btn.setIcon(qta.icon("mdi.eye", color="#355872"))
            self.toggle_btn.setIconSize(QSize(24, 24))
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                }
            """)
            self.toggle_btn.clicked.connect(self.toggle_password)
            layout.addWidget(self.toggle_btn)

    def toggle_password(self):
        if self.input.echoMode() == QLineEdit.EchoMode.Password:
            self.input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setIcon(qta.icon("mdi.eye-off", color="#355872"))
        else:
            self.input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setIcon(qta.icon("mdi.eye", color="#355872"))


class LoginWindow(GradientBackground):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SiMonPro - Login")
        # PyQt6: WindowType
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        # PyQt6: WidgetAttribute
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        # PyQt6: AlignmentFlag
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame(self)
        card.setFixedWidth(400)
        card.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 28px;
                border: none;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 36, 40, 36)
        card_layout.setSpacing(0)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("img/Logo Simonpro Biru.png")
        logo.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setMinimumHeight(80)

        card_layout.addWidget(logo)
        card_layout.addSpacing(5)

        # Title
        title = QLabel("SiMonPro")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #355872;
                font-size: 36px;
                font-weight: 700;
                letter-spacing: 0.5px;
                border: none;
                background: transparent;
                padding-bottom: 6px;
            }
        """)

        subtitle = QLabel("Sistem Monitoring Produksi")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #6B8CA4;
                font-size: 24px;
                letter-spacing: 0.3px;
                border: none;
                background: transparent;
            }
        """)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(50)

        # Username
        username_label = QLabel("Username")
        username_label.setStyleSheet("""
            QLabel {
                color: #355872;
                font-size: 18px;
                font-weight: 600;
                border: none;
                background: transparent;
            }
        """)
        self.username_field = RoundedInputField("Masukkan Username", "fa5s.user")

        card_layout.addWidget(username_label)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.username_field)
        card_layout.addSpacing(18)

        # Password
        password_label = QLabel("Password")
        password_label.setStyleSheet("""
            QLabel {
                color: #355872;
                font-size: 18px;
                font-weight: 600;
                border: none;
                background: transparent;
            }
        """)
        self.password_field = RoundedInputField("Masukkan Password", "fa5s.lock", is_password=True)

        card_layout.addWidget(password_label)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.password_field)
        card_layout.addSpacing(8)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("""
            QLabel {
                color: #C0392B;
                font-size: 14px;
                border: none;
                background: transparent;
            }
        """)
        card_layout.addWidget(self.error_label)
        card_layout.addSpacing(12)

        # Tombol login
        login_btn = QPushButton("MASUK")
        login_btn.setFixedHeight(52)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #9CD5FF;
                color: #355872;
                font-size: 24px;
                font-weight: 700;
                border: 1.5px solid #355872;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #E3F3FF;
                border: 1.5px solid #355872;
                color: #355872;
            }
            QPushButton:pressed {
                background-color: #9CD5FF;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(login_btn)

        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def show_error(self, message: str):
        self.error_label.setText(message)

    def clear_error(self):
        self.error_label.setText("")

    def handle_login(self):
        username = self.username_field.input.text()
        password = self.password_field.input.text()
        self.clear_error()
        self.controller.login(username, password)

    def mousePressEvent(self, event):
        # PyQt6: MouseButton & globalPosition().toPoint()
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def keyPressEvent(self, event):
        # PyQt6: Key namespace
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.handle_login()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LoginWindow()
    window.showMaximized()
    sys.exit(app.exec())