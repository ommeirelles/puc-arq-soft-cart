import requests
from os import environ
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3 import Tag
from schemas import *
from pydantic import BaseModel, Field
from services import ProductService, CartService
from uuid import uuid4

# Tag for OpenAPI documentation
product_tag = Tag(name="Product", description="Product management endpoints")

# Blueprint for product routes
product_blueprint = APIBlueprint('Product', __name__, url_prefix='/product')

class AddProductCartPath(BaseModel):
    """
        Defines the path for adding a product to the cart
    """
    product_id: int

class AddProductCartQuery(BaseModel):
    """
        Defines the query for adding a product to the cart
    """
    cart_guid: str = Field()
    quantity: int = Field(gt=0)

@product_blueprint.post("/<int:product_id>", summary="Add a product to the cart by ID", tags=[product_tag], responses={200: ProductCartData, 400: ErrorSchema})
def addProductToCart(path: AddProductCartPath, query: AddProductCartQuery):
    """
        Add a product by it's ID to the cart
    """
    if (query.cart_guid == 0 or query.cart_guid == None or query.quantity <= 0):
        return {"message": "Cart ID is required"}, 400
    try:
        product = ProductService().getProduct(path.product_id)
        cart = CartService().getCart(query.cart_guid)
        products = CartService().addProductToCart(product.id, cart, query.quantity)
        
        return ProductCartData(data=[ProductCartEntry(product_id=prod.id, cart_guid=query.cart_guid, deleted=False, id=prod.id) for prod in products]).model_dump(), 200
    except Exception as e:
        return {"message": f"Error retrieving product: {str(e)}"}, 404
    


class RemoveFromCartPath(BaseModel):
    """
        Defines the path for removing a product from the cart
    """
    row_id: int = Field(..., description="The row ID of the product to remove from the cart")

class RemoveFromCartQuery(BaseModel):
    """
        Defines the query for removing a product from the cart
    """
    cart_guid: str = Field(..., description="The cart GUID of the product to remove from the cart")
    

@product_blueprint.delete("/<int:row_id>", summary="Removes a product insertion from the cart ", tags=[product_tag], responses={200: SuccessSchema, 400: ErrorSchema})
def removeFromCart(path: RemoveFromCartPath, query: RemoveFromCartQuery):
    """
        Removes a product insertion from the cart
    """
    service = CartService()
    cart = service.getCart(query.cart_guid)
    if (cart == None):
        return {"message": "Cart not found"}, 400

    if (service.cartContains(path.row_id, cart)):
        service.removeFromCart(path.row_id, cart)
        return {"message": "Product removed from cart"}, 200
    else:
        return {"message": "Product not found in cart"}, 400

