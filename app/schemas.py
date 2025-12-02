# app/schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional,List


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchHit(BaseModel):
    id: str
    text: str
    score: float
    department: str
    source_file: str


class SearchResponse(BaseModel):
    hits: list[SearchHit]

class UserOut(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)

class Source(BaseModel):
    id: str
    department: str
    source_file: str
    score: float
    snippet: str


class RagRequest(BaseModel):
    query: str = Field(..., min_length=3)
    top_k: int = 4


class RagResponse(BaseModel):
    answer: str
    sources: List[Source]