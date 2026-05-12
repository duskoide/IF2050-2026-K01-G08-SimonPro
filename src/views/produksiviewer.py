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
from PyQt6.QtCore import Qt, QSize, QDate, QEvent
import qtawesome as qta

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(230)
        self.setStyleSheet(f"QFrame {{ background:{"#355872"}; border:none; }}")

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
        logo_txt.setStyleSheet(f"color:{"#F7F8F0"}; font-size:24px; font-weight:700; border:none; background:transparent;")
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
            lay.addWidget(self._menu_btn(icon_name, label, active))
            lay.addSpacing(6)

        lay.addStretch()

        lay.addWidget(self._menu_btn("mdi.logout", "Keluar", False))
        lay.addSpacing(16)

    def _menu_btn(self, icon_name, label, active):
        btn = QFrame()
        btn.setFixedHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        if active:
            btn.setStyleSheet(f"""
                QFrame {{
                    background: {"#9CD5FF"};
                    border-radius: 10px;
                    border: none;
                }}
            """)
            ico_color  = "#355872"
            txt_color  = "#355872"
            txt_weight = "700"
           
        else:
            btn.setStyleSheet("""
                QFrame {
                    background: transparent;
                    border: none;
                }
                QFrame:hover {
                    background: rgba(156,213,255,0.12);
                    border-radius: 10px;
                }
            """)
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
        lbl.setStyleSheet(f"color:{txt_color}; font-size:{font_size}; font-weight:{txt_weight}; border:none; background:transparent;")

        row.addWidget(ico)
        row.addWidget(lbl)
        row.addStretch()

        return btn

#Topbar
class Topbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        self.setStyleSheet("background:transparent; border:none;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(28, 25, 28, 0)

        title = QLabel("Input Produksi")
        title.setStyleSheet(f"color:{"#355872"}; font-size:36px; font-weight:700; border:none; background:transparent;")
        lay.addWidget(title)
        lay.addStretch()

        #User info
        user_ico = QLabel()
        user_ico.setPixmap(qta.icon("fa5s.user-circle", color="#355872").pixmap(50, 50))
        user_ico.setStyleSheet("border:none; background:transparent;")

        name_lbl = QLabel("Yumna Fathonah")
        name_lbl.setStyleSheet(f"color:{"#355872"}; font-size:18px; font-weight:700; border:none; background:transparent;")
        role_lbl = QLabel("Admin")
        role_lbl.setStyleSheet(f"color:{"#355872"}; font-size:14px; font-weight:400; border:none; background:transparent;")

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
        
        self.product_category_map = {
            'Kaos Polos': 'Atasan',
            'Hoodie': 'Atasan',
            'Dress Floral': 'Dress',
            'Rok Plisket': 'Bawahan',
            'Kemeja': 'Atasan',
            'Celana Jeans': 'Bawahan',
            'Jaket Dilan': 'Outerwear',
            'Blouse': 'Atasan'
        }

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(10)

        # Row 1: Tanggal | Kategori Produk
        row1 = QHBoxLayout()
        row1.setSpacing(18)

        col_tgl = QVBoxLayout()
        col_tgl.setSpacing(6)
        col_tgl.addWidget(make_label("Tanggal"))
        
        self.inp_date = QDateEdit()
        self.inp_date.setFixedHeight(50)
        self.inp_date.setDisplayFormat("dd/MM/yyyy")
        self.inp_date.setDate(QDate.currentDate())
        self.inp_date.setCalendarPopup(True)
        self.inp_date.setStyleSheet(DATE_STYLE)

        self.btn_cal = QPushButton(self.inp_date)
        self.btn_cal.setIcon(qta.icon("mdi.calendar-month-outline", color="#355872"))
        self.btn_cal.setIconSize(QSize(28, 28))
        self.btn_cal.setFixedSize(32, 32)
        self.btn_cal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cal.setStyleSheet("border: none; background: transparent;")
        
        self.inp_date.resizeEvent = lambda e, d=self.inp_date, b=self.btn_cal: (
            b.move(d.width() - 38, (d.height() - 32) // 2))
        self.btn_cal.clicked.connect(self.show_calendar_popup)
        
        col_tgl.addWidget(self.inp_date)

        col_kat = QVBoxLayout()
        col_kat.setSpacing(6)
        col_kat.addWidget(make_label("Kategori Produk"))
        self.inp_kat = QLineEdit()
        self.inp_kat.setReadOnly(True)
        self.inp_kat.setFixedHeight(50)
        self.inp_kat.setStyleSheet(INPUT_STYLE)
        col_kat.addWidget(self.inp_kat)

        row1.addLayout(col_tgl, stretch=1)
        row1.addLayout(col_kat, stretch=1)
        lay.addLayout(row1)

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

        col_jml = QVBoxLayout()
        col_jml.setSpacing(6)
        col_jml.addWidget(make_label("Jumlah Produksi"))
        self.inp_jml = QLineEdit()
        self.inp_jml.setFixedHeight(50)
        self.inp_jml.setPlaceholderText("0")
        self.inp_jml.setStyleSheet(INPUT_STYLE)
        self.inp_jml.setValidator(QIntValidator(0, 9_999_999))
        
        col_jml.addWidget(self.inp_jml)

        row2.addLayout(col_nama, stretch=1)
        row2.addLayout(col_jml, stretch=1)
        lay.addLayout(row2)

        # Row 2 Error: Placeholder to keep row2 aligned
        self.err_jml = QLabel("")
        self.err_jml.setStyleSheet("color: #FF4D4D; font-size: 12px; font-weight: 500; border: none;")
        
        row_err = QHBoxLayout()
        row_err.setSpacing(18)
        row_err.addStretch(1) # For col_nama
        row_err.addWidget(self.err_jml, stretch=1)
        lay.addLayout(row_err)

    def show_calendar_popup(self):
        event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Down, Qt.KeyboardModifier.AltModifier)
        QApplication.postEvent(self.inp_date, event)

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
        
        # Validation
        self.form_card.inp_jml.setStyleSheet(INPUT_STYLE)
        self.form_card.err_jml.setText("")
        
        jml_val = self.form_card.inp_jml.text().strip()
        if not jml_val or int(jml_val) <= 0:
            self.form_card.inp_jml.setStyleSheet(ERROR_STYLE)
            self.form_card.err_jml.setText("Jumlah produksi harus lebih dari 0")
            return
            
        # Success logic placeholder
        print("Data saved successfully!")

    def reset_form(self):
        if not self.form_card: return
        self.form_card.inp_date.setDate(QDate.currentDate())
        self.form_card.combo_produk.setCurrentIndex(0)
        self.form_card.inp_jml.clear()
        self.form_card.inp_jml.setStyleSheet(INPUT_STYLE)
        self.form_card.err_jml.setText("")
        
        if self.defect_card:
            for row in self.defect_card.defect_rows:
                row.inp_jml.clear()

#Main Window
class InputProduksiWindow(GradientBackground):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SiMonPro - Input Produksi")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        self.init_ui()

    def init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(Sidebar())

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(0)
        c_lay.addWidget(Topbar())
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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = InputProduksiWindow()
    window.showMaximized()
    sys.exit(app.exec())