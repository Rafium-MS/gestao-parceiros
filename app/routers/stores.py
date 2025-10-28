from fastapi import APIRouter
from sqlmodel import Session, select
from ..database import engine
from ..models import Store

router = APIRouter()

@router.get("/")
def list_stores():
    with Session(engine) as session:
        return session.exec(select(Store)).all()

@router.post("/", status_code=201)
def create_store(s: Store):
    with Session(engine) as session:
        session.add(s)
        session.commit()
        session.refresh(s)
        return s
