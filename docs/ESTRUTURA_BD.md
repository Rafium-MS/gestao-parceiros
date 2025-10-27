# 🗄️ ESTRUTURA DO BANCO DE DADOS - Sistema de Entregas

## Visão Geral

O sistema utiliza SQLite como banco de dados. O arquivo `entregas.db` é criado automaticamente na primeira execução e contém todas as tabelas e relacionamentos necessários.

## 📊 Diagrama de Relacionamentos

```
┌─────────────┐
│   MARCAS    │
│ (id, nome,  │
│  codigo)    │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────┴──────────────────┐
│        LOJAS            │
│ (id, marca_id, nome,    │
│  codigo, endereco,      │
│  municipio, estado,     │
│  valores...)            │
└──────┬──────────────────┘
       │ N
       │
       │ N
┌──────┴──────────────────┐
│   PARCEIRO_LOJA         │
│ (id, parceiro_id,       │
│  loja_id)               │
└──────┬──────────────────┘
       │ N
       │
       │ 1
┌──────┴──────────────────┐
│     PARCEIROS           │
│ (id, nome, cidade,      │
│  estado, dados_bancarios│
│  valores...)            │
└──────┬──────────────────┘
       │ 1
       │
       │ N
┌──────┴──────────────────┐
│   COMPROVANTES          │
│ (id, parceiro_id,       │
│  loja_id, data,         │
│  quantidades...)        │
└─────────────────────────┘
```

## 📋 TABELAS

### 1. MARCAS
Armazena as marcas de água mineral.

```sql
CREATE TABLE marcas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    codigo_disagua TEXT UNIQUE NOT NULL
);
```

**Campos:**
- `id`: Identificador único (gerado automaticamente)
- `nome`: Nome da marca (ex: "Água Crystal")
- `codigo_disagua`: Código único da marca no sistema Disagua

**Índices:**
- PRIMARY KEY em `id`
- UNIQUE em `codigo_disagua`

---

### 2. LOJAS
Armazena as lojas que recebem entregas de água.

```sql
CREATE TABLE lojas (
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
);
```

**Campos:**
- `id`: Identificador único
- `marca_id`: Referência à marca (FK)
- `nome`: Nome da loja
- `codigo_disagua`: Código único da loja
- `local_entrega`: Endereço completo de entrega
- `municipio`: Cidade da loja
- `estado`: UF (ex: "SP", "RJ")
- `valor_20l`: Valor cobrado pelo galão de 20L
- `valor_10l`: Valor cobrado pelo galão de 10L
- `valor_cx_copo`: Valor cobrado pela caixa de copos
- `valor_1500ml`: Valor cobrado pela garrafa 1500ml

**Relacionamentos:**
- N lojas : 1 marca

**Índices:**
- PRIMARY KEY em `id`
- UNIQUE em `codigo_disagua`
- FOREIGN KEY em `marca_id`

---

### 3. PARCEIROS
Armazena os parceiros/entregadores responsáveis pelas entregas.

```sql
CREATE TABLE parceiros (
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
);
```

**Campos:**
- `id`: Identificador único
- `cidade`: Cidade de atuação do parceiro
- `estado`: UF do parceiro
- `nome_parceiro`: Nome/Razão social do parceiro
- `distribuidora`: Nome da distribuidora vinculada
- `cnpj`: CNPJ do parceiro
- `telefone`: Telefone de contato
- `email`: E-mail de contato
- `dia_pagamento`: Dia do mês para pagamento (1-31)
- `banco`: Nome do banco
- `agencia`: Número da agência
- `conta`: Número da conta
- `chave_pix`: Chave PIX para pagamentos
- `valor_20l`: Valor pago ao parceiro por galão 20L
- `valor_10l`: Valor pago ao parceiro por galão 10L
- `valor_cx_copo`: Valor pago ao parceiro por cx copos
- `valor_1500ml`: Valor pago ao parceiro por garrafa 1500ml

**Observação:** Os valores do parceiro são geralmente menores que os valores da loja, sendo a diferença a margem de lucro.

**Índices:**
- PRIMARY KEY em `id`

---

### 4. PARCEIRO_LOJA
Tabela de relacionamento N:N entre parceiros e lojas.
Define quais lojas cada parceiro pode entregar.

```sql
CREATE TABLE parceiro_loja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parceiro_id INTEGER,
    loja_id INTEGER,
    FOREIGN KEY (parceiro_id) REFERENCES parceiros(id),
    FOREIGN KEY (loja_id) REFERENCES lojas(id),
    UNIQUE(parceiro_id, loja_id)
);
```

**Campos:**
- `id`: Identificador único
- `parceiro_id`: Referência ao parceiro (FK)
- `loja_id`: Referência à loja (FK)

**Relacionamentos:**
- N parceiros : N lojas

**Índices:**
- PRIMARY KEY em `id`
- UNIQUE em (parceiro_id, loja_id) - Impede duplicação
- FOREIGN KEY em `parceiro_id`
- FOREIGN KEY em `loja_id`

---

### 5. COMPROVANTES
Armazena os comprovantes de entrega realizadas.

```sql
CREATE TABLE comprovantes (
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
);
```

**Campos:**
- `id`: Identificador único
- `parceiro_id`: Parceiro que realizou a entrega (FK)
- `loja_id`: Loja que recebeu a entrega (FK)
- `data_entrega`: Data em que a entrega foi realizada
- `qtd_20l`: Quantidade de galões 20L entregues
- `qtd_10l`: Quantidade de galões 10L entregues
- `qtd_cx_copo`: Quantidade de caixas de copos entregues
- `qtd_1500ml`: Quantidade de garrafas 1500ml entregues
- `assinatura`: Nome de quem recebeu a entrega
- `arquivo_comprovante`: Caminho para arquivo anexado (opcional)
- `data_cadastro`: Data/hora de registro no sistema

**Relacionamentos:**
- N comprovantes : 1 parceiro
- N comprovantes : 1 loja

**Índices:**
- PRIMARY KEY em `id`
- FOREIGN KEY em `parceiro_id`
- FOREIGN KEY em `loja_id`

## 🔍 CONSULTAS IMPORTANTES

### Total de entregas por parceiro
```sql
SELECT 
    p.nome_parceiro,
    COUNT(c.id) as total_entregas,
    SUM(c.qtd_20l) as total_20l,
    SUM(c.qtd_10l) as total_10l
FROM parceiros p
LEFT JOIN comprovantes c ON p.id = c.parceiro_id
GROUP BY p.id;
```

### Valor total a receber por parceiro (período)
```sql
SELECT 
    p.nome_parceiro,
    SUM(c.qtd_20l * p.valor_20l + 
        c.qtd_10l * p.valor_10l + 
        c.qtd_cx_copo * p.valor_cx_copo + 
        c.qtd_1500ml * p.valor_1500ml) as total_receber
FROM comprovantes c
JOIN parceiros p ON c.parceiro_id = p.id
WHERE c.data_entrega BETWEEN '2025-01-01' AND '2025-01-31'
GROUP BY p.id;
```

### Valor total por marca (período)
```sql
SELECT 
    m.nome as marca,
    l.nome as loja,
    SUM(c.qtd_20l * l.valor_20l + 
        c.qtd_10l * l.valor_10l + 
        c.qtd_cx_copo * l.valor_cx_copo + 
        c.qtd_1500ml * l.valor_1500ml) as total_cobrado
FROM comprovantes c
JOIN lojas l ON c.loja_id = l.id
JOIN marcas m ON l.marca_id = m.id
WHERE c.data_entrega BETWEEN '2025-01-01' AND '2025-01-31'
GROUP BY l.id;
```

### Lojas atendidas por parceiro
```sql
SELECT 
    p.nome_parceiro,
    l.nome as loja,
    l.municipio,
    l.estado
FROM parceiro_loja pl
JOIN parceiros p ON pl.parceiro_id = p.id
JOIN lojas l ON pl.loja_id = l.id
ORDER BY p.nome_parceiro, l.nome;
```

## 🔐 INTEGRIDADE DOS DADOS

### Constraints Implementadas:

1. **PRIMARY KEYS**: Todas as tabelas têm chave primária auto-incrementada
2. **FOREIGN KEYS**: Relacionamentos garantem integridade referencial
3. **UNIQUE**: Códigos Disagua únicos para marcas e lojas
4. **UNIQUE COMPOSITE**: Não permite duplicar vinculação parceiro-loja
5. **NOT NULL**: Campos obrigatórios definidos
6. **DEFAULT**: Valores padrão para quantidades e data de cadastro

### Cascata de Exclusão (Não implementada):

Atualmente, a exclusão de registros pai (marca, parceiro, loja) não é automaticamente propagada.
**Recomendação:** Implementar ON DELETE CASCADE ou verificações antes de excluir.

## 📊 ÍNDICES RECOMENDADOS (Futura Otimização)

Para melhorar performance em grandes volumes:

```sql
CREATE INDEX idx_comprovantes_data ON comprovantes(data_entrega);
CREATE INDEX idx_comprovantes_parceiro ON comprovantes(parceiro_id);
CREATE INDEX idx_comprovantes_loja ON comprovantes(loja_id);
CREATE INDEX idx_lojas_marca ON lojas(marca_id);
CREATE INDEX idx_lojas_municipio ON lojas(municipio);
CREATE INDEX idx_parceiros_cidade ON parceiros(cidade);
```

## 🔄 MIGRAÇÃO PARA MULTIUSUÁRIO

Quando migrar para PostgreSQL/MySQL:

1. **Tipos de dados:**
   - INTEGER → INT ou SERIAL (auto-incremento)
   - REAL → DECIMAL(10,2) para valores monetários
   - TEXT → VARCHAR(tamanho apropriado)
   - TIMESTAMP → mantém igual

2. **Adicionar campos de auditoria:**
   - `created_by` (usuário que criou)
   - `updated_at` (última atualização)
   - `updated_by` (último usuário que alterou)

3. **Adicionar tabela de usuários:**
   ```sql
   CREATE TABLE usuarios (
       id SERIAL PRIMARY KEY,
       username VARCHAR(50) UNIQUE NOT NULL,
       password_hash VARCHAR(255) NOT NULL,
       nome_completo VARCHAR(100),
       email VARCHAR(100),
       perfil VARCHAR(20), -- admin, operador, consulta
       ativo BOOLEAN DEFAULT TRUE,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

## 💾 BACKUP E RESTORE

### Backup SQLite:
```bash
# Backup completo
cp entregas.db entregas_backup_$(date +%Y%m%d).db

# Ou usando sqlite3
sqlite3 entregas.db ".backup entregas_backup.db"
```

### Restore:
```bash
# Simplesmente copiar o arquivo de volta
cp entregas_backup.db entregas.db
```

## 📈 ESTATÍSTICAS ÚTEIS

### Tamanho médio do banco:
- Banco vazio: ~20 KB
- Com 100 comprovantes: ~100 KB
- Com 1000 comprovantes: ~500 KB

### Performance esperada:
- Consultas simples: < 1ms
- Relatórios complexos: < 100ms
- Limite prático SQLite: ~100.000 registros

---

**Nota:** Este é um banco de dados bem estruturado e normalizado, pronto para escalar conforme a necessidade do negócio!
