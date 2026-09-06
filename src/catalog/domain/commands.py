from decimal import Decimal

from pydantic import BaseModel, Field


class CreateProduct(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    price: Decimal = Field(ge=0)
