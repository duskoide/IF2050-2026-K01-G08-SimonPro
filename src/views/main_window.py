"""Main application window for SiMonPro."""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QApplication,
)

from src.database import test_connection


class MainWindow(QMainWindow):
    """Primary application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SiMonPro — Sistem Monitoring Produksi")
        self.setGeometry(100, 100, 800, 600)

        # Central widget with a simple layout
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title label
        title = QLabel("Selamat Datang di SiMonPro")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # DB status label
        self.status_label = QLabel("Memeriksa koneksi database …")
        self.status_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(self.status_label)

        # Refresh button
        btn = QPushButton("Cek Ulang Koneksi DB")
        btn.clicked.connect(self._check_db)
        layout.addWidget(btn)

        # Add some stretch so widgets sit at the top
        layout.addStretch()

        # Initial DB check
        self._check_db()

    def _check_db(self) -> None:
        """Test database connectivity and update the status label."""
        if test_connection():
            self.status_label.setText("Status Database: ✅ Terhubung")
            self.status_label.setStyleSheet("font-size: 14px; color: green;")
        else:
            self.status_label.setText(
                "Status Database: ❌ Tidak terhubung\\n"
                "Pastikan PostgreSQL berjalan (docker compose up -d)"
            )
            self.status_label.setStyleSheet("font-size: 14px; color: red;")