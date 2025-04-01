# Estrutura do Projeto - Sistema de Gestão de Entregas

## Arquivos Principais
- `app.py` - Ponto de entrada principal da aplicação
- `config.ini` - Arquivo de configuração do sistema
- `README.md` - Documentação do projeto
- `requirements.txt` - Dependências do projeto

## Diretórios e Módulos

### database/
Contém todos os componentes relacionados ao banco de dados.
- `__init__.py` - Torna o diretório um pacote Python
- `db_manager.py` - Gerencia conexões e operações do banco de dados
- `queries.py` - Armazena consultas SQL para reuso

### models/
Implementa o modelo de dados em formato orientado a objetos.
- `__init__.py` - Torna o diretório um pacote Python
- `parceiro.py` - Modelo de dados para Parceiros
- `loja.py` - Modelo de dados para Lojas
- `comprovante.py` - Modelo de dados para Comprovantes
- `associacao.py` - Modelo de dados para Associações

### views/
Contém todas as interfaces gráficas do usuário.
- `__init__.py` - Torna o diretório um pacote Python
- `main_window.py` - Janela principal da aplicação
- `parceiro_view.py` - Interface para gerenciamento de parceiros
- `loja_view.py` - Interface para gerenciamento de lojas
- `comprovante_view.py` - Interface para gerenciamento de comprovantes
- `associacao_view.py` - Interface para gerenciamento de associações
- `relatorio_view.py` - Interface para geração de relatórios

### controllers/
Implementa a lógica de negócios e conecta as views aos models.
- `__init__.py` - Torna o diretório um pacote Python
- `parceiro_controller.py` - Controlador para operações de parceiros
- `loja_controller.py` - Controlador para operações de lojas
- `comprovante_controller.py` - Controlador para operações de comprovantes
- `associacao_controller.py` - Controlador para operações de associações
- `relatorio_controller.py` - Controlador para operações de relatórios

### resources/
Recursos estáticos usados pela aplicação.
- `icons/` - Ícones para a interface gráfica
- `images/` - Imagens para a interface gráfica
- `styles/` - Arquivos de estilo (se aplicável)

### utils/
Utilitários e funções auxiliares.
- `__init__.py` - Torna o diretório um pacote Python
- `validators.py` - Funções para validação de dados (CPF, CNPJ, etc.)
- `formatters.py` - Funções para formatação de dados
- `logger.py` - Sistema de logging da aplicação
- `backup_utils.py` - Utilitários para backup e restauração de dados
- `export_utils.py` - Funções para exportação de dados (PDF, Excel, etc.)

### comprovantes/
Diretório para armazenar os arquivos de comprovantes enviados.
- Este diretório é criado automaticamente pela aplicação se não existir