from models.base import Base
from sqlalchemy import ForeignKey, UniqueConstraint, Integer, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
import uuid
class CartModel(Base):
    __tablename__ = 'carts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guid: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        default=lambda: str(uuid.uuid4())
    )
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

