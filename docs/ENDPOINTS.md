# Mapeamento de endpoints principais

A API definida em [`app.py`](../app.py) expõe os seguintes pontos relevantes para autenticação, gestão de parceiros, lojas, usuários e relatórios.

| Recurso | Método | Rota | Descrição | Permissões |
| --- | --- | --- | --- | --- |
| Autenticação | `POST` | `/api/login` | Valida credenciais, cria a sessão e retorna o usuário autenticado. | Pública |
| Autenticação | `POST` | `/api/logout` | Finaliza a sessão do usuário atual. | Usuário autenticado |
| Sessão | `GET` | `/api/me` | Retorna dados do usuário autenticado. | Usuário autenticado |
| Parceiros | `GET` | `/api/partners` | Lista parceiros com metadados operacionais e financeiros. | Usuário autenticado |
| Parceiros | `POST` | `/api/partners` | Cria um novo parceiro. | Operador ou administrador |
| Parceiros | `PUT` | `/api/partners/<id>` | Atualiza campos de um parceiro existente. | Operador ou administrador |
| Parceiros | `DELETE` | `/api/partners/<id>` | Remove um parceiro. | Operador ou administrador |
| Marcas | `GET` | `/api/brands` | Lista marcas com contagem de lojas. | Usuário autenticado |
| Marcas | `POST` | `/api/brands` | Cadastra uma nova marca. | Operador ou administrador |
| Marcas | `PUT` | `/api/brands/<id>` | Atualiza dados da marca. | Operador ou administrador |
| Marcas | `DELETE` | `/api/brands/<id>` | Remove uma marca existente. | Operador ou administrador |
| Lojas | `GET` | `/api/stores` | Lista lojas com dados comerciais consolidados. | Usuário autenticado |
| Lojas | `POST` | `/api/stores` | Cria uma nova loja vinculada a uma marca. | Operador ou administrador |
| Lojas | `PUT` | `/api/stores/<id>` | Atualiza uma loja. | Operador ou administrador |
| Lojas | `DELETE` | `/api/stores/<id>` | Remove uma loja. | Operador ou administrador |
| Relatórios | `GET` | `/api/report-data` | Consulta registros históricos de desempenho para composição dos relatórios. | Usuário autenticado |
| Relatórios | `GET` | `/api/report-data/export` | Exporta os dados filtrados em Excel/CSV. | Usuário autenticado |
| Relatórios | `POST` | `/api/report-data/seed` | Popula dados de relatório para testes. | Operador ou administrador |
| Usuários | `GET` | `/api/users` | Lista contas cadastradas. | Administrador |
| Usuários | `POST` | `/api/users` | Cria usuário com papel e status definidos. | Administrador |
| Usuários | `PUT` | `/api/users/<id>` | Atualiza papel e status de um usuário. | Administrador |
| Usuários | `PUT` | `/api/users/<id>/password` | Atualiza a senha de um usuário. | Administrador |
| Usuários | `DELETE` | `/api/users/<id>` | Remove um usuário (exceto o administrador padrão). | Administrador |

Todas as respostas seguem o padrão JSON `{ "data": ... }` em caso de sucesso ou `{ "error": { "message": "..." } }` em caso de falha. Durante o desenvolvimento o backend está configurado com CORS (origens padrão `http://localhost:5173` e `http://127.0.0.1:5173`) e suporta cookies de sessão via `supports_credentials`.
