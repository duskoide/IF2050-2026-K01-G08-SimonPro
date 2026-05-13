import importlib

dashboard_module = importlib.import_module("src.services.DashboardService")


class FakeDashboardDb:
    def execute_query(self, sql, params=None):
        normalized = " ".join(sql.split()).lower()

        if "sum(jumlah_aktual)" in normalized and "sum(jumlah_defect)" in normalized:
            return [{"total_aktual": 150, "total_defect": 6}]

        if "sum(jumlah_aktual)" in normalized and "as total" in normalized and "from produksi_harian" in normalized:
            return [{"total": 150}]

        if "count(*) as total from produk" in normalized:
            return [{"total": 8}]

        if "sum(jumlah_target)" in normalized and "from target_produksi" in normalized and "as total" in normalized:
            return [{"total": 200}]

        if "from produksi_harian" in normalized and "group by date_trunc('month', tanggal)" in normalized and "jumlah_aktual" in normalized:
            return [{"bulan": "Jan", "aktual": 75}, {"bulan": "Feb", "aktual": 75}]

        if "from target_produksi" in normalized and "group by date_trunc('month', tanggal_mulai)" in normalized:
            return [{"bulan": "Jan", "target": 100}, {"bulan": "Feb", "target": 100}]

        if "sum(jumlah_defect)" in normalized and "group by date_trunc('month', tanggal)" in normalized:
            return [{"bulan": "Jan", "defect": 3}, {"bulan": "Feb", "defect": 3}]

        return []


def test_dashboard_summary_data(monkeypatch):
    monkeypatch.setattr(dashboard_module, "get_db", lambda: FakeDashboardDb())
    service = dashboard_module.DashboardService()

    data = service.get_summary_data()

    assert data["total_produksi"] == 150
    assert data["jumlah_produk"] == 8
    assert data["tingkat_defect"] == 4.0
    assert data["pencapaian_target"] == (75.0, 200)


def test_dashboard_chart_data_uses_regular_data(monkeypatch):
    monkeypatch.setattr(dashboard_module, "get_db", lambda: FakeDashboardDb())
    service = dashboard_module.DashboardService()

    monkeypatch.setattr(service, "_get_target_vs_aktual", lambda months: (["Jan", "Feb"], [100, 100], [75, 75]))
    monkeypatch.setattr(service, "_get_defect_per_bulan", lambda months: (["Jan", "Feb"], [3, 3]))

    data = service.get_chart_data(months=2)

    assert len(data["labels"]) == 2
    assert data["target"] == [100, 100]
    assert data["actual"] == [75, 75]
    assert data["defect"] == [3, 3]


def test_dashboard_chart_data_falls_back_to_latest(monkeypatch):
    monkeypatch.setattr(dashboard_module, "get_db", lambda: FakeDashboardDb())
    service = dashboard_module.DashboardService()

    monkeypatch.setattr(service, "_get_target_vs_aktual", lambda months: (["Jan", "Feb"], [0, 0], [0, 0]))
    monkeypatch.setattr(service, "_get_defect_per_bulan", lambda months: (["Jan", "Feb"], [0, 0]))
    monkeypatch.setattr(service, "_get_latest_target_vs_aktual", lambda months: (["Mar", "Apr"], [120, 140], [110, 135]))
    monkeypatch.setattr(service, "_get_latest_defect_per_bulan", lambda months: (["Mar", "Apr"], [4, 5]))

    data = service.get_chart_data(months=2)

    assert data == {
        "labels": ["Mar", "Apr"],
        "target": [120, 140],
        "actual": [110, 135],
        "defect": [4, 5],
    }
