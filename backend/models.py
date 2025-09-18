from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Integer, String, Text, Float, Date, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from backend.extensions import db


class Parceiro(db.Model):
    __tablename__ = 'parceiros'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    cpf: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    telefone: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    endereco: Mapped[str] = mapped_column(String, nullable=True)
    data_cadastro: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)
    cidade: Mapped[str] = mapped_column(String, nullable=True)
    estado: Mapped[str] = mapped_column(String, nullable=True)
    banco: Mapped[str] = mapped_column(String, nullable=True)
    agencia: Mapped[str] = mapped_column(String, nullable=True)
    conta: Mapped[str] = mapped_column(String, nullable=True)
    tipo: Mapped[str] = mapped_column(String, nullable=True)
    produto: Mapped[str] = mapped_column(String, nullable=True)
    valor_unidade: Mapped[float] = mapped_column(Float, nullable=True)

    comprovantes = relationship("Comprovante", back_populates="parceiro")
    associacoes = relationship("Associacao", back_populates="parceiro")

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'telefone': self.telefone,
            'email': self.email,
            'endereco': self.endereco,
            'data_cadastro': self.data_cadastro.isoformat(),
            'cidade': self.cidade,
            'estado': self.estado,
            'banco': self.banco,
            'agencia': self.agencia,
            'conta': self.conta,
            'tipo': self.tipo,
            'produto': self.produto,
            'valor_unidade': self.valor_unidade
        }


class Loja(db.Model):
    __tablename__ = 'lojas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    cnpj: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    telefone: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    endereco: Mapped[str] = mapped_column(String, nullable=True)
    contato: Mapped[str] = mapped_column(String, nullable=True)
    data_cadastro: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)
    cidade: Mapped[str] = mapped_column(String, nullable=True)
    estado: Mapped[str] = mapped_column(String, nullable=True)
    agrupamento_id: Mapped[int] = mapped_column(Integer, nullable=True)

    comprovantes = relationship("Comprovante", back_populates="loja")
    associacoes = relationship("Associacao", back_populates="loja")

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cnpj': self.cnpj,
            'telefone': self.telefone,
            'email': self.email,
            'endereco': self.endereco,
            'contato': self.contato,
            'data_cadastro': self.data_cadastro.isoformat(),
            'cidade': self.cidade,
            'estado': self.estado,
            'agrupamento_id': self.agrupamento_id
        }


class Comprovante(db.Model):
    __tablename__ = 'comprovantes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parceiro_id: Mapped[int] = mapped_column(Integer, ForeignKey('parceiros.id'))
    loja_id: Mapped[int] = mapped_column(Integer, ForeignKey('lojas.id'))
    data_entrega: Mapped[datetime] = mapped_column(Date)
    arquivo_comprovante: Mapped[str] = mapped_column(String)
    observacoes: Mapped[str] = mapped_column(Text, nullable=True)
    data_cadastro: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)

    parceiro = relationship("Parceiro", back_populates="comprovantes")
    loja = relationship("Loja", back_populates="comprovantes")

    def to_dict(self):
        return {
            'id': self.id,
            'parceiro_id': self.parceiro_id,
            'loja_id': self.loja_id,
            'data_entrega': self.data_entrega.isoformat(),
            'arquivo_comprovante': self.arquivo_comprovante,
            'observacoes': self.observacoes,
            'data_cadastro': self.data_cadastro.isoformat()
        }


class Associacao(db.Model):
    __tablename__ = 'associacoes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parceiro_id: Mapped[int] = mapped_column(Integer, ForeignKey('parceiros.id'))
    loja_id: Mapped[int] = mapped_column(Integer, ForeignKey('lojas.id'))
    data_associacao: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String)

    parceiro = relationship("Parceiro", back_populates="associacoes")
    loja = relationship("Loja", back_populates="associacoes")

    def to_dict(self):
        return {
            'id': self.id,
            'parceiro_id': self.parceiro_id,
            'loja_id': self.loja_id,
            'data_associacao': self.data_associacao.isoformat(),
            'status': self.status
        }


class Role(db.Model):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="role")

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }


class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), nullable=False)

    role = relationship("Role", back_populates="users")

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role_id': self.role_id
        }
