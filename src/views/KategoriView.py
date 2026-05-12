import os
import sys

os.environ["QT_API"] = "pyqt6"

import qtawesome as qta
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import (QBrush, QColor, QPainter, QPainterPath, QPixmap,
                         QRadialGradient)
from PyQt6.QtWidgets import (QApplication, QComboBox, QDialog, QFrame,
                             QHBoxLayout, QLabel, QLineEdit, QListView,
                             QPushButton, QVBoxLayout, QWidget)

from src.views.messageview import SuccessPopup


class GradientDialog(QDialog):
    RADIUS = 20

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.RADIUS, self.RADIUS)
        painter.setClipPath(path)

        gradient = QRadialGradient(self.width() / 2, self.height() / 2, self.width())

        gradient.setColorAt(0.0, QColor("#F7F8F0"))
        gradient.setColorAt(0.5, QColor("#DCEEF4"))
        gradient.setColorAt(1.0, QColor("#9CD5FF"))
        painter.fillRect(self.rect(), QBrush(gradient))


class EditKategoriDialog(GradientDialog):
    simpanClicked = pyqtSignal(int, str)
    hapusClicked = pyqtSignal(int)
    tambahClicked = pyqtSignal(str)

    ADD_ITEM_TEXT = "Tambah Kategori Baru"
    ADD_ITEM_DATA = "__ADD_NEW__"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedSize(760, 380)

        self._drag_pos = None
        self.is_add_mode = False
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 20, 28, 20)

        # path icon (lebih aman)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        card = QFrame(self)
        card.setStyleSheet("background: transparent; border-radius: 28px;")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(70, 28, 70, 30)
        layout.setSpacing(8)

        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setIconSize(QSize(28, 28))
        self.btn_close.move(690, 18)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setIcon(qta.icon("fa5s.times", color="#355872"))
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: rgba(156, 213, 255, 0.25);
            }
            QPushButton:pressed {
                background-color: rgba(156, 213, 255, 0.4);
            }
        """)
        self.btn_close.clicked.connect(self.reject)

        # Title
        title = QLabel("Edit Kategori")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #355872;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: 0.5px;
                border: none;
                background: transparent;
                padding-bottom: 8px;
            }
        """)
        layout.addWidget(title)

        # Label helper
        def create_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("""
                color: #355872;
                font-size: 15px;
                font-weight: 600;
                margin-left: 105px;
            """)
            return lbl

        layout.addWidget(create_label("Nama Kategori"))
        layout.addSpacing(1)

        self.combo_kategori = QComboBox()
        self.combo_kategori.setView(QListView())
        arrow_label = QLabel(self.combo_kategori)
        arrow_label.setPixmap(
            qta.icon("fa5s.angle-down", color="#355872").pixmap(20, 20)
        )

        arrow_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        arrow_label.move(315, 13)

        self.combo_kategori.setFixedHeight(46)
        self.combo_kategori.setFixedWidth(350)

        self.combo_kategori.setStyleSheet(f"""
            QComboBox {{
                border: 1.5px solid #355872;
                border-radius: 15px;
                padding: 0 12px;
                padding-right: 40px;
                font-size: 16px;
                color: #355872;
                background: transparent;
            }}

            QComboBox:hover {{
                background-color: rgba(156, 213, 255, 0.15);
            }}

            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}

            QComboBox QAbstractItemView {{
                border: 1px solid #355872;
                border-radius: 1px;
                background: #F7F8F0;
                padding: 6px;
                selection-background-color: #9CD5FF;
                selection-color: #355872;
                outline: 0px;
                font-size: 16px;
                color: #355872;
            }}

            QComboBox QAbstractItemView::item {{
                min-height: 30px;
                padding-left: 10px;
                border-radius: 6px;
                font-size: 16px;
                color: #355872;
            }}

            QComboBox QAbstractItemView::item:hover {{
                background-color: #DCEEF4;
            }}

            QComboBox QAbstractItemView::item:selected {{
                background-color: #9CD5FF;
                color: #355872;
                font-weight: 600;
            }}

            QComboBox QAbstractItemView::item {{
                min-height: 30px;
                padding-left: 10px;
                font-size: 16px;
                color: #355872;
            }}

            QComboBox QAbstractItemView::item:hover {{
                background-color: #DCEEF4;
                color: #355872;
            }}

            QComboBox QAbstractItemView::item:selected {{
                background-color: #E3F3FF;
                color: #355872;
                font-weight: 600;
            }}

            QListView {{
                border: 1px solid #355872;
                background: #F7F8F0;
                padding: 4px;
                outline: 0px;
            }}

            QListView::item {{
                border: none;
                border-radius: 6px;
                font-size: 16px;
                color: #355872;
            }}
        """)

        layout.addWidget(self.combo_kategori, alignment=Qt.AlignmentFlag.AlignCenter)
        self.combo_kategori.currentIndexChanged.connect(self._on_kategori_changed)

        layout.addWidget(create_label("Nama Kategori Baru"))
        layout.addSpacing(4)

        self.input_baru = QLineEdit()
        self.input_baru.setFixedHeight(46)
        self.input_baru.setFixedWidth(350)

        self.input_baru.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #355872;
                border-radius: 15px;
                padding: 0 12px;
                font-size: 16px;
                background: transparent;
                color: #355872;
            }
        """)

        layout.addWidget(self.input_baru, alignment=Qt.AlignmentFlag.AlignCenter)

        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(45)

        self.btn_simpan = QPushButton("Simpan Kategori")
        self.btn_simpan.setFixedSize(150, 46)
        self.btn_simpan.setIcon(qta.icon("fa5s.save", color="#355872"))
        self.btn_simpan.setStyleSheet("""
            QPushButton {
                background-color: #9CD5FF;
                color: #355872;
                font-size: 14px;
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
        self.btn_simpan.clicked.connect(self._on_simpan)

        self.btn_hapus = QPushButton("Hapus Kategori")
        self.btn_hapus.setFixedSize(150, 46)
        self.btn_hapus.setIcon(qta.icon("fa5s.trash", color="#355872"))
        self._btn_hapus_style = """
            QPushButton {
                background-color: #FF8D8D;
                color: #355872;
                font-size: 14px;
                font-weight: 700;
                border: 1.5px solid #355872;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #FFC0C0;
                border: 1.5px solid #355872;
                color: #355872;
            }
            QPushButton:pressed {
                background-color: #FFC0C0;
            }
        """
        self._btn_hapus_disabled_style = """
            QPushButton {
                background-color: rgba(255, 141, 141, 0.5);
                color: rgba(53, 88, 114, 0.6);
                font-size: 14px;
                font-weight: 700;
                border: 1.5px solid rgba(53, 88, 114, 0.5);
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 192, 192, 0.6);
                border: 1.5px solid rgba(53, 88, 114, 0.5);
                color: rgba(53, 88, 114, 0.6);
            }
            QPushButton:pressed {
                background-color: rgba(255, 192, 192, 0.7);
            }
        """
        self.btn_hapus.setStyleSheet(self._btn_hapus_style)
        self.btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hapus.clicked.connect(self._on_hapus)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addWidget(self.btn_hapus)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        main_layout.addWidget(card)

    def tampilkan_form_edit(self, kategori_tuples):
        self.combo_kategori.blockSignals(True)
        self.combo_kategori.clear()

        for kid, nama in kategori_tuples:
            self.combo_kategori.addItem(nama, kid)
        self.combo_kategori.addItem(self.ADD_ITEM_TEXT, self.ADD_ITEM_DATA)

        if self.combo_kategori.count() > 0:
            self.combo_kategori.setCurrentIndex(0)
        self.combo_kategori.blockSignals(False)
        self._set_add_mode(
            self.combo_kategori.currentData() == self.ADD_ITEM_DATA
        )
        self.message_label.setText("")

    def _on_simpan(self):
        nama = self.input_baru.text().strip()
        if self.is_add_mode:
            self.tambahClicked.emit(nama)
            return

        kid = self.combo_kategori.currentData()
        self.simpanClicked.emit(kid, nama)

    def _on_hapus(self):
        if self.is_add_mode:
            self._show_inline_error("Tidak bisa hapus saat tambah kategori.")
            return

        kid = self.combo_kategori.currentData()
        self.hapusClicked.emit(kid)

    def _on_kategori_changed(self, index):
        is_add = self.combo_kategori.itemData(index) == self.ADD_ITEM_DATA
        self._set_add_mode(is_add)

    def _set_add_mode(self, enabled: bool) -> None:
        self.is_add_mode = enabled
        if enabled:
            self.btn_hapus.setStyleSheet(self._btn_hapus_disabled_style)
            self.btn_hapus.setCursor(Qt.CursorShape.ForbiddenCursor)
            self.input_baru.clear()
            self._show_inline_error("")
        else:
            self.btn_hapus.setStyleSheet(self._btn_hapus_style)
            self.btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
            self._show_inline_error("")

    def _show_inline_error(self, msg: str) -> None:
        if msg:
            self.message_label.setStyleSheet(
                "color: #C0392B; font-size: 12px; font-weight: 600; "
                "border: none; background: transparent;"
            )
            self.message_label.setText(msg)
            return
        self.message_label.setText("")

    # Display error message in red
    def tampilkan_error(self, msg: str):
        if self.is_add_mode:
            self._show_inline_error(msg)
            return
        self.message_label.setStyleSheet(
            "color: #C0392B; font-size: 14px; font-weight: 600; "
            "border: none; background: transparent;"
        )
        self.message_label.setText(msg)

    # Display success message in green, then close dialog
    def tampilkan_success(self, msg: str):
        popup_parent = self.parent().window() if self.parent() else None
        if not hasattr(self, "_success_popup") or self._success_popup is None:
            self._success_popup = SuccessPopup(parent=popup_parent)
        else:
            self._success_popup.setParent(popup_parent)
        self._success_popup.show_message(msg)
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    dialog = EditKategoriDialog()

    data = [
        (1, "Atasan"),
        (2, "Bawahan"),
        (3, "PakaianDalam"),
    ]

    dialog.simpanClicked.connect(lambda i, n: print(f"Simpan {i} -> {n}"))
    dialog.hapusClicked.connect(lambda i: print(f"Hapus {i}"))

    dialog.tampilkan_form_edit(data)
    dialog.exec()
