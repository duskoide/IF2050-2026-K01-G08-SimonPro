from dataclasses import dataclass
from datetime import date


@dataclass
class TargetProduksi:
    target_id: int
    produk_id: int
    periode: str
    tanggal_mulai: date
    tanggal_selesai: date
    jumlah_target: int
    nama_produk: str | None = None
    nama_kategori: str | None = None

    @classmethod
    def from_row(cls, row) -> "TargetProduksi":
        return cls(
            target_id=row["target_id"],
            produk_id=row["produk_id"],
            periode=row["periode"],
            tanggal_mulai=row["tanggal_mulai"],
            tanggal_selesai=row["tanggal_selesai"],
            jumlah_target=row["jumlah_target"],
            nama_produk=row.get("nama_produk"),
            nama_kategori=row.get("nama_kategori"),
        )

    @staticmethod
    def getAll(db) -> list["TargetProduksi"]:
        rows = db.execute_query(
            "SELECT t.target_id, t.produk_id, t.periode, t.tanggal_mulai, "
            "t.tanggal_selesai, t.jumlah_target, p.nama_produk, p.nama_kategori "
            "FROM target_produksi t "
            "JOIN produk p ON p.produk_id = t.produk_id "
            "ORDER BY t.tanggal_mulai DESC, p.nama_produk ASC"
        )
        return [TargetProduksi.from_row(r) for r in rows]

    @staticmethod
    def getByProdukId(db, produk_id: int) -> list["TargetProduksi"]:
        rows = db.execute_query(
            "SELECT t.target_id, t.produk_id, t.periode, t.tanggal_mulai, "
            "t.tanggal_selesai, t.jumlah_target, p.nama_produk, p.nama_kategori "
            "FROM target_produksi t "
            "JOIN produk p ON p.produk_id = t.produk_id "
            "WHERE t.produk_id = %s "
            "ORDER BY t.tanggal_mulai DESC",
            (produk_id,),
        )
        return [TargetProduksi.from_row(r) for r in rows]

    @staticmethod
    def getTargetBulanan(db, produk_id: int, tanggal_mulai: date, tanggal_selesai: date) -> "TargetProduksi | None":
        rows = db.execute_query(
            "SELECT t.target_id, t.produk_id, t.periode, t.tanggal_mulai, "
            "t.tanggal_selesai, t.jumlah_target, p.nama_produk, p.nama_kategori "
            "FROM target_produksi t "
            "JOIN produk p ON p.produk_id = t.produk_id "
            "WHERE t.produk_id = %s AND t.periode = 'bulanan' "
            "AND t.tanggal_mulai = %s AND t.tanggal_selesai = %s",
            (produk_id, tanggal_mulai, tanggal_selesai),
        )
        return TargetProduksi.from_row(rows[0]) if rows else None

    @staticmethod
    def getTargetHarian(db, produk_id: int, tanggal_mulai: date, tanggal_selesai: date) -> "TargetProduksi | None":
        rows = db.execute_query(
            "SELECT t.target_id, t.produk_id, t.periode, t.tanggal_mulai, "
            "t.tanggal_selesai, t.jumlah_target, p.nama_produk, p.nama_kategori "
            "FROM target_produksi t "
            "JOIN produk p ON p.produk_id = t.produk_id "
            "WHERE t.produk_id = %s AND t.periode = 'harian' "
            "AND t.tanggal_mulai = %s AND t.tanggal_selesai = %s",
            (produk_id, tanggal_mulai, tanggal_selesai),
        )
        return TargetProduksi.from_row(rows[0]) if rows else None

    @staticmethod
    def upsert(db, produk_id: int, periode: str, tanggal_mulai: date, tanggal_selesai: date, jumlah_target: int) -> int:
        existing = db.execute_query(
            "SELECT target_id FROM target_produksi "
            "WHERE produk_id = %s AND periode = %s AND tanggal_mulai = %s AND tanggal_selesai = %s",
            (produk_id, periode, tanggal_mulai, tanggal_selesai),
        )
        if existing:
            db.execute_query(
                "UPDATE target_produksi SET jumlah_target = %s WHERE target_id = %s",
                (jumlah_target, existing[0]["target_id"]),
            )
            return existing[0]["target_id"]
        else:
            rows = db.execute_query(
                "INSERT INTO target_produksi (produk_id, periode, tanggal_mulai, tanggal_selesai, jumlah_target) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING target_id",
                (produk_id, periode, tanggal_mulai, tanggal_selesai, jumlah_target),
            )
            return rows[0]["target_id"]
