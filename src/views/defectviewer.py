import sys
import os

# Tambah root project ke sys.path supaya import src.* berfungsi
# saat file ini dijalankan langsung sebagai script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

os.environ['QT_API'] = 'pyqt6'

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy,
    QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import (
    QPainter, QLinearGradient, QColor, QBrush, QPixmap
)
from PyQt6.QtCore import Qt, QSize
import qtawesome as qta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import numpy as np
from scipy.interpolate import make_interp_spline

from src.services.DefectService import DefectService

# Background
class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0,  QColor("#F7F8F0"))
        gradient.setColorAt(0.42, QColor("#F7F8F0"))
        gradient.setColorAt(0.58, QColor("#F2FAFF"))
        gradient.setColorAt(0.72, QColor("#E7F6FF"))
        gradient.setColorAt(0.86, QColor("#D3EEFF"))
        gradient.setColorAt(1.0,  QColor("#DDF3FF"))

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
        ("mdi.chart-bar", "Pencapaian", False),
        ("ph.warning", "Defect", True),
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

        title = QLabel("Defect")
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

# Stat Card
class StatCard(Card):
    def __init__(self, label, value, sub, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(130)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 16, 22, 16)
        lay.setSpacing(3)

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

# Matplotlib Canvas
class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='none')
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background:transparent;")

# Helper: Generate info badges dari selisih antar bulan
def _gen_defect_info(months, vals):
    items = []
    for i in range(len(vals) - 1, 0, -1):
        diff = abs(vals[i] - vals[i - 1])
        pct  = round(diff / vals[i - 1] * 100) if vals[i - 1] != 0 else 0
        arah = "menurun" if vals[i] < vals[i - 1] else "naik"
        bulan_map = {'Jan': 'Januari', 'Feb': 'Februari', 'Mar': 'Maret',
                     'Apr': 'April', 'May': 'Mei', 'Jun': 'Juni',
                     'Jul': 'Juli', 'Aug': 'Agustus', 'Sep': 'September',
                     'Oct': 'Oktober', 'Nov': 'November', 'Dec': 'Desember'}
        bulan_nama = bulan_map.get(months[i - 1], months[i - 1])
        items.append(f"Tingkat defect {arah} sebesar {pct}% dibandingkan Bulan {bulan_nama}")
    return items


class LineDefectCard(Card):
    def __init__(self, months, vals, parent=None):
        super().__init__(parent)
        self.months = months
        self.vals = vals
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMaximumHeight(550)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(10)

        title = QLabel("Tingkat Defect")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #7AAACE; font-size: 20px; font-weight: 700; "
            "border: none; background: transparent;")
        lay.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Chart
        self.canvas = ChartCanvas(self, width=5, height=3)
        self.canvas.fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.2)
        self.ax = self.canvas.fig.add_subplot(111)

        x    = np.arange(len(self.months))
        if len(self.months) >= 4:
            x_sm = np.linspace(x.min(), x.max(), 300)
            spl  = make_interp_spline(x, self.vals, k=3)
            y_sm = spl(x_sm)
            self.ax.plot(x_sm, y_sm, color='#355872', linewidth=3, label='Defect', zorder=3)
        else:
            self.ax.plot(x, self.vals, color='#355872', linewidth=3, label='Defect', zorder=3)

        self.sc = self.ax.scatter(x, self.vals, color='#355872', s=60, zorder=4, edgecolor='white', linewidth=1.5)

        # Grid & Axis — dynamic y-limit
        max_val = max(self.vals) if self.vals else 100
        y_limit = max(200, int(max_val * 1.2))
        step = max(50, int(y_limit / 4 / 50) * 50)
        self.ax.set_ylim(0, y_limit)
        self.ax.set_yticks(list(range(0, y_limit + 1, step)))
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self.months, color='#355872', fontsize=10)
        self.ax.tick_params(axis='y', colors='#355872', labelsize=10)
        
        # Grid dashed
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#355872', zorder=0)
        
        # Spines
        for spine in ['top', 'right']:
            self.ax.spines[spine].set_visible(False)
        for spine in ['left', 'bottom']:
            self.ax.spines[spine].set_color('#355872')
            self.ax.spines[spine].set_alpha(0.3)

        # Legend (Bottom)
        legend = self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), 
                               ncol=1, frameon=False, fontsize=11, 
                               handlelength=1.5, handletextpad=0.5)
        legend.get_texts()[0].set_color("#355872")

        # Tooltip
        self.tooltip = self.ax.text(0, 0, "",
            ha='center', va='bottom', fontsize=10, color='#355872',
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#355872", lw=1, alpha=0.9),
            zorder=10)
        self.tooltip.set_visible(False)

        lay.addWidget(self.canvas)
        lay.setSpacing(10)

        # Info badges - Centered below chart
        for text in _gen_defect_info(self.months, self.vals):
            badge = QFrame()
            badge.setMinimumWidth(500)
            badge.setStyleSheet("""
                QFrame {
                    background-color: #55BFE6FD;
                    border: 1px solid #355872;
                    border-radius: 12px;
                }
            """)
            b_lay = QHBoxLayout(badge)
            b_lay.setContentsMargins(15, 10, 15, 10)
            lbl = QLabel(text)
            lbl.setStyleSheet(
                "color: #355872; font-size: 16px; font-weight: 600; "
                "border: none; background: transparent;"
            )
            lbl.setWordWrap(True)
            b_lay.addWidget(lbl)
            wrapper = QHBoxLayout()
            wrapper.addSpacing(40) 
            wrapper.addWidget(badge)
            wrapper.addStretch()

            lay.addLayout(wrapper)

        # Connect hover event
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def on_hover(self, event):
        vis = self.tooltip.get_visible()
        found = False

        if event.inaxes == self.ax:
            cont, ind = self.sc.contains(event)
            if cont:
                idx = ind["ind"][0]
                pos = self.sc.get_offsets()[idx]
                self.tooltip.set_text(f"{self.months[idx]}\nDefect: {self.vals[idx]}")

                y_min, y_max = self.ax.get_ylim()
                offset = (y_max - y_min) * 0.05
                self.tooltip.set_position((pos[0], pos[1] + offset))
                self.tooltip.set_visible(True)
                found = True

        if not found and vis:
            self.tooltip.set_visible(False)

        if found or vis != self.tooltip.get_visible():
            self.canvas.draw_idle()

class HBarDefectCard(Card):
    def __init__(self, types, counts, pcts, parent=None):
        super().__init__(parent)
        self.types = types
        self.counts = counts
        self.pcts = pcts
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMaximumHeight(550)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(10)

        title = QLabel("Tingkat Defect Berdasarkan Tipe")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #7AAACE; font-size: 20px; font-weight: 700; "
            "border: none; background: transparent;"
        )
        lay.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Horizontal bar chart
        self.canvas = ChartCanvas(self, width=5, height=3)
        self.canvas.fig.subplots_adjust(left=0.25, right=0.95, top=0.9, bottom=0.15)
        self.ax = self.canvas.fig.add_subplot(111)

        y = np.arange(len(self.types))
        self.bars = self.ax.barh(y, self.counts, color='#9CD5FF',
                                 height=0.8, zorder=3)

        self.ax.set_yticks(y)
        self.ax.set_yticklabels(self.types, color='#355872', fontsize=9)
        self.ax.tick_params(axis='x', colors='#355872', labelsize=10)

        # Dynamic x-axis
        max_count = max(self.counts) if self.counts else 50
        x_limit = max(65, int(max_count * 1.3))
        step = max(15, int(x_limit / 4 / 15) * 15)
        self.ax.set_xlim(0, x_limit)
        self.ax.set_xticks(list(range(0, x_limit + 1, step)))

        self.ax.xaxis.grid(True, linestyle='--', alpha=0.3, color='#355872', zorder=0)
        
        for spine in ['top', 'right']:
            self.ax.spines[spine].set_visible(False)
        for spine in ['left', 'bottom']:
            self.ax.spines[spine].set_color('#355872')
            self.ax.spines[spine].set_alpha(0.3)

        # Tooltip for hover
        self.tooltip = self.ax.text(0, 0, "",
            ha='center', va='center', fontsize=11, color='#355872',
            bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#355872", lw=1, alpha=0.9),
            zorder=10)
        self.tooltip.set_visible(False)

        lay.addWidget(self.canvas)

        # Percentage rows
        for tipe, pct in zip(reversed(self.types), reversed(self.pcts)):
            row_frame = QFrame()
            row_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1.5px solid #355872;
                    border-radius: 12px;
                }
            """)
            r_lay = QHBoxLayout(row_frame)
            r_lay.setContentsMargins(20, 14, 15, 14)
            r_lay.setSpacing(12)

            name_lbl = QLabel(tipe)
            name_lbl.setStyleSheet(
                "color: #355872; font-size: 18px; font-weight: 600; "
                "border: none; background: transparent;"
            )

            badge = QFrame()
            badge.setFixedSize(80, 40)
            badge.setStyleSheet("""
                QFrame {
                    background-color: #B8E4FF;
                    border-radius: 12px;
                    border: none;
                }
            """)
            b_lay = QHBoxLayout(badge)
            b_lay.setContentsMargins(0, 0, 0, 0)
            b_lbl = QLabel(f"{pct}%")
            b_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            b_lbl.setStyleSheet(
                "color: #355872; font-size: 18px; font-weight: 700; "
                "border: none; background: transparent;"
            )
            b_lay.addWidget(b_lbl)

            r_lay.addWidget(name_lbl)
            r_lay.addStretch()
            r_lay.addWidget(badge)
            lay.addWidget(row_frame)

        # Connect hover event
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def on_hover(self, event):
        vis = self.tooltip.get_visible()
        found = False

        for b in self.bars:
            b.set_alpha(1.0)
            b.set_edgecolor('none')
            b.set_linewidth(0)

        if event.inaxes == self.ax:
            for i, bar in enumerate(self.bars):
                if bar.contains(event)[0]:
                    bar.set_alpha(0.8)
                    bar.set_edgecolor('#355872')
                    bar.set_linewidth(1.5)
                    
                    self.tooltip.set_text(f"{self.types[i]}\n{self.counts[i]} unit ({self.pcts[i]}%)")
                    self.tooltip.set_position((
                        bar.get_width() / 2,
                        bar.get_y() + bar.get_height() / 2
                    ))
                    self.tooltip.set_visible(True)
                    found = True
                    break

        if not found and vis:
            self.tooltip.set_visible(False)

        if found or vis != self.tooltip.get_visible():
            self.canvas.draw_idle()


# Main Window
class DefectWindow(GradientBackground):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SiMonPro - Defect")
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
        inner_lay.setSpacing(20)

        # Fetch data from database
        service = DefectService()
        data = service.get_defect_data(months=4)

        months = data["months_labels"]
        vals = data["defect_per_month"]
        types = data["defect_types"]
        counts = data["defect_counts"]
        pcts = data["defect_pcts"]
        total_defect = data["total_defect"]
        defect_rate = data["defect_rate"]
        top_type = data["top_type"]
        top_pct = data["top_pct"]
        mom = data["mom_change"]

        # Stat cards
        mom_arrow = "↑" if mom >= 0 else "↓"
        mom_text = f"{mom_arrow}{abs(mom)}% dari bulan lalu"
        stat_row = QHBoxLayout()
        stat_row.setSpacing(16)
        stat_row.addWidget(StatCard("Total Defect", str(total_defect), mom_text))
        stat_row.addWidget(StatCard("Defect Rate", f"{defect_rate}%", "Target: < 1%"))
        stat_row.addWidget(StatCard("Tipe Defect Terbanyak", top_type, f"{top_pct}% dari total"))
        inner_lay.addLayout(stat_row)

        # Charts row
        chart_row = QHBoxLayout()
        chart_row.setSpacing(16)
        chart_row.addWidget(LineDefectCard(months, vals), stretch=1)
        chart_row.addWidget(HBarDefectCard(types, counts, pcts), stretch=1)
        inner_lay.addLayout(chart_row)

        inner_lay.addStretch()

        scroll.setWidget(inner)
        c_lay.addWidget(scroll)
        root.addWidget(content)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
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
    window = DefectWindow()
    window.showMaximized()
    sys.exit(app.exec())