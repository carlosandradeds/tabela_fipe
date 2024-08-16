import pytest
from unittest.mock import patch
from data_ingestion.insercao_dados import get_data, save_vehicle
from data_ingestion.modelo import Veiculo, Session

# Testando a função get_data
@patch('data_ingestion.insercao_dados.requests.get')
def test_get_data(mock_get):
    # Simulando uma resposta bem-sucedida da API
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"key": "value"}
    
    result = get_data('http://fakeurl-for-testing.com')
    
    assert result == {"key": "value"}
    mock_get.assert_called_once_with('http://fakeurl-for-testing.com')

# Testando a função save_vehicle para um novo veículo
@patch('data_ingestion.insercao_dados.Session', autospec=True)
def test_save_vehicle_new(mock_session):
    session = mock_session()
    
    veiculo_data = {
        'CodigoFipe': '001',
        'Modelo': 'Carro Teste',
        'Valor': 'R$ 25.000,00',
        'Combustivel': 'Gasolina',
        'MesReferencia': 'Agosto/2023',
        'AnoModelo': 2023  
    }
    
    save_vehicle(session, veiculo_data, '001', '001', '2023')
    
    session.add.assert_called_once()
    session.commit.assert_called_once()

# Testando a função save_vehicle para um veículo existente
@patch('data_ingestion.insercao_dados.Session', autospec=True)
@patch('data_ingestion.insercao_dados.Veiculo', autospec=True)
def test_save_vehicle_existing(mock_veiculo, mock_session):
    session = mock_session()
    
    mock_query = session.query.return_value.filter_by.return_value
    mock_query.one.return_value = mock_veiculo
    
    veiculo_data = {
        'CodigoFipe': '001',
        'Modelo': 'Carro Teste',
        'Valor': 'R$ 25.000,00',
        'Combustivel': 'Gasolina',
        'MesReferencia': 'Agosto/2023',
        'AnoModelo': 2023
    }
    
    save_vehicle(session, veiculo_data, '001', '001', '2023')
    
    session.add.assert_not_called()
    session.commit.assert_not_called()
