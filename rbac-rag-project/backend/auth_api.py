from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.database import get_user
from backend.jwt_utils import create_access_token, verify_password

app = FastAPI(title="RBAC Authentication API")

# -------------------------
# Request Model
# -------------------------
class LoginRequest(BaseModel):
    username: str
    password: str

# -------------------------
# Login API
# -------------------------
@app.post("/login")
def login(data: LoginRequest):
    user = get_user(data.username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({
        "sub": user["username"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
