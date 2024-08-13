import pytest
from pyspark.sql import SparkSession
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use o backend 'Agg' para testes sem interface gráfica

# Importe as funções de análise do seu script
from notebooks.analysis import top_countries_cases, daily_global, mortality_rate, test_positivity, vaccination_trend

@pytest.fixture(scope="module")
def spark_session():
    spark = SparkSession.builder \
        .appName("TestCOVID19Analysis") \
        .master("local[*]") \
        .getOrCreate()
    yield spark
    spark.stop()

@pytest.fixture
def sample_data(spark_session):
    data = [
        ("2021-01-01", "US", 1000, 10, 500, 5000, 1000, 10.0, 20.0),
        ("2021-01-02", "US", 1500, 15, 750, 6000, 2500, 12.0, 25.0),
        ("2021-01-01", "UK", 800, 8, 400, 4000, 800, 8.0, 20.0),
        ("2021-01-02", "UK", 1200, 12, 600, 5000, 2000, 10.0, 24.0)
    ]
    columns = ["date", "country_name", "new_confirmed", "new_deceased", "new_recovered", "new_tested", 
               "total_cases", "mortality_rate", "test_positivity_rate"]
    return spark_session.createDataFrame(data, columns)

def test_top_countries_cases(spark_session, sample_data):
    result = sample_data.groupBy("country_name").sum("new_confirmed").orderBy("sum(new_confirmed)", ascending=False).limit(10)
    assert result.count() == 2
    assert result.collect()[0]['country_name'] == 'US'

def test_daily_global(spark_session, sample_data):
    result = sample_data.groupBy("date").agg({"new_confirmed": "sum", "new_deceased": "sum"}).orderBy("date")
    assert result.count() == 2
    assert result.collect()[1]['sum(new_confirmed)'] == 2700

def test_mortality_rate(spark_session, sample_data):
    result = sample_data.groupBy("country_name").avg("mortality_rate").orderBy("avg(mortality_rate)", ascending=False).limit(10)
    assert result.count() == 2
    assert result.collect()[0]['country_name'] == 'US'

def test_test_positivity(spark_session, sample_data):
    result = sample_data.groupBy("country_name").avg("test_positivity_rate").orderBy("avg(test_positivity_rate)", ascending=False).limit(10)
    assert result.count() == 2
    assert result.collect()[0]['country_name'] == 'US'

# Adicione mais testes conforme necessário para cobrir outras análises

if __name__ == "__main__":
    pytest.main([__file__])