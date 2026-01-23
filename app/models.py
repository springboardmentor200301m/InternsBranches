from pydantic import BaseModel
from typing import Optional

# --- AUTH MODELS ---

class Token(BaseModel):
    """
    Defines the shape of the JWT token response.
    Returns: access_token (str) and token_type (str).
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Defines what is inside the decoded token.
    We only store the username here.
    """
    username: Optional[str] = None

class UserLogin(BaseModel):
    """
    Defines what the Frontend sends to log in.
    """
    username: str
    password: str

# --- CHAT MODELS ---

class ChatRequest(BaseModel):
    """
    Defines the question sent by the user.
    """
    question: str

class ChatResponse(BaseModel):
    """
    Defines the answer returned by the bot.
    Includes the AI answer and the source document used.
    """
    answer: str
    source: str