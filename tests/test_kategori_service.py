import importlib

kategori_module = importlib.import_module("src.services.KategoriService")


def test_tambah_kategori_valid(monkeypatch):
    calls = {"tambah": 0}

    monkeypatch.setattr(kategori_module, "get_db", lambda: object())
    monkeypatch.setattr(kategori_module.KategoriProduk, "cekDuplikasi", lambda db, nama, exclude_id=None: False)
    monkeypatch.setattr(
        kategori_module.KategoriProduk,
        "tambah",
        lambda db, nama: calls.__setitem__("tambah", calls["tambah"] + 1),
    )

    service = kategori_module.KategoriService()

    assert service.tambahKategori("Atasan Baru") is True
    assert calls["tambah"] == 1


def test_tambah_kategori_duplikat_ditolak(monkeypatch):
    monkeypatch.setattr(kategori_module, "get_db", lambda: object())
    monkeypatch.setattr(kategori_module.KategoriProduk, "cekDuplikasi", lambda db, nama, exclude_id=None: True)

    service = kategori_module.KategoriService()

    assert service.tambahKategori("Atasan") is False


def test_update_kategori_valid(monkeypatch):
    calls = {"update": 0}

    monkeypatch.setattr(kategori_module, "get_db", lambda: object())
    monkeypatch.setattr(kategori_module.KategoriProduk, "cekDuplikasi", lambda db, nama, exclude_id=None: False)
    monkeypatch.setattr(
        kategori_module.KategoriProduk,
        "simpanPerubahan",
        lambda db, kategori_id, nama_baru: calls.__setitem__("update", calls["update"] + 1),
    )

    service = kategori_module.KategoriService()

    assert service.updateKategori(1, "Atasan Update") is True
    assert calls["update"] == 1


def test_hapus_kategori_ditolak_jika_masih_punya_produk(monkeypatch):
    monkeypatch.setattr(kategori_module, "get_db", lambda: object())
    monkeypatch.setattr(kategori_module.KategoriProduk, "hasProduk", lambda db, kategori_id: True)

    service = kategori_module.KategoriService()

    assert service.hapusKategori(1) is False
