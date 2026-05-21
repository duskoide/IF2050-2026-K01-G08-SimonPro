"""Service layer untuk manajemen target produksi."""

from datetime import date
from calendar import monthrange

from src.database.db_connection import Database
from src.models.TargetProduksi import TargetProduksi


class TargetService:

    def __init__(self, db: Database) -> None:
        self._db = db

    def get_all_targets(self) -> list[TargetProduksi]:
        return TargetProduksi.getAll(self._db)

    def get_all_targets_grouped(self) -> list[dict]:
        targets = self.get_all_targets()
        grouped: dict[tuple, dict] = {}

        for t in targets:
            bulan = t.tanggal_mulai.strftime("%B %Y")
            key = (t.produk_id, t.nama_produk, t.nama_kategori, bulan)
            if key not in grouped:
                grouped[key] = {
                    "produk_id": t.produk_id,
                    "produk": t.nama_produk,
                    "kategori": t.nama_kategori,
                    "periode": bulan,
                    "target_bulanan": 0,
                    "target_harian": 0,
                }
            if t.periode == "bulanan":
                grouped[key]["target_bulanan"] = t.jumlah_target
            elif t.periode == "harian":
                grouped[key]["target_harian"] = t.jumlah_target

        return list(grouped.values())

    def save_target(
        self,
        produk_id: int,
        target_bulanan: int,
        target_harian: int,
        tahun: int,
        bulan: int,
    ) -> None:
        tanggal_mulai = date(tahun, bulan, 1)
        hari_terakhir = monthrange(tahun, bulan)[1]
        tanggal_selesai = date(tahun, bulan, hari_terakhir)

        if target_harian <= 0 < target_bulanan:
            target_harian = target_bulanan // hari_terakhir
        elif target_bulanan <= 0 < target_harian:
            target_bulanan = target_harian * hari_terakhir

        TargetProduksi.upsert(
            self._db, produk_id, "bulanan", tanggal_mulai, tanggal_selesai, target_bulanan
        )
        TargetProduksi.upsert(
            self._db, produk_id, "harian", tanggal_mulai, tanggal_selesai, target_harian
        )

    def check_target_exists(self, produk_id: int, tahun: int, bulan: int) -> bool:
        """Memeriksa apakah target sudah ada untuk produk dan periode tertentu."""
        tanggal_mulai = date(tahun, bulan, 1)
        hari_terakhir = monthrange(tahun, bulan)[1]
        tanggal_selesai = date(tahun, bulan, hari_terakhir)
        
        target_bulanan = TargetProduksi.getTargetBulanan(self._db, produk_id, tanggal_mulai, tanggal_selesai)
        target_harian = TargetProduksi.getTargetHarian(self._db, produk_id, tanggal_mulai, tanggal_selesai)
        
        return target_bulanan is not None or target_harian is not None