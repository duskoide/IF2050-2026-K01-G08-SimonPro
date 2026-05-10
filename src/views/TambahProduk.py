import sys
import os

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QFrame,
    QListView
)

from PyQt6.QtCore import (Qt, QSize)

from PyQt6.QtGui import (
    QPainter, QRadialGradient, QColor,
    QBrush, QPainterPath,
)

import qtawesome as qta


# ── Gradient Dialog ────────────────────────────────────────────────────────────
class GradientDialog(QDialog):
    RADIUS = 20

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(
            0,
            0,
            self.width(),
            self.height(),
            self.RADIUS,
            self.RADIUS
        )

        painter.setClipPath(path)

        gradient = QRadialGradient(
            self.width() / 2,
            self.height() / 2,
            self.width()
        )

        gradient.setColorAt(0.3, QColor("#F7F8F0"))
        gradient.setColorAt(0.5, QColor("#DCEEF4"))
        gradient.setColorAt(1.0, QColor("#9CD5FF"))

        painter.fillRect(self.rect(), QBrush(gradient))


# ── Dialog Tambah Produk (UI Mockup Only) ─────────────────────────────────────
class TambahProdukDialog(GradientDialog):

    _INPUT_SS = """
        QLineEdit {{
            border: 1.5px solid #355872;
            border-radius: 15px;
            padding: 0 12px;
            font-size: 15px;
            background: {bg};
            color: #355872;
        }}
    """
    
    def center_dialog(self):
        screen = QApplication.primaryScreen().availableGeometry()

        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2

        self.move(x, y)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedSize(650, 610)

        self._init_ui()
        self.center_dialog()

    # ── Helper Label ──────────────────────────────────────────────────────────
    @staticmethod
    def _make_label(text: str) -> QLabel:
        lbl = QLabel(text)

        lbl.setStyleSheet("""
            color: #355872;
            font-size: 14px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)

        return lbl

    # ── Helper Row ────────────────────────────────────────────────────────────
    def _make_row(self, label_text: str, widget) -> QVBoxLayout:

        container = QVBoxLayout()

        container.setSpacing(3)

        wrapper = QVBoxLayout()
        wrapper.setSpacing(3)

        label = self._make_label(label_text)

        wrapper.addWidget(label)
        wrapper.addWidget(widget)

        wrapper_widget = QFrame()
        wrapper_widget.setLayout(wrapper)

        wrapper_widget.setFixedWidth(widget.width() + 20)
        
        container.addWidget(
            wrapper_widget,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        return container

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _init_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(28, 10, 28, 10)

        card = QFrame(self)
        
        # ── Close Button ─────────────────────────────────────────────────────
        self.btn_close = QPushButton(self)

        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setIconSize(QSize(28, 28))

        self.btn_close.move(590, 18)

        self.btn_close.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.btn_close.setIcon(
            qta.icon(
                "fa5s.times",
                color="#355872"
            )
        )

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

        self.btn_close.clicked.connect(self.close)        

        card.setStyleSheet("""
            background: transparent;
            border-radius: 28px;
        """)

        layout = QVBoxLayout(card)

        layout.setContentsMargins(20, 28, 20, 28)
        layout.setSpacing(4)

        # ── Title ─────────────────────────────────────────────────────────────
        title = QLabel("Tambah Produk")

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

        layout.addWidget(title)

        # ── Kode Produk ───────────────────────────────────────────────────────
        self.input_kode = QLineEdit("PRD-009")

        self.input_kode.setReadOnly(True)

        self.input_kode.setFixedSize(400, 46)

        self.input_kode.setStyleSheet(
            self._INPUT_SS.format(
                bg="rgba(156, 213, 255, 0.25)"
            )
        )

        layout.addLayout(
            self._make_row("Kode Produk", self.input_kode)
        )

        # ── Nama Produk ───────────────────────────────────────────────────────
        self.input_nama = QLineEdit()

        self.input_nama.setPlaceholderText(
            ""
        )

        self.input_nama.setFixedSize(400, 46)

        self.input_nama.setStyleSheet(
            self._INPUT_SS.format(
                bg="transparent"
            )
        )

        layout.addLayout(
            self._make_row("Nama Produk", self.input_nama)
        )

        # ── Kategori Produk ───────────────────────────────────────────────────
        self.combo_kategori = QComboBox()

        self.combo_kategori.setView(QListView())

        self.combo_kategori.setFixedSize(400, 46)

        self.combo_kategori.addItems([
            "Atasan",
            "Bawahan",
            "Pakaian Dalam"
        ])

        # Custom Arrow Icon
        arrow_lbl = QLabel(self.combo_kategori)

        arrow_lbl.setPixmap(
            qta.icon(
                "fa5s.angle-down",
                color="#355872"
            ).pixmap(24, 24)
        )

        arrow_lbl.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        arrow_lbl.move(368, 13)

        self.combo_kategori.setStyleSheet("""
            QComboBox {
                border: 1.5px solid #355872;
                border-radius: 15px;
                padding: 0 12px;
                padding-right: 40px;
                font-size: 15px;
                color: #355872;
                background: transparent;
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
                selection-background-color: #E3F3FF;
                selection-color: #355872;
                outline: 0px;
                font-size: 15px;
                color: #355872;
            }

            QComboBox QAbstractItemView::item {
                min-height: 30px;
                padding-left: 10px;
                border-radius: 6px;
                font-size: 15px;
                color: #355872;
            }

            QComboBox QAbstractItemView::item:hover {
                background-color: #DCEEF4;
                color: #355872;
            }

            QComboBox QAbstractItemView::item:selected {
                background-color: #E3F3FF;
                color: #355872;
                font-weight: 600;
            }

            QListView {
                border: 1px solid #355872;
                background: #F7F8F0;
                padding: 4px;
                outline: 0px;
            }

            QListView::item {
                border: none;
                border-radius: 6px;
                font-size: 15px;
                color: #355872;
            }
        """)

        layout.addLayout(
            self._make_row(
                "Kategori Produk",
                self.combo_kategori
            )
        )

        # ── Deskripsi ─────────────────────────────────────────────────────────
        self.input_deskripsi = QLineEdit()

        self.input_deskripsi.setPlaceholderText(
            ""
        )

        self.input_deskripsi.setFixedSize(400, 46)

        self.input_deskripsi.setStyleSheet(
            self._INPUT_SS.format(
                bg="transparent"
            )
        )

        layout.addLayout(
            self._make_row(
                "Deskripsi",
                self.input_deskripsi
            )
        )

        # ── Foto Produk ───────────────────────────────────────────────────────
        foto_container = QFrame()

        foto_container.setFixedSize(400, 46)

        foto_container.setStyleSheet("""
            QFrame {
                border: 1.5px solid #355872;
                border-radius: 15px;
                background: transparent;
            }
        """)

        foto_h = QHBoxLayout(foto_container)

        foto_h.setContentsMargins(12, 0, 10, 0)
        foto_h.setSpacing(0)

        self.label_foto = QLabel()

        self.label_foto.setStyleSheet("""
            color: #9AABB8;
            font-size: 15px;
            background: transparent;
            border: none;
        """)

        btn_upload = QPushButton()

        btn_upload.setFixedSize(32, 32)

        btn_upload.setIcon(
            qta.icon(
                "fa5s.upload",
                color="#355872"
            )
        )

        btn_upload.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        btn_upload.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }

            QPushButton:hover {
                background: rgba(156, 213, 255, 0.3);
                border-radius: 8px;
            }
        """)

        foto_h.addWidget(self.label_foto, stretch=1)
        foto_h.addWidget(btn_upload)

        layout.addLayout(
            self._make_row(
                "Foto Produk",
                foto_container
            )
        )

        # ── Spacer ────────────────────────────────────────────────────────────
        layout.addSpacing(8)

        # ── Button Simpan ─────────────────────────────────────────────────────
        self.btn_simpan = QPushButton("Simpan Produk")

        self.btn_simpan.setFixedSize(180, 46)

        self.btn_simpan.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.btn_simpan.setIcon(
            qta.icon(
                "fa5s.save",
                color="#355872"
            )
        )

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

        btn_layout = QHBoxLayout()

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        main_layout.addWidget(card)


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    dialog = TambahProdukDialog()

    dialog.exec()

    sys.exit(app.exec())