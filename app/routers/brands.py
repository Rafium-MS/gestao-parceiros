from fastapi import APIRouter
from sqlmodel import Session, select
from ..database import engine
from ..models import Brand

router = APIRouter()

@router.get("/")
def list_brands():
    with Session(engine) as session:
        return session.exec(select(Brand)).all()

@router.post("/", status_code=201)
def create_brand(b: Brand):
    with Session(engine) as session:
        session.add(b)
        session.commit()
        session.refresh(b)
        return b
