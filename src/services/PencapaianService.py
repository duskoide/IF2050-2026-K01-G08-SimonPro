"""Service untuk UC06 insight tingkat pencapaian target."""

from __future__ import annotations

from datetime import date
from typing import Any

from dateutil.relativedelta import relativedelta

from src.database.db_connection import get_db


class PencapaianService:
    def __init__(self, db=None):
        self.db = db or get_db()

    def get_insight_pencapaian(self, months: int = 4) -> dict[str, Any]:
        months = max(1, int(months or 4))
        period = self._get_period(months)
        if period is None:
            return self._empty_result()

        start_date, end_date = period
        labels, target, actual = self._get_target_vs_actual(start_date, end_date)
        efficiency = [
            self._percentage(actual_value, target_value)
            for actual_value, target_value in zip(actual, target)
        ]
        distribution = self._get_distribution(start_date, end_date)

        total_target = sum(target)
        total_actual = sum(actual)
        avg_efficiency = self._percentage(total_actual, total_target)
        daily_productivity = self._get_daily_productivity(start_date, end_date)

        return {
            "summary": {
                "average_efficiency": avg_efficiency,
                "total_output": total_actual,
                "daily_productivity": daily_productivity,
                "target_total": total_target,
                "period_label": self._period_label(start_date, end_date),
            },
            "charts": {
                "labels": labels,
                "target": target,
                "actual": actual,
                "efficiency": efficiency,
                "distribution": distribution,
            },
            "insights": self._build_trend_insights(labels, efficiency),
        }

    def _get_period(self, months: int) -> tuple[date, date] | None:
        rows = self.db.execute_query(
            """
            SELECT MAX(bulan) AS latest_month
            FROM (
                SELECT DATE_TRUNC('month', tanggal)::date AS bulan
                FROM produksi_harian
                UNION
                SELECT DATE_TRUNC('month', tanggal_mulai)::date AS bulan
                FROM target_produksi
            ) periode_data
            """
        )
        if not rows or rows[0]["latest_month"] is None:
            return None

        latest_month = rows[0]["latest_month"]
        start_month = latest_month - relativedelta(months=months - 1)
        end_date = latest_month + relativedelta(months=1, days=-1)
        return start_month, end_date

    def _get_target_vs_actual(self, start_date: date, end_date: date):
        target_rows = self.db.execute_query(
            """
            SELECT
                DATE_TRUNC('month', tanggal_mulai)::date AS bulan,
                COALESCE(SUM(jumlah_target), 0) AS target
            FROM target_produksi
            WHERE tanggal_mulai >= %s AND tanggal_mulai <= %s
            GROUP BY DATE_TRUNC('month', tanggal_mulai)
            ORDER BY DATE_TRUNC('month', tanggal_mulai)
            """,
            (start_date, end_date),
        )
        actual_rows = self.db.execute_query(
            """
            SELECT
                DATE_TRUNC('month', tanggal)::date AS bulan,
                COALESCE(SUM(jumlah_aktual), 0) AS actual
            FROM produksi_harian
            WHERE tanggal >= %s AND tanggal <= %s
            GROUP BY DATE_TRUNC('month', tanggal)
            ORDER BY DATE_TRUNC('month', tanggal)
            """,
            (start_date, end_date),
        )

        target_map = {row["bulan"]: int(row["target"]) for row in target_rows}
        actual_map = {row["bulan"]: int(row["actual"]) for row in actual_rows}

        labels = []
        target = []
        actual = []
        cursor = start_date
        while cursor <= end_date:
            labels.append(cursor.strftime("%b"))
            target.append(target_map.get(cursor, 0))
            actual.append(actual_map.get(cursor, 0))
            cursor += relativedelta(months=1)

        return labels, target, actual

    def _get_distribution(self, start_date: date, end_date: date):
        rows = self.db.execute_query(
            """
            SELECT
                p.nama_produk,
                COALESCE(SUM(ph.jumlah_aktual), 0) AS total
            FROM produksi_harian ph
            JOIN produk p ON p.produk_id = ph.produk_id
            WHERE ph.tanggal >= %s AND ph.tanggal <= %s
            GROUP BY p.nama_produk
            ORDER BY total DESC, p.nama_produk
            """,
            (start_date, end_date),
        )
        return self._build_distribution(rows)

    def _get_daily_productivity(self, start_date: date, end_date: date) -> int:
        rows = self.db.execute_query(
            """
            SELECT
                COALESCE(SUM(jumlah_aktual), 0) AS total,
                COUNT(DISTINCT tanggal) AS hari
            FROM produksi_harian
            WHERE tanggal >= %s AND tanggal <= %s
            """,
            (start_date, end_date),
        )
        if not rows:
            return 0

        total = int(rows[0]["total"] or 0)
        days = int(rows[0]["hari"] or 0)
        if days == 0:
            return 0
        return round(total / days)

    def _period_label(self, start_date: date, end_date: date) -> str:
        if start_date.year == end_date.year:
            return f"{start_date.strftime('%b')} - {end_date.strftime('%b %Y')}"
        return f"{start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}"

    def _empty_result(self) -> dict[str, Any]:
        return {
            "summary": {
                "average_efficiency": 0.0,
                "total_output": 0,
                "daily_productivity": 0,
                "target_total": 0,
                "period_label": "-",
            },
            "charts": {
                "labels": [],
                "target": [],
                "actual": [],
                "efficiency": [],
                "distribution": {
                    "labels": ["Belum ada data"],
                    "values": [100.0],
                    "totals": [0],
                },
            },
            "insights": ["Belum ada data pencapaian untuk ditampilkan"],
        }

    @staticmethod
    def _percentage(actual: int | float, target: int | float) -> float:
        if target <= 0:
            return 0.0
        return round((actual / target) * 100, 1)

    @staticmethod
    def _build_distribution(rows: list[dict[str, Any]]) -> dict[str, list[Any]]:
        normalized = [
            {"label": row["nama_produk"], "total": int(row["total"] or 0)}
            for row in rows
            if int(row["total"] or 0) > 0
        ]
        if not normalized:
            return {"labels": ["Belum ada data"], "values": [100.0], "totals": [0]}

        top_items = normalized[:3]
        other_total = sum(item["total"] for item in normalized[3:])
        if other_total > 0:
            top_items.append({"label": "Lainnya", "total": other_total})

        total_output = sum(item["total"] for item in top_items)
        return {
            "labels": [item["label"] for item in top_items],
            "values": [
                round((item["total"] / total_output) * 100, 1)
                for item in top_items
            ],
            "totals": [item["total"] for item in top_items],
        }

    @staticmethod
    def _build_trend_insights(labels: list[str], efficiency: list[float]) -> list[str]:
        if not labels or not efficiency:
            return ["Belum ada tren pencapaian"]

        insights = []
        latest_label = labels[-1]
        latest_value = efficiency[-1]
        if latest_value >= 100:
            insights.append(f"{latest_label} mencapai {latest_value}% dari target")
        else:
            gap = round(100 - latest_value, 1)
            insights.append(f"{latest_label} masih kurang {gap}% dari target")

        for idx in range(len(efficiency) - 1, 0, -1):
            diff = round(efficiency[idx] - efficiency[idx - 1], 1)
            if diff == 0:
                insights.append(
                    f"Pencapaian stabil dari {labels[idx - 1]} ke {labels[idx]}"
                )
            else:
                arah = "naik" if diff > 0 else "turun"
                insights.append(
                    f"Pencapaian {arah} {abs(diff)}% dari {labels[idx - 1]}"
                )

        return insights[:3]
