from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.case import AuditEvent

router = APIRouter(prefix="/audit", tags=["Immutable Audit Trail"])

@router.get("/")
def list_audit_events(case_id: Optional[int] = None, limit: int = 100, db: Session = Depends(get_db)):
    """
    DETERMINISTIC: Retrieves immutable audit logs written via ACID transactions.
    """
    query = db.query(AuditEvent)
    if case_id:
        query = query.filter(AuditEvent.case_id == case_id)
    
    events = query.order_by(AuditEvent.created_at.desc()).limit(limit).all()
    return events
