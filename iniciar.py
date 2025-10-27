#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste e validação do Sistema de Entregas
"""

import sys
import os

def verificar_requisitos():
    """Verifica se todos os requisitos estão instalados"""
    print("="*60)
    print("VERIFICAÇÃO DE REQUISITOS DO SISTEMA")
    print("="*60)
    
    # Verificar versão do Python
    print(f"\n✓ Python {sys.version}")
    
    if sys.version_info < (3, 7):
        print("❌ ERRO: Python 3.7 ou superior é necessário!")
        return False
    
    # Verificar tkinter
    try:
        import tkinter as tk
        print("✓ Tkinter está disponível")
    except ImportError:
        print("❌ ERRO: Tkinter não está instalado!")
        print("   No Ubuntu/Debian: sudo apt-get install python3-tk")
        print("   No Fedora: sudo dnf install python3-tkinter")
        return False
    
    # Verificar sqlite3
    try:
        import sqlite3
        print("✓ SQLite3 está disponível")
    except ImportError:
        print("❌ ERRO: SQLite3 não está instalado!")
        return False
    
    print("\n" + "="*60)
    print("✓ TODOS OS REQUISITOS ESTÃO SATISFEITOS!")
    print("="*60)
    return True

def criar_dados_teste():
    """Cria dados de teste no banco de dados"""
    import sqlite3
    from datetime import datetime, timedelta
    
    print("\n" + "="*60)
    print("CRIANDO DADOS DE TESTE")
    print("="*60)
    
    # Remover banco antigo se existir
    if os.path.exists('entregas.db'):
        os.remove('entregas.db')
        print("✓ Banco de dados anterior removido")
    
    conn = sqlite3.connect('entregas.db')
    cursor = conn.cursor()
    
    # Criar tabelas (usando o mesmo código do sistema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marcas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo_disagua TEXT UNIQUE NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lojas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca_id INTEGER,
            nome TEXT NOT NULL,
            codigo_disagua TEXT UNIQUE NOT NULL,
            local_entrega TEXT,
            municipio TEXT,
            estado TEXT,
            valor_20l REAL,
            valor_10l REAL,
            valor_cx_copo REAL,
            valor_1500ml REAL,
            FOREIGN KEY (marca_id) REFERENCES marcas(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parceiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cidade TEXT,
            estado TEXT,
            nome_parceiro TEXT NOT NULL,
            distribuidora TEXT,
            cnpj TEXT,
            telefone TEXT,
            email TEXT,
            dia_pagamento INTEGER,
            banco TEXT,
            agencia TEXT,
            conta TEXT,
            chave_pix TEXT,
            valor_20l REAL,
            valor_10l REAL,
            valor_cx_copo REAL,
            valor_1500ml REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parceiro_loja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parceiro_id INTEGER,
            loja_id INTEGER,
            FOREIGN KEY (parceiro_id) REFERENCES parceiros(id),
            FOREIGN KEY (loja_id) REFERENCES lojas(id),
            UNIQUE(parceiro_id, loja_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comprovantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parceiro_id INTEGER,
            loja_id INTEGER,
            data_entrega DATE,
            qtd_20l INTEGER DEFAULT 0,
            qtd_10l INTEGER DEFAULT 0,
            qtd_cx_copo INTEGER DEFAULT 0,
            qtd_1500ml INTEGER DEFAULT 0,
            assinatura TEXT,
            arquivo_comprovante TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parceiro_id) REFERENCES parceiros(id),
            FOREIGN KEY (loja_id) REFERENCES lojas(id)
        )
    ''')
    
    # Inserir marcas de teste
    cursor.execute("INSERT INTO marcas (nome, codigo_disagua) VALUES (?, ?)", 
                  ("Água Crystal", "CRYS001"))
    cursor.execute("INSERT INTO marcas (nome, codigo_disagua) VALUES (?, ?)", 
                  ("Água Pura Vida", "VIDA002"))
    print("✓ 2 marcas criadas")
    
    # Inserir lojas de teste
    lojas = [
        (1, "Supermercado Central", "LOJA001", "Rua Principal, 100", "São Paulo", "SP", 15.0, 10.0, 12.0, 3.0),
        (1, "Mercado do Bairro", "LOJA002", "Av. Santos, 200", "São Paulo", "SP", 15.0, 10.0, 12.0, 3.0),
        (2, "Loja Express", "LOJA003", "Rua Commerce, 50", "Campinas", "SP", 14.5, 9.5, 11.5, 2.8),
        (2, "Mini Market", "LOJA004", "Av. Central, 300", "Guarulhos", "SP", 14.0, 9.0, 11.0, 2.5),
    ]
    
    for loja in lojas:
        cursor.execute("""
            INSERT INTO lojas (marca_id, nome, codigo_disagua, local_entrega, municipio, 
                             estado, valor_20l, valor_10l, valor_cx_copo, valor_1500ml)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, loja)
    print("✓ 4 lojas criadas")
    
    # Inserir parceiros de teste
    parceiros = [
        ("São Paulo", "SP", "João Transportes", "Distribuidora SP", "12.345.678/0001-90", 
         "(11) 98765-4321", "joao@transporte.com", 15, "Banco do Brasil", "1234", "56789-0", 
         "joao@pix.com", 12.0, 8.0, 9.0, 2.0),
        ("Campinas", "SP", "Maria Logística", "LogCamp", "98.765.432/0001-10", 
         "(19) 97654-3210", "maria@logistica.com", 10, "Itaú", "4567", "12345-6", 
         "maria@pix.com", 11.5, 7.5, 8.5, 1.8),
    ]
    
    for parceiro in parceiros:
        cursor.execute("""
            INSERT INTO parceiros (cidade, estado, nome_parceiro, distribuidora, cnpj, telefone,
                                 email, dia_pagamento, banco, agencia, conta, chave_pix,
                                 valor_20l, valor_10l, valor_cx_copo, valor_1500ml)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, parceiro)
    print("✓ 2 parceiros criados")
    
    # Vincular lojas aos parceiros
    vinculos = [(1, 1), (1, 2), (2, 3), (2, 4)]
    for vinculo in vinculos:
        cursor.execute("INSERT INTO parceiro_loja (parceiro_id, loja_id) VALUES (?, ?)", vinculo)
    print("✓ 4 vínculos parceiro-loja criados")
    
    # Inserir comprovantes de teste
    hoje = datetime.now()
    comprovantes = [
        (1, 1, (hoje - timedelta(days=5)).strftime('%Y-%m-%d'), 10, 5, 3, 20, "José Silva"),
        (1, 2, (hoje - timedelta(days=3)).strftime('%Y-%m-%d'), 8, 4, 2, 15, "Ana Costa"),
        (2, 3, (hoje - timedelta(days=2)).strftime('%Y-%m-%d'), 12, 6, 4, 25, "Pedro Santos"),
        (2, 4, (hoje - timedelta(days=1)).strftime('%Y-%m-%d'), 15, 8, 5, 30, "Carla Lima"),
    ]
    
    for comprovante in comprovantes:
        cursor.execute("""
            INSERT INTO comprovantes (parceiro_id, loja_id, data_entrega, qtd_20l, qtd_10l,
                                    qtd_cx_copo, qtd_1500ml, assinatura)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, comprovante)
    print("✓ 4 comprovantes criados")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✓ DADOS DE TESTE CRIADOS COM SUCESSO!")
    print("="*60)
    print("\nResumo dos dados criados:")
    print("  • 2 Marcas (Água Crystal, Água Pura Vida)")
    print("  • 4 Lojas em diferentes municípios")
    print("  • 2 Parceiros (João Transportes, Maria Logística)")
    print("  • 4 Comprovantes de entrega")
    print("\nAgora você pode executar o sistema e explorar os dados!")

def iniciar_sistema():
    """Inicia o sistema"""
    print("\n" + "="*60)
    print("INICIANDO SISTEMA DE ENTREGAS")
    print("="*60)
    print("\nPressione Ctrl+C para sair\n")
    
    import sistema_entregas
    import tkinter as tk
    
    root = tk.Tk()
    app = sistema_entregas.SistemaEntregas(root)
    root.mainloop()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SISTEMA DE GERENCIAMENTO DE ENTREGAS - ÁGUA MINERAL")
    print("="*60)
    
    # Verificar requisitos
    if not verificar_requisitos():
        sys.exit(1)
    
    # Perguntar se quer criar dados de teste
    print("\n" + "="*60)
    print("OPÇÕES")
    print("="*60)
    print("\n1. Criar banco com dados de teste (recomendado para primeira vez)")
    print("2. Iniciar sistema com banco existente")
    print("3. Sair")
    
    while True:
        try:
            opcao = input("\nEscolha uma opção (1-3): ").strip()
            
            if opcao == "1":
                criar_dados_teste()
                input("\nPressione ENTER para iniciar o sistema...")
                iniciar_sistema()
                break
            elif opcao == "2":
                if not os.path.exists('entregas.db'):
                    print("\n❌ Banco de dados não encontrado!")
                    print("   Execute a opção 1 primeiro para criar o banco.")
                    continue
                iniciar_sistema()
                break
            elif opcao == "3":
                print("\nSaindo...")
                break
            else:
                print("❌ Opção inválida! Escolha 1, 2 ou 3.")
        except KeyboardInterrupt:
            print("\n\nSaindo...")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            break
