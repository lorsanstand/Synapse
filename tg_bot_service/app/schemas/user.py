from typing import Optional

from pydantic import BaseModel

class UserBase(BaseModel):
    tg_id: Optional[int]
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    group: Optional[int] = None


class UserCreateDB(UserBase):
    tg_id: int
    is_admin: Optional[bool] = False
    is_verified: Optional[bool] = False

    class Config:
        from_attributes = True


class UserUpdateDB(UserBase):
    is_admin: Optional[bool] = False
    is_verified: Optional[bool] = False

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    tg_id: int

    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    pass