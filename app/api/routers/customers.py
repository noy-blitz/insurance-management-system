from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.schemas.policy import PolicyCreate, PolicyRead
from app.services import customer_service, policy_service

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    return customer_service.create_customer(db, data)


@router.get("", response_model=list[CustomerRead])
def list_customers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return customer_service.list_customers(db, skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return customer_service.get_customer(db, customer_id)


@router.patch("/{customer_id}", response_model=CustomerRead)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    return customer_service.update_customer(db, customer_id, data)


@router.post("/{customer_id}/policies", response_model=PolicyRead, status_code=201)
def issue_policy(customer_id: int, data: PolicyCreate, db: Session = Depends(get_db)):
    return policy_service.issue_policy(db, customer_id, data)


@router.get("/{customer_id}/policies", response_model=list[PolicyRead])
def get_customer_policies(
    customer_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return policy_service.list_policies_for_customer(db, customer_id, skip=skip, limit=limit)
