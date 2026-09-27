from pydantic import BaseModel, Field, field_validator
from re import fullmatch
from datetime import date

class Address(BaseModel):
    """
        Delivery address with a brazilian CEP
    """
    cep: str = Field(..., description="Brazilian CEP, with or without the dash")
    street: str = Field(min_length=1)
    number: str = Field(min_length=1)
    neighborhood: str = Field(min_length=1)
    city: str = Field(min_length=1)
    state: str = Field(min_length=2, max_length=2, description="Federative unit (UF)")

    @field_validator("cep")
    @classmethod
    def cep_format(cls, value: str) -> str:
        if (fullmatch(r"\d{5}-?\d{3}", value) == None):
            raise ValueError("CEP must have 8 digits, with or without the dash")
        return value

class PaymentRequest(BaseModel):
    """
        Payment information required to pay a cart
    """
    card_number: str = Field(..., description="Card number (13 to 19 digits)")
    card_expiry: str = Field(..., description="Card expiry date (MM/YY or MM/YYYY)")
    card_cvv: str = Field(..., description="Card security code (3 or 4 digits)")
    address: Address = Field(..., description="Delivery address")

    @field_validator("card_number")
    @classmethod
    def card_number_format(cls, value: str) -> str:
        number = value.replace(" ", "")
        if (fullmatch(r"\d{13,19}", number) == None):
            raise ValueError("Card number must have 13 to 19 digits")
        return number

    @field_validator("card_expiry")
    @classmethod
    def card_expiry_valid(cls, value: str) -> str:
        match = fullmatch(r"(\d{2})/(\d{2}|\d{4})", value)
        if (match == None):
            raise ValueError("Card expiry must be in the MM/YY or MM/YYYY format")
        month, year = int(match.group(1)), int(match.group(2))
        if (month < 1 or month > 12):
            raise ValueError("Card expiry month must be between 01 and 12")
        year = year + 2000 if year < 100 else year
        today = date.today()
        if (year < today.year or (year == today.year and month < today.month)):
            raise ValueError("Card is expired")
        return value

    @field_validator("card_cvv")
    @classmethod
    def card_cvv_format(cls, value: str) -> str:
        if (fullmatch(r"\d{3,4}", value) == None):
            raise ValueError("Card security code must have 3 or 4 digits")
        return value

class Payment(BaseModel):
    """
        A registered payment attempt for a cart. Sensitive card data is
        never stored nor returned — only the card brand and the last 4
        digits of the card number
    """
    id: int = Field(gt=0)
    guid: str = Field(min_length=36, max_length=36)
    cart_guid: str = Field(min_length=36, max_length=36)
    user_id: int = Field(gt=0)
    amount: float = Field()
    status: str = Field(..., description="approved or declined")
    card_brand: str = Field()
    card_last4: str = Field(min_length=4, max_length=4)
    address: Address = Field()
