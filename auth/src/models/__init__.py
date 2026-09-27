from models.base import Base
from models.token import TokenModel
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()

def bind_engine(engine):
    Base.metadata.bind = engine
    Session.configure(bind=engine)
