# CSV Importer 🚀

Este é um projeto de estudo em Python que oferece uma solução robusta para importar arquivos CSV para um banco de dados PostgreSQL de forma dinâmica. A aplicação utiliza modelos dinâmicos do SQLAlchemy para criar tabelas e colunas em tempo de execução, formatando os nomes e ingerindo os dados de forma eficiente.

## ✨ Sobre o Projeto

O principal objetivo do **CSV Importer** é automatizar o processo de ETL (Extração, Transformação e Carga) para arquivos CSV, eliminando a necessidade de criar manualmente tabelas e scripts de inserção para cada novo layout de arquivo. A solução é orquestrada por uma API construída com FastAPI, que gerencia o fluxo de forma concisa e eficiente.

### Principais Funcionalidades

  - **API para Upload**: Uma rota `POST /import` para receber arquivos CSV de forma segura.
  - **Detecção de Separador**: Identifica automaticamente se o delimitador do CSV é ponto e vírgula (`;`) ou vírgula (`,`).
  - **Sanitização de Nomes**: Limpa e formata os nomes das colunas e do arquivo (que se tornará o nome da tabela), convertendo-os para o padrão `camelCase` e removendo acentos e caracteres especiais.
  - **Criação Dinâmica de Tabelas**: Utiliza o SQLAlchemy para criar um modelo de dados e a respectiva tabela no banco de dados em tempo de execução, caso ela ainda não exista.
  - **Ingestão Eficiente de Dados**: Processa o CSV em *chunks* (pedaços) utilizando o Pandas, garantindo um baixo consumo de memória mesmo com arquivos muito grandes.
  - **Organização de Arquivos**: Move os arquivos processados para pastas de sucesso (`ok`) ou erro (`error`) para um controle claro do que foi executado.

## 🛠️ Tecnologias Utilizadas

  - **Python 3.10+**
  - **FastAPI**: Para a criação da API REST.
  - **SQLAlchemy**: Para o ORM e a conexão com o banco de dados.
  - **Pandas**: Para a manipulação e leitura eficiente dos arquivos CSV.
  - **PostgreSQL**: Como sistema de gerenciamento de banco de dados.
  - **Uvicorn**: Como servidor ASGI para rodar a aplicação FastAPI.

## 📂 Estrutura do Projeto (Exemplo)

```
.
├── app
│   ├── db
│   │   └── database.py         # Inicialização do módulo de banco de dados
│   ├── routes
│   │   └── import_router.py    # Roteamento para importação de arquivos
│   └── utils
│       └── utils.py             # Funções auxiliares (ex: to_camel_case)
│
├── temp                        # Pasta temporária para arquivos
│   ├── ok/                     # Arquivos processados com sucesso
│   └── error/                  # Arquivos que apresentaram erro
│
├── .env                        # Arquivo para variáveis de ambiente (DB_URL)
├── requirements.txt            # Dependências do projeto   
├── main.py                     # Arquivo principal da aplicação
└── README.md                   # Documentação do projeto
```

## 🏁 Como Começar

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

  - Python 3.10 ou superior
  - PostgreSQL instalado e rodando
  - Um ambiente virtual (recomendado)

### Instalação

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/seu-usuario/csv-importer.git
    cd csv-importer
    ```

2.  **Crie e ative um ambiente virtual:**

    ```bash
    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto e adicione a URL de conexão do seu banco de dados PostgreSQL.

    ```env
    # Exemplo de .env
    DATABASE_URL="postgresql://user:password@host:port/database_name"
    ```

### Executando a Aplicação

Com o ambiente configurado, inicie o servidor da API com o Uvicorn:

```bash
uvicorn app.main:app --reload
```

O servidor estará disponível em `http://127.0.0.1:8000`.

## ⚙️ Como Usar

Para importar um arquivo, envie uma requisição `POST` do tipo `multipart/form-data` para a rota `/import`.

### Exemplo com cURL

```bash
curl -X POST -F "file=@/caminho/para/seu/arquivo.csv" http://127.0.0.1:8000/import
```

> **Nota:** Substitua `/caminho/para/seu/arquivo.csv` pelo caminho real do arquivo que você deseja importar.

## 🌊 Fluxo de Execução

1.  **Recebimento do Arquivo**: A rota `POST /import` recebe o arquivo via `UploadFile`, valida sua extensão (`.csv`) e o salva em uma pasta `./temp`.
2.  **Início do Processamento**: A API chama a função principal de processamento, passando o nome do arquivo.
3.  **Limpeza e Formatação**:
      - Uma função auxiliar detecta o separador (`;` ou `,`).
      - Outra função lê o cabeçalho, limpa cada nome de coluna usando REGEX para remover acentos e caracteres especiais, e converte para `camelCase`.
      - O nome do arquivo também é convertido para `camelCase` para se tornar o nome da tabela.
4.  **Criação da Tabela**: Uma função verifica se a tabela já existe no banco. Se não, ela cria um modelo dinâmico do SQLAlchemy com as colunas formatadas (inicialmente como `String`) e gera a tabela no banco.
5.  **Ingestão dos Dados**: Utilizando `pd.read_csv` com `chunksize`, os dados do arquivo são lidos em lotes e inseridos na tabela correspondente através do método `to_sql`.
6.  **Finalização**: Após a conclusão (com sucesso ou falha), o arquivo é movido da pasta `./temp` para `./temp/ok` ou `./temp/error`, mantendo um registro do resultado do processamento.

## 🎯 Próximos Passos e Melhorias

  - [ ] **Detecção Dinâmica de Tipos**: Implementar uma lógica para inferir o tipo de dado de cada coluna (ex: `Integer`, `Float`, `DateTime`) em vez de usar `String` para todas.
  - [ ] **Processamento em Background**: Mover a lógica de processamento de arquivos para um worker em background (ex: Celery, RQ) para que a API retorne uma resposta imediata e não trave com arquivos grandes.
  - [ ] **Testes Unitários**: Adicionar testes para garantir a robustez das funções auxiliares e do fluxo principal.
  - [ ] **Suporte a Outros Formatos**: Estender a solução para suportar outros tipos de arquivos, como Excel (`.xlsx`) ou Parquet.
