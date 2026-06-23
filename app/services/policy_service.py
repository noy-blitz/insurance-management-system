import uuid
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.policy import Policy, PolicyStatus, PolicyType
from app.repositories.customer_repository import CustomerRepository
from app.repositories.policy_repository import PolicyRepository
from app.schemas.policy import PolicyCancel, PolicyCreate, PolicyUpdate

customer_repository = CustomerRepository()
repository = PolicyRepository()


def _generate_policy_number() -> str:
    return f"POL-{date.today().year}-{uuid.uuid4().hex[:8].upper()}"


def issue_policy(db: Session, customer_id: int, data: PolicyCreate) -> Policy:
    if customer_repository.get(db, customer_id) is None:
        raise NotFoundError(f"Customer {customer_id} not found")

    policy = Policy(
        customer_id=customer_id,
        policy_number=_generate_policy_number(),
        status=PolicyStatus.ACTIVE,
        **data.model_dump(),
    )
    return repository.create(db, policy)


def get_policy(db: Session, policy_id: int) -> Policy:
    policy = repository.get(db, policy_id)
    if policy is None:
        raise NotFoundError(f"Policy {policy_id} not found")
    return policy


def list_policies(
    db: Session,
    customer_id: int | None = None,
    policy_type: PolicyType | None = None,
    status: PolicyStatus | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Policy]:
    return repository.list(
        db, customer_id=customer_id, policy_type=policy_type, status=status, skip=skip, limit=limit
    )


def list_policies_for_customer(
    db: Session, customer_id: int, skip: int = 0, limit: int = 100
) -> list[Policy]:
    if customer_repository.get(db, customer_id) is None:
        raise NotFoundError(f"Customer {customer_id} not found")
    return repository.list(db, customer_id=customer_id, skip=skip, limit=limit)


def update_policy(db: Session, policy_id: int, data: PolicyUpdate) -> Policy:
    policy = get_policy(db, policy_id)
    if policy.status != PolicyStatus.ACTIVE:
        raise ConflictError(f"Policy {policy_id} is {policy.status.value} and cannot be modified")

    updates = data.model_dump(exclude_unset=True)
    start_date = updates.get("start_date", policy.start_date)
    end_date = updates.get("end_date", policy.end_date)
    if end_date <= start_date:
        raise BusinessRuleError("end_date must be after start_date")

    for field, value in updates.items():
        setattr(policy, field, value)
    return repository.update(db, policy)


def cancel_policy(db: Session, policy_id: int, data: PolicyCancel) -> Policy:
    policy = get_policy(db, policy_id)
    if policy.status == PolicyStatus.CANCELLED:
        raise ConflictError(f"Policy {policy_id} is already cancelled")

    policy.status = PolicyStatus.CANCELLED
    policy.cancelled_at = datetime.now(timezone.utc)
    policy.cancellation_reason = data.reason
    return repository.update(db, policy)
