import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: str = Field(max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    national_id: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.match(value):
            raise ValueError("invalid email format")
        return value.lower()


class CustomerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=255)


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    phone: str | None
    national_id: str | None
    address: str | None
    created_at: datetime
    updated_at: datetime
