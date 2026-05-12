from src.database.db_connection import get_db
from src.models.KategoriProduk import KategoriProduk


class KategoriService:
    def __init__(self):
        self.db = get_db()

    def _validasiKategori(self, nama: str) -> bool:
        if nama is None or nama.strip() == "":
            return False
        return True

    def tambahKategori(self, nama: str) -> bool:
        if not self._validasiKategori(nama):
            return False
        if KategoriProduk.cekDuplikasi(self.db, nama):
            return False
        KategoriProduk.tambah(self.db, nama)
        return True

    def updateKategori(self, kategori_id: int, nama_baru: str) -> bool:
        if not self._validasiKategori(nama_baru):
            return False
        if KategoriProduk.cekDuplikasi(self.db, nama_baru, exclude_id=kategori_id):
            return False
        KategoriProduk.simpanPerubahan(self.db, kategori_id, nama_baru)
        return True

    def hapusKategori(self, kategori_id: int) -> bool:
        if KategoriProduk.hasProduk(self.db, kategori_id):
            return False
        KategoriProduk.hapus(self.db, kategori_id)
        return True

    def getDaftarKategori(self) -> list[KategoriProduk]:
        return KategoriProduk.getAll(self.db)

    def getProdukTerbaru(self) -> list[dict]:
        return KategoriProduk.getProdukByKategori(self.db)