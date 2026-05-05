"""Entry point for the SiMonPro desktop application."""

import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont

from src.services.AuthService import AuthService
from src.views.loginpage import LoginWindow
from src.views.main_window import MainWindow
from src.controllers.LoginController import LoginController


def main() -> int:
    app = QApplication(sys.argv)

    # load font
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "font", "Inter_18pt-Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        families = QFontDatabase.applicationFontFamilies(font_id)
        app.setFont(QFont(families[0], 10))
    else:
        print("Font gagal load!")

    # setup auth
    auth_service = AuthService()
    login_window = LoginWindow()
    main_window  = MainWindow()

    def on_login_success():
        login_window.hide()
        main_window.showMaximized()

    controller = LoginController(
        auth_service=auth_service,
        login_view=login_window,
        on_login_success=on_login_success
    )

    login_window.controller = controller
    login_window.showMaximized()

    return sys.exit(app.exec())


if __name__ == "__main__":
    main()