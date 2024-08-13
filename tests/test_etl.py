import pytest
import pandas as pd
import numpy as np
from scripts.etl import extract_data, transform_data, validate_data
from dask.distributed import Client
import os
import tempfile

@pytest.fixture(scope="module")
def dask_client():
    client = Client()
    yield client
    client.close()

@pytest.fixture
def sample_csv():
    # Criar um CSV de exemplo temporário
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
        tmp.write("date,location_key,new_confirmed,new_deceased,new_recovered,new_tested\n")
        tmp.write("2021-01-01,US,1000,10,500,5000\n")
        tmp.write("2021-01-02,US,1500,15,750,6000\n")
    yield tmp.name
    os.unlink(tmp.name)

def test_extract_data(dask_client, sample_csv):
    df = extract_data(sample_csv)
    assert len(df) == 2
    assert list(df.columns) == ['date', 'location_key', 'new_confirmed', 'new_deceased', 'new_recovered', 'new_tested']

def test_transform_data(dask_client):
    input_df = pd.DataFrame({
        'date': ['2021-01-01', '2021-01-02'],
        'location_key': ['US', 'US'],
        'new_confirmed': [1000, 1500],
        'new_deceased': [10, 15],
        'new_recovered': [500, 750],
        'new_tested': [5000, 6000]
    })
    df = transform_data(input_df)
    
    assert 'total_cases' in df.columns
    assert 'mortality_rate' in df.columns
    assert 'test_positivity_rate' in df.columns
    
    # Verificar se o total_cases está correto
    assert df['total_cases'].compute().tolist() == [1000, 2500]
    
    # Verificar se não há valores nulos
    assert df.isnull().sum().compute().sum() == 0

def test_validate_data(dask_client):
    valid_df = pd.DataFrame({
        'date': pd.date_range(start='2021-01-01', periods=2),
        'new_confirmed': [100, 200],
        'new_deceased': [5, 10],
        'new_tested': [1000, 2000],
        'total_cases': [100, 300]
    })
    
    # Não deve levantar exceção
    validate_data(valid_df)
    
    invalid_df = valid_df.copy()
    invalid_df.loc[0, 'new_confirmed'] = -1
    
    # Deve logar um aviso, mas não levantar exceção
    with pytest.warns(UserWarning):
        validate_data(invalid_df)

if __name__ == "__main__":
    pytest.main([__file__])