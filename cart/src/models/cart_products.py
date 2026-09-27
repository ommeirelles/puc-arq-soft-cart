from models.base import Base
from sqlalchemy import String, ForeignKey, UniqueConstraint, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

class CartProductModel(Base):
    __tablename__ = 'carts_products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cart_guid: Mapped[int] = mapped_column(Integer, ForeignKey("carts.guid"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
