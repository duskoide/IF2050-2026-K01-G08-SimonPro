"""Database connection module for SiMonPro.

Provides a singleton Database class that wraps psycopg2 connections
and supports both local Docker Compose and CI environment variables.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


def _get_env_var(key: str, default: str) -> str:
    """Helper to read env vars with a fallback default."""
    return os.environ.get(key, default)


# ---------------------------------------------------------------------------
# Default credentials (Docker Compose local dev)
# ---------------------------------------------------------------------------
DEFAULT_DB_CONFIG = {
    "host": _get_env_var("DB_HOST", "localhost"),
    "user": _get_env_var("DB_USER", "postgres"),
    "password": _get_env_var("DB_PASSWORD", "secret"),
    "dbname": _get_env_var("DB_NAME", "simonpro"),
    "port": int(_get_env_var("DB_PORT", "5432")),
}


class Database:
    """Lightweight wrapper around a psycopg2 connection.

    Implemented as a singleton so repeated calls to ``get_db()`` return the
    same instance (and therefore the same underlying connection) within a
    single process.
    """

    _instance: Database | None = None

    def __new__(cls, *, force_new: bool = False, **kwargs: Any) -> Database:
        if cls._instance is None or force_new:
            instance = super().__new__(cls)
            instance._connection = None
            instance._config = {**DEFAULT_DB_CONFIG, **kwargs}
            instance._in_context = False
            cls._instance = instance
        return cls._instance

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------
    def connect(self) -> None:
        """Open the underlying psycopg2 connection."""
        if self._connection is not None:
            return

        try:
            self._connection = psycopg2.connect(
                **self._config,
                cursor_factory=RealDictCursor,
            )
            self._in_context = False
            logger.info("Database connection established.")
        except psycopg2.Error as exc:
            logger.error("Failed to connect to database: %s", exc)
            raise

    def close(self) -> None:
        """Close the underlying connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed.")

    @property
    def connection(self):
        """Lazy-connect and return the raw psycopg2 connection."""
        if self._connection is None or self._connection.closed:
            self.connect()
        return self._connection

    # ------------------------------------------------------------------
    # Convenience API
    # ------------------------------------------------------------------
    def execute_query(
        self,
        sql: str,
        params: tuple | list | dict | None = None,
    ) -> list[dict[str, Any]]:
        """Run a SELECT-style query and return a list of dict rows."""
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()  # type: ignore[return-value]

    def execute_update(
        self,
        sql: str,
        params: tuple | list | dict | None = None,
    ) -> int:
        """Run an INSERT/UPDATE/DELETE and return the number of rows affected."""
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            if not self._in_context:
                self.connection.commit()
            return cursor.rowcount

    def execute_many(
        self,
        sql: str,
        params_list: list[tuple],
    ) -> int:
        """Run ``executemany`` and return total rows affected."""
        with self.connection.cursor() as cursor:
            cursor.executemany(sql, params_list)
            if not self._in_context:
                self.connection.commit()
            return cursor.rowcount

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------
    def __enter__(self) -> Database:
        self.connect()
        self._in_context = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._in_context = False
        if exc_type is not None:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.close()


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def get_db(**kwargs: Any) -> Database:
    """Return the singleton ``Database`` instance (creating if needed)."""
    return Database(**kwargs)


def test_connection(**kwargs: Any) -> bool:
    """Quick connectivity check. Returns ``True`` if the DB is reachable."""
    db = get_db(force_new=True, **kwargs)
    try:
        db.connect()
        with db.connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except psycopg2.Error as exc:
        logger.warning("Connection test failed: %s", exc)
        return False
    finally:
        db.close()
        Database._instance = None