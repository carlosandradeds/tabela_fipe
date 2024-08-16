# Usar uma imagem base oficial do Python
FROM python:3.11-slim

# Instalar dependências do sistema necessárias para o pipenv, airflow e postgres
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar o Pipfile e o Pipfile.lock para o diretório de trabalho
COPY Pipfile Pipfile.lock ./

# Instalar as dependências usando pipenv para criar um virtualenv
RUN pip install pipenv && pipenv install --deploy

# Copiar o restante do código para o diretório de trabalho
COPY . .

# Especificar o comando para rodar o airflow e o Python dentro do ambiente virtual gerenciado pelo pipenv
CMD ["pipenv", "run", "airflow", "webserver"]
