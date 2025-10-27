"""
Módulo de exportação de dados.

Exporta dados do sistema para diferentes formatos (CSV, Excel, PDF).
"""

import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
from config.settings import EXPORT_DIR


class ExportManager:
    """
    Gerenciador de exportações de dados.
    
    Permite exportar dados para CSV, Excel e PDF.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de exportações."""
        self.logger = logging.getLogger(__name__)
        self.export_dir = EXPORT_DIR
        
        # Garante que o diretório existe
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def exportar_para_csv(self, dados: List[Dict[str, Any]], 
                          nome_arquivo: str, 
                          colunas: List[str] = None) -> Tuple[bool, str]:
        """
        Exporta dados para arquivo CSV.
        
        Args:
            dados: Lista de dicionários com os dados
            nome_arquivo: Nome do arquivo (sem extensão)
            colunas: Lista de colunas a exportar (None = todas)
            
        Returns:
            tuple: (sucesso, caminho do arquivo ou mensagem de erro)
        """
        try:
            if not dados:
                return False, "Não há dados para exportar"
            
            # Gera nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_completo = f"{nome_arquivo}_{timestamp}.csv"
            caminho_arquivo = self.export_dir / nome_completo
            
            # Define colunas (usa todas se não especificado)
            if colunas is None:
                colunas = list(dados[0].keys())
            
            # Escreve o CSV
            with open(caminho_arquivo, 'w', newline='', encoding='utf-8-sig') as arquivo_csv:
                writer = csv.DictWriter(arquivo_csv, fieldnames=colunas, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(dados)
            
            self.logger.info(f"Dados exportados para CSV: {caminho_arquivo}")
            return True, str(caminho_arquivo)
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar para CSV: {e}")
            return False, f"Erro ao exportar para CSV: {str(e)}"
    
    def exportar_para_excel(self, dados: List[Dict[str, Any]], 
                           nome_arquivo: str,
                           nome_planilha: str = "Dados") -> Tuple[bool, str]:
        """
        Exporta dados para arquivo Excel.
        
        Args:
            dados: Lista de dicionários com os dados
            nome_arquivo: Nome do arquivo (sem extensão)
            nome_planilha: Nome da planilha no Excel
            
        Returns:
            tuple: (sucesso, caminho do arquivo ou mensagem de erro)
        """
        try:
            # TODO: Implementar exportação para Excel usando openpyxl ou xlsxwriter
            self.logger.warning("Exportação para Excel ainda não implementada")
            return False, "Exportação para Excel em desenvolvimento. Use CSV por enquanto."
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar para Excel: {e}")
            return False, f"Erro ao exportar para Excel: {str(e)}"
    
    def exportar_para_pdf(self, dados: List[Dict[str, Any]], 
                         nome_arquivo: str,
                         titulo: str = "Relatório") -> Tuple[bool, str]:
        """
        Exporta dados para arquivo PDF.
        
        Args:
            dados: Lista de dicionários com os dados
            nome_arquivo: Nome do arquivo (sem extensão)
            titulo: Título do relatório
            
        Returns:
            tuple: (sucesso, caminho do arquivo ou mensagem de erro)
        """
        try:
            # TODO: Implementar exportação para PDF usando reportlab
            self.logger.warning("Exportação para PDF ainda não implementada")
            return False, "Exportação para PDF em desenvolvimento. Use CSV por enquanto."
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar para PDF: {e}")
            return False, f"Erro ao exportar para PDF: {str(e)}"
    
    def listar_exportacoes(self) -> List[dict]:
        """
        Lista todos os arquivos exportados.
        
        Returns:
            List[dict]: Lista de dicionários com informações dos arquivos
        """
        try:
            exportacoes = []
            
            for arquivo in sorted(self.export_dir.iterdir(), reverse=True):
                if arquivo.is_file():
                    info = {
                        'nome': arquivo.name,
                        'caminho': str(arquivo),
                        'tamanho': arquivo.stat().st_size,
                        'data_criacao': datetime.fromtimestamp(arquivo.stat().st_mtime),
                        'formato': arquivo.suffix[1:].upper()
                    }
                    exportacoes.append(info)
            
            return exportacoes
            
        except Exception as e:
            self.logger.error(f"Erro ao listar exportações: {e}")
            return []
    
    def deletar_exportacao(self, caminho_arquivo: str) -> Tuple[bool, str]:
        """
        Deleta um arquivo de exportação.
        
        Args:
            caminho_arquivo: Caminho do arquivo
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        try:
            arquivo = Path(caminho_arquivo)
            
            if not arquivo.exists():
                return False, "Arquivo não encontrado"
            
            arquivo.unlink()
            self.logger.info(f"Arquivo deletado: {caminho_arquivo}")
            return True, "Arquivo deletado com sucesso!"
            
        except Exception as e:
            self.logger.error(f"Erro ao deletar arquivo: {e}")
            return False, f"Erro ao deletar arquivo: {str(e)}"
    
    def limpar_exportacoes_antigas(self, dias: int = 30):
        """
        Remove exportações mais antigas que o número de dias especificado.
        
        Args:
            dias: Número de dias para considerar arquivo como antigo
        """
        try:
            from datetime import timedelta
            
            limite_data = datetime.now() - timedelta(days=dias)
            
            for arquivo in self.export_dir.iterdir():
                if arquivo.is_file():
                    data_modificacao = datetime.fromtimestamp(arquivo.stat().st_mtime)
                    if data_modificacao < limite_data:
                        arquivo.unlink()
                        self.logger.info(f"Exportação antiga removida: {arquivo.name}")
                        
        except Exception as e:
            self.logger.error(f"Erro ao limpar exportações antigas: {e}")