from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class Partner(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    uf: str
    cnpj: Optional[str] = Field(default=None, unique=True)
    is_active: bool = True
    stores: list["Store"] = Relationship(back_populates="partner")

class Store(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    partner_id: int = Field(foreign_key="partner.id")
    code_matriz: str
    code_loja: str
    city: str
    uf: str
    partner: Partner = Relationship(back_populates="stores")

class Brand(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
