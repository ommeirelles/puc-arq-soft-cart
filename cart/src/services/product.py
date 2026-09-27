import requests
from os import environ
from schemas import Product

cache: dict[int, Product] = {}

class ProductService:
    __api = environ.get("PRODUCT_API_URL")

    def getProduct(self, product_id: int) -> Product:
        if (cache.get(product_id) == None):
            cache[product_id] = Product(**requests.get(f"{self.__api}products/{product_id}").json())

        return cache[product_id]
