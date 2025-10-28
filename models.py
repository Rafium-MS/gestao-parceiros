
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, UniqueConstraint, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Partner(Base):
    __tablename__ = "partners"
    id = Column(Integer, primary_key=True)
    cidade = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    parceiro = Column(String, nullable=False)
    distribuidora = Column(String)
    cnpj_cpf = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String)
    dia_pagamento = Column(Integer)
    banco = Column(String)
    agencia_conta = Column(String)
    pix = Column(String)
    cx_copo = Column(Float, default=0.0)
    dez_litros = Column(Float, default=0.0)
    vinte_litros = Column(Float, default=0.0)
    mil_quinhentos_ml = Column(Float, default=0.0)
    vasilhame = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True)
    marca = Column(String, nullable=False, unique=True)
    cod_disagua = Column(String)
    stores = relationship("Store", back_populates="brand", cascade="all, delete-orphan")

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True)
    marca_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    loja = Column(String, nullable=False)
    cod_disagua = Column(String)
    local_entrega = Column(String, nullable=False)
    endereco = Column(String)
    municipio = Column(String, nullable=False)
    uf = Column(String, nullable=False)
    valor_20l = Column(Float, default=0.0)
    valor_10l = Column(Float, default=0.0)
    valor_1500ml = Column(Float, default=0.0)
    valor_cx_copo = Column(Float, default=0.0)
    valor_vasilhame = Column(Float, default=0.0)
    brand = relationship("Brand", back_populates="stores")

class Connection(Base):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    __table_args__ = (UniqueConstraint('partner_id', 'store_id', name='uq_partner_store'),)

class ReportEntry(Base):
    __tablename__ = "report_entries"
    id = Column(Integer, primary_key=True)
    marca = Column(String, nullable=False)
    loja = Column(String, nullable=False)
    data = Column(Date, nullable=False)
    valor_20l = Column(Float, default=0.0)
    valor_10l = Column(Float, default=0.0)
    valor_1500ml = Column(Float, default=0.0)
    valor_cx_copo = Column(Float, default=0.0)
    valor_vasilhame = Column(Float, default=0.0)

class ReceiptImage(Base):
    __tablename__ = "receipt_images"
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    filename = Column(String, nullable=False)
    size_bytes = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default='operator')  # admin | operator | viewer
    is_active = Column(Boolean, default=True)
