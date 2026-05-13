import sys
import os

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy,
    QScrollArea, QGraphicsDropShadowEffect, QLineEdit,
    QComboBox, QDateEdit, QListView
)
from PyQt6.QtGui import (
    QPainter, QLinearGradient, QColor,
    QBrush, QPixmap, QIntValidator, QKeyEvent
)
from PyQt6.QtCore import Qt, QSize, QDate, QEvent, pyqtSignal
import qtawesome as qta
from src.database.db_connection import get_db
from src.services.ProdukService import ProdukService

#Background
class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())

        gradient.setColorAt(0.0, QColor("#DDF3FF"))
        gradient.setColorAt(0.35, QColor("#EAF7FF"))
        gradient.setColorAt(0.5, QColor("#EAF7FF"))
        gradient.setColorAt(0.65, QColor("#F7F8F0"))
        gradient.setColorAt(1.0, QColor("#F7F8F0"))

        painter.fillRect(self.rect(), QBrush(gradient))

#Card
class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
                border: 1px solid #35587226;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 10))
        self.setGraphicsEffect(shadow)

#Sidebar
class Sidebar(QFrame):
    MENU = [
        ("ph.chart-line-up", "Dashboard", False),
        ("mdi.package-variant-closed", "Produk", False),
        ("fa5s.bullseye", "Target", False),
        ("mdi.clipboard-text-outline", "Input Produksi", True),
        ("mdi.chart-bar", "Pencapaian", False),
        ("ph.warning", "Defect", False),
        ("mdi.file-document-outline", "Laporan", False),
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
    menu_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(230)
        self.setStyleSheet("QFrame { background:#355872; border:none; }")
        self._menu_btns = {}

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 10, 18, 10)
        lay.setSpacing(3)

        # Logo
        logo_f = QFrame()
        logo_f.setFixedHeight(80)
        logo_f.setStyleSheet("background:transparent; border:none;")
        logo_lay = QHBoxLayout(logo_f)
        logo_lay.setContentsMargins(18, 0, 18, 0)
        logo_lay.setSpacing(10)
        logo_ico = QLabel()
        pixmap = QPixmap("img/Logo Simonpro Putih.png")
        if not pixmap.isNull():
            logo_ico.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
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

        for icon_name, label, active in self.MENU:
            btn = self._menu_btn(icon_name, label, active)
            self._menu_btns[label] = btn
            btn.mousePressEvent = self._make_menu_handler(label)
            lay.addWidget(btn)
            lay.addSpacing(6)

        self.set_active("Input Produksi")

        lay.addStretch()

        logout_btn = self._menu_btn("mdi.logout", "Keluar", False)
        logout_btn.mousePressEvent = self._make_logout_handler()
        lay.addWidget(logout_btn)
        lay.addSpacing(16)

    def _make_menu_handler(self, label):
        def handler(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.menu_changed.emit(label)
                self.menu_clicked.emit(label)
        return handler

    def _make_logout_handler(self):
        def handler(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.logout_clicked.emit()
        return handler

    def set_active(self, label):
        for lbl, btn in self._menu_btns.items():
            icon_name = next(
                (i for i, label_text, _ in self.MENU if label_text == lbl), None
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
            font_size = "16px" if lbl == "Input Produksi" else "18px"
            txt_lbl.setStyleSheet(
                f"color:{txt_color}; font-size:{font_size}; font-weight:{txt_weight}; border:none; background:transparent;"
            )

    def _menu_btn(self, icon_name, label, active):
        btn = QFrame()
        btn.setObjectName("menuBtn")
        btn.setFixedHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        if active:
            btn.setStyleSheet(self.ACTIVE_STYLE)
            ico_color  = "#355872"
            txt_color  = "#355872"
            txt_weight = "700"
            
        else:
            btn.setStyleSheet(self.INACTIVE_STYLE)
            ico_color  = "#F7F8F0"
            txt_color  = "#F7F8F0"
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
        if label == "Input Produksi":
            font_size = "16px"  
        else:
            font_size = "18px"
        lbl.setStyleSheet(
            f"color:{txt_color}; font-size:{font_size}; font-weight:{txt_weight}; border:none; background:transparent;"
        )

        row.addWidget(ico)
        row.addWidget(lbl)
        row.addStretch()

        return btn

#Topbar
class Topbar(QFrame):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setFixedHeight(70)
        self.setStyleSheet("background:transparent; border:none;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(28, 25, 28, 0)

        title = QLabel("Input Produksi")
        title.setStyleSheet(
            "color:#355872; font-size:36px; font-weight:700; border:none; background:transparent;"
        )
        lay.addWidget(title)
        lay.addStretch()

        #User info
        user_ico = QLabel()
        user_ico.setPixmap(qta.icon("fa5s.user-circle", color="#355872").pixmap(50, 50))
        user_ico.setStyleSheet("border:none; background:transparent;")

        name = user.username if user else "Admin"
        role = user.role if user else "Admin"
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            "color:#355872; font-size:18px; font-weight:700; border:none; background:transparent;"
        )
        role_lbl = QLabel(role)
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

#Shared Styles
INPUT_STYLE = """
    QLineEdit {
        border: 1px solid #355872;
        border-radius: 10px;
        padding: 0 12px;
        font-size: 16px;
        background: white;
        color: #355872;
    }
    QLineEdit:focus {
        border: 2px solid #9CD5FF;
    }
"""

ERROR_STYLE = """
    QLineEdit {
        border: 2px solid #FF4D4D;
        border-radius: 10px;
        padding: 0 12px;
        font-size: 16px;
        background: white;
        color: #355872;
    }
"""

COMBO_STYLE = """
    QComboBox {
        border: 1px solid #355872;
        border-radius: 10px;
        padding: 0 12px;
        padding-right: 40px;
        font-size: 14px;
        color: #355872;
        background: white;
    }
    QComboBox::drop-down { border: none; width: 30px; }
    QComboBox::down-arrow { image: none; }
    QComboBox QAbstractItemView {
        border: 1px solid #355872;
        background: #FFFFFF;
        padding: 5px;
        outline: 0px;
        font-size: 14px;
        color: #355872;
    }
    QComboBox QAbstractItemView::item {
        min-height: 30px;
        padding-left: 10px;
        border-radius: 6px;
        font-size: 14px;
        color: #355872;
    }
    QComboBox QAbstractItemView::item:hover { background-color: #7FC8FF; }
    QComboBox QAbstractItemView::item:selected { background-color: #9CD5FF; color: #355872; }
"""

DATE_STYLE = """
    QDateEdit {
        border: 1px solid #355872;
        border-radius: 10px;
        padding: 0 12px;
        font-size: 16px;
        background: white;
        color: #355872;
    }
    QDateEdit::drop-down { border: none; width: 0px; }
    
    QCalendarWidget QWidget {
        background-color: #FFFFFF;
        color: #355872;
    }
    QCalendarWidget QAbstractItemView:enabled {
        background-color: #FFFFFF;
        color: #355872;
        selection-background-color: #9CD5FF;
        selection-color: #355872;
    }
    QCalendarWidget QToolButton {
        background-color: transparent;
        color: #355872;
        font-size: 14px;
        font-weight: bold;
        icon-size: 30px;
        border: none;
    }
"""

DEFECT_INPUT_STYLE = """
    QLineEdit {
        border: 1px solid #355872;
        border-radius: 10px;
        padding: 0 12px;
        font-size: 16px;
        background: white;
        color: #355872;
    }
    QLineEdit:read-only {
        color: #355872;
        background: #F0F4F7;
    }
"""

COMBO_ERROR_STYLE = """
    QComboBox {
        border: 2px solid #FF4D4D;
        border-radius: 10px;
        padding: 0 12px;
        padding-right: 40px;
        font-size: 14px;
        color: #355872;
        background: white;
    }
    QComboBox::drop-down { border: none; width: 30px; }
    QComboBox::down-arrow { image: none; }
    QComboBox QAbstractItemView {
        border: 1px solid #355872;
        background: #FFFFFF;
        padding: 5px;
        outline: 0px;
        font-size: 14px;
        color: #355872;
    }
"""

def make_dropdown(items, placeholder):
    cb = QComboBox()
    cb.setEditable(True)
    cb.lineEdit().setReadOnly(False)
    cb.setFixedHeight(50)
    cb.setStyleSheet(COMBO_STYLE)
    cb.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

    cb.addItem("")
    cb.addItems(items)

    cb.lineEdit().setPlaceholderText(placeholder)
    cb.completer().setFilterMode(Qt.MatchFlag.MatchContains)

    # Custom down arrow
    icon_lbl = QLabel(cb)
    icon_lbl.setPixmap(qta.icon("fa5s.angle-down", color="#355872").pixmap(25, 25))
    icon_lbl.setStyleSheet("border:none; background:transparent;")
    icon_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    original_resize = cb.resizeEvent

    def _reposition(e):
        icon_lbl.move(cb.width() - 30, (cb.height() - 20) // 2)
        original_resize(e)

    cb.resizeEvent = _reposition
    return cb

def make_date_field_v2(label_text, show_title=False):
    """Returns (vbox, (t_cb, b_cb, th_cb), (t_err, b_err, th_err))"""
    main_vbox = QVBoxLayout()
    main_vbox.setSpacing(6)

    if show_title:
        title_lbl = make_label(label_text)
        main_vbox.addWidget(title_lbl)

    inputs_hbox = QHBoxLayout()
    inputs_hbox.setSpacing(10)
    inputs_hbox.setContentsMargins(0, 0, 0, 0)

    # Helper for error labels
    def create_error_label():
        lbl = QLabel("")
        lbl.setStyleSheet("""
            color: #FF4D4D;
            font-size: 12px;
            font-weight: 500;
            border:none;
            background:transparent;
        """)
        lbl.setFixedHeight(16)
        return lbl

    # Tanggal
    t_vbox = QVBoxLayout()
    t_vbox.setSpacing(6)
    t_lbl = make_label("Tanggal")
    days = [str(i) for i in range(1, 32)]
    t_cb = make_dropdown(days, "Tgl")
    t_err = create_error_label()
    t_vbox.addWidget(t_lbl)
    t_vbox.addWidget(t_cb)
    t_vbox.addWidget(t_err)
    inputs_hbox.addLayout(t_vbox, 1)

    # Bulan
    b_vbox = QVBoxLayout()
    b_vbox.setSpacing(6)
    b_lbl = make_label("Bulan")
    months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    b_cb = make_dropdown(months, "Bulan")
    b_err = create_error_label()
    b_vbox.addWidget(b_lbl)
    b_vbox.addWidget(b_cb)
    b_vbox.addWidget(b_err)
    inputs_hbox.addLayout(b_vbox, 2)

    # Tahun
    th_vbox = QVBoxLayout()
    th_vbox.setSpacing(6)
    th_lbl = make_label("Tahun")
    years = [str(i).zfill(4) for i in range(2020, 2031)]
    th_cb = make_dropdown(years, "Tahun")
    th_err = create_error_label()
    th_vbox.addWidget(th_lbl)
    th_vbox.addWidget(th_cb)
    th_vbox.addWidget(th_err)
    inputs_hbox.addLayout(th_vbox, 1)

    main_vbox.addLayout(inputs_hbox)
    return main_vbox, (t_cb, b_cb, th_cb), (t_err, b_err, th_err)

def make_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "color: #355872; font-size: 16px; font-weight: 500; "
        "border: none; background: transparent;"
    )
    return lbl


# Form Card (Tanggal, Kategori, Nama Produk, Jumlah)
class FormCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        db = get_db()
        produk_svc = ProdukService(db)
        produks = produk_svc.get_daftar_produk()
        
        self.product_category_map = {p.nama_produk: p.nama_kategori for p in produks}

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(10)

        # Row 1: Tanggal | Kategori Produk
        row1 = QHBoxLayout()
        row1.setSpacing(18)

        # Col Tanggal (Triple Dropdown) - No main title, using individual labels
        lay_tgl, self.tgl_cbs, self.tgl_errs = make_date_field_v2("Tanggal", show_title=False)
        
        col_kat = QVBoxLayout()
        col_kat.setSpacing(6)
        col_kat.addWidget(make_label("Kategori Produk"))
        self.inp_kat = QLineEdit()
        self.inp_kat.setReadOnly(True)
        self.inp_kat.setFixedHeight(50)
        self.inp_kat.setStyleSheet(INPUT_STYLE)
        col_kat.addWidget(self.inp_kat)
        
        # Placeholder for error alignment
        self.err_kat_dummy = QLabel("")
        self.err_kat_dummy.setFixedHeight(16)
        self.err_kat_dummy.setStyleSheet("border: none; background: transparent;")
        col_kat.addWidget(self.err_kat_dummy)

        row1.addLayout(lay_tgl, stretch=1)
        row1.addLayout(col_kat, stretch=1)
        lay.addLayout(row1)

        today = QDate.currentDate()
        months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        self.tgl_cbs[0].setCurrentText(str(today.day()))
        self.tgl_cbs[1].setCurrentText(months[today.month() - 1])
        self.tgl_cbs[2].setCurrentText(str(today.year()))

        # Row 2: Nama Produk | Jumlah Produksi
        row2 = QHBoxLayout()
        row2.setSpacing(18)
        row2.setAlignment(Qt.AlignmentFlag.AlignTop)

        col_nama = QVBoxLayout()
        col_nama.setSpacing(6)
        col_nama.addWidget(make_label("Nama Produk"))
        
        self.combo_produk = QComboBox()
        self.combo_produk.setFixedHeight(50)
        self.combo_produk.setStyleSheet(COMBO_STYLE)
        self.combo_produk.addItems([""] + list(self.product_category_map.keys()))
        self.combo_produk.setEditable(True)
        self.combo_produk.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_produk.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        
        arrow_combo = QLabel(self.combo_produk)
        arrow_combo.setPixmap(qta.icon("fa5s.angle-down", color="#355872").pixmap(25, 25))
        arrow_combo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        arrow_combo.setStyleSheet("border: none; background: transparent;")
        arrow_combo.setFixedSize(25, 25)
        self.combo_produk.resizeEvent = lambda e, c=self.combo_produk, a=arrow_combo: (
            a.move(c.width() - 30, (c.height() - 20) // 2)
        )
        self.combo_produk.currentTextChanged.connect(self.update_category)
        col_nama.addWidget(self.combo_produk)
        
        self.err_produk = QLabel("")
        self.err_produk.setStyleSheet("color: #FF4D4D; font-size: 12px; font-weight: 500; border: none;")
        self.err_produk.setFixedHeight(16)
        col_nama.addWidget(self.err_produk)

        col_jml = QVBoxLayout()
        col_jml.setSpacing(6)
        col_jml.addWidget(make_label("Jumlah Produksi"))
        self.inp_jml = QLineEdit()
        self.inp_jml.setFixedHeight(50)
        self.inp_jml.setPlaceholderText("0")
        self.inp_jml.setStyleSheet(INPUT_STYLE)
        self.inp_jml.setValidator(QIntValidator(0, 9_999_999))
        col_jml.addWidget(self.inp_jml)
        
        self.err_jml = QLabel("")
        self.err_jml.setStyleSheet("color: #FF4D4D; font-size: 12px; font-weight: 500; border: none;")
        self.err_jml.setFixedHeight(16)
        col_jml.addWidget(self.err_jml)

        row2.addLayout(col_nama, stretch=1)
        row2.addLayout(col_jml, stretch=1)
        lay.addLayout(row2)

    def update_category(self, text):
        category = self.product_category_map.get(text, "")
        self.inp_kat.setText(category)

# Defect Row
DEFECT_TYPES = ["Kecacatan Fisik", "Kesalahan Proses", "Kerusakan Material"]

class DefectRow(QFrame):
    def __init__(self, tipe, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(24)

        col_tipe = QVBoxLayout()
        col_tipe.setSpacing(6)
        col_tipe.addWidget(make_label("Tipe Defect"))
        self.inp_tipe = QLineEdit(tipe)
        self.inp_tipe.setFixedHeight(50)
        self.inp_tipe.setReadOnly(True)
        self.inp_tipe.setStyleSheet(DEFECT_INPUT_STYLE)
        col_tipe.addWidget(self.inp_tipe)

        col_jml = QVBoxLayout()
        col_jml.setSpacing(6)
        col_jml.addWidget(make_label("Jumlah Defect"))
        self.inp_jml = QLineEdit()
        self.inp_jml.setFixedHeight(50)
        self.inp_jml.setPlaceholderText("0")
        self.inp_jml.setStyleSheet(DEFECT_INPUT_STYLE)
        self.inp_jml.setValidator(QIntValidator(0, 9_999_999))
        col_jml.addWidget(self.inp_jml)

        lay.addLayout(col_tipe, stretch=1)
        lay.addLayout(col_jml, stretch=1)

#Defect Card
class DefectCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.defect_rows = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(18)

        title = QLabel("Detail Defect")
        title.setStyleSheet(
            "color: #355872; font-size: 20px; font-weight: 700; "
            "border: none; background: transparent;"
        )
        lay.addWidget(title)

        for tipe in DEFECT_TYPES:
            row = DefectRow(tipe)
            self.defect_rows.append(row)
            lay.addWidget(row)

# Bottom Buttons
class BottomBar(QFrame):
    def __init__(self, parent=None, form_card=None, defect_card=None):
        super().__init__(parent)
        self.form_card = form_card
        self.defect_card = defect_card
        self.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 30, 0)
        lay.setSpacing(30)

        # Stretch kiri
        lay.addStretch()
        self.btn_save = QPushButton(" Simpan Data")
        self.btn_save.setIcon(qta.icon("mdi.content-save-outline", color="#355872"))
        self.btn_save.setIconSize(QSize(28, 28))
        self.btn_save.setFixedHeight(44)
        self.btn_save.setFixedWidth(160)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #9CD5FF;
                color: #355872;
                font-size: 16px;
                font-weight: 600;
                border: none;
                border-radius: 12px;
                padding: 0 14px;
            }
            QPushButton:hover { background-color: #E3F3FF; }
        """)
       
        sh1 = QGraphicsDropShadowEffect()
        sh1.setBlurRadius(14)
        sh1.setOffset(0, 4)
        sh1.setColor(QColor(53, 88, 114, 60))
        self.btn_save.setGraphicsEffect(sh1)

        self.btn_reset = QPushButton(" Reset")
        self.btn_reset.setIcon(qta.icon("mdi.refresh", color="#355872"))
        self.btn_reset.setIconSize(QSize(28, 28))
        self.btn_reset.setFixedHeight(44)
        self.btn_reset.setFixedWidth(130)
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #355872;
                font-size: 16px;
                font-weight: 600;
                border: 1px solid #B0CDE0;
                border-radius: 12px;
                padding: 0 14px;
            }
            QPushButton:hover {
                background-color: #EAF6FF;
            }
        """)

        sh2 = QGraphicsDropShadowEffect()
        sh2.setBlurRadius(14)
        sh2.setOffset(0, 4)
        sh2.setColor(QColor(0, 0, 0, 15))
        self.btn_reset.setGraphicsEffect(sh2)

        lay.addStretch(2)
        lay.addWidget(self.btn_save)
        lay.addWidget(self.btn_reset)
        lay.addStretch(2)

        # Stretch kanan
        lay.addStretch()
        
        self.btn_save.clicked.connect(self.save_data)
        self.btn_reset.clicked.connect(self.reset_form)

    def save_data(self):
        if not self.form_card: return
        
        is_valid = True

        # 1. Validasi Dropdown Tanggal
        all_date_inputs = [
            (self.form_card.tgl_cbs[0], self.form_card.tgl_errs[0], "Tanggal wajib diisi"),
            (self.form_card.tgl_cbs[1], self.form_card.tgl_errs[1], "Bulan wajib diisi"),
            (self.form_card.tgl_cbs[2], self.form_card.tgl_errs[2], "Tahun wajib diisi")
        ]

        for cb, err_lbl, err_text in all_date_inputs:
            if cb.currentText().strip() == "":
                cb.setStyleSheet(COMBO_ERROR_STYLE)
                err_lbl.setText(err_text)
                is_valid = False
            else:
                cb.setStyleSheet(COMBO_STYLE)
                err_lbl.setText("")

        # Validasi logika tanggal (jika semua dropdown terisi)
        if is_valid:
            month_map = {
                "Januari": 1, "Februari": 2, "Maret": 3, "April": 4, "Mei": 5, "Juni": 6,
                "Juli": 7, "Agustus": 8, "September": 9, "Oktober": 10, "November": 11, "Desember": 12
            }
            try:
                d = int(self.form_card.tgl_cbs[0].currentText())
                m = month_map[self.form_card.tgl_cbs[1].currentText()]
                y = int(self.form_card.tgl_cbs[2].currentText())
                check_date = QDate(y, m, d)
                if not check_date.isValid():
                    self.form_card.tgl_errs[0].setText("Tanggal tidak valid")
                    self.form_card.tgl_cbs[0].setStyleSheet(COMBO_ERROR_STYLE)
                    is_valid = False
            except:
                is_valid = False

        # 2. Validasi Nama Produk
        self.form_card.combo_produk.setStyleSheet(COMBO_STYLE)
        self.form_card.err_produk.setText("")

        if self.form_card.combo_produk.currentText().strip() == "":
            self.form_card.combo_produk.setStyleSheet(COMBO_ERROR_STYLE)
            self.form_card.err_produk.setText("Nama produk wajib diisi")
            is_valid = False

        # 3. Validasi Jumlah Produksi
        self.form_card.inp_jml.setStyleSheet(INPUT_STYLE)
        self.form_card.err_jml.setText("")
        
        jml_val = self.form_card.inp_jml.text().strip()
        if not jml_val or int(jml_val) <= 0:
            self.form_card.inp_jml.setStyleSheet(ERROR_STYLE)
            self.form_card.err_jml.setText("Jumlah produksi harus lebih dari 0")
            is_valid = False
            
        if not is_valid:
            return

        # Success logic placeholder
        print("Data saved successfully!")

    def reset_form(self):
        if not self.form_card: return
        # Reset dropdowns tanggal ke hari ini
        self.form_card.tgl_cbs[0].setCurrentIndex(0)
        self.form_card.tgl_cbs[1].setCurrentIndex(0)
        self.form_card.tgl_cbs[2].setCurrentIndex(0)
        
        # Reset field lainnya
        self.form_card.combo_produk.setCurrentIndex(0)
        self.form_card.combo_produk.setStyleSheet(COMBO_STYLE)   # ← tambah ini
        self.form_card.err_produk.setText("")
        self.form_card.inp_jml.clear()
        self.form_card.inp_jml.setStyleSheet(INPUT_STYLE)
        self.form_card.err_jml.setText("")
        
        # Reset error dropdown tanggal
        for cb in self.form_card.tgl_cbs:
            cb.setStyleSheet(COMBO_STYLE)
        for err in self.form_card.tgl_errs:
            err.setText("")
        
        if self.defect_card:
            for row in self.defect_card.defect_rows:
                row.inp_jml.clear()

#Main Window
class InputProduksiWindow(GradientBackground):
    logout_clicked = pyqtSignal()

    def __init__(
        self,
        user=None,
        session=None,
        on_logout=None,
        embedded=False,
        on_back=None,
    ):
        super().__init__()
        self.user = user
        self.session = session
        self.on_logout = on_logout
        self.embedded = embedded
        self.on_back = on_back
        if not embedded:
            self.setWindowTitle("SiMonPro - Input Produksi")
        self.init_ui()

    def init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        if not self.embedded:
            self.sidebar = Sidebar()
            self.sidebar.menu_changed.connect(self.navigate_to)
            self.sidebar.menu_changed.connect(self.sidebar.set_active)
            self.sidebar.menu_clicked.connect(self._handle_menu_clicked)
            self.sidebar.logout_clicked.connect(self.logout_clicked)
            if self.on_logout:
                self.sidebar.logout_clicked.connect(self.on_logout)
            root.addWidget(self.sidebar)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(0)
        c_lay.addWidget(Topbar(user=self.user))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(28, 16, 28, 28)
        inner_lay.setSpacing(18)
        
        self.form_card = FormCard()
        self.defect_card = DefectCard()
        self.bottom_bar = BottomBar(form_card=self.form_card, defect_card=self.defect_card)
        
        inner_lay.addWidget(self.form_card)
        inner_lay.addWidget(self.defect_card)
        inner_lay.addWidget(self.bottom_bar)
        inner_lay.addStretch()
        scroll.setWidget(inner)
        c_lay.addWidget(scroll)
        root.addWidget(content)

    def navigate_to(self, label):
        if self.embedded:
            parent = self.parent()
            while parent and not hasattr(parent, "navigate_to"):
                parent = parent.parent()
            if parent and hasattr(parent, "navigate_to"):
                parent.navigate_to(label)

    def _handle_menu_clicked(self, label):
        if label == "Input Produksi":
            return
        if self.on_back:
            self.on_back(label)

    def keyPressEvent(self, event):
        if not self.embedded and event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = InputProduksiWindow()
    window.showMaximized()
    sys.exit(app.exec())
