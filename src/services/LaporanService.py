"""Service untuk UC09 menghasilkan laporan produksi."""

from __future__ import annotations

import locale
import os
from datetime import date, datetime
from typing import Any

from src.database.db_connection import get_db

# sesuaiin lagih path HTML
_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "templates", "laporan_produksi.html"
)


class LaporanService:
    def __init__(self, db=None):
        self.db = db or get_db()

    def generate_laporan(
        self,
        tanggal_awal: date,
        tanggal_akhir: date,
        dicetak_oleh: str = "Sistem",
        output_dir: str = None,
    ) -> dict[str, Any]:

        if tanggal_awal > tanggal_akhir:
            return {
                "success": False,
                "filepath": None,
                "message": "Tanggal mulai tidak boleh lebih dari tanggal akhir.",
                "data": None,
            }

        ringkasan = self._get_ringkasan_performa(tanggal_awal, tanggal_akhir)
        if ringkasan is None:
            return {
                "success": False,
                "filepath": None,
                "message": "Tidak ada data yang bisa dilaporkan!",
                "data": None,
            }

        pencapaian_bulanan = self._get_pencapaian_bulanan(tanggal_awal, tanggal_akhir)
        pencapaian_produk  = self._get_pencapaian_per_produk(tanggal_awal, tanggal_akhir)
        defect_bulanan     = self._get_defect_bulanan(tanggal_awal, tanggal_akhir)
        defect_tipe        = self._get_defect_per_tipe(tanggal_awal, tanggal_akhir)
        kendala_list       = self._get_kendala_produksi(tanggal_awal, tanggal_akhir)

        data_laporan = {
            "periode": {
                "tanggal_awal": tanggal_awal,
                "tanggal_akhir": tanggal_akhir,
                "label": self._format_periode(tanggal_awal, tanggal_akhir),
            },
            "ringkasan":           ringkasan,
            "pencapaian_bulanan":  pencapaian_bulanan,
            "pencapaian_produk":   pencapaian_produk,
            "defect_bulanan":      defect_bulanan,
            "defect_tipe":         defect_tipe,
            "kendala_list":        kendala_list,
            "dicetak_oleh":        dicetak_oleh,
            "generated_at":        datetime.now().strftime("%d %B %Y %H:%M"),
        }

        html_content = self._build_html(data_laporan)
        filepath = self._export_pdf(html_content, tanggal_awal, tanggal_akhir, output_dir)

        return {
            "success": True,
            "filepath": filepath,
            "message": f"Laporan berhasil disimpan di {filepath}",
            "data": data_laporan,
        }

    def get_html_preview(
        self,
        tanggal_awal: date,
        tanggal_akhir: date,
        dicetak_oleh: str = "Sistem",
    ) -> str | None:
        """Return HTML string untuk preview di QWebEngineView (opsional)."""
        ringkasan = self._get_ringkasan_performa(tanggal_awal, tanggal_akhir)
        if ringkasan is None:
            return None

        data_laporan = {
            "periode": {
                "tanggal_awal": tanggal_awal,
                "tanggal_akhir": tanggal_akhir,
                "label": self._format_periode(tanggal_awal, tanggal_akhir),
            },
            "ringkasan":          ringkasan,
            "pencapaian_bulanan": self._get_pencapaian_bulanan(tanggal_awal, tanggal_akhir),
            "pencapaian_produk":  self._get_pencapaian_per_produk(tanggal_awal, tanggal_akhir),
            "defect_bulanan":     self._get_defect_bulanan(tanggal_awal, tanggal_akhir),
            "defect_tipe":        self._get_defect_per_tipe(tanggal_awal, tanggal_akhir),
            "kendala_list":       self._get_kendala_produksi(tanggal_awal, tanggal_akhir),
            "dicetak_oleh":       dicetak_oleh,
            "generated_at":       datetime.now().strftime("%d %B %Y %H:%M"),
        }
        return self._build_html(data_laporan)

    def _get_ringkasan_performa(
        self, tanggal_awal: date, tanggal_akhir: date
    ) -> dict[str, Any] | None:
        """Ambil ringkasan total produksi dan defect dalam periode."""
        rows = self.db.execute_query(
            """
            SELECT
                COALESCE(SUM(ph.jumlah_aktual), 0)  AS total_aktual,
                COUNT(DISTINCT ph.tanggal)           AS hari_kerja,
                COUNT(DISTINCT ph.produk_id)         AS jumlah_produk
            FROM produksi_harian ph
            WHERE ph.tanggal >= %s AND ph.tanggal <= %s
            """,
            (tanggal_awal, tanggal_akhir),
        )

        if not rows or rows[0]["total_aktual"] == 0:
            return None

        row = rows[0]
        total_aktual = int(row["total_aktual"])
        hari_kerja   = int(row["hari_kerja"])

        # Total defect dari tabel detail_defect (bukan kolom di produksi_harian)
        defect_rows = self.db.execute_query(
            """
            SELECT COALESCE(SUM(dd.jumlah_defect), 0) AS total_defect
            FROM detail_defect dd
            JOIN produksi_harian ph ON ph.produksi_id = dd.produksi_id
            WHERE ph.tanggal >= %s AND ph.tanggal <= %s
            """,
            (tanggal_awal, tanggal_akhir),
        )
        total_defect = int(defect_rows[0]["total_defect"]) if defect_rows else 0

        # Total target dalam periode
        target_rows = self.db.execute_query(
            """
            SELECT COALESCE(SUM(jumlah_target), 0) AS total_target
            FROM target_produksi
            WHERE periode = 'bulanan' AND tanggal_mulai <= %s AND tanggal_selesai >= %s
            """,
            (tanggal_akhir, tanggal_awal),
        )
        total_target = int(target_rows[0]["total_target"]) if target_rows else 0

        avg_efficiency       = self._pct(total_aktual, total_target)
        defect_rate          = self._pct(total_defect, total_aktual)
        produktivitas_harian = round(total_aktual / hari_kerja) if hari_kerja else 0

        return {
            "total_aktual":        total_aktual,
            "total_defect":        total_defect,
            "total_target":        total_target,
            "avg_efficiency":      avg_efficiency,       # sama dengan pencapaian_pct
            "defect_rate":         defect_rate,
            "hari_kerja":          hari_kerja,
            "produktivitas_harian": produktivitas_harian,
            "jumlah_produk":       int(row["jumlah_produk"]),
            "produksi_bersih":     total_aktual - total_defect,
        }

    def _get_pencapaian_bulanan(
        self, tanggal_awal: date, tanggal_akhir: date
    ) -> list[dict[str, Any]]:
        """Pencapaian aktual vs target, dikelompokkan per bulan."""
        rows = self.db.execute_query(
            """
            SELECT
                DATE_TRUNC('month', ph.tanggal)::date          AS bulan,
                COALESCE(SUM(ph.jumlah_aktual), 0)             AS aktual
            FROM produksi_harian ph
            WHERE ph.tanggal >= %s AND ph.tanggal <= %s
            GROUP BY bulan
            ORDER BY bulan
            """,
            (tanggal_awal, tanggal_akhir),
        )

        result = []
        for row in rows:
            bulan_date = row["bulan"]
            aktual     = int(row["aktual"] or 0)

            # Target untuk bulan ini — target_produksi overlap dengan bulan tsb
            bulan_awal  = bulan_date.replace(day=1)
            # Akhir bulan: hari pertama bulan berikutnya - 1 hari
            if bulan_date.month == 12:
                bulan_akhir = bulan_date.replace(year=bulan_date.year + 1, month=1, day=1)
            else:
                bulan_akhir = bulan_date.replace(month=bulan_date.month + 1, day=1)

            target_rows = self.db.execute_query(
                """
                SELECT COALESCE(SUM(jumlah_target), 0) AS target
                FROM target_produksi
                WHERE periode = 'bulanan' AND tanggal_mulai < %s AND tanggal_selesai >= %s
                """,
                (bulan_akhir, bulan_awal),
            )
            target      = int(target_rows[0]["target"]) if target_rows else 0
            efisiensi   = self._pct(aktual, target)
            label_bulan = self._format_bulan(bulan_date)

            result.append(
                {
                    "periode":  label_bulan,
                    "target":   target,
                    "aktual":   aktual,
                    "efisiensi": efisiensi,
                }
            )
        return result

    def _get_pencapaian_per_produk(
        self, tanggal_awal: date, tanggal_akhir: date
    ) -> list[dict[str, Any]]:
        """Distribusi produksi per produk dalam periode (untuk dist-grid)."""
        rows = self.db.execute_query(
            """
            SELECT
                p.nama_produk,
                COALESCE(SUM(ph.jumlah_aktual), 0) AS aktual
            FROM produk p
            JOIN produksi_harian ph ON ph.produk_id = p.produk_id
            WHERE ph.tanggal >= %s AND ph.tanggal <= %s
            GROUP BY p.produk_id, p.nama_produk
            HAVING COALESCE(SUM(ph.jumlah_aktual), 0) > 0
            ORDER BY aktual DESC
            """,
            (tanggal_awal, tanggal_akhir),
        )

        grand_total = sum(int(r["aktual"] or 0) for r in rows)
        result = []
        for row in rows:
            aktual = int(row["aktual"] or 0)
            result.append(
                {
                    "nama_produk": row["nama_produk"],
                    "aktual":      aktual,
                    "pct":         self._pct(aktual, grand_total),
                }
            )
        return result

    def _get_defect_bulanan(
        self, tanggal_awal: date, tanggal_akhir: date
    ) -> list[dict[str, Any]]:
        """Jumlah defect dan total produksi per bulan."""
        rows = self.db.execute_query(
            """
            SELECT
                produksi.bulan,
                produksi.total_produksi,
                COALESCE(defect.jumlah_defect, 0) AS jumlah_defect
            FROM (
                SELECT
                    DATE_TRUNC('month', tanggal)::date AS bulan,
                    COALESCE(SUM(jumlah_aktual), 0)    AS total_produksi
                FROM produksi_harian
                WHERE tanggal >= %s AND tanggal <= %s
                GROUP BY bulan
            ) produksi
            LEFT JOIN (
                SELECT
                    DATE_TRUNC('month', ph.tanggal)::date AS bulan,
                    COALESCE(SUM(dd.jumlah_defect), 0)    AS jumlah_defect
                FROM detail_defect dd
                JOIN produksi_harian ph ON ph.produksi_id = dd.produksi_id
                WHERE ph.tanggal >= %s AND ph.tanggal <= %s
                GROUP BY bulan
            ) defect ON defect.bulan = produksi.bulan
            ORDER BY produksi.bulan
            """,
            (tanggal_awal, tanggal_akhir, tanggal_awal, tanggal_akhir),
        )

        result = []
        for row in rows:
            total    = int(row["total_produksi"] or 0)
            defect   = int(row["jumlah_defect"]  or 0)
            pct      = self._pct(defect, total)
            result.append(
                {
                    "periode":        self._format_bulan(row["bulan"]),
                    "jumlah_defect":  defect,
                    "total_produksi": total,
                    "pct_defect":     pct,
                }
            )
        return result

    def _get_defect_per_tipe(
        self, tanggal_awal: date, tanggal_akhir: date
    ) -> list[dict[str, Any]]:
        """Breakdown defect berdasarkan tipe."""
        rows = self.db.execute_query(
            """
            SELECT
                td.nama_defect,
                COALESCE(SUM(dd.jumlah_defect), 0) AS jumlah
            FROM tipe_defect td
            JOIN detail_defect dd ON dd.defect_id = td.defect_id
            JOIN produksi_harian ph ON ph.produksi_id = dd.produksi_id
            WHERE ph.tanggal >= %s AND ph.tanggal <= %s
            GROUP BY td.defect_id, td.nama_defect
            HAVING COALESCE(SUM(dd.jumlah_defect), 0) > 0
            ORDER BY jumlah DESC
            """,
            (tanggal_awal, tanggal_akhir),
        )

        total = sum(int(r["jumlah"] or 0) for r in rows)
        result = []
        for row in rows:
            jumlah = int(row["jumlah"] or 0)
            result.append(
                {
                    "nama_defect": row["nama_defect"],
                    "jumlah":      jumlah,
                    "pct":         self._pct(jumlah, total),
                }
            )
        return result

    def _get_kendala_produksi(
        self, tanggal_awal: date, tanggal_akhir: date
    ) -> list[dict[str, Any]]:
        """Ambil daftar kendala produksi yang tercatat."""
        rows = self.db.execute_query(
            """
            SELECT 
                ph.tanggal, 
                p.nama_produk, 
                ph.kendala_produksi,
                ph.penanggung_jawab
            FROM produksi_harian ph
            JOIN produk p ON p.produk_id = ph.produk_id
            WHERE ph.tanggal >= %s AND ph.tanggal <= %s
              AND ph.kendala_produksi IS NOT NULL 
              AND ph.kendala_produksi != ''
            ORDER BY ph.tanggal DESC
            """,
            (tanggal_awal, tanggal_akhir),
        )
        return [
            {
                "tanggal": r["tanggal"].strftime("%d/%m/%Y"),
                "produk": r["nama_produk"],
                "kendala": r["kendala_produksi"],
                "pj": r["penanggung_jawab"]
            }
            for r in rows
        ]

    # ------------------------------------------------------------------
    # HTML Builder — mengisi placeholder di laporan_produksi.html
    # ------------------------------------------------------------------

    def _build_html(self, data: dict[str, Any]) -> str:
        """Load template HTML lalu isi semua placeholder {{...}}."""
        template_path = os.path.normpath(_TEMPLATE_PATH)
        with open(template_path, encoding="utf-8") as f:
            html = f.read()

        periode    = data["periode"]
        ringkasan  = data["ringkasan"]

        # ── Placeholder header ──────────────────────────────────────────
        html = html.replace("{{period_label}}",    periode["label"])
        html = html.replace("{{dicetak_tanggal}}", data["generated_at"])
        html = html.replace("{{dicetak_oleh}}",    data["dicetak_oleh"])
        html = html.replace("{{tahun}}",           str(datetime.now().year))

        # ── Placeholder stat cards ──────────────────────────────────────
        html = html.replace("{{avg_efficiency}}",     str(ringkasan["avg_efficiency"]))
        html = html.replace("{{total_output}}",       f"{ringkasan['total_aktual']:,}")
        html = html.replace("{{daily_productivity}}", f"{ringkasan['produktivitas_harian']:,}")
        html = html.replace("{{target_total}}",       f"{ringkasan['total_target']:,}")
        html = html.replace("{{total_defect}}",       f"{ringkasan['total_defect']:,}")
        html = html.replace("{{tingkat_defect}}",     str(ringkasan["defect_rate"]))
        html = html.replace("{{produksi_bersih}}",    f"{ringkasan['produksi_bersih']:,}")
        html = html.replace("{{jumlah_produk}}",      str(ringkasan["jumlah_produk"]))
        html = html.replace("{{hari_kerja}}",         str(ringkasan["hari_kerja"]))

        # ── Tabel pencapaian per bulan ──────────────────────────────────
        pencapaian_rows = ""
        for item in data["pencapaian_bulanan"]:
            efisiensi = item["efisiensi"]
            bar_width = min(efisiensi, 100)
            status_class = "success" if efisiensi >= 100 else "warning"
            status_text = "Tercapai" if efisiensi >= 100 else "Di bawah target"
            
            pencapaian_rows += f"""
        <tr>
            <td>{item['periode']}</td>
            <td class="right">{item['target']:,}</td>
            <td class="right">{item['aktual']:,}</td>
            <td class="center">
                <span class="status-chip {status_class}">{efisiensi}%</span>
            </td>
            <td>
                <div class="progress-bg">
                    <div class="progress-fill" style="width:{bar_width}%"></div>
                </div>
                <div class="progress-label">{status_text}</div>
            </td>
        </tr>"""
        html = html.replace("{{pencapaian_rows}}", pencapaian_rows)

        # ── Distribusi produksi per produk ──────────────────────────────
        distribusi_items = ""
        for item in data["pencapaian_produk"]:
            distribusi_items += f"""
        <div class="dist-card">
            <div class="dist-name">{item['nama_produk']}</div>
            <div class="dist-value">{item['pct']}%</div>
            <div class="dist-sub">{item['aktual']:,} unit</div>
        </div>"""
        html = html.replace("{{distribusi_items}}", distribusi_items)

        # ── Insight tren ────────────────────────────────────────────────
        insight_items = self._build_insight(
            data["pencapaian_bulanan"], ringkasan
        )
        html = html.replace("{{insight_items}}", insight_items)

        # ── Tabel defect per bulan ──────────────────────────────────────
        defect_rows = ""
        for item in data["defect_bulanan"]:
            pct = item["pct_defect"]
            if pct < 1:
                badge = '<span class="badge badge-low">Rendah</span>'
            elif pct < 3:
                badge = '<span class="badge badge-mid">Sedang</span>'
            else:
                badge = '<span class="badge badge-high">Tinggi</span>'

            defect_rows += f"""
        <tr>
            <td>{item['periode']}</td>
            <td class="right">{item['total_produksi']:,}</td>
            <td class="right">{item['jumlah_defect']:,}</td>
            <td class="center">{pct}%</td>
            <td>{badge}</td>
        </tr>"""
        html = html.replace("{{defect_rows}}", defect_rows)

        # ── Breakdown defect per tipe ───────────────────────────────────
        defect_type_rows = ""
        for item in data["defect_tipe"]:
            pct = item["pct"]
            bar_width = min(pct, 100)
            defect_type_rows += f"""
        <tr>
            <td>{item['nama_defect']}</td>
            <td class="right">{item['jumlah']:,}</td>
            <td class="center">
                {pct}%
                <div class="progress-bg small">
                    <div class="progress-fill" style="width:{bar_width}%"></div>
                </div>
            </td>
        </tr>"""
        html = html.replace("{{defect_type_rows}}", defect_type_rows)

        # ── Tabel kendala produksi ──────────────────────────────────────
        kendala_rows = ""
        if not data["kendala_list"]:
            kendala_rows = '<tr><td colspan="4" class="center">Tidak ada kendala yang tercatat.</td></tr>'
        else:
            for k in data["kendala_list"]:
                kendala_rows += f"""
            <tr>
                <td style="white-space:nowrap;">{k['tanggal']}</td>
                <td style="font-weight:600;">{k['produk']}</td>
                <td>{k['kendala']}</td>
                <td style="font-size:0.9em;">{k['pj']}</td>
            </tr>"""
        html = html.replace("{{kendala_rows}}", kendala_rows)

        return html

    # ------------------------------------------------------------------
    # Insight generator
    # ------------------------------------------------------------------

    def _build_insight(
        self,
        pencapaian_bulanan: list[dict],
        ringkasan: dict,
    ) -> str:
        """Hasilkan butir-butir insight sebagai <li> HTML."""
        items: list[str] = []

        # Efisiensi rata-rata keseluruhan
        eff = ringkasan["avg_efficiency"]
        if eff >= 100:
            items.append(f"Rata-rata efisiensi produksi sebesar <strong>{eff}%</strong> — target keseluruhan tercapai.")
        else:
            items.append(f"Rata-rata efisiensi produksi sebesar <strong>{eff}%</strong> — masih di bawah target.")

        # Bulan terbaik dan terburuk
        if pencapaian_bulanan:
            terbaik  = max(pencapaian_bulanan, key=lambda x: x["efisiensi"])
            terburuk = min(pencapaian_bulanan, key=lambda x: x["efisiensi"])
            items.append(
                f"Pencapaian tertinggi terjadi pada <strong>{terbaik['periode']}</strong> "
                f"({terbaik['efisiensi']}%)."
            )
            if terbaik["periode"] != terburuk["periode"]:
                items.append(
                    f"Pencapaian terendah terjadi pada <strong>{terburuk['periode']}</strong> "
                    f"({terburuk['efisiensi']}%)."
                )

        # Tingkat defect
        dr = ringkasan["defect_rate"]
        if dr == 0:
            items.append("Tidak ditemukan defect pada periode ini.")
        elif dr < 1:
            items.append(f"Tingkat defect <strong>{dr}%</strong> — dalam batas wajar (&lt;1%).")
        elif dr < 3:
            items.append(f"Tingkat defect <strong>{dr}%</strong> — perlu perhatian lebih lanjut.")
        else:
            items.append(f"Tingkat defect <strong>{dr}%</strong> — melebihi ambang batas, segera investigasi.")

        # Produktivitas harian
        items.append(
            f"Rata-rata produktivitas harian: <strong>{ringkasan['produktivitas_harian']:,} unit/hari</strong> "
            f"dalam {ringkasan['hari_kerja']} hari kerja."
        )

        return "\n".join(f"<li>{item}</li>" for item in items)

    # ------------------------------------------------------------------
    # PDF Export
    # ------------------------------------------------------------------

    def _export_pdf(
        self,
        html_content: str,
        tanggal_awal: date,
        tanggal_akhir: date,
        output_dir: str | None,
    ) -> str:
        """Ekspor HTML ke PDF.

        Gunakan WeasyPrint (direkomendasikan) atau pdfkit.
        Saat ini menyimpan .html sementara jika library PDF belum terpasang.
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.expanduser("~"), "Downloads")

        os.makedirs(output_dir, exist_ok=True)

        base_filename = (
            f"Laporan_Produksi_"
            f"{tanggal_awal.strftime('%Y%m%d')}_"
            f"{tanggal_akhir.strftime('%Y%m%d')}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        filepath = self._unique_filepath(output_dir, base_filename, ".pdf")

        template_dir = os.path.dirname(os.path.normpath(_TEMPLATE_PATH))

        try:
            from weasyprint import HTML  # type: ignore
            HTML(string=html_content, base_url=template_dir).write_pdf(filepath)
        except Exception:
            try:
                from PyQt6.QtWidgets import QApplication
                from PyQt6.QtCore import QMarginsF, QUrl
                from PyQt6.QtGui import QPageLayout, QPageSize, QTextDocument
                from PyQt6.QtPrintSupport import QPrinter

                app = QApplication.instance() or QApplication([])

                document = QTextDocument()
                document.setBaseUrl(QUrl.fromLocalFile(template_dir + os.sep))
                document.setHtml(html_content)

                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(filepath)
                printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
                printer.setPageMargins(
                    QMarginsF(16, 18, 16, 20),
                    QPageLayout.Unit.Millimeter,
                )

                document.print(printer)
            except Exception:
                # Fallback terakhir: simpan HTML agar isi laporan tetap bisa dibuka.
                html_base = os.path.splitext(os.path.basename(filepath))[0] + "_preview"
                html_path = self._unique_filepath(output_dir, html_base, ".html")
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                filepath = html_path

        return filepath

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _unique_filepath(output_dir: str, base_filename: str, extension: str) -> str:
        """Return path baru tanpa menimpa file yang sudah ada."""
        filepath = os.path.join(output_dir, f"{base_filename}{extension}")
        if not os.path.exists(filepath):
            return filepath

        counter = 2
        while True:
            candidate = os.path.join(output_dir, f"{base_filename}_{counter}{extension}")
            if not os.path.exists(candidate):
                return candidate
            counter += 1

    @staticmethod
    def _pct(actual: int | float, target: int | float) -> float:
        if target <= 0:
            return 0.0
        return round((actual / target) * 100, 1)

    @staticmethod
    def _format_periode(tanggal_awal: date, tanggal_akhir: date) -> str:
        fmt_awal  = tanggal_awal.strftime("%d %B %Y")
        fmt_akhir = tanggal_akhir.strftime("%d %B %Y")
        return f"{fmt_awal} s.d. {fmt_akhir}"

    @staticmethod
    def _format_bulan(d: date) -> str:
        """Format tanggal ke label bulan Bahasa Indonesia, misal 'Januari 2025'."""
        _BULAN_ID = [
            "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember",
        ]
        return f"{_BULAN_ID[d.month]} {d.year}"
