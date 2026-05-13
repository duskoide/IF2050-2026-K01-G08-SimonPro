from src.database.db_connection import get_db
from datetime import datetime
from dateutil.relativedelta import relativedelta


class DefectService:
    def __init__(self):
        self.db = get_db()

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
        labels, defect_vals = self._get_defect_per_bulan(months)
        if sum(defect_vals) == 0:
            labels, defect_vals = self._get_latest_defect_per_bulan(months)

        types, counts, pcts = self._get_defect_per_tipe(labels)

        total_defect = sum(defect_vals)
        defect_rate = self._get_defect_rate(labels)
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
    def _get_defect_per_bulan(self, months=4):
        """Return monthly defect count for the last N months."""
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months - 1)
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
        end = month_rows[-1]["bulan"] + relativedelta(months=1, days=-1)

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

    # ------------------------------------------------------------------
    # Defect by type (horizontal bar chart)
    # ------------------------------------------------------------------
    def _get_defect_per_tipe(self, month_labels):
        """Return defect counts & percentages grouped by tipe_defect
        for the months represented by *month_labels*.

        If month_labels is empty we fall back to all-time data.
        """
        if not month_labels:
            where_clause = ""
            params = ()
        else:
            # Derive date range from the first and last month in month_labels.
            # month_labels are like ['Jan','Feb','Mar','Apr'] but without year.
            # We use the latest *distinct* months that exist in produksi_harian
            # that match the number of labels.
            distinct_months_q = """
                SELECT DISTINCT DATE_TRUNC('month', tanggal) AS bulan
                FROM produksi_harian
                ORDER BY bulan DESC
                LIMIT %s
            """
            dm_rows = self.db.execute_query(distinct_months_q, (len(month_labels),))
            if not dm_rows:
                where_clause = ""
                params = ()
            else:
                dm_rows = list(reversed(dm_rows))
                start = dm_rows[0]["bulan"]
                end = dm_rows[-1]["bulan"] + relativedelta(months=1, days=-1)
                where_clause = "WHERE ph.tanggal >= %s AND ph.tanggal <= %s"
                params = (start, end)

        query = f"""
            SELECT 
                td.nama_defect AS tipe,
                COALESCE(SUM(dd.jumlah_defect), 0) AS jumlah
            FROM tipe_defect td
            LEFT JOIN detail_defect dd ON td.defect_id = dd.defect_id
            LEFT JOIN produksi_harian ph ON dd.produksi_id = ph.produksi_id
            {where_clause}
            GROUP BY td.defect_id, td.nama_defect
            ORDER BY jumlah DESC
        """
        rows = self.db.execute_query(query, params)

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
    def _get_defect_rate(self, month_labels):
        """Defect rate = total_defect / total_aktual * 100 for the period."""
        if not month_labels:
            where_clause = ""
            params = ()
        else:
            distinct_months_q = """
                SELECT DISTINCT DATE_TRUNC('month', tanggal) AS bulan
                FROM produksi_harian
                ORDER BY bulan DESC
                LIMIT %s
            """
            dm_rows = self.db.execute_query(distinct_months_q, (len(month_labels),))
            if not dm_rows:
                where_clause = ""
                params = ()
            else:
                dm_rows = list(reversed(dm_rows))
                start = dm_rows[0]["bulan"]
                end = dm_rows[-1]["bulan"] + relativedelta(months=1, days=-1)
                where_clause = "WHERE tanggal >= %s AND tanggal <= %s"
                params = (start, end)

        query = f"""
            SELECT 
                COALESCE(SUM(jumlah_aktual), 0) AS total_aktual,
                COALESCE(SUM(jumlah_defect), 0) AS total_defect
            FROM produksi_harian
            {where_clause}
        """
        row = self.db.execute_query(query, params)
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
