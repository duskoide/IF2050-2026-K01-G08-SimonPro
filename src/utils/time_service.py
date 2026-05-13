from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class TimeService(QObject):
    date_changed = pyqtSignal(object)

    def __init__(
        self,
        timezone: str = "Asia/Jakarta",
        interval_ms: int = 60_000,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._timezone = ZoneInfo(timezone)
        self._current_date = self._read_today()

        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._refresh_date)
        self._timer.start()

    def _read_today(self) -> date:
        return datetime.now(self._timezone).date()

    def _refresh_date(self) -> None:
        today = self._read_today()
        if today != self._current_date:
            self._current_date = today
            self.date_changed.emit(self._current_date)

    def today(self) -> date:
        self._refresh_date()
        return self._current_date

    def now(self) -> datetime:
        return datetime.combine(self.today(), datetime.min.time(), tzinfo=self._timezone)
