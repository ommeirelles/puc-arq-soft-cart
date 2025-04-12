from models.base import Base
from models.cart import CartModel
from models.cart_products import CartProductModel
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()

def bind_engine(engine):
    Base.metadata.bind = engine
    Session.configure(bind=engine)