FROM python:3.11-slim

WORKDIR /app

# Instala Poetry
RUN pip install --no-cache-dir poetry

# Copia arquivos de dependência
COPY pyproject.toml poetry.lock ./

# Instala dependências sem criar virtualenv (container já é isolado)
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --only main

# Copia o código
COPY src/ ./src/

# Pasta de uploads (imagens locais legadas)
RUN mkdir -p uploads

# Cloud Run usa porta 8080
EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
