from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Header
from jose import jwt
import hashlib
import os
from sqlalchemy.orm import Session
from app.db import SessionLocal , User

# ---------------- CONFIG ----------------
SECRET_KEY = f"{os.getenv('SECRET_KEY')}"  # change to a secure random key
ALGORITHM = "HS256"
TOKEN_EXP_MIN = 60  # token expires in 60 minutes

# ---------------- PASSWORD HASHING ----------------
def get_password_hash(password: str) -> str:
    """Hash a password using PBKDF2-SHA256"""
    salt = os.urandom(32)  # 32 bytes = 256 bits
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # Store salt and hash together, separated by $
    return salt.hex() + '$' + pwdhash.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        salt_hex, hash_hex = hashed_password.split('$')
        salt = bytes.fromhex(salt_hex)
        stored_hash = bytes.fromhex(hash_hex)
        pwdhash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return pwdhash == stored_hash
    except (ValueError, AttributeError):
        return False

# ---------------- JWT ----------------
def create_access_token(data: dict) -> str:
    """
    data: {"sub": username, "role": role}
    """
    payload = data.copy()
    payload.update({"exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXP_MIN)})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ---------------- USER AUTH ----------------
def authenticate_user(db: Session, username: str, password: str):
    """
    Return User object if credentials are correct, else None
    """
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def get_current_user(authorization: str = Header(...)) -> User:
    """
    FastAPI dependency to get user info from Bearer token
    Returns: User object from database
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    
    # Get user from database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    finally:
        db.close()

# ---------------- RBAC ----------------
def require_roles(*roles):
    """
    FastAPI dependency generator to enforce role-based access
    Usage:
        user = Depends(require_roles("employee", "c_level"))
    """
    def checker(user=Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Access forbidden for your role")
        return user
    return checker
