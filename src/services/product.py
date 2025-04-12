import requests
from os import environ
from schemas import Product

class ProductService:
    __api = environ.get("PRODUCT_API_URL")
    __instance = None
    __cache: dict[int, Product] = {}

    def __init__(self):
        if (ProductService.__instance != None):
            self = ProductService.__instance
        else:
            ProductService.__instance = self

    def getProduct(self, product_id: int) -> Product:
        print(f"{self.__api}products/{product_id}")
        if (self.__cache.get(product_id) == None):
            self.__cache[product_id] = Product(**requests.get(f"{self.__api}products/{product_id}").json())

        return self.__cache[product_id]
