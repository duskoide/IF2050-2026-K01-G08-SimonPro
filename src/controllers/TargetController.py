"""Controller untuk manajemen target produksi.

Menjembatani view dan service dengan role-gating:
- Admin: akses penuh (Read & Write)
- Owner: akses baca (Read-only) - dibatasi di level UI/Sidebar
"""

from __future__ import annotations
from typing import Callable, Any
from src.services.TargetService import TargetService
from src.services.ProdukService import ProdukService
from src.database.db_connection import Database

class TargetController:
    """Controller yang menangani permintaan dari view terkait target produksi."""

    def __init__(self, db: Database) -> None:
        self._target_service = TargetService(db)
        self._produk_service = ProdukService(db)
        self._on_sukses: Callable[[str], None] | None = None
        self._on_error: Callable[[str], None] | None = None

    def set_on_sukses(self, callback: Callable[[str], None]) -> None:
        self._on_sukses = callback

    def set_on_error(self, callback: Callable[[str], None]) -> None:
        self._on_error = callback

    def _notify_sukses(self, pesan: str) -> None:
        if self._on_sukses:
            self._on_sukses(pesan)

    def _notify_error(self, pesan: str) -> None:
        if self._on_error:
            self._on_error(pesan)

    def get_daftar_produk(self) -> list[dict[str, Any]]:
        """Mengambil daftar produk untuk dropdown."""
        try:
            produk_list = self._produk_service.get_daftar_produk()
            return [
                {
                    "produk_id": p.produk_id,
                    "nama_produk": p.nama_produk,
                    "nama_kategori": p.nama_kategori,
                }
                for p in produk_list
            ]
        except Exception as e:
            self._notify_error(f"Gagal memuat produk: {e}")
            return []

    def get_all_targets_grouped(self) -> list[dict[str, Any]]:
        """Mengambil data target yang sudah dikelompokkan."""
        try:
            return self._target_service.get_all_targets_grouped()
        except Exception as e:
            self._notify_error(f"Gagal memuat target: {e}")
            return []

    def submit_save_target(
        self,
        produk_id: int,
        target_bulanan: int,
        target_harian: int,
        tahun: int,
        bulan: int,
    ) -> bool:
        """Menyimpan atau memperbarui target produksi."""
        try:
            self._target_service.save_target(
                produk_id, target_bulanan, target_harian, tahun, bulan
            )
            self._notify_sukses("Target telah berhasil disimpan.")
            return True
        except Exception as e:
            self._notify_error(f"Gagal menyimpan target: {e}")
            return False

    def check_target_exists(self, produk_id: int, tahun: int, bulan: int) -> bool:
        """Memeriksa keberadaan target via service."""
        try:
            return self._target_service.check_target_exists(produk_id, tahun, bulan)
        except Exception:
            return False
