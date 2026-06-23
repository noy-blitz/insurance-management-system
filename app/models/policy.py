import enum
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PolicyType(str, enum.Enum):
    CAR = "CAR"
    HEALTH = "HEALTH"
    LIFE = "LIFE"
    HOME = "HOME"


class PolicyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class Policy(Base):
    __tablename__ = "policies"
    __table_args__ = (
        CheckConstraint("end_date > start_date", name="ck_policy_end_after_start"),
        CheckConstraint("premium_amount > 0", name="ck_policy_premium_positive"),
        CheckConstraint("coverage_amount > 0", name="ck_policy_coverage_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    policy_type: Mapped[PolicyType] = mapped_column(SAEnum(PolicyType), index=True, nullable=False)
    status: Mapped[PolicyStatus] = mapped_column(
        SAEnum(PolicyStatus), index=True, nullable=False, default=PolicyStatus.ACTIVE
    )
    premium_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    coverage_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )
