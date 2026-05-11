"""Service layer untuk manajemen produk (UC02).

Menyediakan validasi dan logika bisnis sebelum operasi CRUD
didelegasikan ke model Produk.
"""

from src.database.db_connection import Database
from src.models.Produk import Produk


class ProdukService:
    """Service untuk mengelola data produk — CD-10."""

    def __init__(self, db: Database) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Validasi internal
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_nama_produk(nama: str) -> None:
        """Nama produk wajib diisi dan tidak boleh kosong."""
        if not nama or not nama.strip():
            raise ValueError("Nama produk wajib diisi.")

    @staticmethod
    def _validate_satuan(satuan: str) -> None:
        """Satuan wajib diisi."""
        if not satuan or not satuan.strip():
            raise ValueError("Satuan produk wajib diisi.")

    def _validate_kategori_exists(self, nama_kategori: str) -> None:
        """Pastikan nama_kategori terdaftar di tabel kategori_produk."""
        if not nama_kategori or not nama_kategori.strip():
            raise ValueError("Kategori produk wajib dipilih.")
        rows = self._db.execute_query(
            "SELECT 1 FROM kategori_produk WHERE nama_kategori = %s",
            (nama_kategori.strip(),),
        )
        if not rows:
            raise ValueError(f"Kategori '{nama_kategori}' tidak ditemukan.")

    def _validate_nama_unique(self, nama: str, exclude_id: int | None = None) -> None:
        """Pastikan nama_produk belum dipakai produk lain."""
        if Produk.cekNamaExist(self._db, nama.strip(), exclude_id):
            raise ValueError(f"Nama produk '{nama}' sudah digunakan.")

    # ------------------------------------------------------------------
    # Operasi baca
    # ------------------------------------------------------------------
    def get_daftar_produk(self) -> list[Produk]:
        """Daftar produk yang masih aktif."""
        return Produk.getAll(self._db)

    def get_daftar_produk_termasuk_nonaktif(self) -> list[Produk]:
        """Seluruh produk termasuk yang sudah dinonaktifkan."""
        return Produk.getAllIncludingInactive(self._db)

    def get_produk_by_id(self, produk_id: int) -> Produk | None:
        """Satu produk berdasarkan ID."""
        return Produk.getById(self._db, produk_id)

    def get_produk_by_kategori(self, nama_kategori: str) -> list[Produk]:
        """Produk aktif dalam satu kategori."""
        return Produk.getByKategori(self._db, nama_kategori)

    def cari_produk(self, query: str) -> list[Produk]:
        """Cari produk berdasarkan nama (case-insensitive)."""
        return Produk.getByNama(self._db, query)

    def get_daftar_kategori(self) -> list[str]:
        """Daftar nama_kategori yang tersedia (untuk dropdown form)."""
        rows = self._db.execute_query(
            "SELECT nama_kategori FROM kategori_produk ORDER BY nama_kategori ASC"
        )
        return [r["nama_kategori"] for r in rows]

    # ------------------------------------------------------------------
    # Operasi tulis
    # ------------------------------------------------------------------
    def tambah_produk(
        self,
        nama_produk: str,
        deskripsi_produk: str | None,
        satuan: str,
        gambar: str | None,
        nama_kategori: str,
    ) -> Produk:
        """Tambah produk baru setelah lolos validasi."""
        nama = nama_produk.strip()
        sat = satuan.strip() if satuan else ""
        desk = deskripsi_produk.strip() if deskripsi_produk else ""
        gbr = gambar.strip() if gambar else ""
        kat = nama_kategori.strip()

        self._validate_nama_produk(nama)
        self._validate_nama_unique(nama)
        self._validate_satuan(sat)
        self._validate_kategori_exists(kat)

        produk_id = Produk.tambah(self._db, nama, desk, sat, gbr, kat)

        hasil = Produk.getById(self._db, produk_id)
        if hasil is None:
            raise RuntimeError("Gagal mengambil kembali produk yang baru dibuat.")
        return hasil

    def simpan_perubahan(
        self,
        produk_id: int,
        nama_produk: str,
        deskripsi_produk: str | None,
        satuan: str,
        gambar: str | None,
        status_aktif: bool,
        nama_kategori: str,
    ) -> Produk:
        """Simpan perubahan data produk setelah lolos validasi."""
        nama = nama_produk.strip()
        sat = satuan.strip() if satuan else ""
        desk = deskripsi_produk.strip() if deskripsi_produk else ""
        gbr = gambar.strip() if gambar else ""
        kat = nama_kategori.strip()

        self._validate_nama_produk(nama)
        self._validate_nama_unique(nama, exclude_id=produk_id)
        self._validate_satuan(sat)
        self._validate_kategori_exists(kat)

        Produk.simpanPerubahan(
            self._db, produk_id, nama, desk, sat, gbr, status_aktif, kat
        )

        updated = Produk.getById(self._db, produk_id)
        if updated is None:
            raise RuntimeError("Gagal mengambil kembali produk setelah disimpan.")
        return updated

    def nonaktifkan_produk(self, produk_id: int) -> None:
        """Nonaktifkan produk (soft delete)."""
        produk = Produk.getById(self._db, produk_id)
        if produk is None:
            raise ValueError(f"Produk dengan ID {produk_id} tidak ditemukan.")
        Produk.nonaktifkan(self._db, produk_id)

    def cek_nama_tersedia(self, nama: str, exclude_id: int | None = None) -> bool:
        """True bila nama_produk belum dipakai."""
        return not Produk.cekNamaExist(self._db, nama.strip(), exclude_id)

    def get_next_kode_produk(self) -> str:
        """Generate kode produk berikutnya berdasarkan MAX produk_id + 1."""
        rows = self._db.execute_query(
            "SELECT COALESCE(MAX(produk_id), 0) + 1 AS next_id FROM produk"
        )
        next_id = rows[0]["next_id"]
        return f"PRD-{next_id:03d}"
