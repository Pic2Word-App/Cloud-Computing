from typing import Union, Optional

from datetime import datetime
from pydantic import BaseModel

class UsersBase(BaseModel):
    user_id: int | None = None
    username: str
    email: str
    jenis_kelamin: str | None = None
    tanggal_lahir: datetime | None = None


class UserCreate(UsersBase):
    pass


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