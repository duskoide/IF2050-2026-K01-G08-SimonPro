import sys
import os

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy,
    QScrollArea, QGraphicsDropShadowEffect, QLineEdit,
    QGridLayout
)
from PyQt6.QtGui import (
    QPainter, QLinearGradient, QColor,
    QBrush, QFont, QPen, QPainterPath, QPixmap
)
from PyQt6.QtCore import Qt, QSize, QPointF, QRectF
import qtawesome as qta

# Background radial gradient
class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(
            0, self.height(),
            self.width(), 0
        )
        gradient.setColorAt(0.0, QColor("#9CD5FF"))
        gradient.setColorAt(0.3, QColor("#EAF6FF"))
        gradient.setColorAt(0.7, QColor("#F7F8F0"))
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
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 10))
        self.setGraphicsEffect(shadow)

#Image Placeholder
class ImagePlaceholder(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(140)
        self.setStyleSheet("""
            QFrame {
                background-color: #F0F0F0;
                border-radius: 8px;
                border: 1px solid #D0D0D0;
            }
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        ico = QLabel()
        ico.setPixmap(qta.icon("mdi.image-outline", color="#AAAAAA").pixmap(40, 40))
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setStyleSheet("border: none; background: transparent;")
        lay.addWidget(ico, alignment=Qt.AlignmentFlag.AlignCenter)

#Product Card
class ProductCard(Card):
    def __init__(self, name, code, category, description, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
 
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(5)
 
        # Image placeholder
        lay.addWidget(ImagePlaceholder())
 
        # Name row + code badge
        name_row = QHBoxLayout()
        name_row.setSpacing(6)
 
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet(
            "color: #355872; font-size: 18px; font-weight: 700; "
            "border: none; background: transparent;"
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
 
        # Category
        lbl_cat = QLabel(category)
        lbl_cat.setStyleSheet(
            "color: #355872; font-size: 15px; border: none; background: transparent; font-weight: 600;"
        )
        lay.addWidget(lbl_cat)
 
        # Description
        lbl_desc = QLabel(description)
        lbl_desc.setStyleSheet(
            "color: #355872; font-size: 12px; border: none; background: transparent; font-weight: 500;"
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setFixedHeight(56)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lay.addWidget(lbl_desc)
 
        lay.addSpacing(1)
 
        # Edit button
        btn_edit = QPushButton()
        btn_edit.setText("Edit")
        btn_edit.setIcon(qta.icon("mdi.pencil-outline", color="#355872"))
        btn_edit.setIconSize(QSize(25, 25))
        btn_edit.setFixedHeight(32)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet("""
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
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(53, 88, 114, 80))

        btn_edit.setGraphicsEffect(shadow)
        lay.addWidget(btn_edit, alignment=Qt.AlignmentFlag.AlignHCenter)

#Sidebar
class Sidebar(QFrame):
    MENU = [
        ("ph.chart-line-up", "Dashboard", False),
        ("mdi.package-variant-closed", "Produk", True),
        ("fa5s.bullseye", "Target", False),
        ("mdi.clipboard-text-outline", "Input Produksi", False),
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
        lbl.setStyleSheet(f"color:{txt_color}; font-size:18px; font-weight:{txt_weight}; border:none; background:transparent;")

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

        title = QLabel("Kelola Data Produk")
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

#Search Bar
class SearchBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setStyleSheet("""
            QFrame {
                background: transparent;
                border-radius: 22px;
                border: 2px solid rgba(53, 88, 114, 153);
            }
        """)
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
        self.input.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                color: #355872;
                font-size: 16px;
            }
            QLineEdit::placeholder {
                color: #355872;
            }
        """)
 
        lay.addWidget(ico)
        lay.addWidget(self.input)

#Toolbar
class Toolbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        self.setFixedHeight(54)
 
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
 
        search = SearchBar()
        lay.addWidget(search, stretch=1)
 
        # Edit Kategori button
        btn_cat = QPushButton()
        btn_cat.setText("Edit Kategori")
        btn_cat.setIcon(qta.icon("mdi.pencil-outline", color="#355872"))
        btn_cat.setIconSize(QSize(26, 26))
        btn_cat.setFixedHeight(44)
        btn_cat.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cat.setStyleSheet("""
            QPushButton {
                background-color: #9CD5FF;
                color: #355872;
                font-size: 16px;
                font-weight: 600;
                border-radius: 15px;
                padding: 0 14px;
            }
            QPushButton:hover {
                background-color: #E3F3FF;
            }
        """)
 
        # Tambah Produk button
        btn_add = QPushButton()
        btn_add.setText(" Tambah Produk")
        btn_add.setIcon(qta.icon("fa5s.plus", color="#355872"))
        btn_add.setIconSize(QSize(20, 20))
        btn_add.setFixedHeight(44)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #9CD5FF;
                color: #355872;
                font-size: 16px;
                font-weight: 600;
                border: none;
                border-radius: 15px;
                padding: 0 14px;
            }
            QPushButton:hover {
                background-color: #E3F3FF;
            }
        """)
 
        lay.addWidget(btn_cat)
        lay.addWidget(btn_add)
 
 
#Filter Bar
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
            btn.setIconSize(QSize(24, 24))
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #6B8CA4;
                    font-size: 16px;
                    font-weight: 600;
                    border: none;
                    border-radius: 8px;
                    padding: 0 10px;
                }
            """)
            return btn
 
        lay.addWidget(_filter_btn("mdi.sort", "Urutkan"))
        lay.addWidget(_filter_btn("mdi.filter-outline", "Kelompokkan"))
        lay.addStretch()

#Data Produk
PRODUCTS = [
    ("Kaos Polos",   "PRD-001", "Atasan",   "Kaos polos berbahan katun combed 30s yang lembut, adem, dan mampu menyerap keringat dengan baik."),
    ("Hoodie",       "PRD-002", "Atasan",   "Hoodie dengan bahan fleece dan desain streetwear modern yang mengikuti tren anak generasi sekarang."),
    ("Kemeja",       "PRD-003", "Atasan",   "Kemeja flanel dengan motif kotak-kotak klasik yang tidak lekang oleh waktu. Tebal dan nyaman dipakai."),
    ("Dress Floral", "PRD-004", "Dress",    "Dress wanita dengan motif floral yang memberikan kesan segar dan feminin. Menggunakan bahan ringan dan breathable."),
    ("Rok Plisket",  "PRD-005", "Bawahan",  "Rok plisket dengan desain elegan dan bahan yang jatuh dengan indah. Cocok untuk acara formal maupun kasual."),
    ("Celana Jeans", "PRD-006", "Bawahan",  "Celana jeans model slim fit yang mengikuti bentuk kaki namun tetap nyaman karena bahan stretch yang fleksibel."),
    ("Jaket Dilan",  "PRD-007", "Outerwear","Jaket denim dengan desain klasik yang selalu relevan sepanjang waktu. Dibuat dari bahan denim berkualitas tinggi."),
    ("Blouse",       "PRD-008", "Atasan",   "Blouse wanita dengan desain sederhana namun elegan, cocok untuk digunakan di lingkungan kerja."),
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
 
        # Push cards left if fewer than cols in last row
        for col in range(len(PRODUCTS) % cols, cols):
            if len(PRODUCTS) % cols != 0:
                grid.setColumnStretch(col, 1)
 
 
#Main Window
class ProdukWindow(GradientBackground):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SiMonPro - Kelola Data Produk")
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

        sticky = QWidget()
        sticky.setStyleSheet("background: transparent;")
        sticky_lay = QVBoxLayout(sticky)
        sticky_lay.setContentsMargins(28, 12, 28, 16)
        sticky_lay.setSpacing(16)
        sticky_lay.addWidget(Toolbar())
        sticky_lay.addWidget(FilterBar())
        c_lay.addWidget(sticky)
 
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
 
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(28, 12, 28, 28)
        inner_lay.setSpacing(8)

        # Product grid
        inner_lay.addWidget(ProductGrid())
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
    window = ProdukWindow()
    window.showMaximized()
    sys.exit(app.exec())