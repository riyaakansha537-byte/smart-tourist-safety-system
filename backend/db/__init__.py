# ============================================================
# Smart Tourist Safety and Emergency Response System
# Database Subsystem Exports
# ============================================================

from backend.db.connection import (
    init_db_pool,
    get_pool,
    close_db_pool,
    get_db_connection,
    get_db_cursor,
    check_db_health,
)
from backend.db.transactions import transaction_scope

__all__ = [
    "init_db_pool",
    "get_pool",
    "close_db_pool",
    "get_db_connection",
    "get_db_cursor",
    "check_db_health",
    "transaction_scope",
]
