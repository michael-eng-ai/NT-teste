import os
from datetime import datetime
from dask.distributed import Client
from cryptography.fernet import Fernet
import logging
import time

# Importar funções do script ETL
from scripts.etl import extract_data, transform_data, load_data, validate_data, encrypt_file, log_performance

# Configuração de logging
logging.basicConfig(filename='etl_covid_main.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def main():
    # Iniciar o cliente Dask
    client = Client()
    
    # Definir caminhos
    dir_path = "/Users/michaelsantos/Documents/NT-teste/"
    input_file = f"{dir_path}data/raw/aggregated.csv"
    output_path = f"{dir_path}data/processed/covid_data_{datetime.now().strftime('%Y%m%d')}.parquet"
    
    # Gerar chave de criptografia
    key = Fernet.generate_key()
    
    try:
        start_time = time.time()
        
        # Processo ETL
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
        
        # from databricks_api import DatabricksAPI
        # db = DatabricksAPI(
        #     host="https://your-databricks-instance.cloud.databricks.com",
        #     token="your-access-token"
        # )
        # notebook_path = "/notebooks/analysis"
        # response = db.workspace.run_now(notebook_path, timeout_seconds=3600)
        # 
        # localmente:
        import subprocess
        subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", 
                        f"{dir_path}/notebooks/analysis.ipynb"])
        
        logging.info("Análise concluída com sucesso.")
        
    except Exception as e:
        logging.error(f"Erro no processo: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    main()