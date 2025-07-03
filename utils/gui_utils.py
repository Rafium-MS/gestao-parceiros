import logging
from typing import Dict, List


def carregar_combobox_por_cidade(
    db_manager, tabela: str, cidade: str
) -> Dict[str, int]:
    """Retorna itens de uma tabela filtrados pela cidade."""
    try:
        query = f"SELECT id, nome FROM {tabela} WHERE cidade = ? ORDER BY nome"
        db_manager.execute(query, (cidade,))
        resultados = db_manager.fetchall()
        return {row[1]: row[0] for row in resultados}
    except Exception as exc:
        logging.getLogger(__name__).error(
            "Erro ao carregar combobox para %s: %s", tabela, exc
        )
        return {}


def carregar_combobox_cidades_por_parceiro(db_manager, parceiro_id: int) -> List[str]:
    """Carrega as cidades de entregas de um parceiro."""
    try:
        db_manager.execute(
            """
            SELECT DISTINCT l.cidade
            FROM lojas l
            JOIN associacoes a ON l.id = a.loja_id
            WHERE a.parceiro_id = ?
            ORDER BY l.cidade
            """,
            (parceiro_id,),
        )
        return [r[0] for r in db_manager.fetchall() if r[0]]
    except Exception as exc:
        logging.getLogger(__name__).error(
            "Erro ao carregar cidades do parceiro %s: %s", parceiro_id, exc
        )
        return []


def carregar_combobox_parceiros_por_loja(db_manager, loja_id: int) -> Dict[str, int]:
    """Carrega parceiros associados a uma loja."""
    try:
        db_manager.execute(
            """
            SELECT p.id, p.nome
            FROM parceiros p
            JOIN associacoes a ON p.id = a.parceiro_id
            WHERE a.loja_id = ?
            ORDER BY p.nome
            """,
            (loja_id,),
        )
        return {row[1]: row[0] for row in db_manager.fetchall()}
    except Exception as exc:
        logging.getLogger(__name__).error(
            "Erro ao carregar parceiros da loja %s: %s", loja_id, exc
        )
        return {}