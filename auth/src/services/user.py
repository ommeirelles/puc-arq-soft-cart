from sqlalchemy import select
from werkzeug.security import generate_password_hash
from models import UserModel, Session
from schemas import User

class UserService:
    def createUser(self, name: str, email: str, password: str) -> User | None:
        """
            Registers a new user, storing the password as a hash.
            Returns None when the email is already registered
        """
        with Session() as session:
            existing = session.execute(
                select(UserModel).where(UserModel.email == email)
            ).scalar_one_or_none()

            if (existing != None):
                return None

            user = UserModel()
            user.name = name
            user.email = email
            user.password_hash = generate_password_hash(password)
            session.add(user)
            session.commit()
            session.refresh(user)

            return User(id=user.id, name=user.name, email=user.email)

    def getUser(self, user_id: int) -> User | None:
        """
            Returns the user info for the given id
        """
        with Session() as session:
            user = session.execute(
                select(UserModel).where(UserModel.id == user_id)
            ).scalar_one_or_none()

            if (user == None):
                return None

            return User(id=user.id, name=user.name, email=user.email)
