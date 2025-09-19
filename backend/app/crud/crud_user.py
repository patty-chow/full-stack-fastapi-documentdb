from app.crud.base import CRUDBase
from app.schemas.user import User, UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    pass


crud_user = CRUDUser(User, "users")