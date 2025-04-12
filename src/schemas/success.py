from pydantic import BaseModel


class SuccessSchema(BaseModel):
    """ Defines how an success message will be represented
    """
    message: str