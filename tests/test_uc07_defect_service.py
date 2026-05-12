from datetime import datetime
import importlib
import sys
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication, QLabel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import src.services as services
from src.services import DefectService as DefectServiceFromPackage
import src.views.defectviewer as defectviewer

defect_service_module = importlib.import_module("src.services.DefectService")


class FakeDefectDB:
    def __init__(self):
        self.distinct_months = [
            {"bulan": datetime(2026, 2, 1)},
            {"bulan": datetime(2026, 1, 1)},
        ]

    def execute_query(self, sql, params=None):
        normalized = " ".join(sql.split()).lower()

        if "to_char(date_trunc('month', tanggal), 'mon') as bulan" in normalized:
            return [
                {"bulan": "Jan", "defect": 10},
                {"bulan": "Feb", "defect": 5},
            ]

        if "select distinct date_trunc('month', tanggal) as bulan" in normalized:
            return self.distinct_months

        if "td.nama_defect as tipe" in normalized:
            return [
                {"tipe": "Kecacatan Fisik", "jumlah": 9},
                {"tipe": "Kesalahan Proses", "jumlah": 6},
                {"tipe": "Kerusakan Material", "jumlah": 0},
            ]

        if "coalesce(sum(jumlah_aktual), 0) as total_aktual" in normalized:
            return [{"total_aktual": 1500, "total_defect": 15}]

        raise AssertionError(f"Unexpected query: {sql}")


@pytest.fixture
def service(monkeypatch):
    monkeypatch.setattr(defect_service_module, "get_db", lambda: FakeDefectDB())
    return defect_service_module.DefectService()


def test_uc07_defect_service_returns_dashboard_ready_data(service):
    data = service.get_defect_data(months=2)

    assert data == {
        "months_labels": ["Jan", "Feb"],
        "defect_per_month": [10, 5],
        "defect_types": [
            "Kecacatan Fisik",
            "Kesalahan Proses",
            "Kerusakan Material",
        ],
        "defect_counts": [9, 6, 0],
        "defect_pcts": [60, 40, 0],
        "total_defect": 15,
        "defect_rate": 1.0,
        "top_type": "Kecacatan Fisik",
        "top_pct": 60,
        "mom_change": -50.0,
    }


def test_uc07_defect_service_handles_zero_previous_month(service):
    assert service._get_mom_change([0, 8]) == 0.0
    assert service._get_mom_change([20, 10]) == -50.0


def test_uc07_defect_service_exported_from_services_package():
    assert DefectServiceFromPackage is defect_service_module.DefectService


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


def test_uc07_gen_defect_info_describes_monthly_changes():
    result = defectviewer._gen_defect_info(["Jan", "Feb", "Mar"], [100, 80, 120])

    assert result == [
        "Tingkat defect naik sebesar 50% dibandingkan Bulan Februari",
        "Tingkat defect menurun sebesar 20% dibandingkan Bulan Januari",
    ]


def test_uc07_stat_card_renders_defect_summary(qapp):
    card = defectviewer.StatCard("Total Defect", "15", "Turun dari bulan lalu")

    labels = card.findChildren(QLabel)
    rendered_text = [label.text() for label in labels]

    assert rendered_text == ["Total Defect", "15", "Turun dari bulan lalu"]


def test_uc07_defect_window_uses_service_data(monkeypatch, qapp):
    class FakeDefectService:
        def get_defect_data(self, months=4):
            assert months == 4
            return {
                "months_labels": ["Jan", "Feb", "Mar", "Apr"],
                "defect_per_month": [10, 8, 6, 4],
                "defect_types": ["Kecacatan Fisik", "Kesalahan Proses"],
                "defect_counts": [7, 3],
                "defect_pcts": [70, 30],
                "total_defect": 28,
                "defect_rate": 0.9,
                "top_type": "Kecacatan Fisik",
                "top_pct": 70,
                "mom_change": -33.3,
            }

    monkeypatch.setattr(defectviewer, "DefectService", FakeDefectService)

    window = defectviewer.DefectWindow()
    labels = [label.text() for label in window.findChildren(QLabel)]

    assert "Total Defect" in labels
    assert "28" in labels
    assert "Defect Rate" in labels
    assert "0.9%" in labels
    assert "Tipe Defect Terbanyak" in labels
    assert "Kecacatan Fisik" in labels

    window.close()


def test_uc07_init_services_exports_application_services():
    assert services.AuthService.__name__ == "AuthService"
    assert services.DashboardService.__name__ == "DashboardService"
    assert services.DefectService.__name__ == "DefectService"
    assert services.UserDataLocal.__name__ == "UserDataLocal"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
