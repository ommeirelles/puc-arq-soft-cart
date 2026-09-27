from sqlalchemy import select
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
        with Session() as session:
            return session.execute(
                select(CartProductModel).where(CartProductModel.cart_guid == cart.guid, CartProductModel.deleted == False)
            ).scalars().all()

    def getCart(self, guid: str) -> CartModel | None:
        with Session() as session:
            return session.execute(
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

    def closeCart(self, guid: str) -> CartModel | None:
        """
            Marks a cart as deleted, making it stale and unusable.
            Returns None when the cart does not exist
        """
        with Session() as session:
            cart = session.execute(
                select(CartModel).where(CartModel.guid == guid)
            ).scalar_one_or_none()

            if (cart == None):
                return None

            cart.deleted = True
            session.commit()
            session.refresh(cart)

            return cart
        
    def removeProductFromCart(self, product_id: int, cart: CartModel, quantity: int | None = None) -> int:
        """
            Marks units of a product as deleted in the cart, removing all
            units when the quantity is not informed. Returns how many
            units were removed
        """
        with Session() as session:
            rows = session.execute(
                select(CartProductModel).where(
                    CartProductModel.product_id == product_id,
                    CartProductModel.cart_guid == cart.guid,
                    CartProductModel.deleted == False
                ).order_by(CartProductModel.id)
            ).scalars().all()

            to_remove = rows if quantity == None else rows[:quantity]
            for row in to_remove:
                row.deleted = True
            session.commit()

            return len(to_remove)

    def cartContainsProduct(self, product_id: int, cart: CartModel) -> bool:
        with Session() as session:
            return session.execute(
                select(CartProductModel).where(
                    CartProductModel.product_id == product_id,
                    CartProductModel.cart_guid == cart.guid,
                    CartProductModel.deleted == False
                )
            ).scalars().first() != None