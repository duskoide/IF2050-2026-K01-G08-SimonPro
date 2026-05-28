import sys
import os

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame,
    QScrollArea, QGraphicsDropShadowEffect, QLineEdit,
    QComboBox, QHeaderView, QTableWidget, QTableWidgetItem
)
from PyQt6.QtGui import (
    QPainter, QLinearGradient, QColor,
    QBrush, QPixmap,
    QIntValidator
)
from PyQt6.QtCore import Qt, QSize, QDate, pyqtSignal
import qtawesome as qta

from calendar import monthrange

from src.database.db_connection import get_db
from src.controllers.TargetController import TargetController
from src.views.messageview import SuccessPopup
from src.views.OverwriteTarget import TargetPopup

# Background linear gradient
class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#F7F8F0"))
        gradient.setColorAt(1.0, QColor("#B8E4FF"))
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
        ("fa5s.bullseye", "Target", True),
        ("mdi.clipboard-text-outline", "Input Produksi", False),
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

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
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

        self.set_active("Target")
        lay.addStretch()
        logout_btn = self._menu_btn("mdi.logout", "Keluar", False)
        logout_btn.mousePressEvent = self._make_logout_handler()
        lay.addWidget(logout_btn)
        lay.addSpacing(16)

    def _make_menu_handler(self, label):
        def handler(event):
            if event.button() == Qt.MouseButton.LeftButton:
                if self.user and self.user.role == "owner" and label in ["Target", "Input Produksi"]:
                    from src.views.ownerview import OwnerPopup
                    popup = OwnerPopup(self.parent())
                    popup.show_message("Owner tidak memiliki akses untuk menu ini!")
                    popup.exec()
                    return
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
            is_restricted = self.user and self.user.role == "owner" and lbl in ["Target", "Input Produksi"]
            if lbl == label:
                btn.setStyleSheet(self.ACTIVE_STYLE)
                ico_color = "#355872"
                txt_color = "#355872"
                txt_weight = "700"
            else:
                btn.setStyleSheet(self.INACTIVE_STYLE)
                if is_restricted:
                    ico_color = "rgba(247, 248, 240, 0.4)"
                    txt_color = "rgba(247, 248, 240, 0.4)"
                else:
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

        is_restricted = self.user and self.user.role == "owner" and label in ["Target", "Input Produksi"]
        if active:
            btn.setStyleSheet(self.ACTIVE_STYLE)
            ico_color  = "#355872"
            txt_color  = "#355872"
            txt_weight = "700"
        else:
            btn.setStyleSheet(self.INACTIVE_STYLE)
            if is_restricted:
                ico_color = "rgba(247, 248, 240, 0.4)"
                txt_color = "rgba(247, 248, 240, 0.4)"
            else:
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
        font_size = "16px" if label == "Input Produksi" else "18px"
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

        title = QLabel("Pengaturan Target")
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

#Shared field label
def make_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "color: #355872; font-size: 16px; font-weight: 500; "
        "border: none; background: transparent;"
    )
    return lbl

#Shared input style
INPUT_STYLE = """
    QLineEdit {
        border: 1px solid #355872;
        border-radius: 10px;
        padding: 8px 12px;
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
        padding: 8px 12px;
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
        height: 45px;
    }
    QComboBox::drop-down {
        border: none;
        width: 30px;
    }
    QComboBox QAbstractItemView {
        border: 1px solid #355872;
        border-radius: 1px;
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
    QComboBox QAbstractItemView::item:hover {
        background-color: #7FC8FF;
    }
    QComboBox QAbstractItemView::item:selected {
        background-color: #9CD5FF;
        color: #355872;
    }
"""

def make_dropdown(items, placeholder):
    cb = QComboBox()
    cb.setEditable(True)
    cb.lineEdit().setReadOnly(False)
    cb.setFixedHeight(45)
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
    cb.lineEdit().setReadOnly(False)
    return cb

#Form Card Target Baru
class FormCard(Card):
    save_clicked = pyqtSignal(int, str, str, int, int, int, int)

    def __init__(self, parent=None, products=None):
        super().__init__(parent)
        self._products = products or []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        title = QLabel("Tambah Target Baru")
        title.setStyleSheet(
            "color: #355872; font-size: 20px; font-weight: 700; "
            "border: none; background: transparent;"
        )
        lay.addWidget(title)

        row1 = QHBoxLayout()
        row1.setSpacing(18)
        col_produk = QVBoxLayout()
        col_produk.setSpacing(4)
        col_produk.addWidget(make_label("Pilih Produk"))
        self.combo_produk = QComboBox()
        self.combo_produk.setFixedHeight(40)
        self.combo_produk.setStyleSheet(COMBO_STYLE)
        self._refresh_combo()
        self.combo_produk.setEditable(True)
        self.combo_produk.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_produk.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        arrow_combo = QLabel(self.combo_produk)
        arrow_combo.setPixmap(qta.icon("fa5s.angle-down", color="#355872").pixmap(24, 24))
        arrow_combo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        arrow_combo.setStyleSheet("border: none; background: transparent;")
        arrow_combo.setFixedSize(25, 25)
        self.combo_produk.resizeEvent = lambda e, c=self.combo_produk, a=arrow_combo: (
            a.move(c.width() - 28, (c.height() - 20) // 2)
        )
        col_produk.addWidget(self.combo_produk)

        self.err_produk = QLabel("")
        self.err_produk.setVisible(False)
        self.err_produk.setStyleSheet("color: #FF4D4D; font-size: 12px; font-weight: 500; border: none; background: transparent;")
        col_produk.addWidget(self.err_produk)

        col_kat = QVBoxLayout()
        col_kat.setSpacing(4)
        col_kat.addWidget(make_label("Kategori Produk"))
        self.inp_kat = QLineEdit()
        self.inp_kat.setFixedHeight(40)
        self.inp_kat.setReadOnly(True)
        self.inp_kat.setPlaceholderText("")
        self.inp_kat.setStyleSheet(INPUT_STYLE)
        col_kat.addWidget(self.inp_kat)

        row1.addLayout(col_produk, stretch=1)
        row1.addLayout(col_kat, stretch=1)
        lay.addLayout(row1)

        self.err_produk.setVisible(False)
        lay.addWidget(self.err_produk)

        row2 = QHBoxLayout()
        row2.setSpacing(20)

        col_bul = QVBoxLayout()
        col_bul.setSpacing(4)
        col_bul.addWidget(make_label("Target Bulanan"))
        self.inp_bul = QLineEdit()
        self.inp_bul.setFixedHeight(40)
        self.inp_bul.setPlaceholderText("0")
        self.inp_bul.setStyleSheet(INPUT_STYLE)
        self.inp_bul.setValidator(QIntValidator(0, 9_999_999))
        col_bul.addWidget(self.inp_bul)
       
        self.err_bul = QLabel("")
        self.err_bul.setStyleSheet("color: #FF4D4D; font-size: 12px; font-weight: 500; border: none;")
        col_bul.addWidget(self.err_bul)

        col_har = QVBoxLayout()
        col_har.setSpacing(4)
        col_har.addWidget(make_label("Target Harian"))
        self.inp_har = QLineEdit()
        self.inp_har.setFixedHeight(40)
        self.inp_har.setPlaceholderText("0")
        self.inp_har.setStyleSheet(INPUT_STYLE)
        self.inp_har.setValidator(QIntValidator(0, 9_999_999))
        col_har.addWidget(self.inp_har)

        self.err_har = QLabel("")
        self.err_har.setStyleSheet("color: #FF4D4D; font-size: 12px; font-weight: 500; border: none;")
        col_har.addWidget(self.err_har)

        row2.addLayout(col_bul, stretch=1)
        row2.addLayout(col_har, stretch=1)
        lay.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(20)

        # Periode section dengan 2 dropdown (Bulan & Tahun)
        col_per = QVBoxLayout()
        col_per.setSpacing(10)
        col_per.addWidget(make_label("Periode"))

        # Dropdown container
        dropdowns_hbox = QHBoxLayout()
        dropdowns_hbox.setSpacing(15)

        # Bulan dropdown
        bln_vbox = QVBoxLayout()
        bln_vbox.setSpacing(4)
        bln_lbl = QLabel("Bulan")
        bln_lbl.setStyleSheet("color: #355872; font-size: 16px; font-weight: 500; border:none;")
        months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        self.combo_bulan = make_dropdown(months, "Bulan")
        bln_vbox.addWidget(bln_lbl) 
        bln_vbox.addWidget(self.combo_bulan)
        dropdowns_hbox.addLayout(bln_vbox, 1)

        # Tahun dropdown
        thn_vbox = QVBoxLayout()
        thn_vbox.setSpacing(4)
        thn_lbl = QLabel("Tahun")
        thn_lbl.setStyleSheet("color: #355872; font-size: 16px; font-weight: 500; border:none;")
        years = [str(i) for i in range(2020, 2031)]
        self.combo_tahun = make_dropdown(years, "Tahun")
        thn_vbox.addWidget(thn_lbl)
        thn_vbox.addWidget(self.combo_tahun)
        dropdowns_hbox.addLayout(thn_vbox, 1)

        col_per.addLayout(dropdowns_hbox)
        row3.addLayout(col_per, stretch=1)
        col_empty = QVBoxLayout()
        row3.addLayout(col_empty, stretch=1)
        lay.addLayout(row3)

        self.btn_save = QPushButton()
        self.btn_save.setText(" Simpan Target")
        self.btn_save.setIcon(qta.icon("mdi.content-save-outline", color="#355872"))
        self.btn_save.setIconSize(QSize(24, 24))
        self.btn_save.setFixedHeight(38)
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
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(14)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(53, 88, 114, 60))
        self.btn_save.setGraphicsEffect(shadow)
        lay.addWidget(self.btn_save)

        self.combo_produk.currentIndexChanged.connect(self.update_category)
        self.inp_bul.textChanged.connect(self._auto_calculate_harian)
        self.combo_bulan.currentIndexChanged.connect(self._auto_calculate_harian)
        self.combo_tahun.currentIndexChanged.connect(self._auto_calculate_harian)
        self.btn_save.clicked.connect(self.save_target)

    def _refresh_combo(self):
        self.combo_produk.blockSignals(True)
        self.combo_produk.clear()
        self.combo_produk.addItem("", None)
        for p in self._products:
            self.combo_produk.addItem(p["nama_produk"], p["produk_id"])
        self.combo_produk.blockSignals(False)

    def set_products(self, products):
        self._products = products
        self._refresh_combo()

    def update_category(self, index):
        produk_id = self.combo_produk.currentData()
        if produk_id is None:
            self.inp_kat.setText("")
            return
        for p in self._products:
            if p["produk_id"] == produk_id:
                self.inp_kat.setText(p.get("nama_kategori", ""))
                return
        self.inp_kat.setText("")

    def _auto_calculate_harian(self):
        bul_text = self.inp_bul.text().strip()
        if bul_text and bul_text.isdigit() and int(bul_text) > 0:
            bulan_map = {
                "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
                "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
                "September": 9, "Oktober": 10, "November": 11, "Desember": 12
            }
            bulan_str = self.combo_bulan.currentText().strip()
            tahun_str = self.combo_tahun.currentText().strip()
            if bulan_str and tahun_str and bulan_str in bulan_map:
                tahun = int(tahun_str)
                bulan = bulan_map[bulan_str]
                days = monthrange(tahun, bulan)[1]
                harian = int(bul_text) // days
                self.inp_har.setText(str(harian))

    def save_target(self):
        self.combo_produk.setStyleSheet(COMBO_STYLE)
        self.inp_bul.setStyleSheet(INPUT_STYLE)
        self.inp_har.setStyleSheet(INPUT_STYLE)
        self.err_produk.setVisible(False)
        self.err_produk.setText("")
        self.err_bul.setText("")
        self.err_har.setText("")

        valid = True
        produk_id = self.combo_produk.currentData()
        nama_produk = self.combo_produk.currentText()

        if not produk_id:
            self.err_produk.setText("Pilih produk terlebih dahulu")
            self.err_produk.setVisible(True)
            self.combo_produk.setStyleSheet(COMBO_STYLE.replace("1px solid #355872", "2px solid #FF4D4D"))
            valid = False

        bul_val = self.inp_bul.text().strip()
        har_val = self.inp_har.text().strip()
        bul_ok = bool(bul_val) and int(bul_val) > 0
        har_ok = bool(har_val) and int(har_val) > 0

        if not bul_ok and not har_ok:
            self.inp_bul.setStyleSheet(ERROR_STYLE)
            self.err_bul.setText("Isi target bulanan atau target harian")
            self.inp_har.setStyleSheet(ERROR_STYLE)
            self.err_har.setText("Isi target bulanan atau target harian")
            valid = False

        if valid:
            bulan_map = {
                "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
                "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
                "September": 9, "Oktober": 10, "November": 11, "Desember": 12
            }

            bulan_str = self.combo_bulan.currentText().strip()
            tahun_str = self.combo_tahun.currentText().strip()

            if not bulan_str or not tahun_str:
                self.err_bul.setText("Periode harus diisi lengkap!")
                valid = False
            else:
                try:
                    tahun = int(tahun_str)
                    bulan = bulan_map.get(bulan_str, 0)
                    if bulan == 0:
                        self.err_bul.setText("Bulan tidak valid!")
                        valid = False
                    else:
                        self.save_clicked.emit(
                            produk_id,
                            nama_produk,
                            self.inp_kat.text(),
                            int(bul_val) if bul_val else 0,
                            int(har_val) if har_val else 0,
                            tahun,
                            bulan,
                        )
                        self.combo_produk.setCurrentIndex(0)
                        self.inp_bul.clear()
                        self.inp_har.clear()
                        self.combo_bulan.setCurrentIndex(0)
                        self.combo_tahun.setCurrentIndex(0)
                except ValueError:
                    self.err_bul.setText("Tahun harus berupa angka!")
                    valid = False

#Table Card (Target Saat ini)
HEADERS = ["Produk", "Kategori", "Periode", "Target Bulanan", "Target Harian"]

class TableCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(320)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)
        title = QLabel("Target Saat Ini")
        title.setStyleSheet(
            "color: #355872; font-size: 20px; font-weight: 700; "
            "border: none; background: transparent;"
        )
        lay.addWidget(title)
       
        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                border: none;
                color: #355872;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #EAF2FA;
                color: #355872;
            }
            QTableWidget::item:selected {
                background-color: #EAF6FF;
                color: #355872;
            }
            QHeaderView::section {
                background: transparent;
                color: #355872;
                font-size: 16px;
                font-weight: 700;
                border: none;
                border-bottom: 2px solid #C8E4F5;
                padding: 8px;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #C8E4F5;
                border-radius: 3px;
            }
        """)

        lay.addWidget(self.table)

    def set_targets(self, target_list):
        self.table.setRowCount(0)
        for t in target_list:
            self._add_row(
                t["produk"],
                t["kategori"],
                t["periode"],
                f"{t['target_bulanan']:,}",
                f"{t['target_harian']:,}",
            )

    def _add_row(self, produk, kat, periode, bul, har):
        row = self.table.rowCount()
        self.table.insertRow(row)
        items = [produk, kat, periode, bul, har]
        for c, val in enumerate(items):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if c == 2:
                item.setForeground(QColor("#7AAACE"))
            self.table.setItem(row, c, item)
        self.table.setRowHeight(row, 44)

# Main Window
class TargetWindow(GradientBackground):
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

        db = get_db()
        self._controller = TargetController(db)
        self._controller.set_on_sukses(self.tampilkan_sukses)
        self._controller.set_on_error(self.tampilkan_error)

        if not embedded:
            self.setWindowTitle("SiMonPro - Pengaturan Target")
        
        self.init_ui()
        self.success_popup = SuccessPopup(self)
        self.refresh_data()

    def refresh_data(self):
        """Memuat ulang data produk dan target."""
        self._load_products()
        self._refresh_table()

    def _load_products(self):
        produk_list = self._controller.get_daftar_produk()
        if hasattr(self, "form_card"):
            self.form_card.set_products(produk_list)
        return produk_list

    def _refresh_table(self):
        target_list = self._controller.get_all_targets_grouped()
        if hasattr(self, "table_card"):
            self.table_card.set_targets(target_list)

    def _on_save_target(self, produk_id, nama_produk, nama_kategori, target_bulanan, target_harian, tahun, bulan):
        # Cek apakah target sudah ada
        if self._controller.check_target_exists(produk_id, tahun, bulan):
            popup = TargetPopup(parent=self)
            popup.show_message(f"Target untuk '{nama_produk}' pada periode tersebut sudah ada!")
            result = popup.exec()
            
            if result == TargetPopup.BATALKAN:
                return

        if self._controller.submit_save_target(produk_id, target_bulanan, target_harian, tahun, bulan):
            self._refresh_table()

    def tampilkan_sukses(self, pesan):
        self.success_popup.show_message(pesan, duration_ms=5000)

    def tampilkan_error(self, pesan):
        # Gunakan popup yang sama tapi dengan warna error
        self.success_popup.show_message(
            pesan,
            bg_color="#FFE5E5",
            text_color="#B3261E",
            icon_color="#B3261E",
            duration_ms=5000
        )

    def init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        if not self.embedded:
            self.sidebar = Sidebar(user=self.user)
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
        inner_lay.setContentsMargins(28, 20, 28, 28)
        inner_lay.setSpacing(18)
        self.table_card = TableCard()
        produk_list = self._load_products()
        self.form_card = FormCard(products=produk_list)
        self.form_card.save_clicked.connect(self._on_save_target)
        inner_lay.addWidget(self.form_card)
        inner_lay.addWidget(self.table_card)
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
        if label == "Target":
            return
        if self.on_back:
            self.on_back(label)

    def keyPressEvent(self, event):
        if not self.embedded and event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = TargetWindow()
    window.showMaximized()
    sys.exit(app.exec())
