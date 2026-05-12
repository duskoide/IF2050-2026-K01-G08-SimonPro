"""Controller untuk UC06 insight tingkat pencapaian target."""

from __future__ import annotations


class PencapaianController:
    def __init__(self, pencapaian_service, auth_service=None, viewer=None):
        self.pencapaian_service = pencapaian_service
        self.auth_service = auth_service
        self.viewer = viewer

    def set_viewer(self, viewer) -> None:
        self.viewer = viewer

    def _is_allowed(self) -> tuple[bool, str]:
        if self.auth_service is None:
            return True, ""

        session = getattr(self.auth_service, "current_session", None)
        if session is None or not getattr(session, "is_active", False):
            return False, "User belum login"

        if session.get_user_role() not in {"admin", "owner"}:
            return False, "Role tidak memiliki akses insight pencapaian"

        return True, ""

    def request_insight_pencapaian(self, months: int = 4) -> None:
        allowed, pesan = self._is_allowed()
        if not allowed:
            self.viewer.tampilkan_error(pesan)
            return

        try:
            data = self.pencapaian_service.get_insight_pencapaian(months=months)
        except Exception as exc:
            self.viewer.tampilkan_error(f"Gagal memuat insight pencapaian: {exc}")
            return

        self.viewer.tampilkan_insight_pencapaian(data)
