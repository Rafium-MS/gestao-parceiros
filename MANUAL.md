  - python-dateutil (para manipulação de datas)
  - tkcalendar (widget de calendário)
  - pytesseract (para leitura OCR)
  - pdf2image (para converter PDFs em imagens)
  - Tesseract OCR instalado e configurado no `PATH`# Manual do Usuário
# Sistema de Gestão de Parceiros
**Versão 1.0**

![Logo do Sistema](placeholder_for_logo.png)

---

## Sumário

1. [Introdução](#1-introdução)
2. [Requisitos do Sistema](#2-requisitos-do-sistema)
3. [Instalação](#3-instalação)
4. [Iniciando o Sistema](#4-iniciando-o-sistema)
5. [Visão Geral da Interface](#5-visão-geral-da-interface)
6. [Módulos do Sistema](#6-módulos-do-sistema)
   1. [Cadastro de Parceiros](#61-cadastro-de-parceiros)
   2. [Cadastro de Lojas](#62-cadastro-de-lojas)
   3. [Comprovantes de Entrega](#63-comprovantes-de-entrega)
   4. [Associações](#64-associações)
   5. [Relatórios](#65-relatórios)
7. [Funções Administrativas](#7-funções-administrativas)
   1. [Backup do Banco de Dados](#71-backup-do-banco-de-dados)
   2. [Restauração de Backup](#72-restauração-de-backup)
8. [Solução de Problemas](#8-solução-de-problemas)
9. [Perguntas Frequentes](#9-perguntas-frequentes)
10. [Suporte](#10-suporte)

---

## 1. Introdução

O **Sistema de Gestão de Parceiros** é uma aplicação desktop desenvolvida para facilitar o gerenciamento de parceiros, lojas, comprovantes de entregas e geração de relatórios. Com interface intuitiva e recursos abrangentes, o sistema permite o controle completo do fluxo de entregas desde o cadastro de parceiros até a geração de relatórios.

### Principais Funcionalidades:

- Cadastro e gerenciamento de parceiros/entregadores
- Cadastro e gerenciamento de lojas atendidas
- Upload e visualização de comprovantes de entrega
- Associação entre parceiros e lojas
- Geração de relatórios por parceiro, loja e período
- Sistema de backup e restauração de dados

---

## 2. Requisitos do Sistema

Para executar o Sistema de Gestão de Parceiros, seu computador deve atender aos seguintes requisitos:

### Requisitos de Hardware:
- Processador: 1.5 GHz ou superior
- Memória RAM: 2GB ou superior
- Espaço em disco: 500MB disponíveis
- Resolução de tela: Mínimo 1024x768

### Requisitos de Software:
- Sistema Operacional: Windows 7/8/10/11, macOS 10.13+, ou Linux
- Python 3.7 ou superior
- Bibliotecas Python listadas em `requirements.txt`:
  - Pillow (para processamento de imagens)
  - ttkthemes (para temas da interface)
  - pandas (para manipulação de dados)
  - openpyxl (para exportação para Excel)
  - reportlab (para geração de PDF)
  - xlsxwriter (para formatação avançada em Excel)
  - validate-docbr (para validação de documentos brasileiros)
  - email-validator (para validação de e-mails)
  - python-dateutil (para manipulação de datas)
  - tkcalendar (widget de calendário)
  - pytesseract (para leitura OCR)
  - pdf2image (para converter PDFs em imagens)
  - Tesseract OCR instalado e configurado no `PATH`
  - pytesseract (para leitura OCR)
  - pdf2image (para converter PDFs em imagens)

---

## 3. Instalação

### Instalação Padrão

1. **Requisitos Prévios**:
   - Certifique-se de ter o Python 3.7 ou superior instalado
   - Verifique a instalação com o comando: `python --version`

2. **Download do Sistema**:
   - Faça o download do pacote de instalação
   - Extraia o arquivo ZIP em uma pasta de sua preferência

3. **Instalação das Dependências**:
   - Abra o terminal ou prompt de comando
   - Navegue até a pasta do sistema: `cd caminho/para/sistema-gestao-Parceiros`
   - Recomendamos criar um ambiente virtual:
     ```
     python -m venv venv
     
     # No Windows
     venv\Scripts\activate
     
     # No Linux/macOS
     source venv/bin/activate
     ```
   - Instale as dependências:
     ```
     pip install -r requirements.txt
     ```

4. **Primeira Execução**:
   - Execute o aplicativo com: `python app.py`
   - O sistema irá criar automaticamente os diretórios necessários e o banco de dados

---

## 4. Iniciando o Sistema

### Inicialização

1. Navegue até a pasta onde o sistema foi instalado
2. Execute o arquivo principal:
   ```
   python app.py
   ```
3. Na primeira execução, o sistema criará:
   - Banco de dados SQLite
   - Diretório para armazenamento de comprovantes
   - Arquivos de configuração
   - Diretório para logs

### Configuração Inicial

O arquivo `config.ini` contém as configurações do sistema e é criado automaticamente na primeira execução. Você pode editar este arquivo para personalizar:

- Localização do banco de dados
- Diretório para armazenamento de comprovantes
- Tipos de arquivos permitidos para comprovantes
- Configurações de logs

---

## 5. Visão Geral da Interface

A interface do Sistema de Gestão de Parceiros é organizada em abas para fácil navegação:

![Interface Principal](placeholder_for_interface.png)

### Barra de Menu

- **Arquivo**: Opções para backup, restauração e saída do sistema
- **Cadastros**: Acesso rápido aos módulos de cadastro
- **Relatórios**: Acesso às opções de relatórios
- **Ajuda**: Acesso ao manual e informações sobre o sistema

### Área Principal (Notebook)

Organizada em cinco abas principais:
1. **Parceiros**: Gerenciamento de parceiros/entregadores
2. **Lojas**: Gerenciamento de lojas atendidas
3. **Comprovantes**: Registro e visualização de comprovantes de entrega
4. **Associações**: Gerenciamento das relações entre parceiros e lojas
5. **Relatórios**: Geração e exportação de relatórios

### Atalhos de Teclado

O sistema oferece diversos atalhos para agilizar o uso:
- **Ctrl+1** a **Ctrl+5**: Alternar entre as abas 1 a 5
- **Ctrl+B**: Abrir a função de backup
- **Ctrl+R**: Abrir a função de restauração
- **Ctrl+Q**: Sair do sistema
- **F1**: Abrir este manual de ajuda
- **Esc**: Limpar formulário atual

---

## 6. Módulos do Sistema

### 6.1 Cadastro de Parceiros

A tela de Parceiros permite gerenciar todos os entregadores/parceiros do sistema.

![Tela de Parceiros](placeholder_for_parceiros.png)

#### Funcionalidades

- **Adicionar Parceiro**:
  1. Preencha os campos do formulário (Nome é obrigatório)
  2. Clique no botão "Adicionar"
  3. O sistema valida os dados e adiciona o parceiro

- **Editar Parceiro**:
  1. Selecione um parceiro na lista
  2. Os dados serão carregados no formulário
  3. Altere as informações necessárias
  4. Clique em "Salvar Edição"

- **Excluir Parceiro**:
  1. Selecione um parceiro na lista
  2. Clique em "Excluir"
  3. Confirme a exclusão quando solicitado
  
  > **Atenção**: A exclusão de um parceiro remove também todas as associações e comprovantes vinculados a ele.

- **Pesquisar Parceiro**:
  1. Digite o termo de busca no campo "Pesquisar"
  2. Clique em "Buscar" ou pressione Enter
  3. A lista será filtrada de acordo com o termo pesquisado
  4. Para ver todos os parceiros novamente, clique em "Limpar"

#### Campos do Cadastro

- **Nome**: Nome completo do parceiro (obrigatório)
- **CPF**: CPF do parceiro (opcional, mas validado se preenchido)
- **Telefone**: Número de telefone para contato
- **Email**: Endereço de e-mail (validado se preenchido)
- **Endereço**: Endereço completo do parceiro

---

### 6.2 Cadastro de Lojas

A tela de Lojas permite gerenciar todos os estabelecimentos atendidos.

![Tela de Lojas](placeholder_for_lojas.png)

#### Funcionalidades

- **Adicionar Loja**:
  1. Preencha os campos do formulário (Nome é obrigatório)
  2. Clique no botão "Adicionar"
  3. O sistema valida os dados e adiciona a loja

- **Editar Loja**:
  1. Selecione uma loja na lista
  2. Os dados serão carregados no formulário
  3. Altere as informações necessárias
  4. Clique em "Salvar Edição"

- **Excluir Loja**:
  1. Selecione uma loja na lista
  2. Clique em "Excluir"
  3. Confirme a exclusão quando solicitado
  
  > **Atenção**: A exclusão de uma loja remove também todas as associações e comprovantes vinculados a ela.

- **Pesquisar Loja**:
  1. Digite o termo de busca no campo "Pesquisar"
  2. Clique em "Buscar" ou pressione Enter
  3. A lista será filtrada de acordo com o termo pesquisado
  4. Para ver todas as lojas novamente, clique em "Limpar"

#### Campos do Cadastro

- **Nome**: Nome da loja (obrigatório)
- **CNPJ**: CNPJ da loja (opcional, mas validado se preenchido)
- **Telefone**: Número de telefone para contato
- **Email**: Endereço de e-mail (validado se preenchido)
- **Endereço**: Endereço completo da loja
- **Contato**: Nome da pessoa de contato na loja

---

### 6.3 Comprovantes de Entrega

A tela de Comprovantes permite registrar e gerenciar os comprovantes de entrega.

![Tela de Comprovantes](placeholder_for_comprovantes.png)

#### Funcionalidades

- **Adicionar Comprovante**:
  1. Selecione um parceiro (obrigatório)
  2. Selecione uma loja (obrigatório)
  3. Escolha a data da entrega (obrigatório)
  4. Clique em "Selecionar" para escolher o arquivo do comprovante
  5. Adicione observações se necessário
  6. Clique em "Adicionar"

- **Visualizar Comprovante**:
  1. Selecione um comprovante na lista
  2. Clique em "Visualizar"
  3. O sistema abrirá o arquivo com o programa padrão do seu sistema

- **Excluir Comprovante**:
  1. Selecione um comprovante na lista
  2. Clique em "Excluir"
  3. Confirme a exclusão quando solicitado

- **Pesquisar Comprovante**:
  1. Selecione um filtro (Parceiro, Loja ou Data)
  2. Digite ou selecione o valor a ser pesquisado
  3. Clique em "Buscar"
  4. Para ver todos os comprovantes novamente, clique em "Limpar"

#### Campos do Cadastro

- **Parceiro**: Seleção do parceiro responsável pela entrega (obrigatório)
- **Loja**: Seleção da loja onde foi realizada a entrega (obrigatório)
- **Data**: Data em que a entrega foi realizada (obrigatório)
- **Arquivo**: Caminho para o arquivo do comprovante (imagem ou PDF)
- **Observações**: Informações adicionais sobre a entrega

> **Formatos Permitidos**: Por padrão, o sistema aceita arquivos nos formatos PNG, JPG, JPEG e PDF.

---

### 6.4 Associações

A tela de Associações permite gerenciar as relações entre parceiros e lojas.

![Tela de Associações](placeholder_for_associacoes.png)

#### Funcionalidades

- **Criar Associação**:
  1. Selecione um parceiro (obrigatório)
  2. Selecione uma loja (obrigatório)
  3. Escolha o status da associação (Ativo, Inativo, Pendente)
  4. Clique em "Associar"

- **Editar Associação**:
  1. Selecione uma associação na lista
  2. Os dados serão carregados no formulário
  3. Altere o status conforme necessário
  4. Clique em "Salvar Edição"

- **Remover Associação**:
  1. Selecione uma associação na lista
  2. Clique em "Remover"
  3. Confirme a remoção quando solicitado

- **Filtrar Associações**:
  1. Selecione um filtro (Parceiro, Loja ou Status)
  2. Selecione o valor a ser filtrado
  3. Clique em "Filtrar"
  4. Para ver todas as associações novamente, clique em "Limpar Filtro"

#### Campos do Cadastro

- **Parceiro**: Seleção do parceiro (obrigatório)
- **Loja**: Seleção da loja (obrigatório)
- **Status**: Estado atual da associação (Ativo, Inativo, Pendente)
- **Data de Associação**: Data em que a associação foi criada (preenchida automaticamente)

> **Importante**: Uma associação é necessária para registrar comprovantes. Na tela de Comprovantes, só serão exibidas lojas associadas ao parceiro selecionado.

---

### 6.5 Relatórios

A tela de Relatórios permite gerar e exportar relatórios diversos sobre as entregas.

![Tela de Relatórios](placeholder_for_relatorios.png)

#### Tipos de Relatórios

- **Entregas por Parceiro**:
  1. Selecione "Entregas por Parceiro" na caixa de seleção
  2. Escolha o parceiro desejado
  3. Defina o período (opcional)
  4. Clique em "Gerar Relatório"

- **Entregas por Loja**:
  1. Selecione "Entregas por Loja" na caixa de seleção
  2. Escolha a loja desejada
  3. Defina o período (opcional)
  4. Clique em "Gerar Relatório"

- **Entregas por Período**:
  1. Selecione "Entregas por Período" na caixa de seleção
  2. Defina o período (data inicial e final)
  3. Clique em "Gerar Relatório"

#### Exportação de Relatórios

Após gerar um relatório, você pode exportá-lo em diferentes formatos:

- **Exportar para Excel**:
  1. Clique no botão "Exportar para Excel"
  2. Escolha o local onde deseja salvar o arquivo
  3. O sistema criará uma planilha formatada com os dados do relatório

- **Exportar para PDF**:
  1. Clique no botão "Exportar para PDF"
  2. Escolha o local onde deseja salvar o arquivo
  3. O sistema criará um documento PDF formatado com os dados do relatório

> **Dica**: Os relatórios exportados incluem cabeçalho, rodapé e formatação profissional, prontos para impressão ou compartilhamento.

---

## 7. Funções Administrativas

### 7.1 Backup do Banco de Dados

O sistema oferece uma função para criar cópias de segurança do banco de dados.

#### Como Realizar um Backup

1. No menu principal, clique em **Arquivo > Backup do Banco de Dados**
2. Ou use o atalho **Ctrl+B**
3. Escolha o local onde deseja salvar o arquivo de backup
4. O sistema criará uma cópia completa do banco de dados
5. Uma mensagem de confirmação será exibida após a conclusão

> **Recomendação**: Realize backups regularmente, especialmente antes de atualizações do sistema ou após cadastrar muitos dados.

### 7.2 Restauração de Backup

Caso seja necessário, você pode restaurar o sistema a partir de um backup anterior.

#### Como Restaurar um Backup

1. No menu principal, clique em **Arquivo > Restaurar Backup**
2. Ou use o atalho **Ctrl+R**
3. Confirme que deseja prosseguir com a restauração
4. Selecione o arquivo de backup (.db) que deseja restaurar
5. O sistema substituirá o banco de dados atual pelo backup selecionado
6. Após a conclusão, o sistema será reiniciado para aplicar as alterações

> **Atenção**: A restauração substituirá TODOS os dados atuais pelos dados do backup. Recomenda-se fazer um backup do estado atual antes de prosseguir.

---

## 8. Solução de Problemas

### Problemas Comuns e Soluções

#### Erro ao Iniciar o Sistema

**Problema**: O sistema não inicia ou apresenta erro ao abrir.  
**Solução**:
1. Verifique se todas as dependências estão instaladas
2. Confirme que seu Python está na versão 3.7 ou superior
3. Verifique se o arquivo `config.ini` não está corrompido
4. Se o problema persistir, tente reinstalar o sistema

#### Não é Possível Visualizar Comprovantes

**Problema**: Ao clicar em "Visualizar", o comprovante não abre.  
**Solução**:
1. Verifique se o arquivo existe na pasta de comprovantes
2. Confirme se você tem um aplicativo padrão para abrir o tipo de arquivo
3. Verifique se o caminho do arquivo está correto no banco de dados

#### Erro ao Gerar Relatórios

**Problema**: Ocorre um erro ao tentar gerar ou exportar relatórios.  
**Solução**:
1. Verifique se as bibliotecas pandas, openpyxl e reportlab estão instaladas
2. Confirme se existe pelo menos um registro que atenda aos filtros do relatório
3. Verifique se você tem permissões para salvar arquivos no local escolhido

#### Banco de Dados Corrompido

**Problema**: Mensagens de erro indicando problemas com o banco de dados.  
**Solução**:
1. Restaure um backup recente
2. Se não houver backup, crie uma cópia do arquivo .db atual
3. Use ferramentas de recuperação de SQLite se necessário

---

## 9. Perguntas Frequentes

### Gerais

**P: Posso usar o sistema em vários computadores?**  
R: Sim, o sistema pode ser instalado em vários computadores. No entanto, o banco de dados será local em cada instalação. Para compartilhar dados, você precisará realizar backups e restaurá-los nas outras instalações.

**P: O sistema funciona em rede?**  
R: Esta versão não possui suporte nativo para uso em rede com banco de dados compartilhado. Cada instalação utiliza um banco de dados local.

**P: É possível personalizar a interface do sistema?**  
R: Sim, o sistema utiliza o framework ttkthemes que permite alteração de temas. Você pode editar o arquivo `config.ini` para personalizar alguns aspectos da interface.

### Cadastros

**P: Existe limite para o número de parceiros ou lojas?**  
R: Não, o sistema não possui limite para a quantidade de registros, sendo limitado apenas pelos recursos do seu computador.

**P: Os parceiros podem ter acesso ao sistema?**  
R: Não, esta versão do sistema não possui gerenciamento de usuários ou níveis de acesso diferenciados.

### Comprovantes

**P: Qual o tamanho máximo para arquivos de comprovantes?**  
R: Recomenda-se arquivos com até 10MB para melhor desempenho, embora não haja um limite rigoroso definido no sistema.

**P: Quais formatos de arquivo são aceitos para comprovantes?**  
R: Por padrão, o sistema aceita arquivos PNG, JPG, JPEG e PDF. Você pode editar esta configuração no arquivo `config.ini`.

### Backup e Restauração

**P: Com qual frequência devo fazer backup?**  
R: Recomenda-se fazer backup diariamente, ou pelo menos após cada sessão de uso intensivo do sistema.

**P: Os arquivos de comprovantes são incluídos no backup?**  
R: Não, o backup inclui apenas o banco de dados. Os arquivos de comprovantes devem ser copiados separadamente.

---

## 10. Suporte

### Canais de Atendimento

Para obter suporte técnico ou esclarecer dúvidas sobre o Sistema de Gestão de Parceiros, utilize os seguintes canais:

- **E-mail**: 
- **Telefone**: 
- **Site**: 

### Atualizações

Verificações de atualização não estão incluídas nesta versão do sistema. Para garantir que você está usando a versão mais recente:

1. Visite o site do sistema periodicamente
2. Entre em contato com o suporte para informações sobre atualizações
3. Antes de atualizar, sempre faça um backup completo dos seus dados

---

### Desenvolvido por Macete System

*© 2025 - Sistema de Gestão de Parceiros - Todos os direitos reservados*

*Versão deste manual: 1.0 - Abril/2025*
