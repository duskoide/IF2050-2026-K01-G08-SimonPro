"""Controller untuk UC05 input produksi harian."""

from __future__ import annotations


class ProduksiController:
    def __init__(self, produksi_service, auth_service=None, viewer=None):
        self.produksi_service = produksi_service
        self.auth_service = auth_service
        self.viewer = viewer

    def set_viewer(self, viewer) -> None:
        self.viewer = viewer

    def _is_admin(self) -> tuple[bool, str]:
        session = getattr(self.auth_service, "current_session", None)
        if session is None or not getattr(session, "is_active", False):
            return False, "User belum login"
        if session.get_user_role() != "admin":
            return False, "Owner tidak memiliki akses input produksi harian"
        return True, ""

    def request_input_produksi(self) -> None:
        allowed, pesan = self._is_admin()
        if not allowed:
            self.viewer.tampilkan_error(pesan)
            return

        try:
            produk = self.produksi_service.get_produk_aktif()
            tipe_defect = self.produksi_service.get_tipe_defect()
        except Exception as exc:
            self.viewer.tampilkan_error(f"Gagal memuat data form: {exc}")
            return

        if not produk:
            self.viewer.tampilkan_error("Belum ada produk aktif")
            return

        self.viewer.tampilkan_form_input(produk, tipe_defect)

    def submit_input_produksi(
        self,
        tanggal,
        produk_id,
        jumlah_aktual,
        penanggung_jawab,
        kendala_produksi,
        detail_defect,
    ) -> None:
        allowed, pesan = self._is_admin()
        if not allowed:
            self.viewer.tampilkan_error(pesan)
            return

        success, message, _produksi_id = self.produksi_service.inputProduksiHarian(
            tanggal=tanggal,
            produk_id=produk_id,
            jumlah_aktual=jumlah_aktual,
            penanggung_jawab=penanggung_jawab,
            kendala_produksi=kendala_produksi,
            detail_defect=detail_defect,
        )

        if success:
            self.viewer.tampilkan_sukses(message)
            self.viewer.reset_form()
        else:
            self.viewer.tampilkan_error(message)

