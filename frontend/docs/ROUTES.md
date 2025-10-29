# Hierarquia de rotas do frontend

A tabela abaixo documenta as rotas disponíveis na aplicação React e os componentes responsáveis pelo render do
conteúdo. Os caminhos fazem referência ao diretório `src/`.

| Caminho | Tipo | Layout | Componente | Descrição |
| --- | --- | --- | --- | --- |
| `/login` | Pública | — | `pages/LoginPage.tsx` | Fluxo de autenticação inicial e recuperação de sessão. |
| `/conectar` | Pública | `layouts/AppLayout.tsx` | `pages/ConnectPage.tsx` | Página institucional para integração entre parceiros e lojas. |
| `/` | Privada | `layouts/AppLayout.tsx` | `pages/DashboardPage.tsx` | Dashboard com os atalhos principais do sistema. |
| `/parceiros` | Privada | `layouts/AppLayout.tsx` | `pages/PartnersPage.tsx` | Área de gestão de parceiros. |
| `/lojas` | Privada | `layouts/AppLayout.tsx` | `pages/StoresPage.tsx` | Cadastro e manutenção de marcas/lojas. |
| `/comprovantes` | Privada | `layouts/AppLayout.tsx` | `pages/ReceiptsPage.tsx` | Upload e auditoria de comprovantes financeiros. |
| `/relatorios` | Privada | `layouts/AppLayout.tsx` | `pages/ReportsPage.tsx` | Visualização de relatórios e métricas estratégicas. |
| `/usuarios` | Privada | `layouts/AppLayout.tsx` | `pages/UsersPage.tsx` | Administração de usuários e permissões. |
| `/account` | Privada | `layouts/AppLayout.tsx` | `pages/AccountPage.tsx` | Ajustes de conta e redefinição de senha. |

## Componentes auxiliares

- `contexts/AuthContext.tsx`: provê o estado de autenticação, além de funções utilitárias `login` e `logout`.
- `routes/ProtectedRoute.tsx`: guardião responsável por redirecionar usuários não autenticados para `/login`.
- `components/TopNav.tsx`: navegação principal reaproveitada das páginas legadas do Flask.

Os componentes listados formam a base para evolução incremental das features herdadas dos templates Jinja, mantendo a
estrutura pronta para integração com a API Flask.
