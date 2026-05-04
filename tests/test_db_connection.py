"""Tests for the database connection module.

These are integration tests — they require a running PostgreSQL server.
For CI the workflow spins up a Postgres service automatically.
For local dev, run ``docker compose up -d`` first.
"""

import sys
from pathlib import Path

# Allow imports from project root when running this file directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from src.database.db_connection import get_db, test_connection


class TestDatabaseConnection:
    """Integration tests that assume PostgreSQL is reachable."""

    def test_connection_success(self):
        """TC-DB-01: Should return True when database is reachable."""
        assert test_connection() is True

    def test_execute_query_users(self):
        """TC-DB-02: Should be able to query the users table."""
        db = get_db()
        result = db.execute_query("SELECT * FROM users LIMIT 1")
        assert isinstance(result, list)

    def test_execute_query_tipe_defect(self):
        """TC-DB-03: Should fetch the 3 pre-seeded defect types."""
        db = get_db()
        result = db.execute_query("SELECT * FROM tipe_defect")
        assert len(result) == 3
        names = {row["nama_defect"] for row in result}
        assert names == {
            "Kecacatan Fisik",
            "Kesalahan Proses",
            "Kerusakan Material",
        }

    def test_execute_update_and_rollback(self):
        """TC-DB-04: Should insert a row and then delete it cleanly."""
        db = get_db()

        # Insert a test user
        rows = db.execute_update(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            ("testuser", "hashed_pw", "admin"),
        )
        assert rows == 1

        # Verify it exists
        select = db.execute_query(
            "SELECT * FROM users WHERE username = %s", ("testuser",)
        )
        assert len(select) == 1
        assert select[0]["username"] == "testuser"

        # Clean up
        deleted = db.execute_update(
            "DELETE FROM users WHERE username = %s", ("testuser",)
        )
        assert deleted == 1

        # Verify gone
        select_after = db.execute_query(
            "SELECT * FROM users WHERE username = %s", ("testuser",)
        )
        assert len(select_after) == 0

    def test_context_manager_commit(self):
        """TC-DB-05: Context manager should commit on success."""
        db = get_db()
        with db:
            db.execute_update(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                ("ctx_user", "pw", "owner"),
            )

        # Verify persisted
        result = db.execute_query("SELECT * FROM users WHERE username = %s", ("ctx_user",))
        assert len(result) == 1

        # Cleanup
        db.execute_update("DELETE FROM users WHERE username = %s", ("ctx_user",))

    def test_context_manager_rollback(self):
        """TC-DB-06: Context manager should rollback on exception."""
        db = get_db()
        # Clean up any leftover from previous failed runs
        db.execute_update("DELETE FROM users WHERE username = %s", ("rollback_user",))

        try:
            with db:
                db.execute_update(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    ("rollback_user", "pw", "admin"),
                )
                raise RuntimeError("Force rollback")
        except RuntimeError:
            pass

        # Verify NOT persisted
        result = db.execute_query("SELECT * FROM users WHERE username = %s", ("rollback_user",))
        assert len(result) == 0

    def test_singleton_behavior(self):
        """TC-DB-07: Multiple get_db() calls should return same instance."""
        db1 = get_db()
        db2 = get_db()
        assert db1 is db2

    def test_force_new_instance(self):
        """TC-DB-08: force_new=True should create a fresh instance."""
        db1 = get_db()
        db2 = get_db(force_new=True)
        # force_new creates a new instance; old reference (db1) stays valid but is not the singleton
        assert db1 is not db2
        assert db2._connection is None or db2._connection.closed
