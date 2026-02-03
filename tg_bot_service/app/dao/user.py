from app.models.user import UserModel
from app.schemas.user import UserCreateDB, UserUpdateDB
from app.core.dao import BaseDAO

class UserDAO(BaseDAO[UserModel, UserCreateDB, UserUpdateDB]):
    model = UserModel