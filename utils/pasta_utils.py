import os
import shutil
from datetime import datetime


def criar_estrutura_comprovantes(mes: str, ano: str, cidade: str, parceiro: str) -> str:
    """Cria e retorna o caminho da pasta de comprovantes."""
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "comprovantes"
    )
    pasta_mes = f"{mes}-{ano}"
    caminho = os.path.join(base_dir, pasta_mes, cidade, parceiro)
    os.makedirs(caminho, exist_ok=True)
    return caminho


def renomear_comprovantes_auto(path_origem: str, dados: dict) -> str:
    """Move e renomeia um comprovante conforme os dados extraídos."""
    mes = dados.get("mes") or datetime.now().strftime("%B")
    ano = dados.get("ano") or datetime.now().strftime("%Y")
    cidade = dados.get("cidade", "Desconhecida")
    parceiro = dados.get("parceiro", "")
    destino_dir = criar_estrutura_comprovantes(mes, ano, cidade, parceiro)
    extensao = os.path.splitext(path_origem)[1]
    nome_base = dados.get("loja", "comprovante").replace(" ", "_")
    novo_nome = f"{nome_base}{extensao}"
    destino = os.path.join(destino_dir, novo_nome)
    shutil.move(path_origem, destino)
    return destino