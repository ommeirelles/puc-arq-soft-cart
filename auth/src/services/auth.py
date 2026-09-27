import jwt
import requests
from os import environ
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update
from models import TokenModel, Session

class AuthService:
    __api = environ.get("FAKE_STORE_API_URL", "https://fakestoreapi.com/")
    __ttl = int(environ.get("TOKEN_TTL_SECONDS", "3600"))

    def login(self, username: str, password: str) -> str:
        """
            Authenticates the user on the external store API and caches
            the returned token for the configured TTL
        """
        response = requests.post(
            f"{self.__api}auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()

        token: str = response.json().get("token")
        payload = jwt.decode(token, options={"verify_signature": False})

        with Session() as session:
            entry = session.execute(
                select(TokenModel).where(TokenModel.token == token)
            ).scalar_one_or_none()

            if (entry == None):
                entry = TokenModel()
                entry.token = token
                entry.user_id = int(payload.get("sub"))
                session.add(entry)

            entry.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=self.__ttl)
            entry.revoked = False
            session.commit()

        return token

    def getValidToken(self, token: str) -> TokenModel | None:
        """
            Returns the cached token entry when it exists, was not
            revoked and did not expire
        """
        entry = Session().execute(
            select(TokenModel).where(
                TokenModel.token == token,
                TokenModel.revoked == False
            )
        ).scalar_one_or_none()

        if (entry == None or entry.expires_at < datetime.now(timezone.utc).replace(tzinfo=None)):
            return None

        return entry

    def revokeToken(self, token: str) -> bool:
        """
            Invalidates a cached token
        """
        with Session() as session:
            result = session.execute(
                update(TokenModel).where(
                    TokenModel.token == token,
                    TokenModel.revoked == False
                ).values(revoked=True)
            )
            session.commit()

            return result.rowcount > 0
