"""Repository layer responsible for database CRUD operations."""

from .marcas import MarcasRepository
from .lojas import LojasRepository
from .parceiros import ParceirosRepository
from .parceiro_loja import ParceiroLojaRepository
from .comprovantes import ComprovantesRepository

__all__ = [
    "MarcasRepository",
    "LojasRepository",
    "ParceirosRepository",
    "ParceiroLojaRepository",
    "ComprovantesRepository",
]

