from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:
    def get(self, db: Session, customer_id: int) -> Customer | None:
        return db.get(Customer, customer_id)

    def get_by_email(self, db: Session, email: str) -> Customer | None:
        stmt = select(Customer).where(Customer.email == email)
        return db.execute(stmt).scalar_one_or_none()

    def list(self, db: Session, skip: int = 0, limit: int = 100) -> list[Customer]:
        stmt = select(Customer).order_by(Customer.id).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def create(self, db: Session, customer: Customer) -> Customer:
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    def update(self, db: Session, customer: Customer) -> Customer:
        db.commit()
        db.refresh(customer)
        return customer
