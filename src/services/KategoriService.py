from src.database.db_connection import get_db
from src.models.KategoriProduk import KategoriProduk


class KategoriService:
    def __init__(self):
        self.db = get_db()
        # self._daftarKategori: list[KategoriProduk] | None = None

    # memastikan daftarKategori sudah ter-load
    # def _ensureLoaded(self) -> None:
    #     if self._daftarKategori is None:
    #         self._daftarKategori = KategoriProduk.getAll(self.db)

    # def _reload(self) -> None:
    #     self._daftarKategori = KategoriProduk.getAll(self.db) #Re-query setelah mutasi agar in-memory konsisten dengan DB.

    # Validasi
    def _validasiKategori(self, nama: str) -> bool:
        if nama is None or nama.strip() == "":
            return False
        return True

    # Tambah Kategori
    def tambahKategori(self, nama: str) -> bool:
        if not self._validasiKategori(nama):
            return False
        if KategoriProduk.cekDuplikasi(self.db, nama):
            return False
        KategoriProduk.tambah(self.db, nama)
        # self._reload() #Re-query agar kategori_id baru (auto-generated DB) ikut masuk
        return True

    # Update Kategori
    def updateKategori(self, kategori_id: int, nama_baru: str) -> bool:
        if not self._validasiKategori(nama_baru):
            return False
        if KategoriProduk.cekDuplikasi(self.db, nama_baru, exclude_id=kategori_id):
            return False

        # update kategori
        KategoriProduk.simpanPerubahan(self.db, kategori_id, nama_baru)
        # self._ensureLoaded()
        # for k in self._daftarKategori:
        #     if k.kategori_id == kategori_id:
        #         k.nama_kategori = nama_baru
                # break
        return True

    # Hapus Kategori
    # def updateKategori(self, kategori_id, nama_baru):
    #     if not self._validasiKategori(nama_baru):
    #         return False
    #
    #     # cek duplikasi (exclude diri sendiri)
    #     if KategoriProduk.cekDuplikasi(self.db, nama_baru, exclude_id=kategori_id):
    #         return False
    #
    #     # update kategori
    #     KategoriProduk.simpanPerubahan(self.db, kategori_id, nama_baru)
    #     return True

    def hapusKategori(self, kategori_id: int) -> bool:
        KategoriProduk.hapus(self.db, kategori_id)
        return True

    # Get List Kategori
    # def getDaftarKategori(self) -> list[KategoriProduk]:
    #     # self._ensureLoaded()
    #     return self._daftarKategori

    def getDaftarKategori(self) -> list[KategoriProduk]:
        return KategoriProduk.getAll(self.db)
    
    def getProdukTerbaru(self) -> list[dict]:
        return KategoriProduk.getProdukByKategori(self.db)

