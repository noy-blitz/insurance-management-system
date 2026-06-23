from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.policy import PolicyStatus, PolicyType


class PolicyCreate(BaseModel):
    policy_type: PolicyType
    premium_amount: Decimal = Field(gt=0)
    coverage_amount: Decimal = Field(gt=0)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_date_range(self) -> "PolicyCreate":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class PolicyUpdate(BaseModel):
    premium_amount: Decimal | None = Field(default=None, gt=0)
    coverage_amount: Decimal | None = Field(default=None, gt=0)
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> "PolicyUpdate":
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class PolicyCancel(BaseModel):
    reason: str | None = Field(default=None, max_length=255)


class PolicyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_number: str
    customer_id: int
    policy_type: PolicyType
    status: PolicyStatus
    premium_amount: Decimal
    coverage_amount: Decimal
    start_date: date
    end_date: date
    cancelled_at: datetime | None
    cancellation_reason: str | None
    created_at: datetime
    updated_at: datetime
