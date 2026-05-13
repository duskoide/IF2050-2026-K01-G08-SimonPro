from src.database.db_connection import get_db
from datetime import date
from dateutil.relativedelta import relativedelta


class DefectService:
    def __init__(self, time_service=None):
        self.db = get_db()
        self.time_service = time_service

    def _today(self) -> date:
        if self.time_service is not None:
            return self.time_service.today()
        return date.today()

    def _get_period(self, months: int):
        current_date = self._today()
        current_month = current_date.replace(day=1)
        start_month = current_month - relativedelta(months=months - 1)
        return start_month, current_date

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_defect_data(self, months=4):
        """Fetch all defect-related data needed by DefectViewer.

        Returns a dict with:
            - months_labels: list[str]       e.g. ['Jan','Feb','Mar','Apr']
            - defect_per_month: list[int]    total defect per month
            - defect_types: list[str]        e.g. ['Kecacatan Fisik', ...]
            - defect_counts: list[int]       count per type
            - defect_pcts: list[int]         percentage per type
            - total_defect: int
            - defect_rate: float             percentage (e.g. 0.65)
            - top_type: str                  type with highest count
            - top_pct: int                   percentage of top type
        """
        months = max(1, int(months or 4))
        start_date, end_date = self._get_period(months)
        labels, defect_vals = self._get_defect_per_bulan(start_date, end_date)

        types, counts, pcts = self._get_defect_per_tipe(start_date, end_date)

        total_defect = sum(defect_vals)
        defect_rate = self._get_defect_rate(start_date, end_date)
        top_type, top_pct = self._get_top_defect_type(types, counts, pcts)

        # month-over-month change for the "Total Defect" subtitle
        mom = self._get_mom_change(defect_vals)

        return {
            "months_labels": labels,
            "defect_per_month": defect_vals,
            "defect_types": types,
            "defect_counts": counts,
            "defect_pcts": pcts,
            "total_defect": total_defect,
            "defect_rate": defect_rate,
            "top_type": top_type,
            "top_pct": top_pct,
            "mom_change": mom,
        }

    # ------------------------------------------------------------------
    # Monthly defect trend (line chart)
    # ------------------------------------------------------------------
    def _get_defect_per_bulan(self, start_date, end_date):
        """Return monthly defect count for the selected month-year period."""
        query = """
            SELECT 
                DATE_TRUNC('month', tanggal)::date AS bulan,
                COALESCE(SUM(jumlah_defect), 0) AS defect
            FROM produksi_harian
            WHERE tanggal >= %s AND tanggal <= %s
            GROUP BY DATE_TRUNC('month', tanggal)
            ORDER BY DATE_TRUNC('month', tanggal)
        """
        rows = self.db.execute_query(query, (start_date, end_date))

        labels = []
        defect_map = {}
        cursor = start_date
        while cursor <= end_date:
            labels.append(cursor.strftime("%b"))
            defect_map[cursor] = 0
            cursor += relativedelta(months=1)

        for row in rows:
            bulan = row["bulan"]
            if bulan in defect_map:
                defect_map[bulan] = int(row["defect"])

        defect_values = [defect_map[key] for key in defect_map.keys()]
        return labels, defect_values

    # ------------------------------------------------------------------
    # Defect by type (horizontal bar chart)
    # ------------------------------------------------------------------
    def _get_defect_per_tipe(self, start_date, end_date):
        """Return defect counts & percentages grouped by tipe_defect
        for the selected month-year period.
        """
        query = f"""
            SELECT 
                td.nama_defect AS tipe,
                COALESCE(
                    SUM(
                        CASE
                            WHEN ph.produksi_id IS NOT NULL THEN dd.jumlah_defect
                            ELSE 0
                        END
                    ),
                    0
                ) AS jumlah
            FROM tipe_defect td
            LEFT JOIN detail_defect dd ON td.defect_id = dd.defect_id
            LEFT JOIN produksi_harian ph ON dd.produksi_id = ph.produksi_id
                AND ph.tanggal >= %s
                AND ph.tanggal <= %s
            GROUP BY td.defect_id, td.nama_defect
            ORDER BY jumlah DESC
        """
        rows = self.db.execute_query(query, (start_date, end_date))

        types = []
        counts = []
        for r in rows:
            types.append(r["tipe"])
            counts.append(int(r["jumlah"]))

        total = sum(counts) if counts else 0
        pcts = [round((c / total) * 100) if total > 0 else 0 for c in counts]

        return types, counts, pcts

    # ------------------------------------------------------------------
    # Summary helpers
    # ------------------------------------------------------------------
    def _get_defect_rate(self, start_date, end_date):
        """Defect rate = total_defect / total_aktual * 100 for the period."""
        query = """
            SELECT 
                COALESCE(SUM(jumlah_aktual), 0) AS total_aktual,
                COALESCE(SUM(jumlah_defect), 0) AS total_defect
            FROM produksi_harian
            WHERE tanggal >= %s AND tanggal <= %s
        """
        row = self.db.execute_query(query, (start_date, end_date))
        if row:
            total_aktual = int(row[0]["total_aktual"])
            total_defect = int(row[0]["total_defect"])
            if total_aktual > 0:
                return round((total_defect / total_aktual) * 100, 2)
        return 0.0

    def _get_top_defect_type(self, types, counts, pcts):
        """Return the type with the highest count and its percentage."""
        if not types:
            return "-", 0
        return types[0], pcts[0]

    def _get_mom_change(self, defect_vals):
        """Calculate month-over-month change for the latest two months."""
        if len(defect_vals) < 2:
            return 0.0
        prev = defect_vals[-2]
        curr = defect_vals[-1]
        if prev == 0:
            return 0.0
        return round(((curr - prev) / prev) * 100, 1)
