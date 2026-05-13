"""Model untuk data produksi harian."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass
class ProduksiHarian:
    produksi_id: int | None
    tanggal: date
    produk_id: int
    jumlah_aktual: int
    jumlah_defect: int
    penanggung_jawab: str
    kendala_produksi: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "ProduksiHarian":
        return cls(
            produksi_id=row["produksi_id"],
            tanggal=row["tanggal"],
            produk_id=row["produk_id"],
            jumlah_aktual=row["jumlah_aktual"],
            jumlah_defect=row["jumlah_defect"],
            penanggung_jawab=row["penanggung_jawab"],
            kendala_produksi=row.get("kendala_produksi"),
        )

    @staticmethod
    def get_produk_aktif(db) -> list[dict[str, Any]]:
        return db.execute_query(
            """
            SELECT produk_id, nama_produk, satuan, nama_kategori
            FROM produk
            WHERE status_aktif = TRUE
            ORDER BY nama_produk
            """
        )

    @staticmethod
    def get_tipe_defect(db) -> list[dict[str, Any]]:
        return db.execute_query(
            """
            SELECT defect_id, nama_defect
            FROM tipe_defect
            ORDER BY defect_id
            """
        )

    @staticmethod
    def produk_exists(db, produk_id: int) -> bool:
        rows = db.execute_query(
            """
            SELECT 1
            FROM produk
            WHERE produk_id = %s AND status_aktif = TRUE
            LIMIT 1
            """,
            (produk_id,),
        )
        return len(rows) > 0

    @staticmethod
    def tipe_defect_ids(db) -> set[int]:
        rows = db.execute_query("SELECT defect_id FROM tipe_defect")
        return {row["defect_id"] for row in rows}

    @staticmethod
    def tambah(db, produksi: "ProduksiHarian", detail_defect: list[dict[str, int]]) -> int:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO produksi_harian (
                    tanggal,
                    produk_id,
                    jumlah_aktual,
                    jumlah_defect,
                    penanggung_jawab,
                    kendala_produksi
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING produksi_id
                """,
                (
                    produksi.tanggal,
                    produksi.produk_id,
                    produksi.jumlah_aktual,
                    produksi.jumlah_defect,
                    produksi.penanggung_jawab,
                    produksi.kendala_produksi,
                ),
            )
            produksi_id = cursor.fetchone()["produksi_id"]

            if detail_defect:
                cursor.executemany(
                    """
                    INSERT INTO detail_defect (
                        produksi_id,
                        defect_id,
                        jumlah_defect
                    )
                    VALUES (%s, %s, %s)
                    """,
                    [
                        (
                            produksi_id,
                            detail["defect_id"],
                            detail["jumlah_defect"],
                        )
                        for detail in detail_defect
                    ],
                )

            return produksi_id

