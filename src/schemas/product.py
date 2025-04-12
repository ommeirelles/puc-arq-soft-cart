from pydantic import BaseModel, Field

class Product(BaseModel):
    """
    Product schema
    """
    id: int
    title: str
    price: float
    description: str
    category: str
    image: str

class ProductCartEntry(BaseModel):
    """
    Schema of an product added to a cart
    """
    product_id: int = Field(..., description="The product ID")
    id: int = Field(..., description="The product entry ID to the cart")
    cart_guid: str = Field(..., description="The cart GUID")
    deleted: bool = Field(..., description="If the product was deleted from the cart")

class ProductCartData(BaseModel):
    data: list[ProductCartEntry]