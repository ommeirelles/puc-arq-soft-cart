from sqlalchemy import select, update
from models import CartProductModel, CartModel, Session

class CartService:
    def addProductToCart(self, product_id: int, cart: CartModel, quantity: int) -> list[CartProductModel]:
        products: list[CartProductModel] = []
        for i in range(quantity):
            with Session() as session:
                cart_product = CartProductModel()
                cart_product.cart_guid = cart.guid
                cart_product.product_id = product_id
                cart_product.deleted = False

                session.add(cart_product)
                session.commit()
                session.refresh(cart_product)
                products.append(cart_product)
        
        return products

        return products

    def getCartSummary(self, cart: CartModel) -> list[CartProductModel]:
        return Session().execute(
            select(CartProductModel).where(CartProductModel.cart_guid == cart.guid, CartProductModel.deleted == False)
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
                update(CartProductModel).where(
                    CartProductModel.id == row_id, 
                    CartProductModel.cart_guid == cart.guid
                ).values(deleted=True)
            )
            session.commit()

    def cartContains(self, row_id: int, cart: CartModel) -> bool:
        with Session() as session:
            return session.execute(
                select(CartProductModel).where(
                    CartProductModel.id == row_id, 
                    CartProductModel.cart_guid == cart.guid
                )
            ).scalar_one_or_none() != None