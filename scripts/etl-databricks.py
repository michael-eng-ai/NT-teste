# Databricks notebook source
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta.tables import *
from datetime import datetime

# Configuração do Spark com Delta Lake
spark = SparkSession.builder \
    .appName("COVID19_ETL") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()


def log_info(message):
    print(f"INFO: {message}")


def extract_data(file_path):
    """
    Extrai dados do arquivo CSV usando Spark.
    """
    try:
        log_info(f"Iniciando extração de dados de {file_path}")
        df = spark.read.csv(file_path, header=True, inferSchema=True)
        log_info("Dados extraídos com sucesso")
        return df
    except Exception as e:
        log_info(f"Erro ao extrair dados: {str(e)}")
        raise


def transform_data(df):
    """
    Transforma os dados extraídos usando Spark.
    """
    try:
        log_info("Iniciando transformação dos dados")
        
        # Converter data para timestamp
        df = df.withColumn("date", to_timestamp(col("date")))
        
        # Preencher valores nulos
        numeric_columns = [f.name for f in df.schema.fields if isinstance(f.dataType, (IntegerType, DoubleType))]
        df = df.na.fill(0, subset=numeric_columns)
        df = df.na.fill("Unknown")
        
        # Remover linhas duplicadas
        df = df.dropDuplicates()
        
        # Criar coluna de total_cases
        window = Window.partitionBy("location_key").orderBy("date")
        df = df.withColumn("total_cases", sum("new_confirmed").over(window))
        
        # Criar coluna de mortality_rate
        df = df.withColumn("mortality_rate", 
                           when(col("total_cases") > 0, (col("new_deceased") / col("total_cases")) * 100)
                           .otherwise(0))
        
        # Criar coluna de test_positivity_rate
        df = df.withColumn("test_positivity_rate", 
                           when(col("new_tested") > 0, (col("new_confirmed") / col("new_tested")) * 100)
                           .otherwise(0))
        
        log_info("Transformação dos dados concluída")
        return df
    except Exception as e:
        log_info(f"Erro ao transformar dados: {str(e)}")
        raise


def load_data(df, table_name):
    """
    Carrega os dados transformados em uma tabela Delta.
    """
    try:
        log_info(f"Iniciando carregamento dos dados em {table_name}")
        
        # Usar merge para upsert
        delta_table = DeltaTable.forName(spark, table_name)
        
        delta_table.alias("old") \
            .merge(
                df.alias("new"),
                "old.location_key = new.location_key AND old.date = new.date"
            ) \
            .whenMatchedUpdateAll() \
            .whenNotMatchedInsertAll() \
            .execute()
        
        log_info("Dados carregados com sucesso")
    except Exception as e:
        log_info(f"Erro ao carregar dados: {str(e)}")
        raise


def validate_data(df):
    """
    Realiza validações básicas nos dados.
    """
    try:
        log_info("Iniciando validação dos dados")
        
        # Verificar se há valores negativos em colunas que não deveriam ter
        for col in ['new_confirmed', 'new_deceased', 'new_tested', 'total_cases']:
            if df.filter(col(col) < 0).count() > 0:
                log_info(f"Valores negativos encontrados na coluna {col}")
        
        # Verificar se as datas estão dentro de um intervalo esperado
        min_date = df.agg(min("date")).collect()[0][0]
        max_date = df.agg(max("date")).collect()[0][0]
        if min_date < datetime(2020, 1, 1) or max_date > datetime.now():
            log_info(f"Datas fora do intervalo esperado: min={min_date}, max={max_date}")
        
        log_info("Validação dos dados concluída")
    except Exception as e:
        log_info(f"Erro ao validar dados: {str(e)}")
        raise


def main():
    input_file = "/dbfs/FileStore/shared_uploads/michaelsantos@hotmail.com/aggregated.csv"
    table_name = "covid_data"
    
    try:
        start_time = datetime.now()
        
        # Criar a tabela Delta se não existir
        spark.sql(f"CREATE TABLE IF NOT EXISTS {table_name} USING DELTA")
        
        raw_data = extract_data(input_file)
        transformed_data = transform_data(raw_data)
        validate_data(transformed_data)
        load_data(transformed_data, table_name)
        
        end_time = datetime.now()
        log_info(f"Processo ETL concluído com sucesso. Tempo total: {end_time - start_time}")
        
        # Demonstração de Time Travel
        df_version_0 = spark.read.format("delta").option("versionAsOf", 0).table(table_name)
        log_info(f"Número de linhas na versão 0: {df_version_0.count()}")
        
    except Exception as e:
        log_info(f"Erro no processo ETL: {str(e)}")

# COMMAND ----------

if __name__ == "__main__":
    main()