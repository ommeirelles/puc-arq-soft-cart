import requests
from os import environ
from schemas import User

cache: dict[int, User] = {}

class UserService:
    __api = environ.get("FAKE_STORE_API_URL", "https://fakestoreapi.com/")

    def getUser(self, user_id: int) -> User | None:
        if (cache.get(user_id) == None):
            response = requests.get(f"{self.__api}users/{user_id}")
            if (response.status_code != 200):
                return None

            cache[user_id] = User(**response.json())

        return cache[user_id]
