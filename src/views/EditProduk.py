import sys
import os
from pathlib import Path

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton,
    QFrame, QListView, QWidget
)

from PyQt6.QtCore import Qt, QSize

from PyQt6.QtGui import (
    QPainter,
    QLinearGradient,
    QColor,
    QBrush,
    QPainterPath,
)

import qtawesome as qta

from src.models.Produk import Produk
from src.utils.image_utils import pick_image_file, save_image_to_app


# ── Gradient Card Widget ───────────────────────────────────────────────────────
# Sekarang jadi QWidget biasa (bukan QDialog),
# karena dia akan di-embed ke dalam EditProdukDialog
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

        gradient = QLinearGradient(
            0, 0,
            self.width(), self.height()
        )
        gradient.setColorAt(0.0,  QColor("#F7F8F0"))
        gradient.setColorAt(0.45, QColor("#EEF4F6"))
        gradient.setColorAt(1.0,  QColor("#D6ECFA"))

        painter.fillRect(self.rect(), QBrush(gradient))


# ── Overlay Dialog (layer hitam fullscreen) ────────────────────────────────────
class EditProdukDialog(QDialog):
    """
    Layer paling belakang: fullscreen, hitam semi-transparan.
    Card EditProduk di-stack di atasnya sebagai child widget.
    """

    # Ubah nilai alpha (0–255) untuk mengatur opacity overlay
    OVERLAY_COLOR = (0, 0, 0, 160)   # rgba

    def __init__(self, produk=None, categories: list[str] = None, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Fullscreen sesuai layar
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)

        # ── Buat card dan taruh di tengah ────────────────────────────────
        self.card = EditProdukCard(
            produk=produk,
            categories=categories,
            parent=self
        )
        self.card.setFixedSize(650, 610)

        # Posisi card: tengah layar, geser +140 ke kanan (sama seperti semula)
        card_x = (screen.width()  - self.card.width())  // 2
        card_y = (screen.height() - self.card.height()) // 2
        self.card.move(card_x, card_y)

        # Tombol close pada card menutup seluruh overlay
        self.card.btn_close.clicked.connect(self.close)

    def paintEvent(self, event):
        """Gambar layer hitam semi-transparan di seluruh layar."""
        painter = QPainter(self)
        r, g, b, a = self.OVERLAY_COLOR
        painter.fillRect(self.rect(), QColor(r, g, b, a))


# ── Card Edit Produk (QWidget, bukan QDialog) ──────────────────────────────────
class EditProdukCard(GradientCard):

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

    def __init__(self, produk=None, categories: list[str] = None, parent=None):
        super().__init__(parent)

        self.produk = produk
        self._categories = categories or []
        self._selected_image_path: str | None = None

        self._init_ui()
        self._populate_data()

    # ── Helper Label ────────────────────────────────────────────────────────
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

    # ── Helper Row ──────────────────────────────────────────────────────────
    def _make_row(self, label_text: str, widget):
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

    # ── Build UI ────────────────────────────────────────────────────────────
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 10, 28, 10)

        card = QFrame(self)

        # ── Close Button ────────────────────────────────────────────────────
        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setIconSize(QSize(28, 28))
        self.btn_close.move(590, 18)
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
        # Catatan: koneksi .clicked dilakukan di EditProdukDialog

        card.setStyleSheet("""
            background: transparent;
            border-radius: 28px;
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 10)
        layout.setSpacing(0)

        # ── Title ───────────────────────────────────────────────────────────
        title = QLabel("Edit Produk")
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

        # ── Kode Produk ─────────────────────────────────────────────────────
        self.input_kode = QLineEdit()
        self.input_kode.setReadOnly(True)
        self.input_kode.setFixedSize(400, 46)
        self.input_kode.setStyleSheet(self._INPUT_SS.format(bg="#FFFFFF"))
        layout.addLayout(self._make_row("Kode Produk", self.input_kode))

        # ── Nama Produk ─────────────────────────────────────────────────────
        self.input_nama = QLineEdit()
        self.input_nama.setFixedSize(400, 46)
        self.input_nama.setStyleSheet(self._INPUT_SS.format(bg="#FFFFFF"))
        layout.addLayout(self._make_row("Nama Produk", self.input_nama))

        # ── Kategori Produk ─────────────────────────────────────────────────
        self.combo_kategori = QComboBox()
        self.combo_kategori.setView(QListView())
        self.combo_kategori.setFixedSize(400, 46)
        self.combo_kategori.addItems(self._categories)

        arrow_lbl = QLabel(self.combo_kategori)
        arrow_lbl.setPixmap(
            qta.icon("fa5s.angle-down", color="#355872").pixmap(24, 24)
        )
        arrow_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        arrow_lbl.move(368, 13)

        self.combo_kategori.setStyleSheet("""
            QComboBox {
                border: 1.5px solid #355872;
                border-radius: 15px;
                padding: 0 12px;
                padding-right: 40px;
                font-size: 15px;
                color: #355872;
                background: #FFFFFF;
            }
            QComboBox:hover { background-color: rgba(156, 213, 255, 0.15); }
            QComboBox::drop-down { border: none; width: 30px; }
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
        layout.addLayout(self._make_row("Kategori Produk", self.combo_kategori))

        # ── Deskripsi ───────────────────────────────────────────────────────
        self.input_deskripsi = QLineEdit()
        self.input_deskripsi.setFixedSize(400, 46)
        self.input_deskripsi.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #355872;
                border-radius: 15px;
                padding: 0 12px;
                font-size: 15px;
                background: #FFFFFF;
                color: #355872;
            }
        """)
        layout.addLayout(self._make_row("Deskripsi", self.input_deskripsi))

        # ── Foto Produk ─────────────────────────────────────────────────────
        foto_container = QFrame()
        foto_container.setFixedSize(400, 46)
        foto_container.setStyleSheet("""
            QFrame {
                border: 1.5px solid #355872;
                border-radius: 15px;
                background: #FFFFFF;
            }
        """)

        foto_h = QHBoxLayout(foto_container)
        foto_h.setContentsMargins(12, 0, 10, 0)

        self.label_foto = QLabel("Pilih file gambar...")
        self.label_foto.setStyleSheet("""
            background: #FFFFFF;
            border: none;
            color: #9AABB8;
            font-size: 15px;
        """)

        self.btn_upload = QPushButton()
        self.btn_upload.setFixedSize(32, 32)
        self.btn_upload.setIcon(qta.icon("fa5s.upload", color="#355872"))
        self.btn_upload.setStyleSheet("""
            QPushButton { background: #FFFFFF; border: none; }
            QPushButton:hover {
                background: rgba(156, 213, 255, 0.3);
                border-radius: 8px;
            }
        """)
        self.btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_upload.clicked.connect(self._on_upload_clicked)

        foto_h.addWidget(self.label_foto, stretch=1)
        foto_h.addWidget(self.btn_upload)
        layout.addLayout(self._make_row("Foto Produk", foto_container))

        # Spacer
        layout.addSpacing(6)

        # Warning Text
        self.label_warning = QLabel("Nama kategori wajib diisi")
        self.label_warning.setStyleSheet("""
            QLabel {
                color: #FF8D8D;
                font-size: 18px;
                font-weight: 600;
                background: transparent;
                border: none;
            }
        """)
        self.label_warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_warning)

        layout.addSpacing(14)

        # ── Buttons ─────────────────────────────────────────────────────────
        button_layout = QHBoxLayout()

        self.btn_simpan = QPushButton("Simpan Produk")
        self.btn_simpan.setFixedSize(140, 42)
        self.btn_simpan.setIcon(qta.icon("fa5s.save", color="#355872"))
        self.btn_simpan.setStyleSheet("""
            QPushButton {
                background-color: #9CD5FF;
                color: #355872;
                font-size: 13px;
                font-weight: 700;
                border: 1.5px solid #355872;
                border-radius: 12px;
            }
            QPushButton:hover { background-color: #E3F3FF; }
        """)

        self.btn_hapus = QPushButton("Hapus Produk")
        self.btn_hapus.setFixedSize(140, 42)
        self.btn_hapus.setIcon(qta.icon("fa5s.trash-alt", color="#355872"))
        self.btn_hapus.setStyleSheet("""
            QPushButton {
                background-color: #FF8B8B;
                color: #355872;
                font-size: 13px;
                font-weight: 700;
                border: 1.5px solid #355872;
                border-radius: 12px;
            }
            QPushButton:hover { background-color: #FFB1B1; }
        """)

        button_layout.setSpacing(120)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_simpan)
        button_layout.addWidget(self.btn_hapus)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        main_layout.addWidget(card)

    # ── Populate Data ────────────────────────────────────────────────────────
    def _populate_data(self):
        if self.produk is None:
            return

        self.input_kode.setText(f"PRD-{self.produk.produk_id:03d}")
        self.input_nama.setText(self.produk.nama_produk or "")

        index = self.combo_kategori.findText(self.produk.nama_kategori)
        if index >= 0:
            self.combo_kategori.setCurrentIndex(index)

        self.input_deskripsi.setText(self.produk.deskripsi_produk or "")

        if self.produk.gambar:
            self.label_foto.setText(self.produk.gambar)
            self.label_foto.setStyleSheet("""
                background: transparent;
                border: none;
                color: #355872;
                font-size: 15px;
            """)

    def _on_upload_clicked(self):
        raw_path = pick_image_file(self)
        if raw_path:
            self._selected_image_path = raw_path
            self.label_foto.setText(Path(raw_path).name)
            self.label_foto.setStyleSheet("""
                background: transparent;
                border: none;
                color: #355872;
                font-size: 15px;
            """)

    def get_selected_image_relpath(self) -> str | None:
        if self._selected_image_path:
            return save_image_to_app(self._selected_image_path)
        if self.produk and self.produk.gambar:
            return self.produk.gambar
        return None


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    dialog = EditProdukDialog(
        categories=["Atasan", "Bawahan", "Pakaian Dalam"]
    )
    dialog.exec()

    sys.exit(app.exec())