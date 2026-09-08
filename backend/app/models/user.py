from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from app.db.session import Base

class UserRole:
    SUBMITTER = "SUBMITTER"
    ANALYST = "ANALYST"
    COMMITTEE_MEMBER = "COMMITTEE_MEMBER"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default=UserRole.SUBMITTER, nullable=False)
    division = Column(String, nullable=True) # e.g. Consumer Banking, Payments, Commercial Banking, Wealth Management, FCRM
    title = Column(String, nullable=True)    # e.g. "Product Manager, Retail Banking", "CRO", "Senior Analyst"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
