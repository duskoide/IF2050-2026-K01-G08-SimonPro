"""Controller untuk manajemen produk (UC02).

Menjembatani view dan service dengan role-gating:
- Admin: akses penuh (CRUD)
- Owner: akses baca (read-only)
"""

from __future__ import annotations

from typing import Callable

from src.models.Produk import Produk
from src.services.ProdukService import ProdukService


class ProdukController:
    """Controller yang menangani permintaan dari view terkait data produk — CD-11."""

    def __init__(self, service: ProdukService) -> None:
        self._service = service
        self._on_sukses: Callable[[str], None] | None = None
        self._on_error: Callable[[str], None] | None = None

    # ------------------------------------------------------------------
    # Callback wiring (untuk view)
    # ------------------------------------------------------------------
    def set_on_sukses(self, callback: Callable[[str], None]) -> None:
        """Pasang callback untuk notifikasi sukses ke view."""
        self._on_sukses = callback

    def set_on_error(self, callback: Callable[[str], None]) -> None:
        """Pasang callback untuk notifikasi error ke view."""
        self._on_error = callback

    def _notify_sukses(self, pesan: str) -> None:
        if self._on_sukses:
            self._on_sukses(pesan)

    def _notify_error(self, pesan: str) -> None:
        if self._on_error:
            self._on_error(pesan)

    # ------------------------------------------------------------------
    # Role gate
    # ------------------------------------------------------------------
    def _cek_admin(self, user_role: str) -> None:
        """Hanya admin yang boleh melakukan operasi tulis."""
        if user_role != "admin":
            raise PermissionError(
                "Akses ditolak: hanya Admin Produksi yang dapat mengelola data produk."
            )

    @staticmethod
    def _cek_role_valid(user_role: str) -> None:
        """Pastikan role yang diberikan valid (admin atau owner)."""
        if user_role not in ("admin", "owner"):
            raise PermissionError(f"Role tidak dikenal: {user_role}")

    # ------------------------------------------------------------------
    # Operasi baca (admin & owner)
    # ------------------------------------------------------------------
    def get_daftar_produk(self, user_role: str) -> list[Produk]:
        """Daftar produk aktif. Dapat diakses admin maupun owner."""
        self._cek_role_valid(user_role)
        return self._service.get_daftar_produk()

    def get_daftar_produk_termasuk_nonaktif(self, user_role: str) -> list[Produk]:
        """Seluruh produk termasuk nonaktif. Dapat diakses admin maupun owner."""
        self._cek_role_valid(user_role)
        return self._service.get_daftar_produk_termasuk_nonaktif()

    def get_produk_detail(self, user_role: str, produk_id: int) -> Produk | None:
        """Detail satu produk berdasarkan ID."""
        self._cek_role_valid(user_role)
        return self._service.get_produk_by_id(produk_id)

    def get_produk_by_kategori(
        self, user_role: str, nama_kategori: str
    ) -> list[Produk]:
        """Produk aktif dalam kategori tertentu."""
        self._cek_role_valid(user_role)
        return self._service.get_produk_by_kategori(nama_kategori)

    def cari_produk(self, user_role: str, query: str) -> list[Produk]:
        """Cari produk berdasarkan nama."""
        self._cek_role_valid(user_role)
        return self._service.cari_produk(query)

    def get_daftar_kategori(self, user_role: str) -> list[str]:
        """Daftar nama kategori untuk dropdown form."""
        self._cek_role_valid(user_role)
        return self._service.get_daftar_kategori()

    # ------------------------------------------------------------------
    # Operasi tulis (admin only)
    # ------------------------------------------------------------------
    def submit_tambah_produk(
        self,
        user_role: str,
        nama_produk: str,
        deskripsi_produk: str | None,
        satuan: str,
        gambar: str | None,
        nama_kategori: str,
    ) -> Produk | None:
        """Tambah produk baru. Hanya untuk admin."""
        try:
            self._cek_role_valid(user_role)
            self._cek_admin(user_role)
            produk = self._service.tambah_produk(
                nama_produk=nama_produk,
                deskripsi_produk=deskripsi_produk,
                satuan=satuan,
                gambar=gambar,
                nama_kategori=nama_kategori,
            )
            self._notify_sukses(f"Produk '{produk.nama_produk}' berhasil ditambahkan.")
            return produk
        except (ValueError, PermissionError) as e:
            self._notify_error(str(e))
            return None

    def submit_update_produk(
        self,
        user_role: str,
        produk_id: int,
        nama_produk: str,
        deskripsi_produk: str | None,
        satuan: str,
        gambar: str | None,
        status_aktif: bool,
        nama_kategori: str,
    ) -> Produk | None:
        """Simpan perubahan produk. Hanya untuk admin."""
        try:
            self._cek_role_valid(user_role)
            self._cek_admin(user_role)
            produk = self._service.simpan_perubahan(
                produk_id=produk_id,
                nama_produk=nama_produk,
                deskripsi_produk=deskripsi_produk,
                satuan=satuan,
                gambar=gambar,
                status_aktif=status_aktif,
                nama_kategori=nama_kategori,
            )
            self._notify_sukses(f"Produk '{produk.nama_produk}' berhasil disimpan.")
            return produk
        except (ValueError, PermissionError) as e:
            self._notify_error(str(e))
            return None

    def submit_nonaktifkan_produk(self, user_role: str, produk_id: int) -> bool:
        """Nonaktifkan produk. Hanya untuk admin.

        Returns:
            True jika berhasil, False jika gagal.
        """
        try:
            self._cek_role_valid(user_role)
            self._cek_admin(user_role)
            self._service.nonaktifkan_produk(produk_id)
            self._notify_sukses("Produk berhasil dinonaktifkan.")
            return True
        except (ValueError, PermissionError) as e:
            self._notify_error(str(e))
            return False
