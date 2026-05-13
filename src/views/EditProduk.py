import sys
import os
from pathlib import Path

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton,
    QFrame, QListView, QWidget, QGraphicsDropShadowEffect,
    QMessageBox
)

from PyQt6.QtCore import Qt, QSize, QPoint

from PyQt6.QtGui import (
    QPainter,
    QLinearGradient,
    QColor,
    QBrush,
    QPainterPath,
    QRadialGradient,
)

import qtawesome as qta

from src.models.Produk import Produk
from src.models.Session import Session
from src.utils.image_utils import pick_image_file, save_image_to_app
from src.controllers.ProdukController import ProdukController
from src.services.ProdukService import ProdukService
from src.database.db_connection import get_db
from src.views.messageview import SuccessPopup


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
        self.overlay_color = QColor(0, 0, 0, 160)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.overlay_color)

    def showEvent(self, event):
        if self.parentWidget():
            parent_window = self.parentWidget().window()
            self.setGeometry(parent_window.rect())
            self.move(parent_window.mapToGlobal(QPoint(0, 0)))
        super().showEvent(event)


class EditProdukDialog(OverlayDialog):
    """
    Card EditProduk di-stack di atasnya sebagai child widget.
    """

    def __init__(self, produk=None, categories: list[str] = None, user=None, session=None, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ── Buat card dan taruh di tengah ────────────────────────────────
        self.card = EditProdukCard(
            produk=produk,
            categories=categories,
            user=user,
            session=session,
            parent=self
        )
        self.card.setFixedSize(650, 610)
        main_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignCenter)

        self.card.btn_close.clicked.connect(self.close)

    def mousePressEvent(self, event):
        if not self.card.geometry().contains(event.position().toPoint()):
            self.close()
        super().mousePressEvent(event)


# ── Card Edit Produk (QWidget, bukan QDialog) ──────────────────────────────────
class EditProdukCard(GradientCard):

    # Normal styles
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

    _COMBO_SS = """
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
    """

    # Error styles
    _INPUT_ERROR_SS = """
        QLineEdit {
            border: 2px solid #FF4D4D;
            border-radius: 15px;
            padding: 0 12px;
            font-size: 15px;
            background: white;
            color: #355872;
        }
    """

    _COMBO_ERROR_SS = """
        QComboBox {
            border: 2px solid #FF4D4D;
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
    """

    _FRAME_NORMAL_SS = """
        QFrame {
            border: 1.5px solid #355872;
            border-radius: 15px;
            background: #FFFFFF;
        }
    """

    _FRAME_ERROR_SS = """
        QFrame {
            border: 2px solid #FF4D4D;
            border-radius: 15px;
            background: #FFFFFF;
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
            margin-top: 4px;   /* FIX 2: jarak antara field dan error message */
        }
    """

    def __init__(self, produk=None, categories: list[str] = None, user=None, session=None, parent=None):
        super().__init__(parent)

        self.produk = produk
        self.user = user
        self.session = session
        self._categories = categories or []
        self._selected_image_path: str | None = None

        db = get_db()
        produk_service = ProdukService(db)
        self.controller = ProdukController(produk_service)
        self.controller.set_on_error(self._tampilkan_error_msg)

        self._init_ui()
        self._populate_data()

    def _tampilkan_error_msg(self, msg: str):
        QMessageBox.critical(self, "Error", msg)

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

    def _make_error_label(self, text: str) -> QLabel:
        """Buat label error kecil di bawah field, tersembunyi secara default."""
        lbl = QLabel(text)
        lbl.setStyleSheet(self._ERROR_LABEL_SS)
        lbl.setVisible(False)
        return lbl

    # ── Helper Row (dengan slot error label di bawah field) ──────────────────
    def _make_row(self, label_text: str, widget, error_label: QLabel):
        container = QVBoxLayout()
        container.setSpacing(0)

        wrapper = QVBoxLayout()
        wrapper.setSpacing(3)

        label = self._make_label(label_text)
        wrapper.addWidget(label)
        wrapper.addWidget(widget)
        wrapper.setSpacing(3)
        wrapper.addWidget(error_label)   # ← error label tepat di bawah field

        wrapper_widget = QFrame()
        wrapper_widget.setLayout(wrapper)
        wrapper_widget.setFixedWidth(widget.width() + 20)
        wrapper_widget.setStyleSheet("background: transparent; border: none;")

        container.addWidget(
            wrapper_widget,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        return container

    # ── Build UI ────────────────────────────────────────────────────────────
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        # FIX 1: kurangi top margin agar semua konten naik ke atas
        main_layout.setContentsMargins(28, 4, 18, 10)

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
        # FIX 1: kurangi top margin card dan spacing agar konten naik
        layout.setContentsMargins(20, 8, 20, 10)
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
                padding-bottom: 4px;   /* FIX 1: sedikit dikurangi dari 6px */
            }
        """)
        layout.addWidget(title)

        # ── Kode Produk ─────────────────────────────────────────────────────
        self.input_kode = QLineEdit()
        self.input_kode.setReadOnly(True)
        self.input_kode.setFixedSize(400, 46)
        self.input_kode.setStyleSheet(self._INPUT_SS.format(bg="#FFFFFF"))
        _err_kode = self._make_error_label("")
        layout.addLayout(self._make_row("Kode Produk", self.input_kode, _err_kode))

        # ── Nama Produk ─────────────────────────────────────────────────────
        self.input_nama = QLineEdit()
        self.input_nama.setFixedSize(400, 46)
        self.input_nama.setStyleSheet(self._INPUT_SS.format(bg="#FFFFFF"))
        self.err_nama = self._make_error_label("Nama Produk wajib diisi")
        layout.addLayout(self._make_row("Nama Produk", self.input_nama, self.err_nama))

        # ── Kategori Produk ─────────────────────────────────────────────────
        self.combo_kategori = QComboBox()
        self.combo_kategori.setView(QListView())
        self.combo_kategori.setFixedSize(400, 46)
        self.combo_kategori.addItem("Pilih Kategori")
        self.combo_kategori.addItems(self._categories)
        self.combo_kategori.setCurrentIndex(0)

        arrow_lbl = QLabel(self.combo_kategori)
        arrow_lbl.setPixmap(
            qta.icon("fa5s.angle-down", color="#355872").pixmap(24, 24)
        )
        arrow_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        arrow_lbl.move(368, 13)

        self.combo_kategori.setStyleSheet(self._COMBO_SS)
        self.err_kategori = self._make_error_label("Kategori Produk wajib dipilih")
        layout.addLayout(self._make_row("Kategori Produk", self.combo_kategori, self.err_kategori))

        # ── Deskripsi (opsional, tidak ada validasi) ─────────────────────────
        self.input_deskripsi = QLineEdit()
        self.input_deskripsi.setFixedSize(400, 46)
        self.input_deskripsi.setStyleSheet(self._INPUT_SS.format(bg="#FFFFFF"))
        # FIX 3: tidak ada error label untuk deskripsi (bersifat opsional)
        _err_deskripsi_placeholder = self._make_error_label("")
        layout.addLayout(self._make_row("Deskripsi", self.input_deskripsi, _err_deskripsi_placeholder))

        # ── Foto Produk ─────────────────────────────────────────────────────
        self._foto_container = QFrame()
        self._foto_container.setFixedSize(400, 46)
        self._foto_container.setStyleSheet(self._FRAME_NORMAL_SS)

        foto_h = QHBoxLayout(self._foto_container)
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

        self.err_foto = self._make_error_label("Foto Produk wajib diunggah")
        layout.addLayout(self._make_row("Foto Produk", self._foto_container, self.err_foto))

        layout.addSpacing(10)

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

        # Koneksi validasi saat simpan diklik
        self.btn_simpan.clicked.connect(self._on_simpan_clicked)
        self.btn_hapus.clicked.connect(self._on_hapus_clicked)

        # Reset error otomatis saat user berinteraksi
        self.input_nama.textChanged.connect(
            lambda: self._clear_error_line(self.input_nama, self.err_nama)
        )
        # FIX 3: deskripsi tidak punya error, tidak perlu koneksi reset error
        self.combo_kategori.currentIndexChanged.connect(
            lambda: self._clear_error_combo(self.combo_kategori, self.err_kategori)
        )

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
            self._clear_error_frame(self._foto_container, self.err_foto)

    # ── Validasi Simpan ──────────────────────────────────────────────────────
    def _on_simpan_clicked(self):
        """Validasi field wajib; deskripsi bersifat opsional (FIX 3)."""
        nama_kosong      = not self.input_nama.text().strip()
        kategori_kosong  = self.combo_kategori.currentIndex() == 0
        foto_kosong      = self.label_foto.text().strip() in ("", "Pilih file gambar...")

        # Nama
        if nama_kosong:
            self.input_nama.setStyleSheet(self._INPUT_ERROR_SS)
            self.err_nama.setVisible(True)
        else:
            self.input_nama.setStyleSheet(self._INPUT_SS.format(bg="#FFFFFF"))
            self.err_nama.setVisible(False)

        # Kategori
        if kategori_kosong:
            self.combo_kategori.setStyleSheet(self._COMBO_ERROR_SS)
            self.err_kategori.setVisible(True)
        else:
            self.combo_kategori.setStyleSheet(self._COMBO_SS)
            self.err_kategori.setVisible(False)

        # FIX 3: deskripsi tidak divalidasi sama sekali

        # Foto
        if foto_kosong:
            self._foto_container.setStyleSheet(self._FRAME_ERROR_SS)
            self.err_foto.setVisible(True)
        else:
            self._foto_container.setStyleSheet(self._FRAME_NORMAL_SS)
            self.err_foto.setVisible(False)

        ada_error = nama_kosong or kategori_kosong or foto_kosong
        if not ada_error:
            self._do_simpan()

    def _tampilkan_success(self, msg: str):
        popup_parent = self.window().parentWidget().window() if self.window().parentWidget() else self.window()
        if not hasattr(self, "_success_popup") or self._success_popup is None:
            self._success_popup = SuccessPopup(parent=popup_parent)
        else:
            self._success_popup.setParent(popup_parent)
        self._success_popup.show_message(msg)

    def _do_simpan(self):
        """Logika penyimpanan aktual dipanggil setelah validasi lulus."""
        if not self.produk or not self.user:
            QMessageBox.critical(self, "Error", "Data produk atau user tidak lengkap.")
            return

        nama_produk = self.input_nama.text()
        deskripsi_produk = self.input_deskripsi.text()
        nama_kategori = self.combo_kategori.currentText()
        gambar_path = self.get_selected_image_relpath()

        updated_produk = self.controller.submit_update_produk(
            user_role=self.user.role,
            produk_id=self.produk.produk_id,
            nama_produk=nama_produk,
            deskripsi_produk=deskripsi_produk,
            satuan=self.produk.satuan,  # Asumsi satuan tidak diubah di form ini
            gambar=gambar_path,
            status_aktif=self.produk.status_aktif, # Asumsi status aktif tidak diubah
            nama_kategori=nama_kategori
        )

        if updated_produk:
            self._tampilkan_success(f"Produk '{updated_produk.nama_produk}' berhasil diperbarui")
            self.parent().accept() # Close the dialog
        else:
            pass

    def _on_hapus_clicked(self):
        if not self.produk or not self.user:
            QMessageBox.critical(self, "Error", "Data produk atau user tidak lengkap.")
            return

        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus produk '{self.produk.nama_produk}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.controller.submit_nonaktifkan_produk(
                user_role=self.user.role,
                produk_id=self.produk.produk_id
            )
            if success:
                self._tampilkan_success(f"Produk '{self.produk.nama_produk}' berhasil dihapus")
                self.parent().accept()

    # ── Helper: clear error per field ────────────────────────────────────────
    def _clear_error_line(self, widget: QLineEdit, err_lbl: QLabel):
        widget.setStyleSheet(self._INPUT_SS.format(bg="#FFFFFF"))
        err_lbl.setVisible(False)

    def _clear_error_combo(self, combo: QComboBox, err_lbl: QLabel):
        if combo.currentIndex() != 0:
            combo.setStyleSheet(self._COMBO_SS)
            err_lbl.setVisible(False)

    def _clear_error_frame(self, frame: QFrame, err_lbl: QLabel):
        frame.setStyleSheet(self._FRAME_NORMAL_SS)
        err_lbl.setVisible(False)

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

