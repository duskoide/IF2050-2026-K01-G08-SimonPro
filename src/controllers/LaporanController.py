from __future__ import annotations

from datetime import date
from typing import Any

from src.services.LaporanService import LaporanService


class LaporanController:
    def __init__(self, laporan_service: LaporanService = None):
        self.laporan_service = laporan_service or LaporanService()


    def generate_laporan(
        self,
        tanggal_awal: date,
        tanggal_akhir: date,
        dicetak_oleh: str = "Sistem",
        output_dir: str = None,
    ) -> dict[str, Any]:

        validation_error = self._validate_tanggal(tanggal_awal, tanggal_akhir)
        if validation_error:
            return validation_error

        return self.laporan_service.generate_laporan(
            tanggal_awal=tanggal_awal,
            tanggal_akhir=tanggal_akhir,
            dicetak_oleh=dicetak_oleh,
            output_dir=output_dir,
        )

    def get_html_preview(
        self,
        tanggal_awal: date,
        tanggal_akhir: date,
        dicetak_oleh: str = "Sistem",
    ) -> dict[str, Any]:
        
        validation_error = self._validate_tanggal(tanggal_awal, tanggal_akhir)
        if validation_error:
            # Remap key "filepath" → "html" agar konsisten dengan return type ini
            return {
                "success": False,
                "html": None,
                "message": validation_error["message"],
            }

        html = self.laporan_service.get_html_preview(
            tanggal_awal=tanggal_awal,
            tanggal_akhir=tanggal_akhir,
            dicetak_oleh=dicetak_oleh,
        )
        if html is None:
            return {
                "success": False,
                "html": None,
                "message": "Tidak ada data yang bisa dilaporkan!",
            }

        return {
            "success": True,
            "html": html,
            "message": "OK",
        }

    @staticmethod
    def _validate_tanggal(
        tanggal_awal: date | None,
        tanggal_akhir: date | None,
    ) -> dict[str, Any] | None:
        
        if tanggal_awal is None or tanggal_akhir is None:
            return {
                "success": False,
                "filepath": None,
                "message": "Tanggal mulai dan tanggal akhir harus diisi.",
                "data": None,
            }
        if tanggal_awal > tanggal_akhir:
            return {
                "success": False,
                "filepath": None,
                "message": "Tanggal mulai tidak boleh lebih dari tanggal akhir.",
                "data": None,
            }
        return None