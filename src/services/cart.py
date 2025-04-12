from sqlalchemy import select, delete
from models import CartProductModel, CartModel, Session

class CartService:
    __instance = None

    def __init__(self):
        if (CartService.__instance != None):
            self = CartService.__instance
        else:
            CartService.__instance = self

    def addProductToCart(self, product_id: int, cart: CartModel, quantity: int):
        with Session() as session:
            for i in range(quantity):
                cart_product = CartProductModel()
                cart_product.cart_guid = cart.guid
                cart_product.product_id = product_id
                cart_product.deleted = False

                session.add(cart_product)
                session.commit()

    def getCartSummary(self, cart: CartModel) -> list[CartProductModel]:
        return Session().execute(
            select(CartProductModel).where(
                CartProductModel.cart_guid == cart.guid and 
                CartProductModel.deleted == False
            )
        ).scalars()
    
    def getCart(self, guid: str) -> CartModel | None:
        return Session().execute(
            select(CartModel).where(
                CartModel.guid == guid
            )
        ).scalar_one_or_none()

    def saveNewCart(self) -> CartModel:
        with Session() as session:
            cart = CartModel()
            session.add(cart)
            session.commit()
            session.refresh(cart)
            
            return cart
        
    def removeFromCart(self, row_id: int, cart: CartModel):
        with Session() as session:
            session.execute(
                delete(CartProductModel).where(
                    CartProductModel.id == row_id and 
                    CartProductModel.cart_guid == cart.guid
                )
            )

    def cartContains(self, row_id: int, cart: CartModel) -> bool:
        with Session() as session:
            return session.execute(
                select(CartProductModel).where(
                    CartProductModel.id == row_id and 
                    CartProductModel.cart_guid == cart.guid
                )
            ).scalar_one_or_none() != None