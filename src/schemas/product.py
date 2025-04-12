from pydantic import BaseModel

class Product(BaseModel):
    """
    Schema de um produto
    """
    id: int
    title: str
    price: float
    description: str
    category: str
    image: str