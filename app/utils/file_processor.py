import pandas as pd
import os
import unicodedata
import re
from app.db.database import engine
from sqlalchemy import Column, Engine, String, Integer, inspect, text
from sqlalchemy.orm import declarative_base


Base = declarative_base()

def to_camel_case(s: str) -> str:
    """
    Converte uma string para o formato camelCase, removendo acentos,
    caracteres especiais e espaços.
    Exemplo: "Distribuição [de] Renda" -> "distribuicaoRenda"
    """
    # Remove colchetes, retira acentuação e remove caracteres especiais
    s = re.sub(r"\[.*?\]", "", s)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-zA-Z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    # Divide a string transforma em camelCase
    parts = s.split(" ")
    if not parts:
        return ""
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])

def detect_csv_separator(file_path: str) -> str:
    """Detecta se o separador do CSV é ';' ou ','."""
    try:
        # Tenta ler o cabeçalho com ';'
        df_header = pd.read_csv(file_path, sep=';', nrows=0)
        if len(df_header.columns) > 1:
            return ';'
        
        # Se não funcionar, tenta com ','
        df_header = pd.read_csv(file_path, sep=',', nrows=0)
        if len(df_header.columns) > 1:
            return ','
            
    except Exception as e:
        raise ValueError(f"Não foi possível ler o cabeçalho do arquivo: {e}")
    
    raise ValueError("Separador de CSV não detectado ou arquivo com uma única coluna.")

def get_table_and_column_names(file_path: str, separator: str) -> tuple[str, list[str]]:
    """Extrai e converte nomes da tabela e colunas para camelCase."""
    file_name = os.path.basename(file_path)
    table_name = to_camel_case(os.path.splitext(file_name)[0])
    
    df_header = pd.read_csv(file_path, sep=separator, nrows=0)
    camel_case_columns = [to_camel_case(col) for col in df_header.columns]
    
    return table_name, camel_case_columns

def dynamic_table_verify(table_name: str, column_names: list[str], engine: Engine):
    """Cria uma tabela no banco de dados dinamicamente se ela não existir."""
    inspector = inspect(engine)
    if inspector.has_table(table_name):
        print(f"Aviso: A tabela '{table_name}' já existe no banco de dado!")
        if inspector.has_table(table_name):
            with engine.connect() as connection:
                result = connection.execute(text(f'SELECT COUNT(*) FROM "{table_name}";'))
                if result.scalar() > 0:
                    print(f"A tabela '{table_name}' já contém dados. Truncando a tabela...")
                    connection.execute(text(f'TRUNCATE TABLE "{table_name}";'))
                    connection.commit()
                    print('Tabela truncada com sucesso, continuando importação...')
                else:
                    print(f"A tabela '{table_name}' está vazia. Adicionando novos dados.")

        return

    attrs = {
        "__tablename__": table_name,
        "__table_args__": {"extend_existing": True},
        "id": Column(Integer, primary_key=True, autoincrement=True)
    }
    
    for col_name in column_names:
        if col_name.lower() != 'id':
            attrs[col_name] = Column(String)

    DynamicModel = type(table_name.capitalize(), (Base,), attrs)
    Base.metadata.create_all(engine, tables=[DynamicModel.__table__])
    print(f"Tabela '{table_name}' criada com sucesso!")

def ingest_csv_data(file_path: str, table_name: str, column_names: list[str], separator: str, engine) -> int:
    """Ingere dados de um CSV para uma tabela do banco de dados em chunks."""
    total_rows = 0
    with pd.read_csv(file_path, chunksize=1000, sep=separator, iterator=True) as reader:
        for i, chunk in enumerate(reader):
            chunk.columns = column_names  # Renomeia as colunas do chunk
            chunk.to_sql(table_name, engine, if_exists="append", index=False)
            total_rows += len(chunk)
            print(f"  - Chunk {i+1}: {len(chunk)} linhas inseridas.")
    return total_rows

def move_processed_file(file_path: str):
    """Move um arquivo processado para a pasta 'ok'."""
    temp_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    
    processed_dir = os.path.join(temp_dir, "ok")
    os.makedirs(processed_dir, exist_ok=True)
    destination_path = os.path.join(processed_dir, file_name)
    
    os.replace(file_path, destination_path)
    print(f"Arquivo '{file_name}' movido para a pasta 'ok' com sucesso!")

def process_csv_file(file_name: str):
    """
    Orquestra o processo completo de importação de um arquivo CSV para o banco de dados.
    """
    temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'temp'))
    file_path = os.path.join(temp_dir, file_name)

    if not os.path.exists(file_path):
        print(f"Erro: Arquivo não encontrado em {file_path}")
        return

    print(f"Iniciando processamento do arquivo: {file_name}")
    try:
        separator = detect_csv_separator(file_path)
        print(f"Separador detectado: '{separator}'")

        table_name, columns = get_table_and_column_names(file_path, separator)
        print(f"Nome da tabela: {table_name}")
        print(f"Colunas: {columns[0:4]}...")

        dynamic_table_verify(table_name, columns, engine)

        total_rows = ingest_csv_data(file_path, table_name, columns, separator, engine)
        
        move_processed_file(file_path)

        print(f"Importação concluída! Total de {total_rows} linhas inseridas na tabela '{table_name}'.")

    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o processamento de '{file_name}': {e}")
