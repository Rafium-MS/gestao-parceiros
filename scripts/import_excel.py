import os
import pandas as pd
import configparser
from database.db_manager import DatabaseManager
from models.parceiro import Parceiro
from models.loja import Loja

# Caminho padrão dos arquivos
PASTA_IMPORTACAO = os.path.join(os.getcwd(), "dados_importacao")

CAMPOS_PARCEIRO = {
    'nome': 'nome',
    'cpf': 'cpf',
    'telefone': 'telefone',
    'email': 'email',
    'endereco': 'endereco',
    'cidade': 'cidade',
    'estado': 'estado',
    'banco': 'banco',
    'agencia': 'agencia',
    'conta': 'conta',
    'tipo': 'tipo',
    'produto': 'produto',
    'valor_unidade': 'valor_unidade'
}

CAMPOS_LOJA = {
    'nome': 'nome',
    'cnpj': 'cnpj',
    'telefone': 'telefone',
    'email': 'email',
    'endereco': 'endereco',
    'contato': 'contato',
    'cidade': 'cidade',
    'estado': 'estado',
    'agrupamento_id': 'agrupamento_id'
}


def carregar_config(caminho='config.ini'):
    config = configparser.ConfigParser()
    config.read(caminho)
    return config


def normalizar_colunas(df):
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df


def encontrar_aba(nome_chave, sheets):
    for nome, df in sheets.items():
        if nome_chave in nome.lower():
            return df
    return None


def importar_parceiros(df, db_manager):
    for _, row in df.iterrows():
        parceiro = Parceiro(db_manager)
        for col, attr in CAMPOS_PARCEIRO.items():
            if col in row and not pd.isna(row[col]):
                setattr(parceiro, attr, row[col])
        parceiro.salvar()


def importar_lojas(df, db_manager):
    for _, row in df.iterrows():
        loja = Loja(db_manager)
        for col, attr in CAMPOS_LOJA.items():
            if col in row and not pd.isna(row[col]):
                setattr(loja, attr, row[col])
        loja.salvar()


def processar_arquivo(arquivo, db_manager):
    print(f"📂 Processando: {arquivo}")
    try:
        sheets = pd.read_excel(arquivo, sheet_name=None)
        aba_parceiros = encontrar_aba('parceiro', sheets)
        if aba_parceiros is not None:
            importar_parceiros(normalizar_colunas(aba_parceiros), db_manager)
        else:
            print("❌ Aba de parceiros não encontrada.")

        aba_lojas = encontrar_aba('loja', sheets)
        if aba_lojas is not None:
            importar_lojas(normalizar_colunas(aba_lojas), db_manager)
        else:
            print("❌ Aba de lojas não encontrada.")
    except Exception as e:
        print(f"Erro ao processar '{arquivo}': {e}")


def main():
    config = carregar_config()
    db_path = config['DATABASE']['path']
    db_manager = DatabaseManager(db_path)

    if not os.path.exists(PASTA_IMPORTACAO):
        os.makedirs(PASTA_IMPORTACAO)

    arquivos = [f for f in os.listdir(PASTA_IMPORTACAO) if f.endswith(".xlsx")]

    if not arquivos:
        print("Nenhum arquivo .xlsx encontrado na pasta de importação.")
        return

    for nome_arquivo in arquivos:
        caminho_completo = os.path.join(PASTA_IMPORTACAO, nome_arquivo)
        processar_arquivo(caminho_completo, db_manager)

    db_manager.commit()
    db_manager.close_connection()
    print("✅ Importação concluída com sucesso.")


if __name__ == '__main__':
    main()
