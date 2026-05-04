"""Entry point for the SiMonPro desktop application."""

import sys

from PyQt6.QtWidgets import QApplication

from src.views.main_window import MainWindow


def main() -> int:
    """Run the SiMonPro application."""
    app = QApplication(sys.argv)

    import os
    from PyQt6.QtGui import QFontDatabase, QFont

    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "fonts", "Inter-Regular.ttf")

    font_id = QFontDatabase.addApplicationFont(font_path)

    if font_id != -1:
        families = QFontDatabase.applicationFontFamilies(font_id)
        app.setFont(QFont(families[0], 10))
    else:
        print("Font gagal load!")

    window = MainWindow()
    window.show()

    return sys.exit(app.exec())


if __name__ == "__main__":
    main()