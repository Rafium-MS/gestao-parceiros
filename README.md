# Gestão de Parceiros

Aplicação web desenvolvida em Flask para gerenciar parceiros, marcas, lojas e conexões da Diságua. O sistema oferece autenticação com controle de permissões por papel (admin, operator e viewer) e interface web responsiva para cadastro e acompanhamento dos dados principais.

## Funcionalidades
- Autenticação com criação automática do usuário administrador na primeira execução.
- Painel com páginas dedicadas para parceiros, lojas, conexões, comprovantes e relatórios.
- Controle de acesso baseado em papéis com rotas protegidas pelo Flask-Login.
- Upload e armazenamento de imagens de comprovantes em diretório configurável.
- APIs REST para operações CRUD integradas ao banco SQLite `disagua.db` via SQLAlchemy.

## Tecnologias utilizadas
- [Python](https://www.python.org/) 3.11+
- [Flask](https://flask.palletsprojects.com/)
- [Flask-Login](https://flask-login.readthedocs.io/)
- [Flask-CORS](https://flask-cors.readthedocs.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [SQLite](https://www.sqlite.org/)
- HTML, CSS e JavaScript para a camada de apresentação (templates Flask em `templates/`, assets em `static/` e SPA em React dentro de `frontend/`).
- [React](https://react.dev/) + [Vite](https://vitejs.dev/) com [TypeScript](https://www.typescriptlang.org/) para o frontend moderno.
- [ESLint](https://eslint.org/) e [Prettier](https://prettier.io/) para linting e formatação consistentes no frontend.

## Requisitos
1. Python 3.11 ou superior.
2. Pipenv ou `pip` tradicional para instalar dependências listadas em `requirements.txt`.
3. Node.js 18+ e npm para executar o frontend React.
4. (Opcional) Ambiente virtual Python para isolar as dependências do projeto.

## Configuração do ambiente
1. Clone o repositório e acesse a pasta do projeto.
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows PowerShell
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Certifique-se de que o arquivo `disagua.db` está presente ou será criado automaticamente na primeira execução.

## Execução do servidor de desenvolvimento
1. Defina a variável de ambiente `FLASK_APP`:
   ```bash
   export FLASK_APP=app.py        # Linux/macOS
   set FLASK_APP=app.py           # Windows (cmd)
   $env:FLASK_APP = "app.py"      # Windows PowerShell
   ```
2. Inicie o servidor:
   ```bash
   flask run --reload
   ```
3. Acesse `http://localhost:5000` no navegador. O login padrão é `admin` / `admin` (gerado automaticamente se o banco estiver vazio). Altere a senha em "Minha conta" na primeira utilização.

## Frontend React
Um frontend moderno foi configurado dentro do diretório `frontend/` utilizando Vite, React, TypeScript, ESLint, Prettier e aliases de importação (`@/*`).

### Instalação
1. Acesse o diretório do frontend:
   ```bash
   cd frontend
   ```
2. Instale as dependências (gera o arquivo `package-lock.json`):
   ```bash
   npm install
   ```
3. Copie o arquivo de variáveis de ambiente e ajuste conforme necessário:
   ```bash
   cp .env.example .env
   ```
   - `VITE_API_BASE_URL` aponta para a API Flask (por padrão `http://localhost:5000`).
   - Durante o desenvolvimento o servidor Vite também utiliza esse valor para configurar o proxy (`/api -> VITE_API_BASE_URL`).

### Scripts disponíveis
Dentro da pasta `frontend/` execute:
- `npm run dev`: inicia o Vite em modo desenvolvimento (`http://localhost:5173`).
- `npm run build`: gera o build de produção em `frontend/dist`.
- `npm run preview`: simula o build de produção em um servidor local.
- `npm run lint`: executa o ESLint nos arquivos TypeScript/TSX.
- `npm run format`: formata o código com Prettier.

### Integração com Flask
- O build gerado em `frontend/dist` é servido automaticamente pelo Flask quando presente.
- As rotas protegidas (`/`, `/parceiros`, `/lojas`, etc.) entregam o `index.html` do React, mantendo o login obrigatório via Flask-Login.
- Assets gerados pelo Vite (ex.: `/assets/*`, `/favicon.svg`) também são expostos pelo Flask em produção.
- Em desenvolvimento recomenda-se rodar `npm run dev` para hot reload e usar o proxy automático para as rotas `/api`.

### Diretórios gerados automaticamente
- `exports/`: criado na raiz do projeto durante a importação de `config.settings`. Certifique-se de que o usuário do processo possui permissão de escrita, pois os arquivos exportados são gravados nesse local.

## Estrutura principal do projeto
```
.
├── app.py           # Ponto de entrada Flask com rotas, autenticação e configuração do banco
├── config/          # Configurações globais do projeto (ex.: diretórios de exportação)
├── models.py        # Definição das tabelas SQLAlchemy e classes de domínio
├── templates/       # Templates HTML legados da interface web
├── static/          # Arquivos estáticos (CSS, JS, imagens) utilizados pelo backend
├── frontend/        # Aplicação React com Vite + TypeScript
├── disagua.db       # Banco SQLite com os registros da aplicação
├── requirements.txt # Lista de dependências Python
└── desktop.py       # Script auxiliar para execução em modo desktop (PyInstaller ou similares)
```

## Scripts úteis
- `python app.py`: inicia a aplicação diretamente em modo debug, útil para testes rápidos.
- `python desktop.py`: inicializa a aplicação em modo desktop utilizando `pywebview`.

## Testes
O projeto ainda não possui uma suíte de testes automatizados. Recomenda-se configurar testes unitários com `pytest` à medida que novas funcionalidades forem desenvolvidas.

## Contribuição
1. Crie um fork do projeto e uma branch para sua feature/correção.
2. Garanta que o código siga a mesma formatação do restante do projeto.
3. Abra um Pull Request descrevendo as alterações realizadas.

## Licença
Este projeto é de uso interno da Diságua. Consulte os responsáveis antes de reutilizar ou distribuir o código.
