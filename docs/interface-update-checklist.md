# Lista de Atualizações da Interface

Esta lista descreve as atualizações planejadas para modernizar a interface da gestão de parceiros utilizando componentes do shadcn/ui e ícones do Phosphor Icons, garantindo uma experiência responsiva e acessível.

## Ações Prioritárias

- [ ] **Adicionar botões dedicados de importação e exportação**
  - Incluir botões "Importar dados" e "Exportar dados" na barra de ações principal dos módulos de parceiros.
  - Utilizar componentes `Button` do shadcn/ui para manter consistência visual e suporte nativo a estados de carregamento.
  - Associar ícones `UploadSimple` e `DownloadSimple` do Phosphor Icons para reforçar o significado das ações.

- [ ] **Aplicar responsividade com shadcn/ui**
  - Reestruturar os contêineres principais com utilitários responsivos (`flex`, `grid`, `gap`) fornecidos pelo shadcn/ui.
  - Garantir que a tabela de parceiros ofereça rolagem horizontal suave em telas menores e que os botões se reorganizem em pilha.
  - Ajustar tipografia e espaçamento utilizando tokens de design do shadcn/ui para manter legibilidade em diferentes breakpoints.

- [ ] **Integrar Phosphor Icons em elementos de ação**
  - Adicionar ícones relevantes aos botões de criar, importar, exportar e editar parceiros.
  - Garantir contraste adequado entre ícones e fundo, respeitando critérios WCAG.
  - Fornecer rótulos acessíveis (`aria-label`) para todos os botões que utilizarem apenas ícones ou que combinem ícones e texto.

- [ ] **Revisar feedbacks visuais e estados de carregamento**
  - Substituir spinners customizados pelos componentes de `Skeleton` e `Toast` do shadcn/ui, mantendo consistência.
  - Utilizar animações suaves ao abrir modais de importação/exportação para reforçar a percepção de contexto.

- [ ] **Documentar boas práticas de uso**
  - Atualizar o guia interno de estilo com exemplos dos novos componentes shadcn/ui.
  - Registrar no handbook de design as combinações de ícones Phosphor aprovadas para ações críticas.

## Considerações Técnicas

- Instalar dependências necessárias (`@phosphor-icons/react` e `shadcn/ui`), configurando tree-shaking para reduzir o impacto no bundle.
- Centralizar tokens de cor e espaçamento compartilhados em um tema único para facilitar personalização futura.
- Garantir que as mudanças sejam cobertas por testes de regressão visual ou snapshots, quando aplicável.

## Métricas de Sucesso

- Redução de tempo médio para executar operações de importação/exportação graças à descoberta facilitada dos botões.
- Melhor pontuação em auditorias Lighthouse para dispositivos móveis (alvo ≥ 90 em "Best Practices" e "Accessibility").
- Feedback positivo de usuários piloto indicando maior clareza nos fluxos de importação e exportação.
