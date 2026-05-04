"""Entry point for the SiMonPro desktop application."""

import sys

from PyQt6.QtWidgets import QApplication

from src.views.main_window import MainWindow


def main() -> int:
    """Run the SiMonPro application."""
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return sys.exit(app.exec())


if __name__ == "__main__":
    main()