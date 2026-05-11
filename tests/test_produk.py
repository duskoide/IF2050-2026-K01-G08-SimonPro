"""Integration tests for ProdukService and ProdukController (UC02).

Requires a running PostgreSQL server with dummy data loaded.
Run ``docker compose up -d`` then ``python -m pytest tests/test_produk.py -v``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from src.controllers.ProdukController import ProdukController
from src.database.db_connection import get_db, test_connection
from src.models.Produk import Produk
from src.services.ProdukService import ProdukService

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def db():
    """Pastikan database terhubung sebelum menjalankan tes."""
    assert test_connection(), "Database tidak terjangkau. Jalankan docker compose up -d"
    return get_db()


@pytest.fixture(scope="module")
def service(db):
    """Service bersama untuk seluruh modul tes."""
    return ProdukService(db)


@pytest.fixture(scope="module")
def controller(service):
    """Controller bersama untuk seluruh modul tes."""
    return ProdukController(service)


# ---------------------------------------------------------------------------
# ProdukService — Operasi Baca
# ---------------------------------------------------------------------------


class TestProdukServiceBaca:
    """Tes operasi baca pada ProdukService."""

    def test_get_daftar_produk_aktif(self, service):
        """TC-P02-01: get_daftar_produk mengembalikan hanya produk aktif."""
        produk_list = service.get_daftar_produk()
        assert len(produk_list) == 8
        assert all(p.status_aktif for p in produk_list)
        nama_list = {p.nama_produk for p in produk_list}
        assert "Kaos Polos Pria" in nama_list

    def test_get_daftar_produk_termasuk_nonaktif(self, service):
        """TC-P02-02: get_daftar_produk_termasuk_nonaktif mengembalikan semua produk."""
        produk_list = service.get_daftar_produk_termasuk_nonaktif()
        assert len(produk_list) >= 8

    def test_get_produk_by_id_ada(self, service):
        """TC-P02-03: get_produk_by_id dengan ID valid mengembalikan produk."""
        produk = service.get_produk_by_id(1)
        assert produk is not None
        assert produk.produk_id == 1
        assert produk.nama_produk == "Kaos Polos Pria"

    def test_get_produk_by_id_tidak_ada(self, service):
        """TC-P02-04: get_produk_by_id dengan ID tidak valid mengembalikan None."""
        produk = service.get_produk_by_id(9999)
        assert produk is None

    def test_get_produk_by_kategori(self, service):
        """TC-P02-05: get_produk_by_kategori menyaring berdasarkan kategori."""
        produk_list = service.get_produk_by_kategori("Atasan")
        assert len(produk_list) == 3
        assert all(p.nama_kategori == "Atasan" for p in produk_list)

    def test_cari_produk_parsial(self, service):
        """TC-P02-06: cari_produk dengan kata kunci parsial."""
        hasil = service.cari_produk("Kaos")
        assert len(hasil) >= 3
        nama_list = {p.nama_produk for p in hasil}
        assert "Kaos Polos Pria" in nama_list

    def test_cari_produk_tidak_ketemu(self, service):
        """TC-P02-07: cari_produk yang tidak cocok mengembalikan list kosong."""
        hasil = service.cari_produk("XYZ___tidak_ada")
        assert hasil == []

    def test_get_daftar_kategori(self, service):
        """TC-P02-08: get_daftar_kategori mengembalikan 3 kategori."""
        kategori_list = service.get_daftar_kategori()
        assert len(kategori_list) == 3
        assert "Atasan" in kategori_list
        assert "Bawahan" in kategori_list
        assert "Pakaian Dalam" in kategori_list


# ---------------------------------------------------------------------------
# ProdukService — Operasi Tulis
# ---------------------------------------------------------------------------


class TestProdukServiceTulis:
    """Tes operasi tulis (tambah, ubah, nonaktifkan) pada ProdukService."""

    def test_tambah_produk_berhasil(self, service, db):
        """TC-P02-09: tambah_produk dengan data valid berhasil."""
        produk = service.tambah_produk(
            nama_produk="Produk Test Baru",
            deskripsi_produk="Deskripsi test",
            satuan="pcs",
            gambar=None,
            nama_kategori="Atasan",
        )
        assert produk is not None
        assert produk.nama_produk == "Produk Test Baru"
        assert produk.nama_kategori == "Atasan"
        assert produk.status_aktif is True

        # Bersihkan
        Produk.nonaktifkan(db, produk.produk_id)

    def test_tambah_produk_nama_kosong(self, service):
        """TC-P02-10: tambah_produk dengan nama kosong gagal."""
        with pytest.raises(ValueError, match="Nama produk wajib diisi"):
            service.tambah_produk(
                nama_produk="",
                deskripsi_produk=None,
                satuan="pcs",
                gambar=None,
                nama_kategori="Atasan",
            )

    def test_tambah_produk_nama_duplikat(self, service):
        """TC-P02-11: tambah_produk dengan nama yang sudah ada gagal."""
        with pytest.raises(ValueError, match="sudah digunakan"):
            service.tambah_produk(
                nama_produk="Kaos Polos Pria",  # sudah ada di dummy data
                deskripsi_produk=None,
                satuan="pcs",
                gambar=None,
                nama_kategori="Atasan",
            )

    def test_tambah_produk_satuan_kosong(self, service):
        """TC-P02-12: tambah_produk dengan satuan kosong gagal."""
        with pytest.raises(ValueError, match="Satuan produk wajib diisi"):
            service.tambah_produk(
                nama_produk="Produk Unik",
                deskripsi_produk=None,
                satuan="",
                gambar=None,
                nama_kategori="Atasan",
            )

    def test_tambah_produk_kategori_tidak_ada(self, service):
        """TC-P02-13: tambah_produk dengan kategori tidak terdaftar gagal."""
        with pytest.raises(ValueError, match="tidak ditemukan"):
            service.tambah_produk(
                nama_produk="Produk Unik",
                deskripsi_produk=None,
                satuan="pcs",
                gambar=None,
                nama_kategori="KategoriFiktif",
            )

    def test_simpan_perubahan_berhasil(self, service, db):
        """TC-P02-14: simpan_perubahan menyimpan data baru."""
        # Tambah dulu
        produk = service.tambah_produk(
            nama_produk="Produk Edit Test",
            deskripsi_produk="Sebelum edit",
            satuan="pcs",
            gambar=None,
            nama_kategori="Bawahan",
        )

        # Ubah
        updated = service.simpan_perubahan(
            produk_id=produk.produk_id,
            nama_produk="Produk Edit Test Revisi",
            deskripsi_produk="Sesudah edit",
            satuan="set",
            gambar=None,
            status_aktif=True,
            nama_kategori="Atasan",
        )
        assert updated is not None
        assert updated.nama_produk == "Produk Edit Test Revisi"
        assert updated.satuan == "set"
        assert updated.nama_kategori == "Atasan"

        # Bersihkan
        Produk.nonaktifkan(db, produk.produk_id)

    def test_simpan_perubahan_nama_duplikat(self, service, db):
        """TC-P02-15: simpan_perubahan ke nama yang sudah dipakai produk lain gagal."""
        with pytest.raises(ValueError, match="sudah digunakan"):
            service.simpan_perubahan(
                produk_id=1,
                nama_produk="Kemeja Formal Pria",  # milik produk_id=2
                deskripsi_produk=None,
                satuan="pcs",
                gambar=None,
                status_aktif=True,
                nama_kategori="Atasan",
            )

    def test_nonaktifkan_produk_berhasil(self, service, db):
        """TC-P02-16: nonaktifkan_produk mengubah status_aktif menjadi FALSE."""
        # Tambah produk sementara
        produk = service.tambah_produk(
            nama_produk="Produk Untuk Dihapus",
            deskripsi_produk=None,
            satuan="pcs",
            gambar=None,
            nama_kategori="Atasan",
        )
        pid = produk.produk_id

        service.nonaktifkan_produk(pid)

        # Verifikasi — produk masih ada tapi tidak aktif
        p = Produk.getById(db, pid)
        assert p is not None
        assert p.status_aktif is False

    def test_nonaktifkan_produk_id_tidak_ada(self, service):
        """TC-P02-17: nonaktifkan_produk dengan ID tidak valid gagal."""
        with pytest.raises(ValueError, match="tidak ditemukan"):
            service.nonaktifkan_produk(99999)


# ---------------------------------------------------------------------------
# ProdukService — Cek Nama Tersedia
# ---------------------------------------------------------------------------


class TestProdukServiceCekNama:
    """Tes pengecekan ketersediaan nama produk."""

    def test_cek_nama_tersedia_true(self, service):
        """TC-P02-18: Nama yang belum dipakai mengembalikan True."""
        assert service.cek_nama_tersedia("Nama Unik Belum Ada") is True

    def test_cek_nama_tersedia_false(self, service):
        """TC-P02-19: Nama yang sudah dipakai mengembalikan False."""
        assert service.cek_nama_tersedia("Kaos Polos Pria") is False

    def test_cek_nama_tersedia_dengan_exclude(self, service):
        """TC-P02-20: Nama milik sendiri dianggap tersedia saat edit."""
        assert service.cek_nama_tersedia("Kaos Polos Pria", exclude_id=1) is True


# ---------------------------------------------------------------------------
# ProdukController — Role Gating
# ---------------------------------------------------------------------------


class TestProdukControllerRole:
    """Tes role-based access control pada ProdukController."""

    # --- Baca: admin dan owner ---

    def test_get_daftar_produk_admin(self, controller):
        """TC-P02-21: Admin dapat membaca daftar produk."""
        result = controller.get_daftar_produk("admin")
        assert len(result) > 0

    def test_get_daftar_produk_owner(self, controller):
        """TC-P02-22: Owner dapat membaca daftar produk."""
        result = controller.get_daftar_produk("owner")
        assert len(result) > 0

    def test_get_daftar_produk_role_invalid(self, controller):
        """TC-P02-23: Role tidak dikenal ditolak."""
        with pytest.raises(PermissionError):
            controller.get_daftar_produk("tamu")

    # --- Tulis: admin only ---

    def test_submit_tambah_produk_admin(self, controller, db):
        """TC-P02-24: Admin dapat menambah produk."""
        hasil = controller.submit_tambah_produk(
            "admin",
            nama_produk="Produk Controller Test",
            deskripsi_produk=None,
            satuan="pcs",
            gambar=None,
            nama_kategori="Atasan",
        )
        assert hasil is not None
        assert hasil.nama_produk == "Produk Controller Test"

        # Bersihkan
        Produk.nonaktifkan(db, hasil.produk_id)

    def test_submit_tambah_produk_owner_ditolak(self, controller):
        """TC-P02-25: Owner tidak dapat menambah produk."""
        hasil = controller.submit_tambah_produk(
            "owner",
            nama_produk="Produk Owner Test",
            deskripsi_produk=None,
            satuan="pcs",
            gambar=None,
            nama_kategori="Atasan",
        )
        assert hasil is None

    def test_submit_nonaktifkan_produk_admin(self, controller, db):
        """TC-P02-26: Admin dapat menonaktifkan produk."""
        # Tambah dulu via service supaya bisa dites controller-nya
        srv = ProdukService(db)
        produk = srv.tambah_produk(
            nama_produk="Produk Nonaktif Test",
            deskripsi_produk=None,
            satuan="pcs",
            gambar=None,
            nama_kategori="Bawahan",
        )

        ok = controller.submit_nonaktifkan_produk("admin", produk.produk_id)
        assert ok is True

        # Verifikasi sudah nonaktif
        p = Produk.getById(db, produk.produk_id)
        assert p.status_aktif is False

    def test_submit_nonaktifkan_produk_owner_ditolak(self, controller):
        """TC-P02-27: Owner tidak dapat menonaktifkan produk."""
        ok = controller.submit_nonaktifkan_produk("owner", 1)
        assert ok is False


# ---------------------------------------------------------------------------
# ProdukController — Callback
# ---------------------------------------------------------------------------


class TestProdukControllerCallback:
    """Tes wiring callback pada ProdukController."""

    def test_callback_sukses_dipanggil(self, db):
        """TC-P02-28: Callback on_sukses dipanggil setelah operasi berhasil."""
        srv = ProdukService(db)
        ctrl = ProdukController(srv)

        sukses_pesan: list[str] = []
        error_pesan: list[str] = []

        ctrl.set_on_sukses(lambda msg: sukses_pesan.append(msg))
        ctrl.set_on_error(lambda msg: error_pesan.append(msg))

        produk = ctrl.submit_tambah_produk(
            "admin",
            nama_produk="Produk Callback Test",
            deskripsi_produk=None,
            satuan="pcs",
            gambar=None,
            nama_kategori="Pakaian Dalam",
        )

        assert len(sukses_pesan) == 1
        assert "berhasil ditambahkan" in sukses_pesan[0]
        assert len(error_pesan) == 0

        # Bersihkan
        if produk:
            Produk.nonaktifkan(db, produk.produk_id)

    def test_callback_error_dipanggil(self, db):
        """TC-P02-29: Callback on_error dipanggil saat validasi gagal."""
        srv = ProdukService(db)
        ctrl = ProdukController(srv)

        sukses_pesan: list[str] = []
        error_pesan: list[str] = []

        ctrl.set_on_sukses(lambda msg: sukses_pesan.append(msg))
        ctrl.set_on_error(lambda msg: error_pesan.append(msg))

        hasil = ctrl.submit_tambah_produk(
            "admin",
            nama_produk="",  # validasi gagal
            deskripsi_produk=None,
            satuan="pcs",
            gambar=None,
            nama_kategori="Atasan",
        )

        assert hasil is None
        assert len(error_pesan) == 1
        assert "wajib diisi" in error_pesan[0]
        assert len(sukses_pesan) == 0
