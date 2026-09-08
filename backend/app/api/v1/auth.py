from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication & Personas"])

class LoginRequest(BaseModel):
    email: str
    password: str

class SwitchPersonaRequest(BaseModel):
    user_id: int

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    division: Optional[str] = None
    title: Optional[str] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """Returns all pre-seeded persona users for easy persona switching."""
    return db.query(User).all()

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/switch-persona", response_model=TokenResponse)
def switch_persona(req: SwitchPersonaRequest, db: Session = Depends(get_db)):
    """Fast-switch active persona during interactive judge presentations."""
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }
