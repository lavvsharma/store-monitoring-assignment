"""
Author: Lav Sharma
Created on: 28th Oct 2023
"""

from contextlib import contextmanager

from store_monitoring_das.database.Connection import SessionLocal


@contextmanager
def get_db():
    session = SessionLocal()
    try:
        # ========================================================================
        # Create database session
        # ========================================================================
        yield session
    finally:
        session.close()
