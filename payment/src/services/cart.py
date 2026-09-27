import requests
from os import environ
from pydantic import BaseModel, Field

class CartSummaryEntry(BaseModel):
    """
        Entry of the cart summary returned by the cart service
    """
    product_id: int
    quantity: int

class CartSummary(BaseModel):
    """
        Cart summary returned by the cart service
    """
    id: int
    guid: str
    total: float
    items: list[CartSummaryEntry]

class CartService:
    __api = environ.get("CART_API_URL")

    def getCartSummary(self, cart_guid: str, token: str) -> CartSummary | None:
        """
            Fetches the cart summary from the cart service, returning
            None when the cart does not exist
        """
        response = requests.get(
            f"{self.__api}cart/summary",
            params={"guid": cart_guid},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if (response.status_code != 200):
            return None

        return CartSummary(**response.json())

    def closeCart(self, cart_guid: str, token: str) -> bool:
        """
            Closes the cart in the cart service, marking it as stale and
            unusable. The close route is internal to the docker network
        """
        response = requests.post(
            f"{self.__api}internal/cart/{cart_guid}/close",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        return response.status_code == 200
