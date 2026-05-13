from src.database.db_connection import get_db
from datetime import datetime
from dateutil.relativedelta import relativedelta

class DashboardService:
    def __init__(self):
        self.db = get_db()

    def get_summary_data(self):
        """Fetch summary statistics for dashboard cards."""
        return {
            "total_produksi": self._get_total_produksi(),
            "pencapaian_target": self._get_pencapaian_target(),
            "tingkat_defect": self._get_tingkat_defect(),
            "jumlah_produk": self._get_jumlah_produk(),
        }

    def get_chart_data(self, months=4):
        """Fetch data for bar chart (target vs aktual) and line chart (defect).

        If the requested period has no data, falls back to the last ``months``
        months that *do* have data in the database.
        """
        labels, target, actual = self._get_target_vs_aktual(months)
        _, defect_values = self._get_defect_per_bulan(months)

        # When everything is empty (dummy data is old), grab the latest N months
        # that actually exist in the DB.
        if sum(actual) == 0 and sum(target) == 0:
            labels, target, actual = self._get_latest_target_vs_aktual(months)
            _, defect_values = self._get_latest_defect_per_bulan(months)

        return {
            "labels": labels,
            "target": target,
            "actual": actual,
            "defect": defect_values,
        }

    def _get_total_produksi(self):
        row = self.db.execute_query(
            "SELECT COALESCE(SUM(jumlah_aktual), 0) AS total FROM produksi_harian"
        )
        return int(row[0]["total"]) if row else 0

    def _get_tingkat_defect(self):
        row = self.db.execute_query(
            "SELECT COALESCE(SUM(jumlah_aktual), 0) AS total_aktual, "
            "COALESCE(SUM(jumlah_defect), 0) AS total_defect "
            "FROM produksi_harian"
        )
        if row:
            total_aktual = int(row[0]["total_aktual"])
            total_defect = int(row[0]["total_defect"])
            if total_aktual > 0:
                return round((total_defect / total_aktual) * 100, 1)
        return 0.0

    def _get_jumlah_produk(self):
        row = self.db.execute_query(
            "SELECT COUNT(*) AS total FROM produk WHERE status_aktif = TRUE"
        )
        return int(row[0]["total"]) if row else 0

    def _get_pencapaian_target(self):
        row_aktual = self.db.execute_query(
            "SELECT COALESCE(SUM(jumlah_aktual), 0) AS total FROM produksi_harian"
        )
        row_target = self.db.execute_query(
            "SELECT COALESCE(SUM(jumlah_target), 0) AS total FROM target_produksi WHERE periode = 'bulanan'"
        )
        total_aktual = int(row_aktual[0]["total"]) if row_aktual else 0
        total_target = int(row_target[0]["total"]) if row_target else 0
        if total_target > 0:
            return round((total_aktual / total_target) * 100, 1), total_target
        return 0.0, 0

    def _get_target_vs_aktual(self, months=4):
        """Return monthly target vs actual for the last N months."""
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months-1)
        start_date = start_date.replace(day=1)

        query = """
            SELECT 
                TO_CHAR(DATE_TRUNC('month', tanggal), 'Mon') AS bulan,
                COALESCE(SUM(jumlah_aktual), 0) AS aktual
            FROM produksi_harian
            WHERE tanggal >= %s AND tanggal <= %s
            GROUP BY DATE_TRUNC('month', tanggal)
            ORDER BY DATE_TRUNC('month', tanggal)
        """
        rows = self.db.execute_query(query, (start_date, end_date))

        query_target = """
            SELECT 
                TO_CHAR(DATE_TRUNC('month', tanggal_mulai), 'Mon') AS bulan,
                COALESCE(SUM(jumlah_target), 0) AS target
            FROM target_produksi
            WHERE periode = 'bulanan' AND tanggal_mulai >= %s AND tanggal_mulai <= %s
            GROUP BY DATE_TRUNC('month', tanggal_mulai)
            ORDER BY DATE_TRUNC('month', tanggal_mulai)
        """
        rows_target = self.db.execute_query(query_target, (start_date, end_date))

        # Build ordered list of last N months
        labels = []
        target_map = {}
        actual_map = {}

        for i in range(months):
            d = end_date - relativedelta(months=months - 1 - i)
            label = d.strftime("%b")
            labels.append(label)
            target_map[label] = 0
            actual_map[label] = 0

        for r in rows_target:
            bulan = r["bulan"]
            if bulan in target_map:
                target_map[bulan] = int(r["target"])

        for r in rows:
            bulan = r["bulan"]
            if bulan in actual_map:
                actual_map[bulan] = int(r["aktual"])

        target_values = [target_map[lbl] for lbl in labels]
        actual_values = [actual_map[lbl] for lbl in labels]

        return labels, target_values, actual_values

    def _get_latest_target_vs_aktual(self, months=4):
        """Fallback: return the most recent N months that have DB data."""
        query = """
            SELECT DISTINCT DATE_TRUNC('month', tanggal) AS bulan
            FROM produksi_harian
            ORDER BY bulan DESC
            LIMIT %s
        """
        month_rows = self.db.execute_query(query, (months,))
        if not month_rows:
            return [], [], []

        # Oldest → newest
        month_rows = list(reversed(month_rows))
        labels = [m["bulan"].strftime("%b") for m in month_rows]
        start = month_rows[0]["bulan"]
        end   = month_rows[-1]["bulan"] + relativedelta(months=1, days=-1)

        query_actual = """
            SELECT 
                TO_CHAR(DATE_TRUNC('month', tanggal), 'Mon') AS bulan,
                COALESCE(SUM(jumlah_aktual), 0) AS aktual
            FROM produksi_harian
            WHERE tanggal >= %s AND tanggal <= %s
            GROUP BY DATE_TRUNC('month', tanggal)
            ORDER BY DATE_TRUNC('month', tanggal)
        """
        rows = self.db.execute_query(query_actual, (start, end))

        query_target = """
            SELECT 
                TO_CHAR(DATE_TRUNC('month', tanggal_mulai), 'Mon') AS bulan,
                COALESCE(SUM(jumlah_target), 0) AS target
            FROM target_produksi
            WHERE periode = 'bulanan' AND tanggal_mulai >= %s AND tanggal_mulai <= %s
            GROUP BY DATE_TRUNC('month', tanggal_mulai)
            ORDER BY DATE_TRUNC('month', tanggal_mulai)
        """
        rows_target = self.db.execute_query(query_target, (start, end))

        actual_map = {r["bulan"]: int(r["aktual"]) for r in rows}
        target_map = {r["bulan"]: int(r["target"]) for r in rows_target}

        actual_values = [actual_map.get(lbl, 0) for lbl in labels]
        target_values = [target_map.get(lbl, 0) for lbl in labels]

        return labels, target_values, actual_values

    def _get_defect_per_bulan(self, months=4):
        """Return monthly defect count for the last N months."""
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months-1)
        start_date = start_date.replace(day=1)

        query = """
            SELECT 
                TO_CHAR(DATE_TRUNC('month', tanggal), 'Mon') AS bulan,
                COALESCE(SUM(jumlah_defect), 0) AS defect
            FROM produksi_harian
            WHERE tanggal >= %s AND tanggal <= %s
            GROUP BY DATE_TRUNC('month', tanggal)
            ORDER BY DATE_TRUNC('month', tanggal)
        """
        rows = self.db.execute_query(query, (start_date, end_date))

        labels = []
        defect_map = {}
        for i in range(months):
            d = end_date - relativedelta(months=months - 1 - i)
            label = d.strftime("%b")
            labels.append(label)
            defect_map[label] = 0

        for r in rows:
            bulan = r["bulan"]
            if bulan in defect_map:
                defect_map[bulan] = int(r["defect"])

        defect_values = [defect_map[lbl] for lbl in labels]
        return labels, defect_values

    def _get_latest_defect_per_bulan(self, months=4):
        """Fallback: return defect count for the most recent N months with data."""
        query = """
            SELECT DISTINCT DATE_TRUNC('month', tanggal) AS bulan
            FROM produksi_harian
            ORDER BY bulan DESC
            LIMIT %s
        """
        month_rows = self.db.execute_query(query, (months,))
        if not month_rows:
            return [], []

        month_rows = list(reversed(month_rows))
        labels = [m["bulan"].strftime("%b") for m in month_rows]
        start = month_rows[0]["bulan"]
        end   = month_rows[-1]["bulan"] + relativedelta(months=1, days=-1)

        query = """
            SELECT 
                TO_CHAR(DATE_TRUNC('month', tanggal), 'Mon') AS bulan,
                COALESCE(SUM(jumlah_defect), 0) AS defect
            FROM produksi_harian
            WHERE tanggal >= %s AND tanggal <= %s
            GROUP BY DATE_TRUNC('month', tanggal)
            ORDER BY DATE_TRUNC('month', tanggal)
        """
        rows = self.db.execute_query(query, (start, end))
        defect_map = {r["bulan"]: int(r["defect"]) for r in rows}
        defect_values = [defect_map.get(lbl, 0) for lbl in labels]
        return labels, defect_values
