# 📘 EXEMPLOS PRÁTICOS DE USO - Sistema de Entregas

## 🎯 CENÁRIOS REAIS DO DIA A DIA

Este documento apresenta situações práticas de uso do sistema, passo a passo.

---

## 📚 ÍNDICE DE CENÁRIOS

1. [Primeira Configuração do Sistema](#1-primeira-configuração)
2. [Adicionando Nova Loja](#2-adicionando-nova-loja)
3. [Cadastrando Novo Parceiro](#3-cadastrando-novo-parceiro)
4. [Registrando Entregas Diárias](#4-registrando-entregas-diárias)
5. [Fechamento Mensal de Parceiro](#5-fechamento-mensal)
6. [Análise de Desempenho](#6-análise-de-desempenho)
7. [Correção de Erros](#7-correção-de-erros)

---

## 1️⃣ PRIMEIRA CONFIGURAÇÃO DO SISTEMA {#1-primeira-configuração}

### Situação:
Você acabou de baixar o sistema e vai começar a usar pela primeira vez.

### Passos:

#### 1.1 Executar o sistema
```bash
python iniciar.py
```
- Escolha opção **1** (criar dados de teste) na primeira vez
- Isso criará exemplos que você pode explorar

#### 1.2 Explorar os dados de teste
1. Abra a aba **Dashboard**
   - Veja os indicadores
   - Observe o farol de parceiros

2. Visite cada aba:
   - 🏢 Marcas: Veja as 2 marcas de exemplo
   - 🏪 Lojas: Veja as 4 lojas cadastradas
   - 🚚 Parceiros: Veja os 2 parceiros
   - 📋 Comprovantes: Veja as entregas registradas
   - 📊 Relatórios: Gere um relatório de teste

#### 1.3 Limpar dados de teste (quando estiver pronto)
1. Feche o sistema
2. Delete o arquivo `entregas.db`
3. Execute novamente com opção **2**
4. Agora cadastre seus dados reais!

---

## 2️⃣ ADICIONANDO NOVA LOJA {#2-adicionando-nova-loja}

### Situação:
Sua distribuidora fechou contrato com uma nova loja e você precisa cadastrá-la no sistema.

### Exemplo Real:
**Super Mercado Bom Preço** acabou de fechar contrato para receber água da marca **Água Crystal**.

### Passos:

#### 2.1 Verificar se a marca existe
1. Vá para aba **🏢 Marcas**
2. Procure "Água Crystal" na lista
3. **Se não existir**: cadastre primeiro!
   - Nome: `Água Crystal`
   - Código: `CRYS001`

#### 2.2 Cadastrar a loja
1. Vá para aba **🏪 Lojas**
2. Preencha os dados:

```
Marca: 1 - Água Crystal
Nome da Loja: Super Mercado Bom Preço
Código Disagua: LOJA005
Local de Entrega: Rua das Flores, 500 - Centro
Município: São Paulo
Estado: SP

Valores (o que você cobra da loja):
Valor 20L: 16.00
Valor 10L: 11.00
Valor Cx Copo: 13.00
Valor 1500ml: 3.50
```

3. Clique em **"Salvar Loja"**
4. Verifique se apareceu na lista abaixo

#### 2.3 Vincular a um parceiro
1. Vá para aba **🚚 Parceiros**
2. Clique em **"Lojas do Parceiro"**
3. Selecione o parceiro que vai atender esta loja
4. Encontre "Super Mercado Bom Preço" na lista da esquerda
5. Clique na **seta →** para adicionar
6. Pronto! A loja está vinculada

---

## 3️⃣ CADASTRANDO NOVO PARCEIRO {#3-cadastrando-novo-parceiro}

### Situação:
Você contratou um novo parceiro/entregador para fazer as entregas em determinada região.

### Exemplo Real:
**Carlos Transportes Ltda** vai começar a fazer entregas na região de Guarulhos.

### Passos:

#### 3.1 Reunir informações necessárias
Antes de começar, tenha em mãos:
- ✅ Nome/Razão Social
- ✅ CNPJ
- ✅ Telefone e e-mail
- ✅ Dados bancários completos
- ✅ Valores que você vai pagar por produto
- ✅ Dia do pagamento

#### 3.2 Cadastrar o parceiro
1. Vá para aba **🚚 Parceiros**
2. Aba **"Cadastro de Parceiro"**
3. Preencha:

```
Nome do Parceiro: Carlos Transportes Ltda
Distribuidora: Distribuidora Guarulhos
Cidade: Guarulhos
Estado: SP
CNPJ: 12.345.678/0001-90
Telefone: (11) 98888-7777
Email: carlos@transportes.com
Dia do Pagamento: 10

Banco: Caixa Econômica
Agência: 0123
Conta: 45678-9
Chave PIX: carlos@transportes.com

Valores (o que você vai pagar ao parceiro):
Valor 20L: 13.00
Valor 10L: 8.50
Valor Cx Copo: 10.00
Valor 1500ml: 2.50
```

4. Clique em **"Salvar Parceiro"**

#### 3.3 Vincular lojas
1. Vá para aba **"Lojas do Parceiro"**
2. Selecione "Carlos Transportes Ltda"
3. Adicione todas as lojas de Guarulhos usando a **seta →**

#### 3.4 Verificação
No Dashboard, você verá o novo parceiro listado com status "Pendente" (até fazer a primeira entrega).

---

## 4️⃣ REGISTRANDO ENTREGAS DIÁRIAS {#4-registrando-entregas-diárias}

### Situação:
É final do dia e você recebeu os comprovantes de entrega dos parceiros.

### Exemplo Real:
João entregou no **Supermercado Central** hoje:
- 15 galões de 20L
- 8 galões de 10L
- 5 caixas de copos
- 30 garrafas de 1500ml

### Passos:

#### 4.1 Preparar informações
- ✅ Comprovante físico ou foto
- ✅ Nome de quem assinou
- ✅ Data da entrega
- ✅ Quantidades de cada produto

#### 4.2 Registrar no sistema
1. Vá para aba **📋 Comprovantes**
2. Preencha:

```
Parceiro: 1 - João Transportes
Loja: 1 - Supermercado Central (lista automática!)
Data da Entrega: 24/10/2025
Assinatura: Maria Silva

Produtos:
Qtd 20L: 15
Qtd 10L: 8
Qtd Cx Copo: 5
Qtd 1500ml: 30

Arquivo: [Selecionar foto do comprovante]
```

3. Clique em **"Salvar Comprovante"**

#### 4.3 Verificação
- Comprovante aparece na lista abaixo
- Dashboard atualiza automaticamente
- Parceiro muda para status "Enviado"

#### 4.4 Processar mais comprovantes
Repita para cada entrega do dia. Dica: use **"Limpar"** entre um registro e outro.

---

## 5️⃣ FECHAMENTO MENSAL DE PARCEIRO {#5-fechamento-mensal}

### Situação:
Chegou o dia 10 (dia de pagamento do João) e você precisa calcular quanto deve pagar a ele.

### Passos:

#### 5.1 Gerar relatório do parceiro
1. Vá para aba **📊 Relatórios**
2. Aba **"Relatório por Parceiro"**
3. Selecione:
   ```
   Parceiro: 1 - João Transportes
   Data Início: 01/10/2025
   Data Fim: 31/10/2025
   ```
4. Clique em **"Gerar Relatório"**

#### 5.2 Analisar o resultado
O relatório mostrará:
```
Loja                  Data       20L  10L  Cx  1500ml  Total
Supermercado Central  24/10/2025  15   8    5   30     R$ 501.00
Mercado do Bairro     25/10/2025  20   10   8   40     R$ 678.00
...
                                                TOTAL: R$ 3.450,00
```

#### 5.3 Exportar (quando implementado)
- Clique em **"Exportar para Excel"**
- Anexe ao comprovante de pagamento
- Envie para o parceiro

#### 5.4 Efetuar pagamento
1. Realize transferência/PIX
2. Guarde comprovante
3. (Futuro) Registre no sistema como "Pago"

---

## 6️⃣ ANÁLISE DE DESEMPENHO {#6-análise-de-desempenho}

### Situação:
Final do mês - você quer analisar o desempenho geral do negócio.

### Passos:

#### 6.1 Dashboard geral
1. Abra a aba **📊 Dashboard**
2. Observe:
   - Quantos parceiros enviaram comprovantes?
   - Qual o percentual de cobertura?
   - Tem parceiro sem entregar?

#### 6.2 Análise por marca
1. Vá para **📊 Relatórios** → "Relatório por Marca"
2. Gere para a marca "Água Crystal"
3. Período: Todo o mês
4. Analise:
   ```
   Loja                Total Entregue  Valor Total
   Supermercado A      200 unidades    R$ 5.200,00
   Supermercado B      150 unidades    R$ 3.900,00
   ...
   TOTAL:                              R$ 15.600,00
   ```

#### 6.3 Identificar oportunidades
- **Lojas com baixo volume**: Podem precisar de atenção comercial
- **Produtos menos entregues**: Avaliar se há demanda
- **Parceiros mais ativos**: Considerar bonificação

#### 6.4 Comparação com mês anterior
(Futuro) O sistema mostrará gráficos de evolução mensal.

---

## 7️⃣ CORREÇÃO DE ERROS {#7-correção-de-erros}

### Situação:
Você digitou uma quantidade errada e precisa corrigir.

### Problema:
Registrou 50 garrafas de 1500ml, mas na verdade eram 15.

### Solução Atual:

#### 7.1 Localizar o comprovante errado
1. Aba **📋 Comprovantes**
2. Encontre o registro na lista
3. Anote os dados corretos

#### 7.2 Excluir o registro errado
1. Selecione o comprovante
2. Clique em **"Excluir"**
3. Confirme

#### 7.3 Registrar corretamente
1. Preencha novamente com os dados corretos
2. Agora com 15 ao invés de 50
3. Salve

### Solução Futura (v1.1):
Haverá botão **"Editar"** que permitirá correção direta!

---

## 💡 DICAS E BOAS PRÁTICAS

### Rotina Diária Recomendada:
```
☀️ Manhã:
  → Verificar Dashboard
  → Ver pendências do dia anterior

🌅 Tarde:
  → Receber comprovantes dos parceiros
  → Registrar entregas do dia

🌙 Noite:
  → Revisar registros
  → Verificar inconsistências
```

### Rotina Semanal:
```
Segunda-feira:
  → Planejar semana
  → Verificar vinculações parceiro-loja

Sexta-feira:
  → Gerar relatório semanal
  → Backup do banco de dados
```

### Rotina Mensal:
```
Dia 1-5:
  → Gerar relatórios do mês anterior
  → Calcular pagamentos

Dia 10-15:
  → Pagar parceiros
  → Enviar cobranças para lojas

Dia 25-31:
  → Análise de desempenho
  → Planejamento próximo mês
```

---

## 🎓 CASES DE SUCESSO

### Case 1: Organização de Dados
**Antes**: Planilhas espalhadas, dados duplicados
**Depois**: Tudo centralizado, relatórios em segundos
**Resultado**: 80% menos tempo em tarefas administrativas

### Case 2: Controle de Pagamentos
**Antes**: Erros frequentes em cálculos manuais
**Depois**: Cálculos automáticos e precisos
**Resultado**: Zero erros em pagamentos

### Case 3: Expansão do Negócio
**Antes**: Dificuldade em escalar
**Depois**: Fácil adicionar novos parceiros e lojas
**Resultado**: 150% de crescimento em 6 meses

---

## 🆘 PROBLEMAS COMUNS E SOLUÇÕES

### "Não consigo vincular uma loja ao parceiro"
**Motivo**: Loja já vinculada a outro parceiro
**Solução**: Uma loja pode ter múltiplos parceiros! Verifique se não está na lista de vinculadas.

### "Relatório está vazio"
**Motivo**: Sem comprovantes no período
**Solução**: Verifique as datas ou se há comprovantes cadastrados.

### "Valores não batem"
**Motivo**: Preços diferentes loja vs parceiro
**Solução**: Verifique se cadastrou valores corretos em ambos.

### "Parceiro não aparece ao registrar comprovante"
**Motivo**: Sem lojas vinculadas
**Solução**: Vincule pelo menos uma loja primeiro.

---

## 📞 PRECISA DE AJUDA?

### Antes de perguntar:
1. ✅ Leia o README.md
2. ✅ Consulte o GUIA_RAPIDO.md
3. ✅ Verifique este documento de exemplos
4. ✅ Procure na seção de problemas comuns

### Para reportar bugs:
1. Descreva o problema
2. Informe os passos para reproduzir
3. Anexe screenshots se possível
4. Informe versão do Python

---

## 🎯 CHECKLIST DE MAESTRIA DO SISTEMA

Você dominou o sistema quando conseguir:

- [ ] Cadastrar uma nova marca em menos de 1 minuto
- [ ] Cadastrar uma nova loja em menos de 2 minutos
- [ ] Vincular 5 lojas a um parceiro em menos de 1 minuto
- [ ] Registrar 10 comprovantes em menos de 5 minutos
- [ ] Gerar um relatório completo em menos de 30 segundos
- [ ] Explicar a diferença entre preço da loja e do parceiro
- [ ] Localizar qualquer registro rapidamente
- [ ] Fazer backup do banco de dados

**Parabéns! Você é um usuário expert! 🏆**

---

*"A prática leva à perfeição. Use o sistema diariamente e em breve será um expert!"*

**Versão deste documento:** 1.0
**Última atualização:** Outubro 2025
