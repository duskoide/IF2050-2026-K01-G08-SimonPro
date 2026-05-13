from datetime import date

from src.services.PencapaianService import PencapaianService


class FakeTimeService:
    def today(self):
        return date(2026, 4, 15)


class FakePencapaianDb:
    def execute_query(self, sql, params=None):
        if "FROM target_produksi" in sql and "jumlah_target" in sql:
            return [
                {"bulan": date(2026, 3, 1), "target": 100},
                {"bulan": date(2026, 4, 1), "target": 200},
            ]
        if "FROM produksi_harian" in sql and "jumlah_aktual" in sql and "GROUP BY DATE_TRUNC" in sql:
            return [
                {"bulan": date(2026, 3, 1), "actual": 80},
                {"bulan": date(2026, 4, 1), "actual": 220},
            ]
        if "JOIN produk" in sql:
            return [
                {"nama_produk": "Kaos", "total": 180},
                {"nama_produk": "Kemeja", "total": 80},
                {"nama_produk": "Celana", "total": 40},
            ]
        if "COUNT(DISTINCT tanggal)" in sql:
            return [{"total": 300, "hari": 6}]
        return []


def test_get_insight_pencapaian_menghitung_ringkasan_dan_grafik():
    service = PencapaianService(db=FakePencapaianDb(), time_service=FakeTimeService())

    result = service.get_insight_pencapaian(months=2)

    assert result["summary"]["average_efficiency"] == 100.0
    assert result["summary"]["total_output"] == 300
    assert result["summary"]["target_total"] == 300
    assert result["summary"]["daily_productivity"] == 50
    assert result["charts"]["labels"] == ["Mar", "Apr"]
    assert result["charts"]["target"] == [100, 200]
    assert result["charts"]["actual"] == [80, 220]
    assert result["charts"]["efficiency"] == [80.0, 110.0]
    assert result["charts"]["distribution"]["labels"] == ["Kaos", "Kemeja", "Celana"]


def test_build_distribution_mengelompokkan_produk_lainnya():
    rows = [
        {"nama_produk": "A", "total": 50},
        {"nama_produk": "B", "total": 30},
        {"nama_produk": "C", "total": 10},
        {"nama_produk": "D", "total": 10},
    ]

    distribution = PencapaianService._build_distribution(rows)

    assert distribution["labels"] == ["A", "B", "C", "Lainnya"]
    assert distribution["totals"] == [50, 30, 10, 10]
    assert distribution["values"] == [50.0, 30.0, 10.0, 10.0]
