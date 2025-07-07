import argparse
import configparser
import os
import pandas as pd
from database.db_manager import DatabaseManager
from models.parceiro import Parceiro
from models.loja import Loja


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

def main():
    parser = argparse.ArgumentParser(description='Importa dados de parceiros e lojas a partir de um arquivo Excel.')
    parser.add_argument('arquivo', help='Caminho para o arquivo Excel')
    args = parser.parse_args()

    if not os.path.exists(args.arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {args.arquivo}")

    config = carregar_config()
    db_path = config['DATABASE']['path']
    db_manager = DatabaseManager(db_path)

    sheets = pd.read_excel(args.arquivo, sheet_name=None)
    if 'parceiros' in sheets:
        importar_parceiros(sheets['parceiros'], db_manager)
    if 'lojas' in sheets:
        importar_lojas(sheets['lojas'], db_manager)

    db_manager.commit()
    db_manager.close_connection()
    print('Importação concluída.')

if __name__ == '__main__':
    main()