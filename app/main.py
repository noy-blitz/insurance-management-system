from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers import customers, policies
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(customers.router)
app.include_router(policies.router)


@app.exception_handler(NotFoundError)
def handle_not_found(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
def handle_conflict(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(BusinessRuleError)
def handle_business_rule(request: Request, exc: BusinessRuleError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/health")
def health_check():
    return {"status": "ok"}
