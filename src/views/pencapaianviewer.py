import sys
import os
import math

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy,
    QScrollArea, QGraphicsDropShadowEffect, QMessageBox
)
from PyQt6.QtGui import (
    QPainter, QLinearGradient, QColor, QBrush,
    QPen, QPainterPath, QPixmap, QFont, QFontMetrics
)
from PyQt6.QtCore import Qt, QSize, QRectF, QPointF, pyqtSignal
import qtawesome as qta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from src.controllers.PencapaianController import PencapaianController
from src.services.PencapaianService import PencapaianService


# Background
class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0,  QColor("#F7F8F0"))
        gradient.setColorAt(0.45, QColor("#EEF8FF"))
        gradient.setColorAt(0.75, QColor("#D8EEFF"))
        gradient.setColorAt(1.0,  QColor("#BFE5FF"))
        painter.fillRect(self.rect(), QBrush(gradient))


# Card
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
        shadow.setBlurRadius(35)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(53, 88, 114, 25))
        self.setGraphicsEffect(shadow)


#Sidebar
class Sidebar(QFrame):
    MENU = [
        ("ph.chart-line-up", "Dashboard", False),
        ("mdi.package-variant-closed", "Produk", False),
        ("fa5s.bullseye", "Target", False),
        ("mdi.clipboard-text-outline", "Input Produksi", False),
        ("mdi.chart-bar", "Pencapaian", True),
        ("ph.warning", "Defect", False),
        ("mdi.file-document-outline", "Laporan", False),
    ]

    logout_clicked = pyqtSignal()
    menu_changed = pyqtSignal(str)
    menu_clicked = pyqtSignal(str)

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
            menu_btn = self._menu_btn(icon_name, label, active)
            self._menu_btns[label] = menu_btn
            menu_btn.mousePressEvent = self._make_menu_handler(label)
            lay.addWidget(menu_btn)
            lay.addSpacing(6)

        self.set_active("Pencapaian")

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

        title = QLabel("Pencapaian Produksi")
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

# Stat Card
class StatCard(Card):
    def __init__(self, label, value, sub, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(140)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 18, 24, 18)
        lay.setSpacing(4)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            "color: #7AAACE; font-size: 18px; font-weight: 600; "
            "border: none; background: transparent;"
        )
        val = QLabel(value)
        val.setStyleSheet(
            "color: #355872; font-size: 34px; font-weight: 700; "
            "border: none; background: transparent;"
        )
        sub_lbl = QLabel(sub)
        sub_lbl.setStyleSheet(
            "color: #7AAACE; font-size: 17px; font-weight: 500; border: none; background: transparent;"
        )

        lay.addWidget(lbl)
        lay.addWidget(val)
        lay.addWidget(sub_lbl)
        self.value_lbl = val
        self.sub_lbl = sub_lbl

    def set_value(self, value):
        self.value_lbl.setText(value)

    def set_sub(self, sub):
        self.sub_lbl.setText(sub)


# Matplotlib Canvas Integration
class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='none')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background:transparent;")

class PieChartCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(430)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(25, 18, 20, 15)
        lay.setSpacing(4)
        
        title = QLabel("Distribusi Produksi\nPer Produk")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #7AAACE; font-size: 20px; font-weight: 700; border:none; line-height: 130%;")
        lay.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.canvas = ChartCanvas(self, width=4, height=5)
        self.canvas.fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
        self.ax = self.canvas.fig.add_subplot(111)
        
        self.labels = ['Belum ada data']
        self.sizes = [100.0]
        self.totals = [0]
        self.colors = ['#355872', '#5A88A8', '#9CD5FF', '#D8EEFF']
        
        self.wedges, self.texts = self._draw_pie()
        self.ax.axis('equal')
        self.ax.margins(0)

        self.tooltip = self.ax.text(
            0, 0, "", ha="center", va="center", 
            bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#355872", lw=1, alpha=0.9),
            fontsize=10, fontweight='medium', color='#355872', zorder=10
        )
        self.tooltip.set_visible(False)

        lay.addWidget(self.canvas)
        lay.addSpacing(2)
        
        # Legend layout
        self.legend_lay = QVBoxLayout()
        self.legend_lay.setSpacing(8)
        lay.addLayout(self.legend_lay)
        self._build_legend()

        # Connect hover event
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def _draw_pie(self):
        colors = self.colors[:len(self.labels)]
        if len(colors) < len(self.labels):
            colors.extend([self.colors[-1]] * (len(self.labels) - len(colors)))

        return self.ax.pie(
            self.sizes, startangle=90, colors=colors,
            radius=1.1,
            wedgeprops={
                'edgecolor': 'white',
                'linewidth': 1
            }
        )

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _build_legend(self):
        self._clear_layout(self.legend_lay)
        for i, label in enumerate(self.labels):
            row = QHBoxLayout()
            dot = QLabel()
            dot.setFixedSize(14, 14)
            dot.setStyleSheet(f"background-color: {self.colors[i % len(self.colors)]}; border-radius: 7px; border:none;")
            lbl = QLabel(f"{label}")
            lbl.setStyleSheet("color: #355872; font-size: 16px; font-weight: 500; border:none;")
            val = QLabel(f"{self.sizes[i]}%")
            val.setStyleSheet("color: #7AAACE; font-size: 16px; font-weight: 600; border:none;")
            row.addWidget(dot)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            self.legend_lay.addLayout(row)

    def set_data(self, distribution):
        self.labels = distribution.get("labels") or ["Belum ada data"]
        self.sizes = distribution.get("values") or [100.0]
        self.totals = distribution.get("totals") or [0]
        self.ax.clear()
        self.wedges, self.texts = self._draw_pie()
        self.ax.axis('equal')
        self.tooltip = self.ax.text(
            0, 0, "", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#355872", lw=1, alpha=0.9),
            fontsize=10, fontweight='medium', color='#355872', zorder=10
        )
        self.tooltip.set_visible(False)
        self._build_legend()
        self.canvas.draw_idle()

    def on_hover(self, event):
        if event.inaxes == self.ax:
            for i, wedge in enumerate(self.wedges):
                cont, ind = wedge.contains(event)
                if cont:
                    # Explode effect
                    explode = [0] * len(self.wedges)
                    explode[i] = 0.1
                    for j, w in enumerate(self.wedges):
                        # Calculate center shift for explosion
                        theta = (w.theta1 + w.theta2) / 2
                        x = explode[j] * np.cos(np.deg2rad(theta))
                        y = explode[j] * np.sin(np.deg2rad(theta))
                        w.set_center((x, y))
                        
                    # Update tooltip
                    total = self.totals[i] if i < len(self.totals) else 0
                    self.tooltip.set_text(f"{self.labels[i]}\n{self.sizes[i]}%\n{total:,} unit")
                    self.tooltip.set_position((0, 0)) # Center of pie
                    self.tooltip.set_visible(True)
                    self.canvas.draw_idle()
                    return
            
            # Reset if not hovering any wedge
            for w in self.wedges:
                w.set_center((0, 0))
            self.tooltip.set_visible(False)
            self.canvas.draw_idle()

class BarChartCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(25, 18, 25, 18)

        title = QLabel("Target Produksi")
        title.setStyleSheet("color: #7AAACE; font-size: 20px; font-weight: 700; border:none;")
        lay.addWidget(title)

        self.canvas = ChartCanvas(self, width=6, height=3)
        self.canvas.fig.subplots_adjust(left=0.08, right=0.75, top=0.92, bottom=0.18)
        self.ax = self.canvas.fig.add_subplot(111)
        
        self.weeks = ['Minggu 1', 'Minggu 2', 'Minggu 3', 'Minggu 4']
        self.target_vals = [2500, 2800, 2600, 3000]
        self.actual_vals = [2300, 2900, 2750, 3100]
        
        x = np.arange(len(self.weeks))
        width = 0.3
        
        self.target_bars = self.ax.bar(x - 0.18, self.target_vals, width,
            label='Target', color='#9CD5FF', zorder=3)
        self.actual_bars = self.ax.bar(x + 0.18, self.actual_vals, width,
            label='Actual', color='#7AAACE', zorder=3)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self.weeks, color='#355872', fontsize=9)
        self.ax.tick_params(axis='y', colors='#355872', labelsize=9)
        self.legend = self.ax.legend(frameon=False, loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=12,
                        handlelength=1.2, handleheight=1.2)
        self.legend.get_texts()[0].set_color("#9CD5FF")  # Target
        self.legend.get_texts()[1].set_color("#7AAACE")  # Actual

        # Grid and Spines
        self.ax.yaxis.grid(True, linestyle='--', alpha=0.3, zorder=0)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.tooltip = self.ax.text(0, 0, "",
            ha='center', va='center', fontsize=9, color='#355872',
            bbox=dict(
                boxstyle="round,pad=0.4", fc="white", ec="#355872", lw=1))

        self.tooltip.set_visible(False)
        lay.addWidget(self.canvas)

        # Connect hover event
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def set_data(self, labels, target_vals, actual_vals):
        self.weeks = labels or []
        self.target_vals = target_vals or []
        self.actual_vals = actual_vals or []
        self.ax.clear()

        if not self.weeks:
            self.weeks = ["-"]
            self.target_vals = [0]
            self.actual_vals = [0]

        x = np.arange(len(self.weeks))
        width = 0.3
        self.target_bars = self.ax.bar(x - 0.18, self.target_vals, width,
            label='Target', color='#9CD5FF', zorder=3)
        self.actual_bars = self.ax.bar(x + 0.18, self.actual_vals, width,
            label='Actual', color='#7AAACE', zorder=3)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self.weeks, color='#355872', fontsize=9)
        self.ax.tick_params(axis='y', colors='#355872', labelsize=9)
        max_value = max(self.target_vals + self.actual_vals + [1])
        self.ax.set_ylim(0, max_value * 1.2)
        self.legend = self.ax.legend(frameon=False, loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=12,
                        handlelength=1.2, handleheight=1.2)
        self.legend.get_texts()[0].set_color("#9CD5FF")
        self.legend.get_texts()[1].set_color("#7AAACE")

        self.ax.yaxis.grid(True, linestyle='--', alpha=0.3, zorder=0)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.tooltip = self.ax.text(0, 0, "",
            ha='center', va='center', fontsize=9, color='#355872',
            bbox=dict(
                boxstyle="round,pad=0.4", fc="white", ec="#355872", lw=1))
        self.tooltip.set_visible(False)
        self.canvas.draw_idle()

    def on_hover(self, event):
        vis = self.tooltip.get_visible()
        found = False

        for b in list(self.target_bars) + list(self.actual_bars):
            b.set_alpha(1.0)
            b.set_edgecolor('none')
            b.set_linewidth(0)

        if event.inaxes == self.ax:
            # Target bars
            for i, bar in enumerate(self.target_bars):
                if bar.contains(event)[0]:
                    bar.set_alpha(0.8)
                    bar.set_edgecolor('#355872')
                    bar.set_linewidth(1)
                    self.tooltip.set_text(f"{self.weeks[i]}\nTarget: {self.target_vals[i]}")
                    self.tooltip.set_position((
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() / 2
                    ))
                    self.tooltip.set_visible(True)
                    found = True
                    break

            # Actual bars
            if not found:
                for i, bar in enumerate(self.actual_bars):
                    if bar.contains(event)[0]:
                        bar.set_alpha(0.8)
                        bar.set_edgecolor('#355872')
                        bar.set_linewidth(1)
                        pct = (self.actual_vals[i] / self.target_vals[i]) * 100 if self.target_vals[i] else 0
                        self.tooltip.set_text(
                            f"{self.weeks[i]}\nActual: {self.actual_vals[i]}\n({pct:.1f}% dari target)"
                        )
                        self.tooltip.set_position((
                            bar.get_x() + bar.get_width() / 2,
                            bar.get_height() / 2
                        ))
                        self.tooltip.set_visible(True)
                        found = True
                        break

        if not found and vis:
            self.tooltip.set_visible(False)

        if found or vis != self.tooltip.get_visible():
            self.canvas.draw_idle()

class LineChartCard(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_lay = QHBoxLayout(self)
        main_lay.setContentsMargins(25, 20, 25, 20)
        main_lay.setSpacing(20)

        # Kolom Kiri (Widget Statistik)
        left_col = QVBoxLayout()
        left_col.setSpacing(15)

        title = QLabel("Trend Efisiensi\nProduksi")
        title.setStyleSheet("color: #7AAACE; font-size: 20px; font-weight: 700; border:none; background:transparent;")
        left_col.addWidget(title)

        self.weeks = ['-']
        self.efficiency = [0.0]

        self.badge_layout = QVBoxLayout()
        self.badge_layout.setSpacing(12)
        left_col.addLayout(self.badge_layout)
        
        left_col.addStretch()
        main_lay.addLayout(left_col, 1)

        # Kolom Kanan (Grafik)
        self.canvas = ChartCanvas(self, width=5, height=3)
        self.canvas.fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.25)
        self.ax = self.canvas.fig.add_subplot(111)
        
        x = np.arange(len(self.weeks))
        self.ax.plot(x, self.efficiency, color='#355872', linewidth=3, label='Efisiensi %', zorder=3)
        self.sc = self.ax.scatter(x, self.efficiency, color='#355872', s=60, zorder=4, edgecolor='white', linewidth=1.5)
        
        # Grid & Sumbu
        self.ax.set_ylim(0, 120)
        self.ax.set_yticks([0, 30, 60, 90, 120])
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self.weeks, color='#355872', fontsize=9)
        self.ax.tick_params(axis='y', colors='#355872', labelsize=9)
        
        # Grid dashed (Horizontal & Vertikal)
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#355872', zorder=0)
        
        # Spines
        for spine in ['top', 'right']:
            self.ax.spines[spine].set_visible(False)
        for spine in ['left', 'bottom']:
            self.ax.spines[spine].set_color('#355872')
            self.ax.spines[spine].set_alpha(0.3)
        
        # Legend (Bottom)
        legend = self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), 
                  ncol=1, frameon=False, fontsize=10, 
                  handlelength=1.5, handletextpad=0.5)
        legend.get_texts()[0].set_color("#355872")

        # Tooltip
        self.tooltip = self.ax.text(0, 0, "",
            ha='center', va='bottom', fontsize=9, color='#355872',
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#355872", lw=1),
            zorder=10)
        self.tooltip.set_visible(False)

        main_lay.addWidget(self.canvas, 2)

        # Connect hover event
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def set_data(self, labels, efficiency, insights):
        self.weeks = labels or ["-"]
        self.efficiency = efficiency or [0.0]
        self.ax.clear()

        while self.badge_layout.count():
            item = self.badge_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for text in (insights or ["Belum ada tren pencapaian"]):
            badge = QFrame()
            badge.setStyleSheet("""
                QFrame {
                    background-color: #80BFE6FD;
                    border: 1px solid #355872;
                    border-radius: 12px;
                }
            """)
            badge_lay = QHBoxLayout(badge)
            badge_lay.setContentsMargins(12, 8, 12, 8)
            badge_lay.setSpacing(8)

            lbl = QLabel(text)
            lbl.setStyleSheet("color: #355872; font-size: 15px; font-weight: 500; border:none; background:transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge_lay.addWidget(lbl)
            badge_lay.addStretch()
            self.badge_layout.addWidget(badge)

        x = np.arange(len(self.weeks))
        self.ax.plot(x, self.efficiency, color='#355872', linewidth=3, label='Efisiensi %', zorder=3)
        self.sc = self.ax.scatter(x, self.efficiency, color='#355872', s=60, zorder=4, edgecolor='white', linewidth=1.5)

        y_max = max(self.efficiency + [100])
        y_limit = max(120, y_max * 1.15)
        self.ax.set_ylim(0, y_limit)
        self.ax.set_yticks(np.linspace(0, y_limit, 5))
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self.weeks, color='#355872', fontsize=9)
        self.ax.tick_params(axis='y', colors='#355872', labelsize=9)
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#355872', zorder=0)

        for spine in ['top', 'right']:
            self.ax.spines[spine].set_visible(False)
        for spine in ['left', 'bottom']:
            self.ax.spines[spine].set_color('#355872')
            self.ax.spines[spine].set_alpha(0.3)

        legend = self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2),
                  ncol=1, frameon=False, fontsize=10,
                  handlelength=1.5, handletextpad=0.5)
        legend.get_texts()[0].set_color("#355872")

        self.tooltip = self.ax.text(0, 0, "",
            ha='center', va='bottom', fontsize=9, color='#355872',
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#355872", lw=1),
            zorder=10)
        self.tooltip.set_visible(False)
        self.canvas.draw_idle()

    def on_hover(self, event):
        vis = self.tooltip.get_visible()
        found = False

        if event.inaxes == self.ax:
            cont, ind = self.sc.contains(event)
            if cont:
                idx = ind["ind"][0]
                pos = self.sc.get_offsets()[idx]
                
                self.tooltip.set_text(f"{self.weeks[idx]}\nEfisiensi: {self.efficiency[idx]}%")
                
                # Hitung y tooltip agar tidak keluar batas atas
                y_min, y_max = self.ax.get_ylim()
                offset = (y_max - y_min) * 0.05
                self.tooltip.set_position((pos[0], pos[1] + offset))
                
                self.tooltip.set_visible(True)
                found = True

        if not found and vis:
            self.tooltip.set_visible(False)

        if found or vis != self.tooltip.get_visible():
            self.canvas.draw_idle()

# Main Window
class PencapaianWindow(GradientBackground):
    def __init__(
        self,
        user=None,
        session=None,
        on_logout=None,
        controller=None,
        on_back=None,
        embedded=False,
    ):
        super().__init__()
        self.user = user
        self.session = session
        self.on_logout = on_logout
        self.on_back = on_back
        self.embedded = embedded
        self.controller = controller or PencapaianController(PencapaianService(), viewer=self)
        self.controller.set_viewer(self)
        if not embedded:
            self.setWindowTitle("SiMonPro - Pencapaian Produksi")
        self.init_ui()
        self.load_data()

    def init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        if not self.embedded:
            self.sidebar = Sidebar(user=self.user)
            self.sidebar.menu_clicked.connect(self._handle_menu_clicked)
            self.sidebar.menu_changed.connect(self.sidebar.set_active)
            if self.on_logout:
                self.sidebar.logout_clicked.connect(self.on_logout)
            root.addWidget(self.sidebar)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.addWidget(Topbar(user=self.user))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(28, 16, 28, 28)
        inner_lay.setSpacing(24)

        # 1. Stats Row
        stats_lay = QHBoxLayout()
        stats_lay.setSpacing(20)
        self.card_efficiency = StatCard("Rata-rata Efisiensi", "0%", "-")
        self.card_output = StatCard("Total Output", "0", "Unit produksi")
        self.card_daily = StatCard("Produktivitas Harian", "0", "Unit / hari")
        stats_lay.addWidget(self.card_efficiency, 1)
        stats_lay.addWidget(self.card_output, 1)
        stats_lay.addWidget(self.card_daily, 1)
        inner_lay.addLayout(stats_lay)

        # 2. Main Dashboard Layout (Grid-like)
        dash_lay = QHBoxLayout()
        dash_lay.setSpacing(24)

        # Left Column (Pie Chart)
        left_col = QVBoxLayout()
        self.pie_chart = PieChartCard()
        left_col.addWidget(self.pie_chart)
        dash_lay.addLayout(left_col, 1)

        # Right Column (Bar & Line Chart)
        right_col = QVBoxLayout()
        right_col.setSpacing(24)
        self.bar_chart = BarChartCard()
        self.line_chart = LineChartCard()
        right_col.addWidget(self.bar_chart, stretch=1)
        right_col.addWidget(self.line_chart, stretch=1)
        dash_lay.addLayout(right_col, 2)

        inner_lay.addLayout(dash_lay)
        inner_lay.addStretch()

        scroll.setWidget(inner)
        c_lay.addWidget(scroll)
        root.addWidget(content)

    def load_data(self):
        self.controller.request_insight_pencapaian(months=4)

    def tampilkan_insight_pencapaian(self, data):
        summary = data["summary"]
        charts = data["charts"]

        self.card_efficiency.set_value(f"{summary['average_efficiency']}%")
        self.card_efficiency.set_sub(summary["period_label"])
        self.card_output.set_value(f"{summary['total_output']:,}")
        self.card_output.set_sub(f"Target: {summary['target_total']:,}")
        self.card_daily.set_value(f"{summary['daily_productivity']:,}")
        self.card_daily.set_sub("Unit / hari produksi")

        self.pie_chart.set_data(charts["distribution"])
        self.bar_chart.set_data(charts["labels"], charts["target"], charts["actual"])
        self.line_chart.set_data(charts["labels"], charts["efficiency"], data["insights"])

    def tampilkan_error(self, pesan):
        QMessageBox.warning(self, "Pencapaian Produksi", pesan)

    def _handle_menu_clicked(self, label):
        if label == "Pencapaian":
            return
        if self.on_back:
            self.on_back(label)

    def keyPressEvent(self, event):
        if not self.embedded and event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PencapaianWindow()
    window.showMaximized()
    sys.exit(app.exec())
