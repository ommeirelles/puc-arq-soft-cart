from flask import g
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3 import Tag
from schemas import *
from pydantic import BaseModel, Field
from services import CartService, ViaCepService, PaymentService

# Tag for OpenAPI documentation
payment_tag = Tag(name="Payment", description="Payment endpoints")

# Blueprint for payment routes
payment_blueprint = APIBlueprint('Payment', __name__, url_prefix='/pay')

class PaymentPath(BaseModel):
    """
        Defines the path for paying a cart
    """
    cart_guid: str = Field(..., description="The GUID of the cart being paid")

@payment_blueprint.post("/<string:cart_guid>", summary="Pays a cart", tags=[payment_tag], security=[{"bearerAuth": []}], responses={201: Payment, 400: ErrorSchema, 402: Payment, 409: ErrorSchema, 502: ErrorSchema})
def pay(path: PaymentPath, body: PaymentRequest):
    """
        Pays a cart with the informed card and delivery address
    """
    cart = CartService().getCartSummary(path.cart_guid, g.token)
    if (cart == None):
        return ErrorSchema(message="Cart not found").model_dump(), 400
    if (len(cart.items) == 0):
        return ErrorSchema(message="Cart is empty").model_dump(), 400

    service = PaymentService()
    if (service.getApprovedPayment(path.cart_guid) != None):
        return ErrorSchema(message="Cart already paid").model_dump(), 409

    viaCep = ViaCepService()
    try:
        cepAddress = viaCep.getAddress(body.address.cep)
    except Exception as e:
        return ErrorSchema(message=f"Error validating the CEP: {str(e)}").model_dump(), 502
    if (cepAddress == None):
        return ErrorSchema(message="CEP not found").model_dump(), 400
    if (not viaCep.matches(cepAddress, body.address)):
        return ErrorSchema(message="Address city/state does not match the CEP").model_dump(), 400

    approved = service.luhnCheck(body.card_number)
    payment = service.savePayment(
        cart_guid=path.cart_guid,
        user_id=g.user["id"],
        amount=cart.total,
        status="approved" if approved else "declined",
        payment=body
    )

    if (approved):
        CartService().closeCart(path.cart_guid, g.token)

    response = Payment(
        id=payment.id,
        guid=payment.guid,
        cart_guid=payment.cart_guid,
        user_id=payment.user_id,
        amount=payment.amount,
        status=payment.status,
        card_brand=payment.card_brand,
        card_last4=payment.card_last4,
        address=body.address
    ).model_dump()
    return response, 201 if approved else 402
