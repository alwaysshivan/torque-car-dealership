from decimal import Decimal
from typing import Literal
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class Login(StrictModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator('email')
    @classmethod
    def valid_email(cls, value):
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
            raise ValueError('Enter a valid email address')
        return value.lower()


class Register(Login):
    name: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=10, max_length=128)


class VehicleInput(StrictModel):
    make: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=80)
    category: Literal['SUV', 'Sedan', 'Hatchback', 'Coupe', 'Truck', 'MPV']
    price: Decimal = Field(gt=0, le=1000000000, decimal_places=2)
    quantity: int = Field(ge=0, le=100000, strict=True)
    year: int = Field(default=2026, ge=1900, le=2100, strict=True)
    fuel: Literal['Petrol', 'Diesel', 'Electric', 'Hybrid', 'CNG'] = 'Petrol'
    color: str = Field(default='Silver', min_length=1, max_length=40)


class Quantity(StrictModel):
    quantity: int = Field(default=1, gt=0, le=100000, strict=True)
