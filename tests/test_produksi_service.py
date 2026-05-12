from datetime import date

from src.database.db_connection import get_db
from src.services.ProduksiService import ProduksiService


def test_validasi_menolak_defect_melebihi_aktual():
    service = ProduksiService(db=None)

    success, message, produksi_id = service.inputProduksiHarian(
        tanggal=date(2026, 5, 8),
        produk_id=1,
        jumlah_aktual=5,
        penanggung_jawab="Budi",
        detail_defect=[
            {"defect_id": 1, "jumlah_defect": 4},
            {"defect_id": 2, "jumlah_defect": 2},
        ],
    )

    assert success is False
    assert produksi_id is None
    assert message == "Jumlah defect tidak boleh melebihi jumlah aktual"


def test_validasi_menolak_penanggung_jawab_kosong():
    service = ProduksiService(db=None)

    success, message, produksi_id = service.inputProduksiHarian(
        tanggal=date(2026, 5, 8),
        produk_id=1,
        jumlah_aktual=5,
        penanggung_jawab="",
        detail_defect=[],
    )

    assert success is False
    assert produksi_id is None
    assert message == "Penanggung jawab wajib diisi"


def test_input_produksi_harian_menyimpan_detail_defect():
    db = get_db()
    service = ProduksiService(db=db)

    db.execute_update(
        "INSERT INTO kategori_produk (nama_kategori) VALUES (%s) ON CONFLICT DO NOTHING",
        ("Kategori Test UC05",),
    )
    produk_rows = db.execute_query(
        """
        INSERT INTO produk (
            nama_produk,
            deskripsi_produk,
            satuan,
            gambar,
            status_aktif,
            nama_kategori
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING produk_id
        """,
        (
            "Produk Test UC05",
            "Produk untuk test UC05",
            "pcs",
            None,
            True,
            "Kategori Test UC05",
        ),
    )
    db.connection.commit()
    produk_id = produk_rows[0]["produk_id"]

    try:
        success, message, produksi_id = service.inputProduksiHarian(
            tanggal=date(2026, 5, 8),
            produk_id=produk_id,
            jumlah_aktual=12,
            penanggung_jawab="Siti",
            kendala_produksi="Mesin perlu disetel ulang",
            detail_defect=[
                {"defect_id": 1, "jumlah_defect": 2},
                {"defect_id": 2, "jumlah_defect": 1},
                {"defect_id": 3, "jumlah_defect": 0},
            ],
        )

        assert success is True
        assert message == "Data produksi harian berhasil disimpan"
        assert produksi_id is not None

        produksi_rows = db.execute_query(
            "SELECT * FROM produksi_harian WHERE produksi_id = %s",
            (produksi_id,),
        )
        assert produksi_rows[0]["jumlah_aktual"] == 12
        assert produksi_rows[0]["jumlah_defect"] == 3
        assert produksi_rows[0]["penanggung_jawab"] == "Siti"

        detail_rows = db.execute_query(
            """
            SELECT defect_id, jumlah_defect
            FROM detail_defect
            WHERE produksi_id = %s
            ORDER BY defect_id
            """,
            (produksi_id,),
        )
        assert detail_rows == [
            {"defect_id": 1, "jumlah_defect": 2},
            {"defect_id": 2, "jumlah_defect": 1},
        ]
    finally:
        db.execute_update(
            "DELETE FROM produksi_harian WHERE produk_id = %s",
            (produk_id,),
        )
        db.execute_update("DELETE FROM produk WHERE produk_id = %s", (produk_id,))
        db.execute_update(
            "DELETE FROM kategori_produk WHERE nama_kategori = %s",
            ("Kategori Test UC05",),
        )

