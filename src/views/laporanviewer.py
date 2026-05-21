import sys
import os

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy,
    QScrollArea, QGraphicsDropShadowEffect, QComboBox,
    QMessageBox
)
from PyQt6.QtGui import (
    QPainter, QLinearGradient, QColor, QBrush, QPixmap,
    QFont
)
from PyQt6.QtCore import Qt, QSize, QDate, QEvent, pyqtSignal
import qtawesome as qta

from src.controllers.LaporanController import LaporanController
from src.views.messageview import SuccessPopup

#Background
class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#DDF3FF"))
        gradient.setColorAt(0.4, QColor("#EAF7FF"))
        gradient.setColorAt(0.5, QColor("#EAF7FF"))
        gradient.setColorAt(0.95, QColor("#F7F8F0"))
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
        ("mdi.clipboard-text-outline", "Input Produksi", False),
        ("mdi.chart-bar", "Pencapaian", False),
        ("ph.warning", "Defect", False),
        ("mdi.file-document-outline", "Laporan", True),
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
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setFixedHeight(70)
        self.setStyleSheet("background:transparent; border:none;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(28, 25, 28, 0)

        title = QLabel("Laporan")
        title.setStyleSheet("color:#355872; font-size:36px; font-weight:700; border:none; background:transparent;")
        lay.addWidget(title)
        lay.addStretch()

        #User info
        user_ico = QLabel()
        user_ico.setPixmap(qta.icon("fa5s.user-circle", color="#355872").pixmap(50, 50))
        user_ico.setStyleSheet("border:none; background:transparent;")

        name = user.username if user else "Admin"
        role = user.role if user else "Admin"
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("color:#355872; font-size:18px; font-weight:700; border:none; background:transparent;")
        role_lbl = QLabel(role)
        role_lbl.setStyleSheet("color:#355872; font-size:14px; font-weight:400; border:none; background:transparent;")

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

#Dropdown style & helper
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

def make_date_field_v2(label_text):
    """Returns (vbox, (t_cb, b_cb, th_cb), (t_err, b_err, th_err))"""
    main_vbox = QVBoxLayout()
    main_vbox.setSpacing(10)

    title_lbl = QLabel(label_text)
    title_lbl.setStyleSheet("color: #355872; font-size: 16px; font-weight: 600; border:none; background:transparent;")
    main_vbox.addWidget(title_lbl)

    inputs_hbox = QHBoxLayout()
    inputs_hbox.setSpacing(10)

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
    t_vbox.setSpacing(4)
    t_lbl = QLabel("Tanggal")
    t_lbl.setStyleSheet("color: #355872; font-size: 16px; font-weight: 500; border:none;")
    days = [str(i) for i in range(1, 32)] # Fixed range to 31
    t_cb = make_dropdown(days, "Tanggal")
    t_err = create_error_label()
    t_vbox.addWidget(t_lbl)
    t_vbox.addWidget(t_cb)
    t_vbox.addWidget(t_err)
    inputs_hbox.addLayout(t_vbox, 1)

    # Bulan
    b_vbox = QVBoxLayout()
    b_vbox.setSpacing(4)
    b_lbl = QLabel("Bulan")
    b_lbl.setStyleSheet("color: #355872; font-size: 16px; font-weight: 500; border:none;")
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
    th_vbox.setSpacing(4)
    th_lbl = QLabel("Tahun")
    th_lbl.setStyleSheet("color: #355872; font-size: 16px; font-weight: 500; border:none;")
    years = [str(i).zfill(4) for i in range(2020, 2031)]
    th_cb = make_dropdown(years, "Tahun")
    th_err = create_error_label()
    th_vbox.addWidget(th_lbl)
    th_vbox.addWidget(th_cb)
    th_vbox.addWidget(th_err)
    inputs_hbox.addLayout(th_vbox, 1)

    main_vbox.addLayout(inputs_hbox)
    return main_vbox, (t_cb, b_cb, th_cb), (t_err, b_err, th_err)
 
# Form Card
class LaporanCard(Card):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.controller = LaporanController()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
 
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 24)
        lay.setSpacing(25)
 
        # Date row
        date_row = QHBoxLayout()
        date_row.setSpacing(40)
        
        lay_start, self.start_cbs, self.start_errs = make_date_field_v2("Tanggal Mulai")
        lay_end, self.end_cbs, self.end_errs = make_date_field_v2("Tanggal Akhir")
        
        date_row.addLayout(lay_start, stretch=1)
        date_row.addLayout(lay_end, stretch=1)
        lay.addLayout(date_row)
 
        # Generate button — centered
        self.btn = QPushButton(" Download ")
        self.btn.setIcon(qta.icon("mdi.file-document-outline", color="#355872"))
        self.btn.setIconSize(QSize(28, 28))
        self.btn.setFixedHeight(45)
        self.btn.setFixedWidth(200)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setStyleSheet("""
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
        self.btn.setGraphicsEffect(shadow)
        
        self.btn.clicked.connect(self.generate_laporan)
        lay.setSpacing(10)
        lay.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    def validate_inputs(self):
        all_inputs = [
            (self.start_cbs[0], self.start_errs[0], "Tanggal wajib diisi!"),
            (self.start_cbs[1], self.start_errs[1], "Bulan wajib diisi!"),
            (self.start_cbs[2], self.start_errs[2], "Tahun wajib diisi!"),

            (self.end_cbs[0], self.end_errs[0], "Tanggal wajib diisi!"),
            (self.end_cbs[1], self.end_errs[1], "Bulan wajib diisi!"),
            (self.end_cbs[2], self.end_errs[2], "Tahun wajib diisi!")
        ]

        is_valid = True

        # Validasi kosong
        for cb, err_lbl, err_text in all_inputs:
            if cb.currentText().strip() == "":
                cb.setStyleSheet(COMBO_ERROR_STYLE)
                err_lbl.setText(err_text)
                is_valid = False
            else:
                cb.setStyleSheet(COMBO_STYLE)
                err_lbl.setText("")

        # Validasi tanggal jika semua terisi
        if is_valid:
            month_map = {
                "Januari": 1,
                "Februari": 2,
                "Maret": 3,
                "April": 4,
                "Mei": 5,
                "Juni": 6,
                "Juli": 7,
                "Agustus": 8,
                "September": 9,
                "Oktober": 10,
                "November": 11,
                "Desember": 12
            }

            try:
                start_date = QDate(
                    int(self.start_cbs[2].currentText()),
                    month_map[self.start_cbs[1].currentText()],
                    int(self.start_cbs[0].currentText())
                )

                end_date = QDate(
                    int(self.end_cbs[2].currentText()),
                    month_map[self.end_cbs[1].currentText()],
                    int(self.end_cbs[0].currentText())
                )

                if not start_date.isValid():
                    self.start_errs[0].setText("Tanggal tidak valid")
                    self.start_cbs[0].setStyleSheet(COMBO_ERROR_STYLE)
                    is_valid = False

                if not end_date.isValid():
                    self.end_errs[0].setText("Tanggal tidak valid")
                    self.end_cbs[0].setStyleSheet(COMBO_ERROR_STYLE)
                    is_valid = False

                if start_date > end_date:
                    self.end_errs[0].setText("Tanggal akhir harus setelah tanggal mulai")
                    self.end_cbs[0].setStyleSheet(COMBO_ERROR_STYLE)
                    is_valid = False

            except:
                is_valid = False

        if is_valid:
            return start_date.toPyDate(), end_date.toPyDate()

        return None, None

    def generate_laporan(self):
        tanggal_awal, tanggal_akhir = self.validate_inputs()
        if tanggal_awal is None or tanggal_akhir is None:
            return

        dicetak_oleh = getattr(self.user, "username", None) or "Admin"
        output_dir = os.path.join(os.path.expanduser("~"), "Downloads")

        self.btn.setEnabled(False)
        self.btn.setText(" Membuat PDF...")

        try:
            result = self.controller.generate_laporan(
                tanggal_awal=tanggal_awal,
                tanggal_akhir=tanggal_akhir,
                dicetak_oleh=dicetak_oleh,
                output_dir=output_dir,
            )

            # Cek parent window untuk notifikasi kustom
            parent_window = self.window()
            has_custom_notify = hasattr(parent_window, "tampilkan_sukses") and hasattr(parent_window, "tampilkan_error")

            if result.get("success"):
                msg = f"Laporan berhasil dibuat:\n{result.get('filepath')}"
                if has_custom_notify:
                    parent_window.tampilkan_sukses(msg)
                else:
                    QMessageBox.information(self, "Laporan berhasil", msg)
            else:
                msg = result.get("message", "Laporan gagal dibuat.")
                if has_custom_notify:
                    parent_window.tampilkan_error(msg)
                else:
                    QMessageBox.warning(self, "Laporan gagal", msg)
        except Exception as exc:
            msg = f"Terjadi kesalahan saat membuat laporan:\n{exc}"
            parent_window = self.window()
            if hasattr(parent_window, "tampilkan_error"):
                parent_window.tampilkan_error(msg)
            else:
                QMessageBox.critical(self, "Laporan gagal", msg)
        finally:
            self.btn.setEnabled(True)
            self.btn.setText(" Download ")

# Main Window
class LaporanWindow(GradientBackground):
    def __init__(self, user=None, session=None, on_logout=None, on_back=None, embedded=False):
        super().__init__()
        self.user = user
        self.session = session
        self.on_logout = on_logout
        self.on_back = on_back
        self.embedded = embedded
        if not embedded:
            self.setWindowTitle("SiMonPro - Laporan")
        self.init_ui()
        self.success_popup = SuccessPopup(self)

    def tampilkan_sukses(self, pesan):
        self.success_popup.show_message(pesan, duration_ms=5000)

    def tampilkan_error(self, pesan):
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
            self.sidebar = Sidebar()
            self.sidebar.menu_clicked.connect(self._handle_menu_clicked)
            self.sidebar.menu_changed.connect(self.sidebar.set_active)
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
 
        inner_lay.addWidget(LaporanCard(user=self.user))
        inner_lay.addStretch()
 
        scroll.setWidget(inner)
        c_lay.addWidget(scroll)
        root.addWidget(content)

    def _handle_menu_clicked(self, label):
        if label == "Laporan":
            return
        if self.on_back:
            self.on_back(label)
 
    def keyPressEvent(self, event):
        if not self.embedded and event.key() == Qt.Key.Key_Escape:
            self.close()
 
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LaporanWindow()
    window.showMaximized()
    sys.exit(app.exec())
