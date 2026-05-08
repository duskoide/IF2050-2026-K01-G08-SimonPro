"""Service untuk UC05 input produksi harian."""

from __future__ import annotations

from datetime import date
from typing import Any

from src.database.db_connection import get_db
from src.models.ProduksiHarian import ProduksiHarian


class ProduksiService:
    def __init__(self, db=None):
        self.db = db or get_db()

    def get_produk_aktif(self) -> list[dict[str, Any]]:
        return ProduksiHarian.get_produk_aktif(self.db)

    def get_tipe_defect(self) -> list[dict[str, Any]]:
        return ProduksiHarian.get_tipe_defect(self.db)

    def inputProduksiHarian(
        self,
        tanggal,
        produk_id,
        jumlah_aktual,
        penanggung_jawab,
        kendala_produksi=None,
        detail_defect=None,
    ) -> tuple[bool, str, int | None]:
        detail_defect = detail_defect or []
        produksi_data = {
            "tanggal": tanggal,
            "produk_id": produk_id,
            "jumlah_aktual": jumlah_aktual,
            "penanggung_jawab": penanggung_jawab,
            "kendala_produksi": kendala_produksi,
            "detail_defect": detail_defect,
        }

        valid, pesan, normalized = self._validasiProduksi(produksi_data)
        if not valid:
            return False, pesan, None

        if not ProduksiHarian.produk_exists(self.db, normalized["produk_id"]):
            return False, "Produk tidak ditemukan atau tidak aktif", None

        defect_ids = ProduksiHarian.tipe_defect_ids(self.db)
        for detail in normalized["detail_defect"]:
            if detail["defect_id"] not in defect_ids:
                return False, "Tipe defect tidak ditemukan", None

        jumlah_defect = sum(
            detail["jumlah_defect"] for detail in normalized["detail_defect"]
        )
        produksi = ProduksiHarian(
            produksi_id=None,
            tanggal=normalized["tanggal"],
            produk_id=normalized["produk_id"],
            jumlah_aktual=normalized["jumlah_aktual"],
            jumlah_defect=jumlah_defect,
            penanggung_jawab=normalized["penanggung_jawab"],
            kendala_produksi=normalized["kendala_produksi"],
        )

        try:
            with self.db:
                produksi_id = ProduksiHarian.tambah(
                    self.db,
                    produksi,
                    normalized["detail_defect"],
                )
            return True, "Data produksi harian berhasil disimpan", produksi_id
        except Exception as exc:
            return False, f"Gagal menyimpan data produksi: {exc}", None

    def _validasiProduksi(self, data: dict[str, Any]) -> tuple[bool, str, dict[str, Any]]:
        try:
            produk_id = int(data.get("produk_id"))
        except (TypeError, ValueError):
            return False, "Produk wajib dipilih", {}

        try:
            jumlah_aktual = int(data.get("jumlah_aktual"))
        except (TypeError, ValueError):
            return False, "Jumlah aktual harus berupa angka", {}

        tanggal = data.get("tanggal")
        if not isinstance(tanggal, date):
            return False, "Tanggal produksi wajib diisi", {}

        penanggung_jawab = (data.get("penanggung_jawab") or "").strip()
        if not penanggung_jawab:
            return False, "Penanggung jawab wajib diisi", {}

        if jumlah_aktual < 0:
            return False, "Jumlah aktual tidak boleh negatif", {}

        detail_defect = []
        for detail in data.get("detail_defect") or []:
            try:
                defect_id = int(detail.get("defect_id"))
                jumlah_defect = int(detail.get("jumlah_defect"))
            except (TypeError, ValueError):
                return False, "Detail defect harus berupa angka", {}

            if jumlah_defect < 0:
                return False, "Jumlah defect tidak boleh negatif", {}

            if jumlah_defect > 0:
                detail_defect.append(
                    {
                        "defect_id": defect_id,
                        "jumlah_defect": jumlah_defect,
                    }
                )

        total_defect = sum(detail["jumlah_defect"] for detail in detail_defect)
        if total_defect > jumlah_aktual:
            return False, "Jumlah defect tidak boleh melebihi jumlah aktual", {}

        normalized = {
            "tanggal": tanggal,
            "produk_id": produk_id,
            "jumlah_aktual": jumlah_aktual,
            "penanggung_jawab": penanggung_jawab,
            "kendala_produksi": (data.get("kendala_produksi") or "").strip() or None,
            "detail_defect": detail_defect,
        }
        return True, "", normalized

