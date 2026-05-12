from src.services.KategoriService import KategoriService
from src.models.Session import Session


class KategoriController:
    def __init__(self, session: Session):
        self.session = session
        self.service = KategoriService()
        self.viewer = None

    def set_viewer(self, viewer):
        self.viewer = viewer

    # Req Edit Kategori
    def request_edit_kategori(self):
        # cek role (hanya admin)
        if self.session is None or not self.session.is_active:
            if self.viewer:
                self.viewer.tampilkan_error("User belum login.")
            return False

        role = self.session.get_user_role()
        if role == "owner":
            if self.viewer:
                self.viewer.tampilkan_error("Owner tidak memiliki akses.")
            return False

        # ambil data kategori
        kategori_list = self.service.getDaftarKategori()

        # ubah ke format (id, nama)
        data = [(k.kategori_id, k.nama_kategori) for k in kategori_list]

        if self.viewer:
            self.viewer.tampilkan_form_edit(data)

        return True

    # Tambah Kategori
    def submit_tambah_kategori(self, nama):
        if not self.service.tambahKategori(nama):
            if self.viewer:
                self.viewer.tampilkan_error("Gagal menambah kategori.")
            return False

        if self.viewer:
            self.viewer.tampilkan_success("Kategori berhasil ditambahkan.")
        return True

    # Update Kategori
    def submit_update_kategori(self, kategori_id, nama_baru):
        if not self.service.updateKategori(kategori_id, nama_baru):
            if self.viewer:
                self.viewer.tampilkan_error("Gagal mengubah kategori.")
            return False

        if self.viewer:
            self.viewer.tampilkan_success("Kategori berhasil diubah.")
        return True

    # Hapus Kategori
    def submit_hapus_kategori(self, kategori_id):
        if not self.service.hapusKategori(kategori_id):
            if self.viewer:
                self.viewer.tampilkan_error("Kategori tidak bisa dihapus.")
            return False

        if self.viewer:
            self.viewer.tampilkan_success("Kategori berhasil dihapus.")
        return True

    # Get List Kategori (untuk isi dropdown)
    def get_all_kategori(self):
        kategori_list = self.service.getDaftarKategori()
        return [(k.kategori_id, k.nama_kategori) for k in kategori_list]
