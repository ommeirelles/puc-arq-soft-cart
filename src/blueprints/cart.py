import requests
from os import environ
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3 import Tag
from schemas import *
from pydantic import BaseModel, Field
from services import ProductService, CartService
from uuid import uuid4
from models import CartModel

# Tag for OpenAPI documentation
cart_tag = Tag(name="Cart", description="Cart management endpoints")

# Blueprint for product routes
cart_blueprint = APIBlueprint('Cart', __name__, url_prefix='/cart')

@cart_blueprint.get("", summary="Creates a new cart", tags=[cart_tag], responses={200: Cart, 400: ErrorSchema})
def new_cart():
    """
        Creates a new cart
    """
    cart = CartService().saveNewCart()
    return Cart(id=cart.id, guid=cart.guid, deleted=cart.deleted).model_dump(), 200


class CartPath(BaseModel):
    guid: str = Field(..., description="Cart GUID")

@cart_blueprint.get("/summary", summary="Gets cart summary", tags=[cart_tag], responses={200: CartSummary, 400: ErrorSchema})
def summary(query: CartPath):
    """
        Summary of the cart
    """
    cartService = CartService()
    cart = cartService.getCart(query.guid)
    if (cart.deleted == True):
        return ErrorSchema(message="Cart not found").model_dump(), 400

    prodService = ProductService()
    items = cartService.getCartSummary(cart)
    summary = CartSummary(id=cart.id, guid=cart.guid, total=0, items=[])
    for item in list(items):
        product = prodService.getProduct(item.product_id)
        summary.total += product.price
        summary.items.append(ProductCartEntry(product_id=product.id, id=item.id, cart_guid=cart.guid, deleted=item.deleted))

    return summary.model_dump(), 200
