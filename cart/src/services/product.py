import requests
from os import environ
from schemas import Product

cache: dict[int, Product] = {}

class ProductService:
    __api = environ.get("PRODUCT_API_URL")

    def getProduct(self, product_id: int) -> Product:
        if (cache.get(product_id) == None):
            response = requests.get(f"{self.__api}products/{product_id}", timeout=10)
            response.raise_for_status()
            cache[product_id] = Product(**response.json())

        return cache[product_id]
