import jwt
from os import environ
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from werkzeug.security import check_password_hash
from models import UserModel, Session

class AuthService:
    __ttl = int(environ.get("TOKEN_TTL_SECONDS", "3600"))
    __secret = environ.get("SECRET", "MY_SECRET_KEY")

    def login(self, email: str, password: str) -> str:
        """
            Validates the user credentials against the database and
            returns a signed JWT session token valid for the
            configured TTL
        """
        with Session() as session:
            user = session.execute(
                select(UserModel).where(UserModel.email == email)
            ).scalar_one_or_none()

        if (user == None or not check_password_hash(user.password_hash, password)):
            raise Exception("Invalid email or password")

        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "iat": now,
            "exp": now + timedelta(seconds=self.__ttl),
        }

        return jwt.encode(payload, self.__secret, algorithm="HS256")

    def validateToken(self, token: str) -> int | None:
        """
            Validates the JWT signature and expiration, returning the
            id of the user the token belongs to
        """
        try:
            payload = jwt.decode(token, self.__secret, algorithms=["HS256"])
        except jwt.PyJWTError:
            return None

        return int(payload.get("sub"))
