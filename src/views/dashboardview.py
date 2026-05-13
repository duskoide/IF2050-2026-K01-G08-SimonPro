import os
import sys

os.environ["QT_API"] = "pyqt6"

import qtawesome as qta
from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.services.DashboardService import DashboardService
from src.views.targetviewer import TargetWindow
from src.views.pencapaianviewer import PencapaianWindow
from src.views.defectviewer import DefectWindow
from src.views.produksiviewer import InputProduksiWindow
from src.views.laporanviewer import LaporanWindow


# Background radial gradient
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


# Card
class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
                border: 1px solid #35587226;
            }
            """
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 10))
        self.setGraphicsEffect(shadow)


# Stat Card
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
        lbl_title.setStyleSheet(
            "color:#7AAACE; font-size:20px; border:none; background:transparent;"
        )

        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet(
            "color:#355872; font-size:24px; font-weight:700; border:none; background:transparent;"
        )

        self.lbl_sub = QLabel(sub)
        self.lbl_sub.setStyleSheet(
            "color:#7AAACE; font-size:18px; border:none; background:transparent;"
        )

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
        self.setMouseTracking(True)
        self.hover_index = -1
        self.hover_pos = None

    def set_data(self, labels, target, actual):
        self.labels = labels
        self.target = target
        self.actual = actual
        self.update()

    def mouseMoveEvent(self, event):
        W, H = self.width(), self.height()
        pl, pr = 54, 16
        cw = W - pl - pr
        n = len(self.labels)
        if n > 0:
            gw = cw / n
            x = event.position().x()
            idx = int((x - pl) / gw)
            if 0 <= idx < n:
                self.hover_index = idx
                self.hover_pos = event.position()
            else:
                self.hover_index = -1
        else:
            self.hover_index = -1
        self.update()

    def leaveEvent(self, event):
        self.hover_index = -1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        pl, pr, pt, pb = 54, 16, 16, 62
        cw = W - pl - pr
        ch = H - pt - pb
        max_v = max(self.target + self.actual + [1]) * 1.1
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
            p.drawText(
                0,
                int(y) - 6,
                pl - 6,
                14,
                Qt.AlignmentFlag.AlignRight,
                str(int(max_v * i / 4)),
            )

        # Bars
        for i, lbl in enumerate(self.labels):
            cx = pl + i * gw + gw / 2

            th = (self.target[i] / max_v) * ch
            tx, ty = cx - bw - 2, pt + ch - th
            
            # Hover effect for target bar
            color_target = QColor("#7AAACE")
            if self.hover_index == i:
                color_target = color_target.lighter(110)
            
            p.setBrush(QBrush(color_target))
            p.setPen(Qt.PenStyle.NoPen)
            path = QPainterPath()
            path.addRoundedRect(QRectF(tx, ty, bw, th), 4, 4)
            p.drawPath(path)

            ah = (self.actual[i] / max_v) * ch
            ax, ay = cx + 2, pt + ch - ah
            
            # Hover effect for actual bar
            color_actual = QColor("#9CD5FF")
            if self.hover_index == i:
                color_actual = color_actual.lighter(110)
                
            p.setBrush(QBrush(color_actual))
            path2 = QPainterPath()
            path2.addRoundedRect(QRectF(ax, ay, bw, ah), 4, 4)
            p.drawPath(path2)

            p.setPen(QColor("#355872"))
            p.drawText(
                int(cx - gw / 2),
                H - pb + 6,
                int(gw),
                16,
                Qt.AlignmentFlag.AlignHCenter,
                lbl,
            )

        # Legend
        ly = H - pb + 30
        box_w = 18
        text_w = 50
        spacing = 8
        group_gap = 20
        total_w = box_w + spacing + text_w + group_gap + box_w + spacing + text_w
        start_x = (W - total_w) / 2
        p.setBrush(QBrush(QColor("#7AAACE")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(int(start_x), ly, box_w, 18, 2, 2)
        p.setPen(QColor("#7AAACE"))
        p.drawText(
            int(start_x + box_w + spacing),
            ly,
            text_w,
            18,
            Qt.AlignmentFlag.AlignCenter,
            "Target",
        )

        lx2 = start_x + box_w + spacing + text_w + group_gap
        p.setBrush(QBrush(QColor("#9CD5FF")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(int(lx2), ly, box_w, 18, 2, 2)
        p.setPen(QColor("#9CD5FF"))
        p.drawText(
            int(lx2 + box_w + spacing),
            ly,
            text_w,
            18,
            Qt.AlignmentFlag.AlignCenter,
            "Aktual",
        )

        # Tooltip
        if self.hover_index != -1 and self.hover_pos:
            idx = self.hover_index
            target = self.target[idx]
            actual = self.actual[idx]
            percent = (actual / target * 100) if target > 0 else 0
            
            text = f"{self.labels[idx]}\nTarget: {target:,}\nAktual: {actual:,}\nPencapaian: {percent:.1f}%"
            
            p.setFont(QFont("Inter", 12))
            metrics = p.fontMetrics()
            lines = text.split('\n')
            tw = max([metrics.horizontalAdvance(l) for l in lines]) + 20
            th = metrics.height() * len(lines) + 10
            
            tx = self.hover_pos.x() + 10
            ty = self.hover_pos.y() - th - 10
            
            if tx + tw > W: tx = self.hover_pos.x() - tw - 10
            if ty < 0: ty = self.hover_pos.y() + 10
            
            rect = QRectF(tx, ty, tw, th)
            p.setBrush(QBrush(QColor(53, 88, 114, 230)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(rect, 5, 5)
            
            p.setPen(QColor("#FFFFFF"))
            for i, line in enumerate(lines):
                p.drawText(int(tx + 10), int(ty + metrics.ascent() + 5 + i * metrics.height()), line)


# Line Chart
class LineChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.labels = ["Jan", "Feb", "Mar", "Apr"]
        self.values = [120, 115, 145, 85]
        self.actual = [1000, 1000, 1000, 1000]
        self.setMinimumHeight(380)
        self.setMouseTracking(True)
        self.hover_index = -1
        self.hover_pos = None

    def set_data(self, labels, values, actual=None):
        self.labels = labels
        self.values = values
        if actual:
            self.actual = actual
        self.update()

    def mouseMoveEvent(self, event):
        W, H = self.width(), self.height()
        pl, pr = 54, 16
        cw = W - pl - pr
        n = len(self.labels)
        if n > 1:
            gw = cw / (n - 1)
            x = event.position().x()
            idx = round((x - pl) / gw)
            if 0 <= idx < n:
                self.hover_index = idx
                self.hover_pos = event.position()
            else:
                self.hover_index = -1
        elif n == 1:
            self.hover_index = 0
            self.hover_pos = event.position()
        else:
            self.hover_index = -1
        self.update()

    def leaveEvent(self, event):
        self.hover_index = -1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        pl, pr, pt, pb = 54, 16, 16, 62
        cw = W - pl - pr
        ch = H - pt - pb
        max_v = max(self.values + [1]) * 1.2
        n = len(self.values)
        if n == 0:
            return

        def px(i):
            if n > 1:
                return pl + i * cw / (n - 1)
            return pl + cw / 2

        def py(v):
            return pt + ch - (v / max_v) * ch

        # Grid
        for i in range(5):
            y = pt + ch - i * ch / 4
            p.setPen(QPen(QColor("#7AAACE"), 1, Qt.PenStyle.DashLine))
            p.drawLine(int(pl), int(y), int(W - pr), int(y))
            p.setPen(QColor("#6B8CA4"))
            p.drawText(
                0,
                int(y) - 6,
                pl - 6,
                14,
                Qt.AlignmentFlag.AlignRight,
                str(int(max_v * i / 4)),
            )

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
            p.drawLine(
                QPointF(px(i), py(self.values[i])),
                QPointF(px(i + 1), py(self.values[i + 1])),
            )

        # Titik
        for i in range(n):
            color = QColor("#FFFFFF")
            if self.hover_index == i:
                color = QColor("#9CD5FF")
            p.setBrush(QBrush(color))
            p.setPen(QPen(QColor("#355872"), 2))
            p.drawEllipse(QPointF(px(i), py(self.values[i])), 5, 5)

        # Label X
        p.setPen(QColor("#355872"))
        for i in range(n):
            p.drawText(
                int(px(i)) - 20,
                H - pb + 6,
                40,
                16,
                Qt.AlignmentFlag.AlignHCenter,
                self.labels[i],
            )

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

        p.drawText(
            int(start_x + line_w + spacing),
            ly,
            text_w,
            18,
            Qt.AlignmentFlag.AlignLeft,
            "Defect",
        )

        # Tooltip
        if self.hover_index != -1 and self.hover_pos:
            idx = self.hover_index
            defect = self.values[idx]
            actual = self.actual[idx] if idx < len(self.actual) else 0
            percent = (defect / actual * 100) if actual > 0 else 0
            
            text = f"{self.labels[idx]}\nDefect: {defect:,}\nRate: {percent:.1f}%"
            
            p.setFont(QFont("Inter", 12))
            metrics = p.fontMetrics()
            lines = text.split('\n')
            tw = max([metrics.horizontalAdvance(l) for l in lines]) + 20
            th = metrics.height() * len(lines) + 10
            
            tx = self.hover_pos.x() + 10
            ty = self.hover_pos.y() - th - 10
            
            if tx + tw > W: tx = self.hover_pos.x() - tw - 10
            if ty < 0: ty = self.hover_pos.y() + 10
            
            rect = QRectF(tx, ty, tw, th)
            p.setBrush(QBrush(QColor(53, 88, 114, 230)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(rect, 5, 5)
            
            p.setPen(QColor("#FFFFFF"))
            for i, line in enumerate(lines):
                p.drawText(int(tx + 10), int(ty + metrics.ascent() + 5 + i * metrics.height()), line)


# Sidebar
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
            btn.mousePressEvent = self._make_menu_handler(label)
            lay.addWidget(btn)
            lay.addSpacing(6)

        self.set_active("Dashboard")

        lay.addStretch()

        # Logout button — clickable
        logout_btn = self._menu_btn("mdi.logout", "Keluar")
        logout_btn.mousePressEvent = self._make_logout_handler()
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


# Topbar
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
        title.setStyleSheet(
            "color:#355872; font-size:36px; font-weight:700; border:none; background:transparent;"
        )
        lay.addWidget(title)
        lay.addStretch()

        # User info
        user_ico = QLabel()
        user_ico.setPixmap(qta.icon("fa5s.user-circle", color="#355872").pixmap(50, 50))
        user_ico.setStyleSheet("border:none; background:transparent;")

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            "color:#355872; font-size:18px; font-weight:700; border:none; background:transparent;"
        )
        role_lbl = QLabel(user.role if user else "Admin")
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


# Dashboard Window
class DashboardWindow(GradientBackground):
    def __init__(self, user=None, session=None, on_logout=None):
        super().__init__()
        self.user = user
        self.session = session
        self.on_logout = on_logout
        self._target_window = None
        self.pencapaian_window = None
        self.defect_window = None
        self.input_window = None
        self.dashboard_service = DashboardService()
        self.setWindowTitle("SiMonPro - Dashboard")
        self.init_ui()
        self.load_data()

    def init_ui(self):
        from src.views.produklistview import ProdukWindow

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.menu_changed.connect(self.navigate_to)
        self.sidebar.menu_changed.connect(self.sidebar.set_active)
        self.sidebar.menu_clicked.connect(self._handle_menu_clicked)
        if self.on_logout:
            self.sidebar.logout_clicked.connect(self.on_logout)
        root.addWidget(self.sidebar)

        # Stacked pages
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background:transparent; border:none;")

        # Page 0 — Dashboard
        dashboard_page = QWidget()
        dashboard_page.setStyleSheet("background:transparent;")
        d_lay = QVBoxLayout(dashboard_page)
        d_lay.setContentsMargins(0, 0, 0, 0)
        d_lay.setSpacing(0)
        self.topbar = Topbar(user=self.user)
        d_lay.addWidget(self.topbar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background:transparent; border:none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(28, 8, 28, 28)
        inner_lay.setSpacing(18)

        sub = QLabel("Ringkasan Performa Produksi")
        sub.setStyleSheet(
            "color:#7AAACE; font-size:18px; border:none; background:transparent;"
        )
        inner_lay.addWidget(sub)

        self.stat_row = QHBoxLayout()
        self.stat_row.setSpacing(14)
        self.card_total_produksi = StatCard(
            "mdi.cube-outline", "Total Produksi", "0", "-"
        )
        self.card_pencapaian = StatCard(
            "mdi.trending-up", "Pencapaian Target", "0%", "-"
        )
        self.card_defect = StatCard(
            "mdi.alert-circle-outline", "Tingkat Defect", "0%", "-"
        )
        self.card_jumlah_produk = StatCard(
            "mdi.package-variant", "Jumlah Produk", "0", "-"
        )
        self.stat_row.addWidget(self.card_total_produksi)
        self.stat_row.addWidget(self.card_pencapaian)
        self.stat_row.addWidget(self.card_defect)
        self.stat_row.addWidget(self.card_jumlah_produk)
        inner_lay.addLayout(self.stat_row)

        chart_row = QHBoxLayout()
        chart_row.setSpacing(14)

        self.bar_chart = BarChart()
        bar_card = Card()
        bar_lay = QVBoxLayout(bar_card)
        bar_lay.setContentsMargins(18, 16, 18, 16)
        bar_lay.setSpacing(10)
        bar_title = QLabel("Pencapaian Target")
        bar_title.setStyleSheet(
            "color:#355872; font-size:18px; font-weight:700; border:none; background:transparent;"
        )
        bar_lay.addWidget(bar_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        bar_lay.addWidget(self.bar_chart)

        self.line_chart = LineChart()
        line_card = Card()
        line_lay = QVBoxLayout(line_card)
        line_lay.setContentsMargins(18, 16, 18, 16)
        line_lay.setSpacing(10)
        line_title = QLabel("Tingkat Defect")
        line_title.setStyleSheet(
            "color:#355872; font-size:18px; font-weight:700; border:none; background:transparent;"
        )
        line_lay.addWidget(line_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        line_lay.addWidget(self.line_chart)

        chart_row.addWidget(bar_card)
        chart_row.addWidget(line_card)
        inner_lay.addLayout(chart_row)
        inner_lay.addStretch()

        scroll.setWidget(inner)
        d_lay.addWidget(scroll)

        # Page 1 — Produk
        self.produk_page = ProdukWindow(
            user=self.user,
            session=self.session,
            on_logout=self.on_logout,
            embedded=True,
        )
        # Page 2 — Target
        self.target_page = TargetWindow(
            user=self.user,
            session=self.session,
            on_logout=self.on_logout,
            embedded=True,
        )
        # Page 3 — Defect
        self.defect_page = DefectWindow(
            user=self.user,
            session=self.session,
            on_logout=self.on_logout,
            embedded=True,
        )
        # Page 4 — Input Produksi
        self.input_page = InputProduksiWindow(
            user=self.user,
            session=self.session,
            on_logout=self.on_logout,
            embedded=True,
        )
        # Page 5 — Pencapaian
        self.pencapaian_page = PencapaianWindow(
            user=self.user,
            session=self.session,
            on_logout=self.on_logout,
            embedded=True,
        )
        # Page 6 — Laporan
        self.laporan_page = LaporanWindow(
            user=self.user,
            session=self.session,
            on_logout=self.on_logout,
            embedded=True,
        )
        self.pages.addWidget(dashboard_page)
        self.pages.addWidget(self.produk_page)
        self.pages.addWidget(self.target_page)
        self.pages.addWidget(self.defect_page)
        self.pages.addWidget(self.input_page)
        self.pages.addWidget(self.pencapaian_page)
        self.pages.addWidget(self.laporan_page)

        root.addWidget(self.pages)

    def navigate_to(self, label):
        if label == "Produk":
            self.pages.setCurrentIndex(1)
            return
        if label == "Target":
            self.pages.setCurrentIndex(2)
            return
        if label == "Defect":
            self.pages.setCurrentIndex(3)
            return
        if label == "Input Produksi":
            self.pages.setCurrentIndex(4)
            return
        if label == "Pencapaian":
            self.pages.setCurrentIndex(5)
            return
        if label == "Laporan":
            self.pages.setCurrentIndex(6)
            return

        self.pages.setCurrentIndex(0)
        if label == "Dashboard":
            self.load_data()

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
                charts["labels"], charts["target"], charts["actual"]
            )
            self.line_chart.set_data(charts["labels"], charts["defect"], charts["actual"])
        except Exception as e:
            print(f"[Dashboard] Gagal memuat data: {e}")

    def _handle_menu_clicked(self, label):
        if label in (
            "Dashboard",
            "Produk",
            "Target",
            "Pencapaian",
            "Defect",
            "Input Produksi",
            "Laporan",
        ):
            self.navigate_to(label)

    def _navigate_from_child(self, label):
        if self.pencapaian_window:
            self.pencapaian_window.close()
            self.pencapaian_window = None
        if self.defect_window:
            self.defect_window.close()
            self.defect_window = None
        self.showMaximized()
        self.raise_()
        self.activateWindow()
        self.navigate_to(label)

    def _show_dashboard(self):
        if self.pencapaian_window:
            self.pencapaian_window.close()
            self.pencapaian_window = None
        if self.defect_window:
            self.defect_window.close()
            self.defect_window = None
        self.showMaximized()

    def _handle_child_logout(self):
        if self.pencapaian_window:
            self.pencapaian_window.close()
            self.pencapaian_window = None
        if self.defect_window:
            self.defect_window.close()
            self.defect_window = None
        if self.on_logout:
            self.on_logout()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DashboardWindow()
    window.showMaximized()
    sys.exit(app.exec())
