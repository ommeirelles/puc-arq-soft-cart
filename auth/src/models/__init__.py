from models.base import Base
from models.user import UserModel
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()

def bind_engine(engine):
    Base.metadata.bind = engine
    Session.configure(bind=engine)
