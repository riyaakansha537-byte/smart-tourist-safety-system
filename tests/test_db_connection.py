# ============================================================
# Smart Tourist Safety and Emergency Response System
# Tests: Database Connection Layer & ThreadedConnectionPool
# ============================================================

import threading
import time
from unittest.mock import MagicMock, patch
import pytest

from backend.config import Config
from backend.db.connection import (
    init_db_pool,
    get_pool,
    close_db_pool,
    get_db_connection,
    get_db_cursor,
    check_db_health,
)
from backend.db.transactions import transaction_scope

class TestConfig:
    """Validates configuration parameters."""

    def test_config_db_params(self):
        params = Config.get_db_params()
        assert "host" in params
        assert "port" in params
        assert "dbname" in params
        assert "user" in params
        assert "password" in params
        assert params["dbname"] == "tourist_safety_db"
        assert params["user"] == "tourist_admin"

class TestConnectionPoolMocked:
    """Validates ThreadedConnectionPool behavior, concurrency, and context managers."""

    @pytest.fixture(autouse=True)
    def clean_pool(self):
        """Ensures pool state is reset before and after each test."""
        close_db_pool()
        yield
        close_db_pool()

    @patch("backend.db.connection.pool.ThreadedConnectionPool")
    def test_pool_initialization(self, mock_pool_cls):
        mock_instance = MagicMock()
        mock_instance.closed = False
        mock_pool_cls.return_value = mock_instance

        p = init_db_pool(minconn=2, maxconn=5)
        assert p is mock_instance
        mock_pool_cls.assert_called_once_with(
            minconn=2,
            maxconn=5,
            **Config.get_db_params()
        )

    @patch("backend.db.connection.pool.ThreadedConnectionPool")
    def test_get_db_connection_checkout_and_return(self, mock_pool_cls):
        mock_instance = MagicMock()
        mock_instance.closed = False
        mock_conn = MagicMock()
        mock_instance.getconn.return_value = mock_conn
        mock_pool_cls.return_value = mock_instance

        # Test context manager
        with get_db_connection() as conn:
            assert conn is mock_conn
            mock_instance.getconn.assert_called_once()

        # Verify connection returned to pool
        mock_instance.putconn.assert_called_once_with(mock_conn)

    @patch("backend.db.connection.pool.ThreadedConnectionPool")
    def test_get_db_cursor_commits_on_success(self, mock_pool_cls):
        mock_instance = MagicMock()
        mock_instance.closed = False
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_instance.getconn.return_value = mock_conn
        mock_pool_cls.return_value = mock_instance

        with get_db_cursor(commit=True) as cur:
            cur.execute("SELECT 1")

        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_instance.putconn.assert_called_once_with(mock_conn)

    @patch("backend.db.connection.pool.ThreadedConnectionPool")
    def test_get_db_cursor_rolls_back_on_error(self, mock_pool_cls):
        mock_instance = MagicMock()
        mock_instance.closed = False
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_instance.getconn.return_value = mock_conn
        mock_pool_cls.return_value = mock_instance

        with pytest.raises(ValueError):
            with get_db_cursor(commit=True):
                raise ValueError("Simulated DB error")

        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_instance.putconn.assert_called_once_with(mock_conn)

    @patch("backend.db.connection.pool.ThreadedConnectionPool")
    def test_multithreaded_concurrent_connections(self, mock_pool_cls):
        """Simulates 5 worker threads acquiring and releasing connections concurrently."""
        mock_instance = MagicMock()
        mock_instance.closed = False
        mock_conn = MagicMock()
        mock_instance.getconn.return_value = mock_conn
        mock_pool_cls.return_value = mock_instance

        results = []

        def worker_task(thread_id):
            with get_db_connection() as conn:
                time.sleep(0.01)
                results.append(thread_id)

        threads = [
            threading.Thread(target=worker_task, args=(i,), name=f"Worker-{i}")
            for i in range(5)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 5
        assert mock_instance.getconn.call_count == 5
        assert mock_instance.putconn.call_count == 5

    @patch("backend.db.connection.pool.ThreadedConnectionPool")
    def test_transaction_scope_rollback(self, mock_pool_cls):
        mock_instance = MagicMock()
        mock_instance.closed = False
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_instance.getconn.return_value = mock_conn
        mock_pool_cls.return_value = mock_instance

        with pytest.raises(RuntimeError):
            with transaction_scope() as cur:
                cur.execute("INSERT INTO emergency_logs ...")
                raise RuntimeError("Failed midway through ACID transaction")

        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
