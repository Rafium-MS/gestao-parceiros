# Disagua Desktop — Flask + PyQt5 (com Auth, Usuários e Exportações)

## Rodando
```
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python desktop.py
```
Login inicial: **admin / admin** (criado automaticamente).

## Módulos incluídos
- Autenticação (Flask-Login), **/account** para trocar senha.
- **/users** (apenas admin): CRUD de usuários + papéis (admin/operator/viewer).
- Parceiros, Marcas, Lojas, Conexões, Comprovantes (upload), Relatórios (filtros + **export Excel/PDF**).
