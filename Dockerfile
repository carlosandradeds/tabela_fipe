# Usar uma imagem base oficial do Python
FROM python:3.11-slim

# Instalar dependências do sistema necessárias para o pipenv, airflow e postgres
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar pipenv
RUN pip install pipenv

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar o Pipfile e o Pipfile.lock para o diretório de trabalho
COPY Pipfile Pipfile.lock ./

# Instalar as dependências do projeto
RUN pipenv install --deploy --system

# Copiar o restante do código para o diretório de trabalho
COPY . .

# Copiar os DAGs do Airflow para o diretório do Airflow
COPY dags/ /opt/airflow/dags/

# Expor a porta do Airflow
EXPOSE 8080

# Comando padrão para rodar o Airflow scheduler e o webserver
CMD ["airflow", "webserver"]
