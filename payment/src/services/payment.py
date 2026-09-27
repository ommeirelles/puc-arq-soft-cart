from sqlalchemy import select
from models import PaymentModel, Session
from schemas import PaymentRequest

class PaymentService:
    def luhnCheck(self, card_number: str) -> bool:
        """
            Validates the card number with the Luhn algorithm
        """
        total = 0
        for index, digit in enumerate(reversed(card_number)):
            value = int(digit)
            if (index % 2 == 1):
                value *= 2
                if (value > 9):
                    value -= 9
            total += value
        return total % 10 == 0

    def cardBrand(self, card_number: str) -> str:
        """
            Detects the card brand from the number prefix
        """
        if (card_number.startswith("4")):
            return "visa"
        if (card_number[:2] in ("34", "37")):
            return "amex"
        if (51 <= int(card_number[:2]) <= 55 or 2221 <= int(card_number[:4]) <= 2720):
            return "mastercard"
        if (card_number[:4] == "6011" or card_number[:2] == "65"):
            return "discover"
        return "unknown"

    def getApprovedPayment(self, cart_guid: str) -> PaymentModel | None:
        with Session() as session:
            return session.execute(
                select(PaymentModel).where(
                    PaymentModel.cart_guid == cart_guid,
                    PaymentModel.status == "approved"
                )
            ).scalars().first()

    def savePayment(self, cart_guid: str, user_id: int, amount: float, status: str, payment: PaymentRequest) -> PaymentModel:
        """
            Persists the payment attempt. Following common payment
            security rules, sensitive card data is never stored: the
            full card number, the expiry date and the security code are
            discarded, keeping only the card brand and the last 4 digits
        """
        with Session() as session:
            model = PaymentModel()
            model.cart_guid = cart_guid
            model.user_id = user_id
            model.amount = amount
            model.status = status
            model.card_brand = self.cardBrand(payment.card_number)
            model.card_last4 = payment.card_number[-4:]
            model.cep = payment.address.cep
            model.street = payment.address.street
            model.number = payment.address.number
            model.neighborhood = payment.address.neighborhood
            model.city = payment.address.city
            model.state = payment.address.state

            session.add(model)
            session.commit()
            session.refresh(model)

            return model
