# Auditoria de assets legados

Este projeto possuía arquivos estáticos servidos diretamente pelo Flask no diretório `static/`. A tabela abaixo documenta o que será reaproveitado na migração para o frontend em React.

| Caminho | Tipo | Situação | Observações |
| --- | --- | --- | --- |
| `static/style.css` | CSS global | Reescrito | Os estilos foram incorporados ao tema do frontend (`frontend/src/styles/theme.css` e módulos CSS dos componentes). Mantemos o arquivo apenas para o legado até a conclusão total da migração. |

Atualmente não existem arquivos JavaScript ou imagens adicionais em `static/`. Novos assets compartilhados devem ser adicionados ao diretório `frontend/public/` (para arquivos estáticos públicos) ou importados diretamente nos componentes React quando fizer sentido para o bundler (Vite).

## Orientações para novos assets

- Fontes web devem ser declaradas em `frontend/index.html` utilizando `link rel="preconnect"`/`link rel="stylesheet"` ou importadas via CSS.
- Ícones e imagens utilizadas por componentes React devem ser armazenadas em `frontend/public/` quando forem referenciadas por URL absoluta ou importadas de `frontend/src/assets/` quando precisarem participar do pipeline do bundler.
- Scripts inline nos templates Jinja foram substituídos por componentes React e hooks dedicados para manter o encapsulamento e a reutilização.
