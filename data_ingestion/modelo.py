from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL 

# Configurando a engine e a sessão
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

Base = declarative_base()

# Modelo de dados
class Veiculo(Base):
    __tablename__ = 'veiculos'

    id = Column(Integer, primary_key=True)
    codigo_marca = Column(String)
    codigo_modelo = Column(String)
    codigo_ano = Column(String)
    nome = Column(String)
    valor = Column(Float)
    combustivel = Column(String)
    referencia = Column(String)
    fipe_codigo = Column(String)
    ano_modelo = Column(Integer)

# Criar a tabela no banco de dados
Base.metadata.create_all(engine)
