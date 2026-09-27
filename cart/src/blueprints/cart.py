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

@cart_blueprint.get("", summary="Creates a new cart", tags=[cart_tag], security=[{"bearerAuth": []}], responses={200: Cart})
def new_cart():
    """
        Creates a new cart
    """
    cart = CartService().saveNewCart()
    return Cart(id=cart.id, guid=cart.guid, deleted=cart.deleted).model_dump(), 200


class CartPath(BaseModel):
    guid: str = Field(..., description="Cart GUID")

@cart_blueprint.get("/summary", summary="Gets cart summary", tags=[cart_tag], security=[{"bearerAuth": []}], responses={200: CartSummary, 400: ErrorSchema, 502: ErrorSchema})
def summary(query: CartPath):
    """
        Summary of the cart
    """
    cartService = CartService()
    cart = cartService.getCart(query.guid)
    if (cart == None or cart.deleted == True):
        return ErrorSchema(message="Cart not found").model_dump(), 400

    prodService = ProductService()
    items = cartService.getCartSummary(cart)
    summary = CartSummary(id=cart.id, guid=cart.guid, total=0, items=[])

    quantityByProduct: dict[int, int] = {}
    for item in list(items):
        quantityByProduct[item.product_id] = quantityByProduct.get(item.product_id, 0) + 1

    try:
        for product_id, quantity in quantityByProduct.items():
            product = prodService.getProduct(product_id)
            summary.total += product.price * quantity
            summary.items.append(CartSummaryEntry(product_id=product.id, quantity=quantity))
    except Exception as e:
        return ErrorSchema(message=f"Error retrieving product: {str(e)}").model_dump(), 502

    return summary.model_dump(), 200
