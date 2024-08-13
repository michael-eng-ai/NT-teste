import pyarrow as pa
import pyarrow.parquet as pq
import dask.dataframe as dd
import numpy as np
from dask.distributed import Client
from datetime import datetime
import logging
from cryptography.fernet import Fernet
import psutil
import time
import os

# Configuração de logging
logging.basicConfig(filename='etl_covid_secure.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def encrypt_file(file_path, key):
    """
    Criptografa o arquivo especificado usando a chave fornecida.
    """
    f = Fernet(key)
    with open(file_path, 'rb') as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(file_path + '.encrypted', 'wb') as file:
        file.write(encrypted_data)
    os.remove(file_path)  # Remove o arquivo não criptografado
    logging.info(f"Arquivo {file_path} criptografado com sucesso")

def log_performance():
    """
    Registra o desempenho atual do sistema.
    """
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    logging.info(f"CPU: {cpu_percent}%, Memory: {memory_percent}%")

def extract_data(file_path):
    """
    Extrai dados do arquivo CSV usando PyArrow e converte para Dask DataFrame.
    """
    try:
        logging.info(f"Iniciando extração de dados de {file_path}")
        table = pa.csv.read_csv(file_path)
        df = dd.from_pandas(table.to_pandas(), npartitions=4)  # Ajuste o número de partições conforme necessário
        logging.info("Dados extraídos com sucesso")
        return df
    except Exception as e:
        logging.error(f"Erro ao extrair dados: {e}")
        raise

def transform_data(df):
    """
    Transforma os dados extraídos usando Dask.
    """
    try:
        logging.info("Iniciando transformação dos dados")
        
        # Converter data para datetime
        df['date'] = dd.to_datetime(df['date'])
        
        # Preencher valores nulos em colunas numéricas com 0
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df = df[numeric_columns].fillna(0)
        
        # Preencher valores nulos em colunas de texto com 'Unknown'
        text_columns = df.select_dtypes(include=[object]).columns
        df = df[text_columns].fillna('Unknown')
        
        # Remover linhas duplicadas
        df = df.drop_duplicates()
        
        # Criar coluna de total_cases
        df['total_cases'] = df.groupby('location_key')['new_confirmed'].cumsum()
        
        # Criar coluna de mortality_rate
        df['mortality_rate'] = (df['new_deceased'] / df['total_cases'] * 100).fillna(0)
        
        # Criar coluna de test_positivity_rate
        df['test_positivity_rate'] = (df['new_confirmed'] / df['new_tested'] * 100).fillna(0)
        
        logging.info("Transformação dos dados concluída")
        return df
    except Exception as e:
        logging.error(f"Erro ao transformar dados: {e}")
        raise

def load_data(df, output_path):
    """
    Carrega os dados transformados em um arquivo parquet usando PyArrow.
    """
    try:
        logging.info(f"Iniciando carregamento dos dados em {output_path}")
        df.compute().to_parquet(output_path, engine='pyarrow')
        logging.info("Dados carregados com sucesso")
    except Exception as e:
        logging.error(f"Erro ao carregar dados: {e}")
        raise

def validate_data(df):
    """
    Realiza validações básicas nos dados.
    """
    try:
        logging.info("Iniciando validação dos dados")
        
        # Verificar se há valores negativos em colunas que não deveriam ter
        for col in ['new_confirmed', 'new_deceased', 'new_tested', 'total_cases']:
            if (df[col] < 0).any().compute():
                logging.warning(f"Valores negativos encontrados na coluna {col}")
        
        # Verificar se as datas estão dentro de um intervalo esperado
        min_date = df['date'].min().compute()
        max_date = df['date'].max().compute()
        if min_date < pd.Timestamp('2020-01-01') or max_date > pd.Timestamp.now():
            logging.warning(f"Datas fora do intervalo esperado: min={min_date}, max={max_date}")
        
        logging.info("Validação dos dados concluída")
    except Exception as e:
        logging.error(f"Erro ao validar dados: {e}")
        raise

def main():
    # Iniciar o cliente Dask
    client = Client()
    dir_path = "/Users/michaelsantos/Documents/NT-teste/data"
    input_file = f"{dir_path}/raw/aggregated.csv"
    output_path = f"{dir_path}/processed/covid_data_{datetime.now().strftime('%Y%m%d')}.parquet"
    
    # Gerar chave de criptografia
    key = Fernet.generate_key()
    
    try:
        start_time = time.time()
        
        raw_data = extract_data(input_file)
        log_performance()
        
        transformed_data = transform_data(raw_data)
        log_performance()
        
        validate_data(transformed_data)
        log_performance()
        
        load_data(transformed_data, output_path)
        log_performance()
        
        # Criptografar o arquivo de saída
        encrypt_file(output_path, key)
        
        end_time = time.time()
        logging.info(f"Processo ETL concluído com sucesso. Tempo total: {end_time - start_time} segundos")
    except Exception as e:
        logging.error(f"Erro no processo ETL: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
    
