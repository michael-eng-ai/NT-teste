# Projeto de ETL e Análise de Dados COVID-19 usando Databricks e Delta Lake

## Visão Geral

Este projeto implementa um pipeline de ETL (Extract, Transform, Load) para dados de COVID-19, utilizando Databricks e Delta Lake. O pipeline extrai dados de uma fonte pública, realiza transformações necessárias e carrega os dados em um formato otimizado para análise.

## Arquitetura

Docs/architecture.md

O pipeline é construído sobre a arquitetura lakehouse do Databricks:

1. **Bronze Layer**: Dados brutos ingeridos via AutoLoader
2. **Silver Layer**: Dados limpos e transformados armazenados em Delta Lake
3. **Gold Layer**: Agregações e feature engineering para análise e ML

## Tecnologias Utilizadas

- **Databricks**: Plataforma unificada para processamento de dados e machine learning
- **Delta Lake**: Formato de armazenamento otimizado para big data
- **PySpark**: API Python para Apache Spark
- **Databricks AutoLoader**: Para ingestão eficiente de dados
- **MLflow**: Para gerenciamento do ciclo de vida de modelos de ML (implementação futura)

## Principais Características

- **Ingestão de Dados**: Utiliza Databricks AutoLoader para ingestão incremental eficiente
- **Transformação**: Limpeza de dados, cálculo de métricas e agregações usando PySpark
- **Armazenamento**: Dados armazenados em formato Delta Lake para transações ACID e performance otimizada
- **Análise**: Utiliza Spark SQL e bibliotecas de visualização integradas ao Databricks
- **Segurança**: Implementa controle de acesso granular e criptografia usando recursos do Databricks
- **Monitoramento**: Usa Databricks Jobs e SQL Analytics para monitoramento em tempo real

## Processo ETL

### Extração

```python
def extract_data(file_path):
    return (spark.readStream
                 .format("cloudFiles")
                 .option("cloudFiles.format", "csv")
                 .option("header", "true")
                 .schema(schema)
                 .load(file_path))
```

### Transformação

```python
def transform_data(df):
    return (df.withColumn("date", to_date(col("date")))
              .na.fill(0)
              .na.fill("Unknown")
              .dropDuplicates()
              .withColumn("total_cases", sum("new_confirmed").over(Window.partitionBy("location_key").orderBy("date")))
              .withColumn("mortality_rate", when(col("total_cases") > 0, (col("new_deceased") / col("total_cases")) * 100).otherwise(0))
              .withColumn("test_positivity_rate", when(col("new_tested") > 0, (col("new_confirmed") / col("new_tested")) * 100).otherwise(0)))
```

### Carregamento

```python
def load_data(df, table_name):
    (df.writeStream
       .format("delta")
       .outputMode("append")
       .option("checkpointLocation", f"/delta/{table_name}/_checkpoints")
       .table(table_name))
```

## Análises e Insights

O projeto inclui várias análises descritivas, incluindo:

- Países com maior número total de casos
- Evolução diária de novos casos e óbitos globalmente
- Taxa de mortalidade média por país
- Taxa de positividade dos testes por país

[Incluir aqui algumas visualizações ou insights chave]

## Segurança e Monitoramento

- **Segurança**: Utiliza Databricks Secrets, Table Access Control, e criptografia em repouso e em trânsito
- **Monitoramento**: Implementa dashboards em Databricks SQL Analytics e integração com Azure Monitor

## Melhorias Futuras

1. Implementação de MLflow para gerenciamento de modelos de ML
2. Uso de Databricks Feature Store para gerenciar features
3. Implementação de Auto ML para previsão de casos de COVID-19
4. Integração com Delta Sharing para compartilhamento seguro de dados
5. Utilização de Databricks Workflows para orquestração complexa

## Como Executar

1. Clone este repositório
2. Configure seu ambiente Databricks
3. Execute o notebook principal `main_etl_pipeline.py`

## Contribuindo

Contribuições são bem-vindas! Por favor, leia o arquivo CONTRIBUTING.md para detalhes sobre nosso código de conduta e o processo de submissão de pull requests.

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes.

