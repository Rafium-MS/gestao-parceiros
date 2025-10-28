# Disagua Desktop (Python + Flask + PyQt5)

Este MVP transforma seus HTMLs em um app desktop:
- **Flask** serve as páginas e expõe uma **API REST**.
- **SQLite** armazena os dados.
- **PyQt5 + QtWebEngine** abre o app como janela desktop.

## Como rodar (Windows/Mac/Linux)

1) Crie e ative um ambiente virtual (opcional, mas recomendado)
```
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

2) Instale as dependências
```
pip install -r requirements.txt
```

> Observação: No Linux, pode ser necessário instalar pacotes do Qt/WebEngine via gerenciador do sistema.

3) Inicie o app desktop
```
python desktop.py
```

O aplicativo abrirá uma janela carregando `http://127.0.0.1:5000/`.

## APIs principais (MVP)
- `GET /api/partners` — lista parceiros
- `POST /api/partners` — cria parceiro (JSON)
- `GET /api/brands` — lista marcas
- `POST /api/brands` — cria marca
- `GET /api/stores` — lista lojas
- `POST /api/stores` — cria loja
- `GET /api/connections` — lista conexões
- `POST /api/connections` — cria conexão `{ partner_id, store_id }`
- `GET /api/report-data` — filtra relatórios por `startDate`, `endDate`, `marca`
- `POST /api/report-data/seed?n=100` — gera registros de exemplo
- `POST /api/upload` — upload de imagens de comprovantes (`multipart/form-data` com `files[]` e `brand_id`)

## Próximos passos
- Substituir o uso de `localStorage` nos HTMLs por chamadas `fetch` à API acima.
- Criar endpoints **PUT/DELETE** para edição/remoção.
- Mapear os formulários atuais para `fetch('/api/...', { method: 'POST', body: JSON })`.
- Implementar autenticação simples (e.g., `Flask-Login`).
- Exportações para Excel/PDF (usar `pandas`/`openpyxl`/`reportlab`/`jsPDF` conforme preferência).
