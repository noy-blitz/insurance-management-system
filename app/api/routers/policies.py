from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.policy import PolicyStatus, PolicyType
from app.schemas.policy import PolicyCancel, PolicyRead, PolicyUpdate
from app.services import policy_service

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("", response_model=list[PolicyRead])
def list_policies(
    customer_id: int | None = None,
    policy_type: PolicyType | None = None,
    status: PolicyStatus | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return policy_service.list_policies(
        db, customer_id=customer_id, policy_type=policy_type, status=status, skip=skip, limit=limit
    )


@router.get("/{policy_id}", response_model=PolicyRead)
def get_policy(policy_id: int, db: Session = Depends(get_db)):
    return policy_service.get_policy(db, policy_id)


@router.patch("/{policy_id}", response_model=PolicyRead)
def update_policy(policy_id: int, data: PolicyUpdate, db: Session = Depends(get_db)):
    return policy_service.update_policy(db, policy_id, data)


@router.post("/{policy_id}/cancel", response_model=PolicyRead)
def cancel_policy(policy_id: int, data: PolicyCancel | None = None, db: Session = Depends(get_db)):
    return policy_service.cancel_policy(db, policy_id, data or PolicyCancel())
