import pytest
import sqlite3
from src.run_management import initialize_db

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Initialize the database before running any tests."""
    initialize_db()
