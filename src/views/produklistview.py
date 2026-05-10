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


class DimOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())

from src.views.KategoriView import EditKategoriDialog
from src.controllers.KategoriController import KategoriController


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
    def __init__(self, name, code, category, description, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(5)

        lay.addWidget(ImagePlaceholder())

        name_row = QHBoxLayout()
        name_row.setSpacing(6)

        lbl_name = QLabel(name)
        lbl_name.setStyleSheet(
            "color: #355872; font-size: 18px; font-weight: 700; border: none; background: transparent;"
        )
        lbl_name.setWordWrap(False)

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

        lbl_cat = QLabel(category)
        lbl_cat.setStyleSheet(
            "color: #355872; font-size: 15px; border: none; background: transparent; font-weight: 600;"
        )
        lay.addWidget(lbl_cat)

        lbl_desc = QLabel(description)
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
        QFrame {
            background: #9CD5FF;
            border-radius: 10px;
            border: none;
        }
    """
    INACTIVE_STYLE = """
        QFrame {
            background: transparent;
            border: none;
        }
        QFrame:hover {
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
            icon_name = next((i for i, l in self.MENU if l == lbl), None)
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
        self._drag_pos = None
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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self.window().frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


class SearchBar(QFrame):
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

        lay.addWidget(ico)
        lay.addWidget(self.input)


class Toolbar(QFrame):
    edit_kategori_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        self.setFixedHeight(54)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        search = SearchBar()
        lay.addWidget(search, stretch=1)

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

        btn_add = QPushButton()
        btn_add.setText(" Tambah Produk")
        btn_add.setIcon(qta.icon("mdi.plus", color="#FFFFFF"))
        btn_add.setIconSize(QSize(20, 20))
        btn_add.setFixedHeight(46)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet(
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

        lay.addWidget(self.btn_cat)
        lay.addWidget(btn_add)


class FilterBar(QFrame):
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

        lay.addWidget(_filter_btn("mdi.sort", "Urutkan"))
        lay.addWidget(_filter_btn("mdi.filter-outline", "Kelompokkan"))
        lay.addStretch()


PRODUCTS = [
    (
        "Kaos Polos",
        "PRD-001",
        "Atasan",
        "Kaos polos berbahan katun combed 30s yang lembut, adem, dan mampu menyerap keringat dengan baik.",
    ),
    (
        "Hoodie",
        "PRD-002",
        "Atasan",
        "Hoodie dengan bahan fleece dan desain streetwear modern yang mengikuti tren anak generasi sekarang.",
    ),
    (
        "Kemeja",
        "PRD-003",
        "Atasan",
        "Kemeja flanel dengan motif kotak-kotak klasik yang tidak lekang oleh waktu. Tebal dan nyaman dipakai.",
    ),
    (
        "Dress Floral",
        "PRD-004",
        "Dress",
        "Dress wanita dengan motif floral yang memberikan kesan segar dan feminin. Menggunakan bahan ringan dan breathable.",
    ),
    (
        "Rok Plisket",
        "PRD-005",
        "Bawahan",
        "Rok plisket dengan desain elegan dan bahan yang jatuh dengan indah. Cocok untuk acara formal maupun kasual.",
    ),
    (
        "Celana Jeans",
        "PRD-006",
        "Bawahan",
        "Celana jeans model slim fit yang mengikuti bentuk kaki namun tetap nyaman karena bahan stretch yang fleksibel.",
    ),
    (
        "Jaket Dilan",
        "PRD-007",
        "Outerwear",
        "Jaket denim dengan desain klasik yang selalu relevan sepanjang waktu. Dibuat dari bahan denim berkualitas tinggi.",
    ),
    (
        "Blouse",
        "PRD-008",
        "Atasan",
        "Blouse wanita dengan desain sederhana namun elegan, cocok untuk digunakan di lingkungan kerja.",
    ),
]


class ProductGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(16)

        cols = 4
        for idx, (name, code, cat, desc) in enumerate(PRODUCTS):
            row, col = divmod(idx, cols)
            grid.addWidget(ProductCard(name, code, cat, desc), row, col)

        for col in range(len(PRODUCTS) % cols, cols):
            if len(PRODUCTS) % cols != 0:
                grid.setColumnStretch(col, 1)


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
        self._drag_pos = None

        if not embedded:
            self.setWindowTitle("SiMonPro - Kelola Data Produk")
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()

    def init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar hanya dirender saat jendela mandiri
        if not self.embedded:
            sidebar = Sidebar()
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
        sticky_lay.addWidget(self.toolbar)
        sticky_lay.addWidget(FilterBar())
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

        inner_lay.addWidget(ProductGrid())
        inner_lay.addStretch()

        scroll.setWidget(inner)
        c_lay.addWidget(scroll)
        root.addWidget(content)

    def _on_edit_kategori(self):
        if not self.session:
            return

        parent_window = self.window()

        overlay = DimOverlay(parent_window)
        overlay.setGeometry(parent_window.rect())
        overlay.show()
        overlay.raise_()

        dialog = EditKategoriDialog(parent=parent_window)
        controller = KategoriController(self.session)
        controller.set_viewer(dialog)

        dialog.simpanClicked.connect(controller.submit_update_kategori)
        dialog.hapusClicked.connect(controller.submit_hapus_kategori)

        try:
            controller.request_edit_kategori()
        except Exception as e:
            dialog.tampilkan_error(f"Gagal memuat data kategori: {e}")

        dialog.exec()
        overlay.close()

    def navigate_to(self, label):
        # Saat embedded, delegasikan ke DashboardWindow via parent
        if self.embedded and hasattr(self.parent(), "navigate_to"):
            self.parent().navigate_to(label)

    def keyPressEvent(self, event):
        if not self.embedded and event.key() == Qt.Key.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ProdukWindow(embedded=False)
    window.showMaximized()
    sys.exit(app.exec())
