# Sistema de Gestão de Parceiro

Um sistema desktop para gerenciamento de parceiros, lojas atendidas, comprovantes de entregas e geração de relatórios.

## Recursos Principais

- **Cadastro de Parceiros**: Gerenciamento completo de entregadores/parceiros.
- **Cadastro de Lojas**: Cadastro e gerenciamento das lojas atendidas.
- **Comprovantes de Entrega**: Upload e visualização de comprovantes de entrega.
- **Associação Parceiros-Lojas**: Gerenciamento das relações entre parceiros e lojas.
- **Relatórios**: Geração de relatórios de entregas por parceiro, loja e período.
- **Sistema de Backup**: Backup e restauração automática de dados.

## Requisitos

- Python 3.7 ou superior
- Bibliotecas Python listadas em `requirements.txt`

## Instalação

1. Clone este repositório:
   ```
   git clone https://github.com/seu-usuario/sistema-gestao-entregas.git
   cd sistema-gestao-entregas
   ```

2. Crie um ambiente virtual (recomendado):
   ```
   python -m venv venv
   
   # No Windows
   venv\Scripts\activate
   
   # No Linux/Mac
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Execute o aplicativo:
   ```
   python app.py
   ```

## Estrutura do Projeto

O projeto segue o padrão de arquitetura MVC (Model-View-Controller) para organizar o código de forma modular e facilitar a manutenção:

- **Models**: Representa os dados e regras de negócio.
- **Views**: Interface do usuário.
- **Controllers**: Conecta os modelos às views e implementa a lógica de negócio.
- **Database**: Gerenciamento de conexão e operações do banco de dados.
- **Utils**: Funções utilitárias como validadores e formatadores.
- **Resources**: Recursos estáticos como ícones e imagens.
- **Comprovantes**: Diretório para armazenar os arquivos de comprovantes de entrega.

```
Sistema de Gestão de Entregas/
│
├── app.py                  # Ponto de entrada da aplicação
├── config.ini              # Configurações do sistema
├── requirements.txt        # Dependências do projeto
│
├── database/               # Gerenciamento do banco de dados
│   ├── __init__.py
│   ├── db_manager.py       # Gerenciador de conexão com o banco
│   └── queries.py          # Consultas SQL reutilizáveis
│
├── models/                 # Modelos de dados
│   ├── __init__.py
│   ├── parceiro.py         # Modelo para parceiros
│   ├── loja.py             # Modelo para lojas
│   ├── comprovante.py      # Modelo para comprovantes
│   └── associacao.py       # Modelo para associações
│
├── views/                  # Interfaces gráficas
│   ├── __init__.py
│   ├── main_window.py      # Janela principal da aplicação
│   ├── parceiro_view.py    # Interface de parceiros
│   ├── loja_view.py        # Interface de lojas
│   ├── comprovante_view.py # Interface de comprovantes
│   ├── associacao_view.py  # Interface de associações
│   └── relatorio_view.py   # Interface de relatórios
│
├── controllers/            # Controladores
│   ├── __init__.py
│   ├── parceiro_controller.py
│   ├── loja_controller.py
│   ├── comprovante_controller.py
│   ├── associacao_controller.py
│   └── relatorio_controller.py
│
├── utils/                  # Utilitários
│   ├── __init__.py
│   ├── validators.py       # Validação de CPF, CNPJ, etc.
│   ├── formatters.py       # Formatação de dados
│   ├── logger.py           # Sistema de logging
│   ├── backup_utils.py     # Funções de backup
│   └── export_utils.py     # Funções para exportação
│
├── resources/              # Recursos estáticos
│   ├── icons/              # Ícones da interface
│   ├── images/             # Imagens
│   └── styles/             # Estilos para a interface
│
└── comprovantes/           # Diretório para armazenar comprovantes
```

## Guia de Uso

### Cadastro de Parceiros

1. Acesse a aba "Parceiros"
2. Preencha os campos com os dados do parceiro:
   - Nome (obrigatório)
   - CPF (opcional, mas deve ser válido se informado)
   - Telefone
   - Email
   - Endereço
3. Clique em "Adicionar" para salvar
4. Para editar, selecione um parceiro na lista, modifique os dados e clique em "Salvar Edição"
5. Para excluir, selecione um parceiro na lista e clique em "Excluir"

### Cadastro de Lojas

1. Acesse a aba "Lojas"
2. Preencha os campos com os dados da loja:
   - Nome (obrigatório)
   - CNPJ (opcional, mas deve ser válido se informado)
   - Telefone
   - Email
   - Endereço
   - Contato (nome da pessoa de contato)
3. Clique em "Adicionar" para salvar
4. Para editar ou excluir, utilize os mesmos procedimentos do cadastro de parceiros

### Comprovantes de Entrega

1. Acesse a aba "Comprovantes"
2. Selecione o parceiro e a loja relacionados à entrega
3. Informe a data da entrega
4. Clique em "Selecionar" para escolher o arquivo do comprovante
5. Adicione observações se necessário
6. Clique em "Adicionar" para salvar o comprovante
7. Para visualizar, selecione um comprovante na lista e clique em "Visualizar"

### Associações Parceiros-Lojas

1. Acesse a aba "Associações"
2. Selecione o parceiro e a loja que deseja associar
3. Escolha o status da associação (Ativo, Inativo, Pendente)
4. Clique em "Associar" para criar a associação
5. Para editar ou remover associações, selecione-as na lista e utilize os botões correspondentes

### Relatórios

1. Acesse a aba "Relatórios"
2. Selecione o tipo de relatório desejado:
   - Entregas por Parceiro
   - Entregas por Loja
   - Entregas por Período
3. Configure os filtros conforme necessário
4. Clique em "Gerar Relatório"
5. Use os botões "Exportar para Excel" ou "Exportar para PDF" para salvar o relatório

## Backup e Restauração

Para realizar backup do banco de dados:
1. No menu principal, acesse "Arquivo" > "Backup"
2. Escolha o local para salvar o arquivo de backup

Para restaurar um backup:
1. No menu principal, acesse "Arquivo" > "Restaurar Backup" 
2. Selecione o arquivo de backup desejado

## Solução de Problemas

### Comprovantes Não Visualizados
- Verifique se o arquivo existe no diretório de comprovantes
- Confirme se o visualizador padrão para o tipo de arquivo está configurado

### Erros de Banco de Dados
- Verifique se o arquivo do banco de dados não está corrompido
- Restaure um backup recente

### Problemas com CPF/CNPJ
- Certifique-se de que os documentos são válidos
- O sistema valida automaticamente o formato e o algoritmo de verificação

## Customização

O sistema pode ser customizado editando o arquivo `config.ini` para alterar:
- Localização do banco de dados
- Diretório de comprovantes
- Formatos de arquivos permitidos
- Configurações de logs

## Contribuições

Contribuições são bem-vindas! Siga estes passos:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Envie para o branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

### Desenvolvido por Macete Systems
