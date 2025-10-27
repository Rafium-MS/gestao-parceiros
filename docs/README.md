# Sistema de Gerenciamento de Entregas - Água Mineral

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Tkinter (já vem instalado com Python)

## 🚀 Como Executar

1. Certifique-se de ter Python instalado:
```bash
python --version
```

2. Execute o sistema:
```bash
python sistema_entregas.py
```

## 📚 Manual de Uso

### 1. Cadastro de Marca
- Acesse a aba "🏢 Marcas"
- Preencha o nome da marca (o código Disagua é opcional)
- Clique em "Salvar Marca"

### 2. Cadastro de Lojas
- Acesse a aba "🏪 Lojas"
- Selecione a marca
- Preencha os dados da loja e valores dos produtos
- Clique em "Salvar Loja"

### 3. Cadastro de Parceiros
- Acesse a aba "🚚 Parceiros"
- Preencha os dados do parceiro
- Informe os valores que ele receberá por produto
- Clique em "Salvar Parceiro"

### 4. Vincular Lojas aos Parceiros
- Na aba "🚚 Parceiros", clique em "Lojas do Parceiro"
- Selecione o parceiro
- Use as setas para adicionar/remover lojas

### 5. Registrar Comprovantes
- Acesse a aba "📋 Comprovantes"
- Selecione parceiro e loja
- Informe data, quantidades e assinatura
- Opcionalmente, anexe um arquivo
- Clique em "Salvar Comprovante"

### 6. Gerar Relatórios
- Acesse a aba "📊 Relatórios"
- Escolha entre "Relatório por Marca" ou "Relatório por Parceiro"
- Selecione os filtros desejados
- Clique em "Gerar Relatório"

### 7. Dashboard
- Visualize indicadores em tempo real
- Acompanhe quais parceiros já enviaram comprovantes
- Veja o percentual de relatórios preenchidos

## 🔧 Estrutura do Banco de Dados

O sistema cria automaticamente um arquivo `entregas.db` com as seguintes tabelas:

- **marcas**: Cadastro de marcas
- **lojas**: Cadastro de lojas vinculadas a marcas
- **parceiros**: Cadastro de parceiros/entregadores
- **parceiro_loja**: Vínculo entre parceiros e lojas
- **comprovantes**: Registro de entregas realizadas

## 📊 Diferença de Preços

- **Valores da Loja**: Preço cobrado pelo serviço (aparece no relatório da marca)
- **Valores do Parceiro**: Preço pago ao parceiro pelo serviço (aparece no relatório do parceiro)

## 🔄 Migração para Multiusuário

Atualmente o sistema usa SQLite (arquivo local). Para migrar para um banco multiusuário:

1. Instalar PostgreSQL ou MySQL
2. Adaptar as conexões no código
3. Configurar servidor de aplicação

## 💡 Dicas

- Use formato de data: DD/MM/AAAA
- Valores monetários podem usar vírgula ou ponto
- O dashboard atualiza automaticamente ao registrar comprovantes
- Backup regular do arquivo entregas.db é recomendado

## 🐛 Suporte

Para melhorias ou correções, entre em contato com o desenvolvedor.
