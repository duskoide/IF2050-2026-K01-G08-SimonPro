import os
import sys

os.environ['QT_API'] = 'pyqt6'

import qtawesome as qta
from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (QBrush, QColor, QFont, QLinearGradient, QPainter,
                         QPainterPath, QPen, QPixmap)
from PyQt6.QtWidgets import (QApplication, QFrame, QGraphicsDropShadowEffect,
                             QHBoxLayout, QLabel, QPushButton, QScrollArea,
                             QSizePolicy, QVBoxLayout, QWidget)

from src.services.DashboardService import DashboardService
from src.views.pencapaianviewer import PencapaianWindow


# Background radial gradient
class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(
            0, self.height(),
            self.width(), 0
        )
        gradient.setColorAt(0.0, QColor("#B8E4FF"))
        gradient.setColorAt(0.2, QColor("#EAF6FF"))
        gradient.setColorAt(0.6, QColor("#F7F8F0"))
        gradient.setColorAt(1.0, QColor("#F7F8F0"))
        painter.fillRect(self.rect(), QBrush(gradient))


#Card
class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {"#FFFFFF"};
                border-radius: 15px;
                border: 1px solid {"#35587226"};
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 10))
        self.setGraphicsEffect(shadow)


#Stat Card
class StatCard(Card):
    def __init__(self, icon_name, title, value, sub, parent=None):
        super().__init__(parent)
        self.setFixedHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(1)

        # Baris atas: ikon bulat + trend
        top = QHBoxLayout()
        top.setSpacing(3)

        icon_bg = QFrame()
        icon_bg.setFixedSize(50, 50)
        icon_bg.setStyleSheet("background:#9CD5FF; border-radius:11px; border:none;")
        icon_inner = QHBoxLayout(icon_bg)
        icon_inner.setContentsMargins(0, 0, 0, 0)
        ico = QLabel()
        ico.setPixmap(qta.icon(icon_name, color="#355872").pixmap(40, 40))
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setStyleSheet("border:none; background:transparent;")
        icon_inner.addWidget(ico, alignment=Qt.AlignmentFlag.AlignCenter)

        top.addWidget(icon_bg)
        top.addStretch()

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color:#7AAACE; font-size:20px; border:none; background:transparent;")

        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet("color:#355872; font-size:24px; font-weight:700; border:none; background:transparent;")

        self.lbl_sub = QLabel(sub)
        self.lbl_sub.setStyleSheet("color:#7AAACE; font-size:18px; border:none; background:transparent;")

        layout.addLayout(top)
        layout.addSpacing(1)
        layout.addWidget(lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addWidget(self.lbl_sub)

    def set_value(self, value):
        self.lbl_value.setText(value)

    def set_sub(self, sub):
        self.lbl_sub.setText(sub)


# Bar Chart
class BarChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.labels = ["Jan", "Feb", "Mar", "Apr"] 
        self.target = [10500, 11000, 11500, 11800] 
        self.actual = [10000, 10800, 11200, 11600]
        self.setMinimumHeight(380)

    def set_data(self, labels, target, actual):
        self.labels = labels
        self.target = target
        self.actual = actual
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        pl, pr, pt, pb = 54, 16, 16, 62
        cw = W - pl - pr
        ch = H - pt - pb
        max_v = max(self.target + self.actual) * 1.1
        n = len(self.labels)
        if n == 0:
            return
        gw = cw / n
        bw = gw * 0.28

        # Grid
        for i in range(5):
            y = pt + ch - i * ch / 4
            p.setPen(QPen(QColor("#7AAACE"), 1, Qt.PenStyle.DashLine))
            p.drawLine(int(pl), int(y), int(W - pr), int(y))
            p.setPen(QColor("#6B8CA4"))
            p.drawText(0, int(y) - 6, pl - 6, 14, Qt.AlignmentFlag.AlignRight,
                       str(int(max_v * i / 4)))

        # Bars
        for i, lbl in enumerate(self.labels):
            cx = pl + i * gw + gw / 2

            th = (self.target[i] / max_v) * ch
            tx, ty = cx - bw - 2, pt + ch - th
            p.setBrush(QBrush(QColor("#7AAACE")))
            p.setPen(Qt.PenStyle.NoPen)
            path = QPainterPath()
            path.addRoundedRect(QRectF(tx, ty, bw, th), 4, 4)
            p.drawPath(path)

            ah = (self.actual[i] / max_v) * ch
            ax, ay = cx + 2, pt + ch - ah
            p.setBrush(QBrush(QColor("#9CD5FF")))
            path2 = QPainterPath()
            path2.addRoundedRect(QRectF(ax, ay, bw, ah), 4, 4)
            p.drawPath(path2)

            p.setPen(QColor("#355872"))
            p.drawText(int(cx - gw / 2), H - pb + 6, int(gw), 16,
                       Qt.AlignmentFlag.AlignHCenter, lbl)

        # Legend
        ly = H - pb + 30
        box_w = 18
        text_w = 50
        spacing = 8
        group_gap = 20
        total_w = (
            box_w + spacing + text_w +
            group_gap +
            box_w + spacing + text_w
        )
        start_x = (W - total_w) / 2
        p.setBrush(QBrush(QColor("#7AAACE")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(int(start_x), ly, box_w, 18, 2, 2)
        p.setPen(QColor("#7AAACE"))
        p.drawText(int(start_x + box_w + spacing), ly, text_w, 18, Qt.AlignmentFlag.AlignCenter, "Target")

        lx2 = start_x + box_w + spacing + text_w + group_gap
        p.setBrush(QBrush(QColor("#9CD5FF")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(int(lx2), ly, box_w, 18, 2, 2)
        p.setPen(QColor("#9CD5FF"))
        p.drawText(int(lx2 + box_w + spacing), ly, text_w, 18, Qt.AlignmentFlag.AlignCenter, "Aktual")


#Line Chart
class LineChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.labels = ["Jan", "Feb", "Mar", "Apr"]
        self.values = [120, 115, 145, 85]
        self.setMinimumHeight(380)

    def set_data(self, labels, values):
        self.labels = labels
        self.values = values
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        pl, pr, pt, pb = 54, 16, 16, 62
        cw = W - pl - pr
        ch = H - pt - pb
        max_v = 180
        n = len(self.values)
        if n == 0:
            return

        def px(i): return pl + i * cw / (n - 1)
        def py(v): return pt + ch - (v / max_v) * ch

        # Grid
        for i in range(5):
            y = pt + ch - i * ch / 4
            p.setPen(QPen(QColor("#7AAACE"), 1, Qt.PenStyle.DashLine))
            p.drawLine(int(pl), int(y), int(W - pr), int(y))
            p.setPen(QColor("#6B8CA4"))
            p.drawText(0, int(y) - 6, pl - 6, 14, Qt.AlignmentFlag.AlignRight,
                       str(int(max_v * i / 4)))

        # Area fill
        fill = QPainterPath()
        fill.moveTo(px(0), pt + ch)
        for i in range(n):
            fill.lineTo(px(i), py(self.values[i]))
        fill.lineTo(px(n - 1), pt + ch)
        fill.closeSubpath()
        fc = QColor("#9CD5FF")
        fc.setAlpha(55)
        p.setBrush(QBrush(fc))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(fill)

        # Line
        p.setPen(QPen(QColor("#355872"), 2.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(n - 1):
            p.drawLine(QPointF(px(i), py(self.values[i])),
                       QPointF(px(i + 1), py(self.values[i + 1])))

        # Titik
        for i in range(n):
            p.setBrush(QBrush(QColor("#FFFFFF")))
            p.setPen(QPen(QColor("#355872"), 2))
            p.drawEllipse(QPointF(px(i), py(self.values[i])), 5, 5)

        # Label X
        p.setPen(QColor("#355872"))
        for i in range(n):
            p.drawText(int(px(i)) - 20, H - pb + 6, 40, 16,
                       Qt.AlignmentFlag.AlignHCenter, self.labels[i])

        # Legend
        ly = H - pb + 30
        text_w = 60
        line_w = 18
        spacing = 10
        total_w = line_w + spacing + text_w
        start_x = (W - total_w) / 2
        # garis legend
        p.setPen(QPen(QColor("#355872"), 3))
        p.drawLine(int(start_x), ly + 9, int(start_x + line_w), ly + 8)

        # titik legend
        p.setBrush(QBrush(QColor("#FFFFFF")))
        p.setPen(QPen(QColor("#355872"), 2))

        p.drawEllipse(QPointF(start_x + line_w / 2, ly + 9), 4, 4)

        # text legend
        p.setPen(QColor("#355872"))

        p.drawText(int(start_x + line_w + spacing), ly, text_w, 18, Qt.AlignmentFlag.AlignLeft, "Defect")


#Sidebar
class Sidebar(QFrame):
    MENU = [
        ("ph.chart-line-up", "Dashboard", True),
        ("mdi.package-variant-closed", "Produk", False),
        ("fa5s.bullseye", "Target", False),
        ("mdi.clipboard-text-outline", "Input Produksi", False),
        ("mdi.chart-bar", "Pencapaian", False),
        ("ph.warning", "Defect", False),
        ("mdi.file-document-outline", "Laporan", False),
    ]

    logout_clicked = pyqtSignal()
    menu_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(230)
        self.setStyleSheet("QFrame { background:#355872; border:none; }")

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
        logo_txt.setStyleSheet("color:#F7F8F0; font-size:24px; font-weight:700; border:none; background:transparent;")
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
            menu_btn = self._menu_btn(icon_name, label, active)
            menu_btn.mousePressEvent = self._make_menu_handler(label)
            lay.addWidget(menu_btn)
            lay.addSpacing(6)

        lay.addStretch()

        # Logout button — clickable
        logout_btn = self._menu_btn("mdi.logout", "Keluar", False)
        logout_btn.mousePressEvent = lambda event: (
            self.logout_clicked.emit()
            if event.button() == Qt.MouseButton.LeftButton else None
        )
        lay.addWidget(logout_btn)
        lay.addSpacing(16)

    def _make_menu_handler(self, label):
        return lambda event: (
            self.menu_clicked.emit(label)
            if event.button() == Qt.MouseButton.LeftButton else None
        )

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
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setFixedHeight(70)
        self.setStyleSheet("background:transparent; border:none;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(28, 25, 28, 0)

        name = user.username if user else "Admin"
        title = QLabel(f"Selamat Datang, {name}!")
        title.setStyleSheet("color:#355872; font-size:36px; font-weight:700; border:none; background:transparent;")
        lay.addWidget(title)
        lay.addStretch()

        #User info
        user_ico = QLabel()
        user_ico.setPixmap(qta.icon("fa5s.user-circle", color="#355872").pixmap(50, 50))
        user_ico.setStyleSheet("border:none; background:transparent;")

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("color:#355872; font-size:18px; font-weight:700; border:none; background:transparent;")
        role_lbl = QLabel(user.role if user else "Admin")
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


# Dashboard Window
class DashboardWindow(GradientBackground):
    def __init__(self, user=None, session=None, on_logout=None):
        super().__init__()
        self.user = user
        self.session = session
        self.on_logout = on_logout
        self.pencapaian_window = None
        self.dashboard_service = DashboardService()
        self.setWindowTitle("SiMonPro - Dashboard")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        self.init_ui()
        self.load_data()

    def init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.menu_clicked.connect(self._handle_menu_clicked)
        if self.on_logout:
            self.sidebar.logout_clicked.connect(self.on_logout)
        root.addWidget(self.sidebar)

        # Konten
        content = QWidget()
        content.setStyleSheet("background:transparent;")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(0)
        self.topbar = Topbar(user=self.user)
        c_lay.addWidget(self.topbar)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background:transparent; border:none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(28, 8, 28, 28)
        inner_lay.setSpacing(18)

        # Sub-judul
        sub = QLabel("Ringkasan Performa Produksi")
        sub.setStyleSheet("color:#7AAACE; font-size:18px; border:none; background:transparent;")
        inner_lay.addWidget(sub)

        # Stat cards — simpan referensi agar bisa di-update
        self.stat_row = QHBoxLayout()
        self.stat_row.setSpacing(14)
        self.card_total_produksi = StatCard("mdi.cube-outline",         "Total Produksi",    "0", "-")
        self.card_pencapaian = StatCard("mdi.trending-up",          "Pencapaian Target", "0%",  "-")
        self.card_defect = StatCard("mdi.alert-circle-outline", "Tingkat Defect",    "0%",   "-")
        self.card_jumlah_produk = StatCard("mdi.package-variant",      "Jumlah Produk",     "0",     "-")
        self.stat_row.addWidget(self.card_total_produksi)
        self.stat_row.addWidget(self.card_pencapaian)
        self.stat_row.addWidget(self.card_defect)
        self.stat_row.addWidget(self.card_jumlah_produk)
        inner_lay.addLayout(self.stat_row)

        # Charts — simpan referensi agar bisa di-update
        chart_row = QHBoxLayout()
        chart_row.setSpacing(14)

        self.bar_chart = BarChart()
        bar_card = Card()
        bar_lay = QVBoxLayout(bar_card)
        bar_lay.setContentsMargins(18, 16, 18, 16)
        bar_lay.setSpacing(10)
        bar_title = QLabel("Pencapaian Target")
        bar_title.setStyleSheet("color:#355872; font-size:18px; font-weight:700; border:none; background:transparent;")
        bar_lay.addWidget(bar_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        bar_lay.addWidget(self.bar_chart)

        self.line_chart = LineChart()
        line_card = Card()
        line_lay = QVBoxLayout(line_card)
        line_lay.setContentsMargins(18, 16, 18, 16)
        line_lay.setSpacing(10)
        line_title = QLabel("Tingkat Defect")
        line_title.setStyleSheet("color:#355872; font-size:18px; font-weight:700; border:none; background:transparent;")
        line_lay.addWidget(line_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        line_lay.addWidget(self.line_chart)

        chart_row.addWidget(bar_card)
        chart_row.addWidget(line_card)
        inner_lay.addLayout(chart_row)
        inner_lay.addStretch()

        scroll.setWidget(inner)
        c_lay.addWidget(scroll)
        root.addWidget(content)

    def load_data(self):
        try:
            summary = self.dashboard_service.get_summary_data()
            charts = self.dashboard_service.get_chart_data()

            # Update stat cards
            total = summary["total_produksi"]
            self.card_total_produksi.set_value(f"{total:,}")
            self.card_total_produksi.set_sub("Total akumulasi")

            pencapaian, target_total = summary["pencapaian_target"]
            self.card_pencapaian.set_value(f"{pencapaian}%")
            self.card_pencapaian.set_sub(f"Target: {target_total:,}")

            defect = summary["tingkat_defect"]
            self.card_defect.set_value(f"{defect}%")
            self.card_defect.set_sub("Dari total produksi")

            jumlah = summary["jumlah_produk"]
            self.card_jumlah_produk.set_value(str(jumlah))
            self.card_jumlah_produk.set_sub("Dalam produksi")

            # Update charts
            self.bar_chart.set_data(
                charts["labels"],
                charts["target"],
                charts["actual"]
            )
            self.line_chart.set_data(
                charts["labels"],
                charts["defect"]
            )
        except Exception as e:
            print(f"[Dashboard] Gagal memuat data: {e}")

    def _handle_menu_clicked(self, label):
        if label == "Pencapaian":
            self._open_pencapaian()

    def _open_pencapaian(self):
        self.pencapaian_window = PencapaianWindow(
            user=self.user,
            session=self.session,
            on_logout=self._handle_child_logout,
            on_back=self._show_dashboard,
        )
        self.pencapaian_window.showMaximized()
        self.hide()

    def _show_dashboard(self):
        if self.pencapaian_window:
            self.pencapaian_window.close()
            self.pencapaian_window = None
        self.showMaximized()

    def _handle_child_logout(self):
        if self.pencapaian_window:
            self.pencapaian_window.close()
            self.pencapaian_window = None
        if self.on_logout:
            self.on_logout()

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
    window = DashboardWindow()
    window.showMaximized()
    sys.exit(app.exec())
