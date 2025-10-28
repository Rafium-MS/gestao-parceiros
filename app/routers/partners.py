from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import engine
from ..models import Partner

router = APIRouter()

@router.get("/")
def list_partners():
    with Session(engine) as session:
        return session.exec(select(Partner)).all()

@router.post("/", status_code=201)
def create_partner(p: Partner):
    with Session(engine) as session:
        session.add(p)
        session.commit()
        session.refresh(p)
        return p
