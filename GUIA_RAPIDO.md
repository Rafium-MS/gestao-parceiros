# 🚀 GUIA RÁPIDO - Sistema de Entregas de Água

## 📦 INSTALAÇÃO RÁPIDA

### Windows
1. Baixe os arquivos
2. Abra o terminal (cmd ou PowerShell) na pasta dos arquivos
3. Execute:
```
python iniciar.py
```

### Linux / Mac
1. Baixe os arquivos
2. Abra o terminal na pasta dos arquivos
3. Execute:
```
python3 iniciar.py
```

## 🎯 PRIMEIRO USO

Quando executar pela primeira vez, escolha a opção **1** para criar dados de teste.
Isso vai criar:
- 2 Marcas de exemplo
- 4 Lojas
- 2 Parceiros
- 4 Comprovantes de entrega

Assim você pode explorar todas as funcionalidades do sistema!

## 🗺️ NAVEGAÇÃO RÁPIDA

### Dashboard (📊)
Veja resumo geral do sistema:
- Quantos parceiros enviaram comprovantes
- Percentual de preenchimento
- Total de lojas cadastradas

### Marcas (🏢)
1. Preencha nome e código
2. Clique em "Salvar Marca"

### Lojas (🏪)
1. Selecione a marca
2. Preencha dados e valores
3. Clique em "Salvar Loja"

### Parceiros (🚚)
**Aba "Cadastro de Parceiro":**
1. Preencha dados do parceiro
2. Informe valores que ele receberá
3. Clique em "Salvar Parceiro"

**Aba "Lojas do Parceiro":**
1. Selecione o parceiro
2. Use as setas → para adicionar lojas
3. Use as setas ← para remover lojas

### Comprovantes (📋)
1. Selecione parceiro (só aparecem lojas vinculadas a ele)
2. Selecione loja
3. Informe data e quantidades
4. Opcional: anexe arquivo
5. Clique em "Salvar Comprovante"

### Relatórios (📊)
**Por Marca:**
- Mostra quanto a marca cobra das lojas
- Use filtros de data se necessário
- Total geral aparece no rodapé

**Por Parceiro:**
- Mostra quanto o parceiro vai receber
- Use filtros de data se necessário
- Total a receber aparece no rodapé

## 💡 DICAS IMPORTANTES

### Diferença de Preços
- **Valores da Loja**: O que a marca cobra do cliente final
- **Valores do Parceiro**: O que você paga ao entregador
- A diferença entre eles é sua margem!

### Formato de Data
Use sempre: `DD/MM/AAAA`
Exemplo: `24/10/2025`

### Backup
O sistema cria um arquivo `entregas.db` na mesma pasta.
**FAÇA BACKUP REGULAR DESTE ARQUIVO!**
Ele contém todos os seus dados.

### Vinculação de Lojas
Antes de registrar comprovantes:
1. Cadastre parceiros
2. Vincule lojas aos parceiros (aba "Lojas do Parceiro")
3. Só então registre comprovantes

### Exportação (Em desenvolvimento)
A exportação para Excel está planejada para próxima versão.

## 🔧 RESOLUÇÃO DE PROBLEMAS

### "Código Disagua já cadastrado"
- Cada marca e loja precisa de código único
- Verifique se não está duplicado

### "Selecione uma marca/parceiro"
- Certifique-se de ter cadastrado antes
- Clique no dropdown para selecionar

### Loja não aparece ao registrar comprovante
- Verifique se a loja está vinculada ao parceiro
- Vá em Parceiros → Lojas do Parceiro

### Banco de dados travado
- Feche todas as janelas do sistema
- Reinicie o sistema

## 📞 PRÓXIMOS PASSOS

Após dominar o sistema básico:

1. **Exportação para Excel**: Implementar botões de exportação
2. **Gráficos**: Adicionar visualizações gráficas
3. **Backup Automático**: Sistema de backup programado
4. **Multiusuário**: Migrar para PostgreSQL/MySQL
5. **Sistema Web**: Versão acessível via navegador

## 🎓 FLUXO DE TRABALHO RECOMENDADO

### Configuração Inicial (1ª vez):
1. Cadastrar todas as marcas
2. Cadastrar todas as lojas
3. Cadastrar todos os parceiros
4. Vincular lojas aos parceiros

### Uso Diário:
1. Receber comprovantes dos parceiros
2. Registrar na aba "Comprovantes"
3. Verificar Dashboard
4. Gerar relatórios quando necessário

### Uso Mensal:
1. Gerar relatório por parceiro (para pagamento)
2. Gerar relatório por marca (para faturamento)
3. Fazer backup do arquivo entregas.db

## ✅ CHECKLIST DE INÍCIO

- [ ] Sistema instalado e funcionando
- [ ] Marcas cadastradas
- [ ] Lojas cadastradas
- [ ] Parceiros cadastrados
- [ ] Lojas vinculadas aos parceiros
- [ ] Primeiro comprovante registrado
- [ ] Dashboard visualizado
- [ ] Primeiro relatório gerado
- [ ] Backup do banco de dados

---

**Desenvolvido especialmente para gerenciamento de entregas de água mineral**

Para suporte ou melhorias, mantenha este documento junto com os arquivos do sistema.
