from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.policy import Policy, PolicyStatus, PolicyType


class PolicyRepository:
    def get(self, db: Session, policy_id: int) -> Policy | None:
        return db.get(Policy, policy_id)

    def get_by_policy_number(self, db: Session, policy_number: str) -> Policy | None:
        stmt = select(Policy).where(Policy.policy_number == policy_number)
        return db.execute(stmt).scalar_one_or_none()

    def list(
        self,
        db: Session,
        customer_id: int | None = None,
        policy_type: PolicyType | None = None,
        status: PolicyStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Policy]:
        stmt = select(Policy)
        if customer_id is not None:
            stmt = stmt.where(Policy.customer_id == customer_id)
        if policy_type is not None:
            stmt = stmt.where(Policy.policy_type == policy_type)
        if status is not None:
            stmt = stmt.where(Policy.status == status)
        stmt = stmt.order_by(Policy.id).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def create(self, db: Session, policy: Policy) -> Policy:
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    def update(self, db: Session, policy: Policy) -> Policy:
        db.commit()
        db.refresh(policy)
        return policy
