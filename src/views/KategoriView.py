import sys
import os

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QFrame, QWidget,
)
from PyQt6.QtWidgets import QListView
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QRadialGradient, QColor,
    QBrush, QPainterPath, QPixmap
)
import qtawesome as qta

class GradientDialog(QDialog):
    RADIUS = 20

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(
            0, 0, self.width(), self.height(),
            self.RADIUS, self.RADIUS
        )
        painter.setClipPath(path)

        gradient = QRadialGradient(
            self.width() / 2,
            self.height() / 2,
            self.width() 
        )

        gradient.setColorAt(0.0, QColor("#F7F8F0"))
        gradient.setColorAt(0.5, QColor("#DCEEF4"))
        gradient.setColorAt(1.0, QColor("#9CD5FF"))   
        painter.fillRect(self.rect(), QBrush(gradient))

class EditKategoriDialog(GradientDialog):

    simpanClicked = pyqtSignal(int, str)
    hapusClicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedSize(760, 380)

        self._drag_pos = None
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

        layout.addWidget(
            self.combo_kategori,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

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

        layout.addWidget(
            self.input_baru,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

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
        self.btn_hapus.setStyleSheet("""
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
        """)
        self.btn_hapus.clicked.connect(self._on_hapus)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addWidget(self.btn_hapus)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        main_layout.addWidget(card)

    def tampilkan_form_edit(self, kategori_tuples):
        self.combo_kategori.clear()

        for kid, nama in kategori_tuples:
            self.combo_kategori.addItem(nama, kid)

        self.exec()

    def _on_simpan(self):
        kid = self.combo_kategori.currentData()
        nama = self.input_baru.text().strip()

        self.simpanClicked.emit(kid, nama)

    def _on_hapus(self):
        kid = self.combo_kategori.currentData()

        self.hapusClicked.emit(kid)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    dialog = EditKategoriDialog()

    data = [
        (1, "Atasan"),
        (2, "Bawahan"),
        (3, "PakaianDalam"),
    ]

    dialog.tampilkan_form_edit(data)

    dialog.simpanClicked.connect(lambda i, n: print(f"Simpan {i} -> {n}"))
    dialog.hapusClicked.connect(lambda i: print(f"Hapus {i}"))

    sys.exit(app.exec())