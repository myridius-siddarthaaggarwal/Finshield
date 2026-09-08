import pytest
from app.db.session import engine, Base, SessionLocal
from app.db.init_db import seed_database
from app.models.case import RiskCase

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure database schema and benchmark seed cases exist before running any tests."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        cases_count = db.query(RiskCase).count()
        if cases_count < 7:
            seed_database()
    finally:
        db.close()
    yield
