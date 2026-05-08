from dataclasses import dataclass


@dataclass
class Produk:
    produk_id: int
    nama_produk: str
    deskripsi_produk: str
    satuan: str
    gambar: str
    status_aktif: bool
    nama_kategori: str

    @classmethod
    def from_row(cls, row) -> "Produk":
        return cls(
            produk_id=row["produk_id"],
            nama_produk=row["nama_produk"],
            deskripsi_produk=row.get("deskripsi_produk"),
            satuan=row.get("satuan"),
            gambar=row.get("gambar"),
            status_aktif=row.get("status_aktif", True),
            nama_kategori=row["nama_kategori"],
        )

    @staticmethod
    def getAll(db) -> list["Produk"]:
        rows = db.execute_query(
            "SELECT produk_id, nama_produk, deskripsi_produk, satuan, gambar, "
            "status_aktif, nama_kategori "
            "FROM produk "
            "WHERE status_aktif = TRUE "
            "ORDER BY nama_produk ASC"
        )
        return [Produk.from_row(r) for r in rows]

    @staticmethod
    def getById(db, produk_id: int) -> "Produk | None":
        rows = db.execute_query(
            "SELECT produk_id, nama_produk, deskripsi_produk, satuan, gambar, "
            "status_aktif, nama_kategori "
            "FROM produk "
            "WHERE produk_id = %s",
            (produk_id,),
        )
        return Produk.from_row(rows[0]) if rows else None

    @staticmethod
    def getByKategori(db, nama_kategori: str) -> list["Produk"]:
        rows = db.execute_query(
            "SELECT produk_id, nama_produk, deskripsi_produk, satuan, gambar, "
            "status_aktif, nama_kategori "
            "FROM produk "
            "WHERE nama_kategori = %s AND status_aktif = TRUE "
            "ORDER BY nama_produk ASC",
            (nama_kategori,),
        )
        return [Produk.from_row(r) for r in rows]

    @staticmethod
    def tambah(
        db,
        nama_produk: str,
        deskripsi_produk: str,
        satuan: str,
        gambar: str,
        nama_kategori: str,
    ) -> None:
        db.execute_update(
            "INSERT INTO produk "
            "(nama_produk, deskripsi_produk, satuan, gambar, status_aktif, nama_kategori) "
            "VALUES (%s, %s, %s, %s, TRUE, %s)",
            (nama_produk, deskripsi_produk, satuan, gambar, nama_kategori),
        )

    @staticmethod
    def simpanPerubahan(
        db,
        produk_id: int,
        nama_produk: str,
        deskripsi_produk: str,
        satuan: str,
        gambar: str,
        status_aktif: bool,
        nama_kategori: str,
    ) -> None:
        db.execute_update(
            "UPDATE produk "
            "SET nama_produk = %s, deskripsi_produk = %s, satuan = %s, "
            "gambar = %s, status_aktif = %s, nama_kategori = %s "
            "WHERE produk_id = %s",
            (
                nama_produk,
                deskripsi_produk,
                satuan,
                gambar,
                status_aktif,
                nama_kategori,
                produk_id,
            ),
        )

    @staticmethod
    def nonaktifkan(db, produk_id: int) -> None:
        db.execute_update(
            "UPDATE produk SET status_aktif = FALSE WHERE produk_id = %s",
            (produk_id,),
        )

    @staticmethod
    def getAllWithKategori(db) -> list[dict]:
        rows = db.execute_query(
            "SELECT produk_id, nama_produk, deskripsi_produk, satuan, gambar, "
            "status_aktif, nama_kategori "
            "FROM produk "
            "ORDER BY nama_kategori ASC, nama_produk ASC"
        )
        return rows

    @staticmethod
    def getByNama(db, nama_produk: str) -> list["Produk"]:
        rows = db.execute_query(
            "SELECT produk_id, nama_produk, deskripsi_produk, satuan, gambar, "
            "status_aktif, nama_kategori "
            "FROM produk "
            "WHERE nama_produk ILIKE %s "
            "ORDER BY nama_produk ASC",
            (f"%{nama_produk}%",),
        )
        return [Produk.from_row(r) for r in rows]

    @staticmethod
    def cekNamaExist(db, nama_produk: str, exclude_id: int | None = None) -> bool:
        if exclude_id is not None:
            rows = db.execute_query(
                "SELECT 1 FROM produk WHERE nama_produk = %s AND produk_id != %s",
                (nama_produk, exclude_id),
            )
        else:
            rows = db.execute_query(
                "SELECT 1 FROM produk WHERE nama_produk = %s", (nama_produk,)
            )
        return len(rows) > 0

    @staticmethod
    def getAllIncludingInactive(db) -> list["Produk"]:
        rows = db.execute_query(
            "SELECT produk_id, nama_produk, deskripsi_produk, satuan, gambar, "
            "status_aktif, nama_kategori "
            "FROM produk "
            "ORDER BY nama_produk ASC"
        )
        return [Produk.from_row(r) for r in rows]

    def __str__(self) -> str:
        return self.nama_produk
