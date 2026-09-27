from pydantic import BaseModel, Field
from schemas import Product, ProductCartEntry

class Cart(BaseModel):
    """
    Schema de um produto
    """
    id: int = Field(gt=0)
    guid: str = Field(min_length=36, max_length=36)
    deleted: bool = Field()

class CartSummary(BaseModel):
    """
    Summary of the cart
    """
    id: int = Field(gt=0)
    guid: str = Field(min_length=36, max_length=36)
    total: float = Field()
    items: list[ProductCartEntry] = Field()