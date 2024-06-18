from typing import Optional

from datetime import datetime
from pydantic import BaseModel

class UsersBase(BaseModel):
    user_id: int | None = None
    username: str | None = None
    email: str | None = None
    jenis_kelamin: str | None = None
    tanggal_lahir: datetime | None = None

class UserCreate(UsersBase):
    password: str

class UserLogin(UsersBase):
    password: str

class UserUpdate(UsersBase):
    username: Optional[str]
    jenis_kelamin: Optional[str]
    tanggal_lahir: Optional[datetime]

class Users(UsersBase):
    user_id: int
    email: str
    username: str

    class Config:
        orm_mode = True
        
class TokenBase(BaseModel):
    user_id: int | None = None
    username: str | None = None
    access_token: str | None = None
    token_type: str | None = None
    
class Token(TokenBase):
    token_id: int
    user_id: int
    access_token: str
    
    class Config:
        orm_mode = True