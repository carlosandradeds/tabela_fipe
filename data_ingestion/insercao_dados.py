import requests
import logging
import time
from sqlalchemy.orm.exc import NoResultFound
import os
import sys

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_ingestion.modelo import Veiculo, Session

def get_data(url, retries=5, delay=1):
    """
    Faz a requisição HTTP com suporte a retries e backoff exponencial.
    """
    for i in range(retries):
        try:
            logging.info(f'Fazendo requisição para a URL: {url}')
            response = requests.get(url)
            if response.status_code == 200:
                logging.info(f'Sucesso na requisição. URL: {url}')
                return response.json()
            elif response.status_code == 429:
                logging.warning(f'Muitas requisições. Aguardando {delay} segundos antes de tentar novamente.')
                time.sleep(delay)
                delay *= 2  # Backoff exponencial
            else:
                logging.warning(f'Falha na requisição. Status code: {response.status_code}, URL: {url}')
                return None
        except requests.exceptions.RequestException as req:
            logging.error(f'Erro ao fazer a requisição para a URL: {url}, Erro: {req}')
            return None
    logging.error(f'Número máximo de tentativas alcançado para a URL: {url}')
    return None

def save_vehicle(session, veiculo, codigo_marca, codigo_modelo, codigo_ano):
    try:
        logging.info(f'Verificando se o veículo já existe no banco de dados. Marca: {codigo_marca}, Modelo: {codigo_modelo}, Ano: {codigo_ano}')
        existing_vehicle = session.query(Veiculo).filter_by(
            codigo_marca=codigo_marca,
            codigo_modelo=codigo_modelo,
            codigo_ano=codigo_ano,
            fipe_codigo=veiculo.get('CodigoFipe')
        ).one_or_none()

        if existing_vehicle:
            logging.info(f'Veículo {existing_vehicle.nome} já existe no banco de dados.')
        else:
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
            logging.debug(f"Tentando commitar o veículo {novo_veiculo.nome} ao banco de dados.")
            session.commit()
            logging.info(f'Veículo {novo_veiculo.nome} adicionado ao banco de dados.')
    except Exception as e:
        logging.error(f'Erro ao salvar o veículo no banco de dados. Marca: {codigo_marca}, Modelo: {codigo_modelo}, Ano: {codigo_ano}, Erro: {e}')
        session.rollback()  # Faz o rollback em caso de erro
        raise  # Relevante para depuração

def get_fipe():
    session = None
    try:
        session = Session()
        logging.info('Sessão criada com sucesso.')

        url_marcas = 'https://parallelum.com.br/fipe/api/v1/carros/marcas'
        marcas = get_data(url_marcas)
        if not marcas:
            logging.error('Não foi possível obter as marcas.')
            return

        codigos_marca = [marca['codigo'] for marca in marcas]
        logging.info(f'Encontradas {len(codigos_marca)} marcas.')

        for codigo_marca in codigos_marca:
            url_modelos = f'https://parallelum.com.br/fipe/api/v1/carros/marcas/{codigo_marca}/modelos'
            modelos = get_data(url_modelos)
            if not modelos:
                logging.warning(f'Nenhum modelo encontrado para a marca {codigo_marca}.')
                continue
            codigos_modelo = [cd_modelo['codigo'] for cd_modelo in modelos['modelos']]
            logging.info(f'Encontrados {len(codigos_modelo)} modelos para a marca {codigo_marca}.')

            for codigo_modelo in codigos_modelo:
                url_anos = f'https://parallelum.com.br/fipe/api/v1/carros/marcas/{codigo_marca}/modelos/{codigo_modelo}/anos'
                anos = get_data(url_anos)
                if not anos:
                    logging.warning(f'Nenhum ano encontrado para o modelo {codigo_modelo} da marca {codigo_marca}.')
                    continue
                codigos_anos = [cd_ano['codigo'] for cd_ano in anos]
                logging.info(f'Encontrados {len(codigos_anos)} anos para o modelo {codigo_modelo} da marca {codigo_marca}.')

                for codigo_ano in codigos_anos:
                    url_fipe = f'https://parallelum.com.br/fipe/api/v1/carros/marcas/{codigo_marca}/modelos/{codigo_modelo}/anos/{codigo_ano}'
                    veiculo = get_data(url_fipe)
                    if veiculo:
                        try:
                            save_vehicle(session, veiculo, codigo_marca, codigo_modelo, codigo_ano)
                        except Exception as e:
                            logging.error(f"Erro ao processar o veículo com código de ano {codigo_ano}: {e}")
                            session.rollback()  # Rola de volta para permitir que o próximo veículo seja processado
    except Exception as e:
        logging.error(f'Erro durante a execução do processo: {e}')
    finally:
        if session:
            session.close()
            logging.info('Sessão do banco de dados encerrada.')

if __name__ == "__main__":
    get_fipe()
