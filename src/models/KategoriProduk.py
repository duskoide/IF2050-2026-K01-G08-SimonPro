from dataclasses import dataclass

@dataclass
class KategoriProduk:
    kategori_id: int
    nama_kategori: str

    @classmethod
    def from_row(cls, row) -> "KategoriProduk":
        return cls(
            kategori_id=row["kategori_id"],
            nama_kategori=row["nama_kategori"],
        )

    # Cek Duplikasi
    @staticmethod
    def cekDuplikasi(db, nama, exclude_id=None):
        if exclude_id is not None:
            rows = db.execute_query(
                "SELECT 1 FROM kategori_produk "
                "WHERE LOWER(nama_kategori) = LOWER(%s) "
                "AND kategori_id != %s",
                (nama, exclude_id),
            )
        else:
            rows = db.execute_query(
                "SELECT 1 FROM kategori_produk "
                "WHERE LOWER(nama_kategori) = LOWER(%s)",
                (nama,),
            )
        return len(rows) > 0

    # simpan perubahan
    @staticmethod
    def simpanPerubahan(db, kategori_id: int, nama_baru: str) -> None:
        old = db.execute_query(
            "SELECT nama_kategori FROM kategori_produk WHERE kategori_id = %s",
            (kategori_id,),
        )
        if not old:
            return
        nama_lama = old[0]["nama_kategori"]
        with db:
            db.execute_update(
                "UPDATE produk SET nama_kategori = %s WHERE nama_kategori = %s",
                (nama_baru, nama_lama),
            )
            db.execute_update(
                "UPDATE kategori_produk SET nama_kategori = %s WHERE kategori_id = %s",
                (nama_baru, kategori_id),
            )
    
    # Insert
    @staticmethod
    def tambah(db, nama):
        db.execute_update(
            "INSERT INTO kategori_produk (nama_kategori) VALUES (%s)",
            (nama,),
        )

    # update
    # def update(db, kategori_id, nama_baru):
    #     db.execute_update(
    #         "UPDATE kategori_produk SET nama_kategori = %s "
    #         "WHERE kategori_id = %s",
    #         (nama_baru, kategori_id),
    #     )

    # delete
    @staticmethod
    def hapus(db, kategori_id: int) -> None:
        db.execute_update(
            "DELETE FROM kategori_produk WHERE kategori_id = %s",
            (kategori_id,),
        )

    @staticmethod
    def hasProduk(db, kategori_id: int) -> bool:
        nama = db.execute_query(
            "SELECT nama_kategori FROM kategori_produk WHERE kategori_id = %s",
            (kategori_id,),
        )
        if not nama:
            return False
        rows = db.execute_query(
            "SELECT 1 FROM produk WHERE nama_kategori = %s LIMIT 1",
            (nama[0]["nama_kategori"],),
        )
        return len(rows) > 0

    @staticmethod
    def getAll(db) -> list["KategoriProduk"]:
        rows = db.execute_query(
            "SELECT kategori_id, nama_kategori "
            "FROM kategori_produk "
            "ORDER BY nama_kategori ASC"
        )
        return [KategoriProduk.from_row(r) for r in rows]

    @staticmethod
    def getProdukByKategori(db) -> list[dict]:
        rows = db.execute_query(
            "SELECT p.produk_id, p.nama_produk, p.deskripsi_produk, "
            "       p.satuan, p.gambar, p.status_aktif, "
            "       p.nama_kategori, k.kategori_id "
            "FROM produk p "
            "JOIN kategori_produk k "
            "ON LOWER(p.nama_kategori) = LOWER(k.nama_kategori) "
            "ORDER BY k.nama_kategori ASC, p.nama_produk ASC"
        )
        return rows  # list[dict], diproses Produk.from_row() di layer atas
 

    def __str__(self) -> str:
        return self.nama_kategori