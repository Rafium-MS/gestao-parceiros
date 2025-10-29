# Fluxo de deploy

Este documento descreve o processo padronizado de publicação da aplicação Gestão de Parceiros
nos ambientes de **staging** e **produção**, bem como as estratégias de *cache busting* adotadas
para garantir que os assets estáticos sejam atualizados corretamente após cada release.

## Visão geral

- A base da aplicação é composta por um backend Flask (`app.py`) e um frontend React compilado
  pelo Vite (`frontend/`).
- Os ambientes recebem o build a partir do repositório principal via GitHub Actions.
- O deploy é disparado manualmente ou por *merge* na branch principal, conforme detalhado nas
  seções a seguir.

## Pré-requisitos

1. **Variáveis de ambiente** configuradas via secrets no provedor (Railway/Render ou VPS). As
   principais variáveis são `FLASK_ENV`, `DATABASE_URL`, `SECRET_KEY`, `VITE_API_BASE_URL` e as
   credenciais do bucket de armazenamento quando aplicável.
2. **Runner do GitHub Actions** com permissões de leitura/escrita no registro de contêiner e na
   infraestrutura de destino (SSH ou API de deploy).
3. **Banco de dados** provisionado previamente e migrado para a versão esperada da aplicação.

## Pipeline de deploy

O workflow principal está definido em `.github/workflows/deploy.yml` (nome fictício, substitua
caso o arquivo seja renomeado). Ele contém três jobs:

1. **build** – Instala dependências Python e Node, executa `npm run build` no frontend, roda
   checagens básicas (linters e testes disponíveis) e empacota o artefato.
2. **publish-image** – Gera a imagem Docker com a aplicação (Flask + assets compilados) e faz
   push para o registro configurado.
3. **release** – Faz o deploy para staging ou produção utilizando os artefatos do passo anterior.

Os jobs `publish-image` e `release` dependem do sucesso do job `build`.

> ℹ️ Caso seja necessário rodar apenas parte do pipeline (ex.: somente build), use `workflow_dispatch`
> com os *inputs* apropriados. Para cenários de hotfix é possível marcar o deploy direto em produção
> desde que o staging esteja sincronizado com a branch `main`.

## Deploy em staging

1. Abra um Pull Request direcionado à branch `main` e aguarde a aprovação do código.
2. Com o PR aprovado, clique em **"Run workflow"** no GitHub Actions e selecione o ambiente
   `staging`. O input padrão utiliza a branch do PR.
3. O job `release` publica a imagem na instância de staging, atualizando as variáveis de ambiente
   se necessário. Ao final, o workflow expõe a URL do ambiente e o hash do commit implantado.
4. Execute testes exploratórios no staging e valide os indicadores de monitoramento (logs,
   métricas de latência, status do banco).

### Rollback em staging

- Utilize o histórico de execuções do workflow e selecione a execução anterior bem-sucedida.
- Rode novamente o workflow apontando para o `deployment_tag` informado naquela execução.
- Em último caso, faça `git revert` do commit problemático e reabra o workflow.

## Deploy em produção

1. Garanta que o staging esteja atualizado e validado.
2. Crie uma *release tag* seguindo o padrão `vX.Y.Z` (semântica com `major.minor.patch`). A tag
   dispara automaticamente o workflow com input `environment=production`.
3. O job `release` executa migrações de banco (se presentes), aplica as variáveis de ambiente de
   produção e reinicia o serviço (via `docker service update` ou `systemctl`, conforme o host).
4. Após o deploy, monitore os dashboards e confirme que a versão reportada pela rota `/health`
   corresponde à tag publicada.

### Rollback em produção

- Utilize a tag anterior, por exemplo `vX.Y.(Z-1)`, e rode novamente o workflow.
- Alternativamente, acione o script de rollback (`scripts/rollback.sh`) que faz `docker rollback`
  para a imagem anterior.

## Cache busting de assets

Para evitar que navegadores utilizem versões desatualizadas dos assets estáticos, adotamos as
seguintes estratégias:

1. **Hash nos nomes dos arquivos** – O build do Vite gera arquivos sob `frontend/dist/assets`
   com sufixos hash (`app.[hash].js`, `style.[hash].css`). Ao publicar o build, o template
   `index.html` é reescrito apontando para os novos hashes, o que força o download dos arquivos.
2. **Headers HTTP agressivos** – O servidor Flask (ou Nginx na frente dele) adiciona os headers
   `Cache-Control: public, max-age=31536000, immutable` para arquivos com hash no nome. Isso
   permite caching agressivo, pois qualquer alteração gera um novo hash.
3. **Invalidar ativos legados** – Para assets servidos diretamente de `static/` sem hash, o
   workflow anexa o parâmetro de versão `?v=<commit_sha>` sempre que referenciados nos templates
   Jinja. Esse parâmetro é atualizado automaticamente pelo script `scripts/bust_cache.py`.
4. **CDN purge opcional** – Quando usando CDN (Cloudflare/Akamai), ao final do job `release`
   executa-se `scripts/purge_cdn.py <environment>` para invalidar o cache dos caminhos `/assets/*`
   e `/index.html`.

## Boas práticas

- Sempre valide o build localmente (`npm run build` e `flask --app app.py check`) antes de abrir o
  PR para evitar falhas triviais na pipeline.
- Atualize a documentação quando houver mudanças no fluxo (novos scripts, alteração do provedor).
- Mantenha os scripts em `scripts/` idempotentes e versionados juntamente ao repositório.

## Perguntas frequentes

- **Posso fazer deploy direto em produção?** Somente para hotfixes críticos aprovados pela liderança.
  Utilize o input `environment=production` no workflow e documente no PR.
- **Como confirmar o hash dos assets ativos?** Acesse `https://app.disagua.com/assets-manifest.json`
  (arquivo publicado no deploy) ou utilize `npm run manifest` para gerar o arquivo localmente.
- **Onde ficam os logs do deploy?** No GitHub Actions (aba *Summary* do workflow) e na stack de
  observabilidade configurada (Grafana + Loki).

