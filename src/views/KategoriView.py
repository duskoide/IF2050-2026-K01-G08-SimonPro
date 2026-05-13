import os
import sys

os.environ["QT_API"] = "pyqt6"

import qtawesome as qta
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QPoint
from PyQt6.QtGui import (QBrush, QColor, QPainter, QPainterPath, QPixmap,
                         QRadialGradient, QFont)
from PyQt6.QtWidgets import (QApplication, QComboBox, QDialog, QFrame,
                             QHBoxLayout, QLabel, QLineEdit, QListView,
                             QPushButton, QVBoxLayout, QWidget)

from src.views.messageview import SuccessPopup


# ── Gradient Card Widget ───────────────────────────────────────────────────────
class GradientCard(QWidget):
    RADIUS = 20

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

        gradient = QRadialGradient(self.width() / 2, self.height() / 2, self.width())
        gradient.setColorAt(0.0, QColor("#F7F8F0"))
        gradient.setColorAt(0.5, QColor("#DCEEF4"))
        gradient.setColorAt(1.0, QColor("#9CD5FF"))

        painter.fillRect(self.rect(), QBrush(gradient))


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


# ── Overlay Dialog (layer hitam fullscreen) ────────────────────────────────────
class OverlayDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Overlay color: hitam dengan alpha 160
        self.overlay_color = QColor(0, 0, 0, 160)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.overlay_color)

    def showEvent(self, event):
        if self.parentWidget():
            # Mengikuti ukuran window utama (parent)
            parent_window = self.parentWidget().window()
            self.setGeometry(parent_window.rect())
            
            # Posisikan dialog tepat di atas parent window
            self.move(parent_window.mapToGlobal(QPoint(0, 0)))
        super().showEvent(event)


class EditKategoriDialog(OverlayDialog):
    """
    Dialog kontainer yang menampung EditKategoriCard dengan efek overlay hitam.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout utama untuk menampung card di tengah
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.card = EditKategoriCard(parent=self)
        self.card.setFixedSize(650, 360) # Sedikit ditambah heightnya untuk error label
        
        # Tambahkan card ke layout dengan alignment center
        main_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignCenter)

        # Ekspos sinyal dari card ke dialog untuk kompatibilitas controller
        self.simpanClicked = self.card.simpanClicked
        self.hapusClicked = self.card.hapusClicked
        self.tambahClicked = self.card.tambahClicked

        self.card.btn_close.clicked.connect(self.reject)

    def tampilkan_form_edit(self, kategori_tuples):
        self.card.tampilkan_form_edit(kategori_tuples)

    def tampilkan_error(self, msg: str):
        self.card.tampilkan_error(msg)

    def tampilkan_success(self, msg: str):
        self.card.tampilkan_success(msg)
        self.accept()

    def mousePressEvent(self, event):
        # Jika area hitam di luar card diklik, tutup dialog
        if not self.card.geometry().contains(event.position().toPoint()):
            self.reject()
        super().mousePressEvent(event)


class EditKategoriCard(GradientCard):
    simpanClicked = pyqtSignal(int, str)
    hapusClicked = pyqtSignal(int)
    tambahClicked = pyqtSignal(str)

    ADD_ITEM_TEXT = "Tambah Kategori Baru"
    ADD_ITEM_DATA = "__ADD_NEW__"

    _INPUT_NORMAL_SS = """
        QLineEdit {
            border: 1.5px solid #355872;
            border-radius: 15px;
            padding: 0 12px;
            font-size: 16px;
            background: #FFFFFF;
            color: #355872;
        }
    """

    _INPUT_ERROR_SS = """
        QLineEdit {
            border: 2px solid #FF4D4D;
            border-radius: 15px;
            padding: 0 12px;
            font-size: 16px;
            background: #FFFFFF;
            color: #355872;
        }
    """

    _COMBO_NORMAL_SS = """
        QComboBox {
            border: 1.5px solid #355872;
            border-radius: 15px;
            padding: 0 12px;
            padding-right: 40px;
            font-size: 16px;
            color: #355872;
            background: #FFFFFF;
        }
        QComboBox:hover {
            background-color: rgba(156, 213, 255, 0.15);
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #355872;
            border-radius: 1px;
            background: #F7F8F0;
            padding: 6px;
            selection-background-color: #9CD5FF;
            selection-color: #355872;
            outline: 0px;
            font-size: 16px;
            color: #355872;
        }
        QComboBox QAbstractItemView::item {
            min-height: 30px;
            padding-left: 10px;
            border-radius: 6px;
            font-size: 16px;
            color: #355872;
        }
        QComboBox QAbstractItemView::item:hover {
            background-color: #DCEEF4;
        }
        QComboBox QAbstractItemView::item:selected {
            background-color: #9CD5FF;
            color: #355872;
            font-weight: 600;
        }
    """

    _COMBO_ERROR_SS = """
        QComboBox {
            border: 2px solid #FF4D4D;
            border-radius: 15px;
            padding: 0 12px;
            padding-right: 40px;
            font-size: 16px;
            color: #355872;
            background: #FFFFFF;
        }
        QComboBox:hover {
            background-color: rgba(156, 213, 255, 0.15);
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #355872;
            border-radius: 1px;
            background: #F7F8F0;
            padding: 6px;
            selection-background-color: #9CD5FF;
            selection-color: #355872;
            outline: 0px;
            font-size: 16px;
            color: #355872;
        }
    """

    _ERROR_LABEL_SS = """
        QLabel {
            color: #FF4D4D;
            font-size: 12px;
            font-weight: 500;
            background: transparent;
            border: none;
            padding-left: 4px;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_add_mode = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(38, 18, 38, 28)
        layout.setSpacing(8)

        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setIconSize(QSize(28, 28))
        self.btn_close.move(590, 15)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setIcon(qta.icon("fa5s.times", color="#355872"))
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: rgba(156, 213, 255, 0.25);
            }
            QPushButton:pressed {
                background-color: rgba(156, 213, 255, 0.4);
            }
        """)

        # Title
        title = QLabel("Edit Kategori")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #355872;
                font-size: 36px;
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
        layout.addSpacing(0)

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
        self.combo_kategori.setStyleSheet(self._COMBO_NORMAL_SS)

        layout.addWidget(self.combo_kategori, alignment=Qt.AlignmentFlag.AlignCenter)
        self.combo_kategori.currentIndexChanged.connect(self._on_kategori_changed)

        layout.addWidget(create_label("Nama Kategori Baru"))
        layout.addSpacing(0)

        # Group input_baru dan message_label agar rapat
        input_container = QVBoxLayout()
        input_container.setSpacing(4)
        
        self.input_baru = QLineEdit()
        self.input_baru.setFixedHeight(46)
        self.input_baru.setFixedWidth(350)
        self.input_baru.setStyleSheet(self._INPUT_NORMAL_SS)
        self.input_baru.textChanged.connect(lambda: self._show_inline_error(""))

        self.message_label = QLabel("")
        self.message_label.setFixedWidth(350)
        self.message_label.setStyleSheet(self._ERROR_LABEL_SS)
        self.message_label.setVisible(False)

        input_container.addWidget(self.input_baru, alignment=Qt.AlignmentFlag.AlignCenter)
        input_container.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(input_container)

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
        self.message_label.setVisible(False)
        self.input_baru.setStyleSheet(self._INPUT_NORMAL_SS)
        self.combo_kategori.setStyleSheet(self._COMBO_NORMAL_SS)

    def _on_simpan(self):
        nama = self.input_baru.text().strip()
        
        if self.is_add_mode:
            # Kondisi 1: Menambah kategori baru
            if not nama:
                self._show_inline_error("Nama kategori baru wajib diisi untuk menambah kategori.")
                return
            self.tambahClicked.emit(nama)
        else:
            # Kondisi 3: Edit kategori
            if not nama:
                self._show_inline_error("Nama kategori baru wajib diisi untuk mengubah kategori.")
                return
            kid = self.combo_kategori.currentData()
            self.simpanClicked.emit(kid, nama)

    def _on_hapus(self):
        # Kondisi 2: Menghapus kategori
        if self.is_add_mode:
            # "Tambah Kategori Baru" terpilih, padahal mau hapus (invalid)
            self._show_inline_error("Pilih kategori yang ingin dihapus (bukan Tambah Baru).", combo_error=True)
            return
        
        # Jika combo kosong (safety check)
        if self.combo_kategori.currentIndex() == -1:
             self._show_inline_error("Kotak nama kategori wajib diisi.", combo_error=True)
             return

        kid = self.combo_kategori.currentData()
        self.hapusClicked.emit(kid)

    def _on_kategori_changed(self, index):
        is_add = self.combo_kategori.itemData(index) == self.ADD_ITEM_DATA
        self._set_add_mode(is_add)
        self.combo_kategori.setStyleSheet(self._COMBO_NORMAL_SS)
        self._show_inline_error("")

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

    def _show_inline_error(self, msg: str, combo_error=False) -> None:
        if msg:
            self.message_label.setText(msg)
            self.message_label.setVisible(True)
            if combo_error:
                self.combo_kategori.setStyleSheet(self._COMBO_ERROR_SS)
            else:
                self.input_baru.setStyleSheet(self._INPUT_ERROR_SS)
        else:
            self.message_label.setText("")
            self.message_label.setVisible(False)
            self.input_baru.setStyleSheet(self._INPUT_NORMAL_SS)
            self.combo_kategori.setStyleSheet(self._COMBO_NORMAL_SS)

    def tampilkan_error(self, msg: str):
        self._show_inline_error(msg)

    def tampilkan_success(self, msg: str):
        popup_parent = self.parent().window() if self.parent() else None
        if not hasattr(self, "_success_popup") or self._success_popup is None:
            self._success_popup = SuccessPopup(parent=popup_parent)
        else:
            self._success_popup.setParent(popup_parent)
        self._success_popup.show_message(msg)


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
