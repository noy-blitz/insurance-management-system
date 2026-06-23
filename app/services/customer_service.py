from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate

repository = CustomerRepository()


def create_customer(db: Session, data: CustomerCreate) -> Customer:
    if repository.get_by_email(db, data.email) is not None:
        raise ConflictError(f"Customer with email '{data.email}' already exists")

    customer = Customer(**data.model_dump())
    return repository.create(db, customer)


def get_customer(db: Session, customer_id: int) -> Customer:
    customer = repository.get(db, customer_id)
    if customer is None:
        raise NotFoundError(f"Customer {customer_id} not found")
    return customer


def list_customers(db: Session, skip: int = 0, limit: int = 100) -> list[Customer]:
    return repository.list(db, skip=skip, limit=limit)


def update_customer(db: Session, customer_id: int, data: CustomerUpdate) -> Customer:
    customer = get_customer(db, customer_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    return repository.update(db, customer)
