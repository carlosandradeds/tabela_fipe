import requests
from sqlalchemy.orm.exc import NoResultFound
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_ingestion.modelo import Veiculo, Session

def get_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Falha na requisição. Status code: {response.status_code}')
            return None
    except requests.exceptions.RequestException as req:
        print(f'Erro ao fazer a requisição: {req}')                     
        return None

def save_vehicle(session, veiculo, codigo_marca, codigo_modelo, codigo_ano):
    try:
        existing_vehicle = session.query(Veiculo).filter_by(
            codigo_marca=codigo_marca,
            codigo_modelo=codigo_modelo,
            codigo_ano=codigo_ano,
            fipe_codigo=veiculo.get('CodigoFipe')
        ).one()
        print(f'Veículo {existing_vehicle.nome} já existe no banco de dados.')
    except NoResultFound:
        novo_veiculo = Veiculo(
            codigo_marca=codigo_marca,
            codigo_modelo=codigo_modelo,
            codigo_ano=codigo_ano,
            nome=veiculo.get('Modelo'),
            valor=float(veiculo.get('Valor').replace('R$', '').replace('.', '').replace(',', '.').strip()) if veiculo.get('Valor') else None,
            combustivel=veiculo.get('Combustivel'),
            referencia=veiculo.get('MesReferencia'),
            fipe_codigo=veiculo.get('CodigoFipe')
        )
        session.add(novo_veiculo)
        session.commit()
        print(f'Veículo {novo_veiculo.nome} adicionado ao banco de dados.')

def get_fipe():
    url_marcas = 'https://parallelum.com.br/fipe/api/v1/carros/marcas'
    marcas = get_data(url_marcas)
    if not marcas:
        return

    codigos_marca = [marca['codigo'] for marca in marcas]

    for codigo_marca in codigos_marca:
        url_modelos = f'https://parallelum.com.br/fipe/api/v1/carros/marcas/{codigo_marca}/modelos'
        modelos = get_data(url_modelos)
        if not modelos:
            continue
        codigos_modelo = [cd_modelo['codigo'] for cd_modelo in modelos['modelos']]

        for codigo_modelo in codigos_modelo:
            url_anos = f'https://parallelum.com.br/fipe/api/v1/carros/marcas/{codigo_marca}/modelos/{codigo_modelo}/anos'
            anos = get_data(url_anos)
            if not anos:
                continue
            codigos_anos = [cd_ano['codigo'] for cd_ano in anos]

            for codigo_ano in codigos_anos:
                url_fipe = f'https://parallelum.com.br/fipe/api/v1/carros/marcas/{codigo_marca}/modelos/{codigo_modelo}/anos/{codigo_ano}'
                veiculo = get_data(url_fipe)
                if veiculo:
                    save_vehicle(session, veiculo, codigo_marca, codigo_modelo, codigo_ano)

if __name__ == "__main__":
    session = Session()
    get_fipe()
    session.close()
