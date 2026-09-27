from json import dumps
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func

class Base(DeclarativeBase):
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    def to_JSON(self):
        return dumps(
            self.as_dict(),
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)