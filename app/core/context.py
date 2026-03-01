"""Shared application context — holds the singleton Database instance."""
from typing import Optional

_db = None


def set_db(db) -> None:
    global _db
    _db = db


def get_db():
    return _db
