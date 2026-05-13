"""Entry point for the SiMonPro desktop application."""

import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont

from src.services.AuthService import AuthService
from src.views.loginpage import LoginWindow
from src.views.dashboardview import DashboardWindow
from src.controllers.LoginController import LoginController
from src.utils.time_service import TimeService


def main() -> int:
    app = QApplication(sys.argv)

    # load font
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "font", "Inter-Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        families = QFontDatabase.applicationFontFamilies(font_id)
        app.setFont(QFont(families[0], 10))
    else:
        print("Font gagal load!")

    # setup auth
    auth_service = AuthService()
    time_service = TimeService()
    login_window = LoginWindow()
    dashboard_window = None

    def on_login_success(user, session):
        nonlocal dashboard_window
        dashboard_window = DashboardWindow(
            user=user,
            session=session,
            time_service=time_service,
            on_logout=lambda: on_logout(session)
        )
        dashboard_window.showMaximized()
        login_window.hide()

    def on_logout(session):
        nonlocal dashboard_window
        # Invalidate session in database
        if session:
            auth_service.logout(session.session_id)
        # Close dashboard and show login again
        if dashboard_window:
            dashboard_window.close()
            dashboard_window = None
        # Clear login fields before showing
        login_window.clear_fields()
        login_window.showMaximized()

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
