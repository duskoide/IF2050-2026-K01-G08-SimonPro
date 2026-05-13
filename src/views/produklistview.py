"""Produk list view for SiMonPro."""

import os
import sys

os.environ["QT_API"] = "pyqt6"

import qtawesome as qta
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.controllers.KategoriController import KategoriController
from src.views.KategoriView import EditKategoriDialog
from src.views.TambahProduk import TambahProdukDialog
from src.views.EditProduk import EditProdukDialog
from src.database.db_connection import get_db
from src.services.KategoriService import KategoriService
from src.services.ProdukService import ProdukService
from src.models.Produk import Produk
from src.utils.image_utils import load_product_pixmap


class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, self.height(), self.width(), 0)
        gradient.setColorAt(0.0, QColor("#B8E4FF"))
        gradient.setColorAt(0.2, QColor("#EAF6FF"))
        gradient.setColorAt(0.6, QColor("#F7F8F0"))
        gradient.setColorAt(1.0, QColor("#F7F8F0"))
        painter.fillRect(self.rect(), QBrush(gradient))


class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "QFrame { background-color: #FFFFFF; border-radius: 15px; border: 1px solid #35587226; }"
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 10))
        self.setGraphicsEffect(shadow)


class ImagePlaceholder(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(160)
        self.setStyleSheet(
            "background: #EAF6FF; border-radius: 12px; border: 1px solid #35587226;"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        ico = QLabel()
        ico.setPixmap(qta.icon("mdi.image-outline", color="#355872").pixmap(48, 48))
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setStyleSheet("border: none; background: transparent;")
        lay.addWidget(ico, alignment=Qt.AlignmentFlag.AlignCenter)


class ProductCard(Card):
    def __init__(self, produk, parent=None, on_edit_clicked=None):
        super().__init__(parent)
        self.produk = produk
        self.setFixedWidth(280)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(5)

        pixmap = load_product_pixmap(produk.gambar) if produk.gambar else None
        if pixmap:
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_label.setFixedHeight(160)
            img_label.setStyleSheet(
                "background: #EAF6FF; border-radius: 12px; border: 1px solid #35587226;"
            )
            lay.addWidget(img_label)
        else:
            lay.addWidget(ImagePlaceholder())

        name_row = QHBoxLayout()
        name_row.setSpacing(6)

        lbl_name = QLabel(produk.nama_produk)
        lbl_name.setStyleSheet(
            "color: #355872; font-size: 18px; font-weight: 700; border: none; background: transparent;"
        )
        lbl_name.setWordWrap(False)

        code = f"PRD-{produk.produk_id:03d}"
        lbl_code = QLabel(code)
        lbl_code.setStyleSheet(
            "color: #355872; font-size: 12px; font-weight: 600; "
            "border: 1px solid #355872; border-radius: 10px; "
            "background: transparent; padding: 1px 6px;"
        )
        lbl_code.setFixedHeight(25)

        name_row.addWidget(lbl_name)
        name_row.addStretch()
        name_row.addWidget(lbl_code)
        lay.addLayout(name_row)

        lbl_cat = QLabel(produk.nama_kategori)
        lbl_cat.setStyleSheet(
            "color: #355872; font-size: 15px; border: none; background: transparent; font-weight: 600;"
        )
        lay.addWidget(lbl_cat)

        desc = produk.deskripsi_produk or "Tidak ada deskripsi."
        lbl_desc = QLabel(desc)
        lbl_desc.setStyleSheet(
            "color: #355872; font-size: 12px; border: none; background: transparent; font-weight: 500;"
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setFixedHeight(56)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lay.addWidget(lbl_desc)

        lay.addSpacing(1)

        btn_edit = QPushButton()
        btn_edit.setText("Edit")
        btn_edit.setIcon(qta.icon("mdi.pencil-outline", color="#355872"))
        btn_edit.setIconSize(QSize(25, 25))
        btn_edit.setFixedHeight(32)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(
            """
            QPushButton {
                background-color: #9CD5FF;
                color: #355872;
                font-size: 15px;
                font-weight: 600;
                border-radius: 15px;
                padding: 5 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E3F3FF;
            }
            """
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(53, 88, 114, 80))
        btn_edit.setGraphicsEffect(shadow)
        if on_edit_clicked:
            btn_edit.clicked.connect(lambda checked, p=produk: on_edit_clicked(p))
        lay.addWidget(btn_edit, alignment=Qt.AlignmentFlag.AlignHCenter)


class Sidebar(QFrame):
    MENU = [
        ("ph.chart-line-up", "Dashboard"),
        ("mdi.package-variant-closed", "Produk"),
        ("fa5s.bullseye", "Target"),
        ("mdi.clipboard-text-outline", "Input Produksi"),
        ("mdi.chart-bar", "Pencapaian"),
        ("ph.warning", "Defect"),
        ("mdi.file-document-outline", "Laporan"),
    ]

    ACTIVE_STYLE = """
        QFrame#menuBtn {
            background: #9CD5FF;
            border-radius: 10px;
            border: none;
        }
    """
    INACTIVE_STYLE = """
        QFrame#menuBtn {
            background: transparent;
            border: none;
        }
        QFrame#menuBtn:hover {
            background: rgba(156,213,255,0.12);
            border-radius: 10px;
        }
    """

    logout_clicked = pyqtSignal()
    menu_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(230)
        self.setStyleSheet("QFrame { background:#355872; border:none; }")
        self._menu_btns = {}

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 10, 18, 10)
        lay.setSpacing(3)

        logo_f = QFrame()
        logo_f.setFixedHeight(80)
        logo_f.setStyleSheet("background:transparent; border:none;")
        logo_lay = QHBoxLayout(logo_f)
        logo_lay.setContentsMargins(18, 0, 18, 0)
        logo_lay.setSpacing(10)
        logo_ico = QLabel()
        pixmap = QPixmap("img/Logo Simonpro Putih.png")
        logo_ico.setPixmap(
            pixmap.scaled(
                40,
                40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        logo_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_ico.setMinimumHeight(50)
        logo_txt = QLabel("SiMonPro")
        logo_txt.setStyleSheet(
            "color:#F7F8F0; font-size:24px; font-weight:700; border:none; background:transparent;"
        )
        logo_lay.addWidget(logo_ico)
        logo_lay.addWidget(logo_txt)
        logo_lay.addStretch()
        lay.addWidget(logo_f)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background:rgba(156,213,255,0); border:none;")
        lay.addWidget(sep)
        lay.addSpacing(8)

        for icon_name, label in self.MENU:
            btn = self._menu_btn(icon_name, label)
            self._menu_btns[label] = btn
            btn.mousePressEvent = lambda event, lbl=label: (
                self.menu_changed.emit(lbl)
                if event.button() == Qt.MouseButton.LeftButton
                else None
            )
            lay.addWidget(btn)
            lay.addSpacing(6)

        self.set_active("Produk")

        lay.addStretch()

        logout_btn = self._menu_btn("mdi.logout", "Keluar")
        logout_btn.mousePressEvent = lambda event: (
            self.logout_clicked.emit()
            if event.button() == Qt.MouseButton.LeftButton
            else None
        )
        lay.addWidget(logout_btn)
        lay.addSpacing(16)

    def set_active(self, label):
        for lbl, btn in self._menu_btns.items():
            icon_name = next(
                (i for i, label_text in self.MENU if label_text == lbl), None
            )
            if lbl == label:
                btn.setStyleSheet(self.ACTIVE_STYLE)
                ico_color = "#355872"
                txt_color = "#355872"
                txt_weight = "700"
            else:
                btn.setStyleSheet(self.INACTIVE_STYLE)
                ico_color = "#F7F8F0"
                txt_color = "#F7F8F0"
                txt_weight = "600"
            row_lay = btn.layout()
            ico_lbl = row_lay.itemAt(0).widget()
            txt_lbl = row_lay.itemAt(1).widget()
            if icon_name:
                ico_lbl.setPixmap(qta.icon(icon_name, color=ico_color).pixmap(24, 24))
            txt_lbl.setStyleSheet(
                f"color:{txt_color}; font-size:18px; font-weight:{txt_weight}; border:none; background:transparent;"
            )

    def _menu_btn(self, icon_name, label):
        btn = QFrame()
        btn.setObjectName("menuBtn")
        btn.setFixedHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(self.INACTIVE_STYLE)

        ico_color = "#F7F8F0"
        txt_color = "#F7F8F0"
        txt_weight = "600"

        row = QHBoxLayout(btn)
        row.setContentsMargins(16, 0, 16, 0)
        row.setSpacing(12)

        ico = QLabel()
        ico.setPixmap(qta.icon(icon_name, color=ico_color).pixmap(24, 24))
        ico.setFixedSize(30, 30)
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setStyleSheet("border:none; background:transparent;")

        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color:{txt_color}; font-size:18px; font-weight:{txt_weight}; border:none; background:transparent;"
        )

        row.addWidget(ico)
        row.addWidget(lbl)
        row.addStretch()

        return btn


class Topbar(QFrame):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setFixedHeight(70)
        self.setStyleSheet("background:transparent; border:none;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(28, 25, 28, 0)

        name = getattr(user, "username", "Admin")
        title = QLabel("Kelola Data Produk")
        title.setStyleSheet(
            "color:#355872; font-size:36px; font-weight:700; border:none; background:transparent;"
        )
        lay.addWidget(title)
        lay.addStretch()

        user_ico = QLabel()
        user_ico.setPixmap(qta.icon("fa5s.user-circle", color="#355872").pixmap(50, 50))
        user_ico.setStyleSheet("border:none; background:transparent;")

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            "color:#355872; font-size:18px; font-weight:700; border:none; background:transparent;"
        )
        role_lbl = QLabel(getattr(user, "role", "Admin"))
        role_lbl.setStyleSheet(
            "color:#355872; font-size:14px; font-weight:400; border:none; background:transparent;"
        )

        info_col = QFrame()
        info_col.setStyleSheet("background:transparent; border:none;")
        info_lay = QVBoxLayout(info_col)
        info_lay.setContentsMargins(0, 0, 0, 0)
        info_lay.setSpacing(0)
        info_lay.addWidget(name_lbl)
        info_lay.addWidget(role_lbl)

        lay.addWidget(user_ico)
        lay.addSpacing(3)
        lay.addWidget(info_col)


class SearchBar(QFrame):
    textChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self.setStyleSheet(
            "background: #FFFFFF; border-radius: 23px; border: 1px solid #35587226;"
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 8))
        self.setGraphicsEffect(shadow)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(8)

        ico = QLabel()
        ico.setPixmap(qta.icon("fa5s.search", color="#355872").pixmap(18, 18))
        ico.setStyleSheet("border: none; background: transparent;")

        self.input = QLineEdit()
        self.input.setPlaceholderText("Cari produk...")
        self.input.setStyleSheet(
            """
            QLineEdit {
                background: transparent;
                border: none;
                color: #355872;
                font-size: 16px;
            }
            QLineEdit::placeholder {
                color: #355872;
            }
            """
        )
        self.input.textChanged.connect(self.textChanged.emit)

        lay.addWidget(ico)
        lay.addWidget(self.input)


class Toolbar(QFrame):
    edit_kategori_clicked = pyqtSignal()
    tambah_produk_clicked = pyqtSignal()
    search_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        self.setFixedHeight(54)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        self.search_bar = SearchBar()
        self.search_bar.textChanged.connect(self.search_changed.emit)
        lay.addWidget(self.search_bar, stretch=1)

        self.btn_cat = QPushButton()
        self.btn_cat.setText("Edit Kategori")
        self.btn_cat.setIcon(qta.icon("mdi.folder-outline", color="#355872"))
        self.btn_cat.setIconSize(QSize(20, 20))
        self.btn_cat.setFixedHeight(46)
        self.btn_cat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cat.setStyleSheet(
            """
            QPushButton {
                background-color: #FFFFFF;
                color: #355872;
                font-size: 15px;
                font-weight: 600;
                border-radius: 23px;
                padding: 0 20px;
                border: 1.5px solid #355872;
            }
            QPushButton:hover {
                background-color: #E3F3FF;
            }
            """
        )
        self.btn_cat.clicked.connect(self.edit_kategori_clicked.emit)

        self.btn_add = QPushButton()
        self.btn_add.setText(" Tambah Produk")
        self.btn_add.setIcon(qta.icon("mdi.plus", color="#FFFFFF"))
        self.btn_add.setIconSize(QSize(20, 20))
        self.btn_add.setFixedHeight(46)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(
            """
            QPushButton {
                background-color: #355872;
                color: #FFFFFF;
                font-size: 15px;
                font-weight: 600;
                border-radius: 23px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #4A6E8A;
            }
            """
        )
        self.btn_add.clicked.connect(self.tambah_produk_clicked.emit)

        lay.addWidget(self.btn_cat)
        lay.addWidget(self.btn_add)


class FilterBar(QFrame):
    urutkan_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        def _filter_btn(icon_name, text):
            btn = QPushButton()
            btn.setText(f"  {text}")
            btn.setIcon(qta.icon(icon_name, color="#355872"))
            btn.setIconSize(QSize(18, 18))
            btn.setFixedHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #FFFFFF;
                    color: #355872;
                    font-size: 14px;
                    font-weight: 600;
                    border-radius: 19px;
                    padding: 0 16px;
                    border: 1px solid #35587250;
                }
                QPushButton:hover {
                    background-color: #E3F3FF;
                }
                """
            )
            return btn

        self.btn_urutkan = _filter_btn("mdi.sort-ascending", "Urutkan")
        self.btn_urutkan.clicked.connect(self.urutkan_clicked.emit)
        lay.addWidget(self.btn_urutkan)
        lay.addWidget(_filter_btn("mdi.filter-outline", "Kelompokkan"))
        lay.addStretch()


class ProductGrid(QWidget):
    def __init__(self, products=None, parent=None, on_edit_clicked=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(16)
        self.cols = 4
        self._on_edit_clicked = on_edit_clicked
        if products:
            self.set_products(products)

    def set_products(self, products: list[Produk]):
        # Bersihkan widget lama
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for idx, produk in enumerate(products):
            row, col = divmod(idx, self.cols)
            card = ProductCard(
                produk,
                parent=self,
                on_edit_clicked=self._on_edit_clicked,
            )
            self._grid.addWidget(card, row, col)

        # Atur stretch pada kolom kosong di baris terakhir
        remainder = len(products) % self.cols
        if remainder != 0:
            for col in range(remainder, self.cols):
                self._grid.setColumnStretch(col, 1)
        else:
            # Hapus stretch yang mungkin ada sebelumnya
            for col in range(self.cols):
                self._grid.setColumnStretch(col, 0)


class ProdukWindow(GradientBackground):
    """Page untuk menampilkan daftar produk.

    Ketika ``embedded=True``, sidebar tidak dirender karena
    DashboardWindow sudah menyediakan sidebar sendiri.
    """

    def __init__(self, user=None, session=None, on_logout=None, embedded=False):
        super().__init__()
        self.user = user
        self.session = session
        self.on_logout = on_logout
        self.embedded = embedded

        # Inisialisasi service untuk mengambil data produk dari database
        db = get_db()
        self._produk_service = ProdukService(db)

        if not embedded:
            self.setWindowTitle("SiMonPro - Kelola Data Produk")

        self.init_ui()
        self.load_produk()

    def load_produk(self, query: str | None = None):
        try:
            if query and query.strip():
                produk_list = self._produk_service.cari_produk(query.strip())
            else:
                produk_list = self._produk_service.get_daftar_produk()
            if getattr(self, '_sort_descending', False):
                produk_list.reverse()
            self.product_grid.set_products(produk_list)
        except Exception as e:
            print(f"[ProdukWindow] Gagal memuat data produk: {e}")

    def _toggle_sort(self):
        self._sort_descending = not getattr(self, '_sort_descending', False)
        self.load_produk()

    def _on_search_changed(self, text: str):
        """Pencarian realtime saat user mengetik di search box."""
        self.load_produk(query=text)

    def init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar hanya dirender saat jendela mandiri
        if not self.embedded:
            sidebar = Sidebar()
            if self.on_logout:
                sidebar.logout_clicked.connect(self.on_logout)
            sidebar.menu_changed.connect(self.navigate_to)
            root.addWidget(sidebar)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(0)
        self.topbar = Topbar(user=self.user)
        c_lay.addWidget(self.topbar)

        sticky = QWidget()
        sticky.setStyleSheet("background: transparent;")
        sticky_lay = QVBoxLayout(sticky)
        sticky_lay.setContentsMargins(28, 12, 28, 16)
        sticky_lay.setSpacing(16)
        self.toolbar = Toolbar()
        self.toolbar.edit_kategori_clicked.connect(self._on_edit_kategori)
        self.toolbar.tambah_produk_clicked.connect(self._on_tambah_produk)
        self.toolbar.search_changed.connect(self._on_search_changed)
        sticky_lay.addWidget(self.toolbar)
        self.filter_bar = FilterBar()
        self.filter_bar.urutkan_clicked.connect(self._toggle_sort)
        sticky_lay.addWidget(self.filter_bar)
        c_lay.addWidget(sticky)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(28, 12, 28, 28)
        inner_lay.setSpacing(8)

        self.product_grid = ProductGrid(on_edit_clicked=self._on_edit_produk)
        inner_lay.addWidget(self.product_grid)
        inner_lay.addStretch()

        scroll.setWidget(inner)
        c_lay.addWidget(scroll)
        root.addWidget(content)

    def _on_edit_kategori(self):
        if not self.session:
            return

        dialog = EditKategoriDialog(parent=self)
        controller = KategoriController(self.session)
        controller.set_viewer(dialog)

        dialog.simpanClicked.connect(controller.submit_update_kategori)
        dialog.hapusClicked.connect(controller.submit_hapus_kategori)
        dialog.tambahClicked.connect(controller.submit_tambah_kategori)

        controller.request_edit_kategori()
        if dialog.exec():
            self.load_produk()

    def _on_tambah_produk(self):
        kode_produk = "Akan tergenerate otomatis"
        kategori_list = []
        try:
            kode_produk = self._produk_service.get_next_kode_produk()
        except Exception as e:
            print(f"[ProdukWindow] Gagal generate kode produk: {e}")
        try:
            kategori_list = self._produk_service.get_daftar_kategori()
        except Exception as e:
            print(f"[ProdukWindow] Gagal memuat kategori: {e}")

        dialog = TambahProdukDialog(
            kode_produk=kode_produk,
            categories=kategori_list,
            parent=self,
        )
        if dialog.exec():
            self.load_produk()

    def _on_edit_produk(self, produk: Produk):
        if not produk:
            return

        kategori_list = []
        try:
            kategori_list = self._produk_service.get_daftar_kategori()
        except Exception as e:
            print(f"[ProdukWindow] Gagal memuat kategori: {e}")

        dialog = EditProdukDialog(
            produk=produk,
            categories=kategori_list,
            user=self.user,
            session=self.session,
            parent=self
        )
        if dialog.exec():
            self.load_produk()

    def navigate_to(self, label):
        # Saat embedded, delegasikan ke DashboardWindow via parent
        if self.embedded:
            parent = self.parent()
            while parent and not hasattr(parent, "navigate_to"):
                parent = parent.parent()
            if parent and hasattr(parent, "navigate_to"):
                parent.navigate_to(label)

    def keyPressEvent(self, event):
        if not self.embedded and event.key() == Qt.Key.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ProdukWindow(embedded=False)
    window.showMaximized()
    sys.exit(app.exec())
