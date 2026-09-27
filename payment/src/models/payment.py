from models.base import Base
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
import uuid

class PaymentModel(Base):
    """
        A payment attempt for a cart. Following common payment security
        rules, sensitive card data is never persisted: the full card
        number, the expiry date and the security code are only used
        during the request and are never written to the database — only
        the card brand and the last 4 digits are stored
    """
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guid: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        default=lambda: str(uuid.uuid4())
    )
    cart_guid: Mapped[str] = mapped_column(String(36), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    card_brand: Mapped[str] = mapped_column(String(20), nullable=False)
    card_last4: Mapped[str] = mapped_column(String(4), nullable=False)
    cep: Mapped[str] = mapped_column(String(9), nullable=False)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    number: Mapped[str] = mapped_column(String(20), nullable=False)
    neighborhood: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
