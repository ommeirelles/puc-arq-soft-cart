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

@product_blueprint.post("/<int:product_id>", summary="Add a product to the cart by ID", tags=[product_tag], security=[{"bearerAuth": []}], responses={200: ProductCartData, 400: ErrorSchema, 404: ErrorSchema})
def addProductToCart(path: AddProductCartPath, query: AddProductCartQuery):
    """
        Add a product by it's ID to the cart
    """
    cart = CartService().getCart(query.cart_guid)
    if (cart == None or cart.deleted == True):
        return {"message": "Cart not found"}, 400

    try:
        product = ProductService().getProduct(path.product_id)
        products = CartService().addProductToCart(product.id, cart, query.quantity)

        return ProductCartData(data=[ProductCartEntry(product_id=prod.product_id, cart_guid=query.cart_guid, deleted=False, id=prod.id) for prod in products]).model_dump(), 200
    except Exception as e:
        return {"message": f"Error retrieving product: {str(e)}"}, 404
    


class RemoveFromCartPath(BaseModel):
    """
        Defines the path for removing a product from the cart
    """
    product_id: int = Field(..., description="The product ID to remove from the cart")

class RemoveFromCartQuery(BaseModel):
    """
        Defines the query for removing a product from the cart
    """
    cart_guid: str = Field(..., description="The cart GUID of the product to remove from the cart")
    quantity: int | None = Field(default=None, gt=0, description="How many units to remove; removes all units when omitted")


@product_blueprint.delete("/<int:product_id>", summary="Removes units of a product from the cart", tags=[product_tag], security=[{"bearerAuth": []}], responses={200: SuccessSchema, 400: ErrorSchema})
def removeFromCart(path: RemoveFromCartPath, query: RemoveFromCartQuery):
    """
        Removes units of a product from the cart
    """
    service = CartService()
    cart = service.getCart(query.cart_guid)
    if (cart == None or cart.deleted == True):
        return {"message": "Cart not found"}, 400

    if (service.cartContainsProduct(path.product_id, cart)):
        service.removeProductFromCart(path.product_id, cart, query.quantity)
        return {"message": "Product removed from cart"}, 200
    else:
        return {"message": "Product not found in cart"}, 400

