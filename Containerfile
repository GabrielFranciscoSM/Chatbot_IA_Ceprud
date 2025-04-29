# Usar imagen base de Python 3.12
FROM python:3.12-slim

# Exponer puerto Flask
EXPOSE 5001

# Variables de entorno
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para sentencepiece
RUN apt-get update && apt-get install -y \
    pkg-config \
    cmake \
    build-essential

# Copiar archivos necesarios
COPY app.py /app/app.py
COPY query_logic.py /app/query_logic.py
COPY get_embedding_function.py /app/get_embedding_function.py 
COPY populate_database.py /app/populate_database.py
COPY templates/index.html /app/templates/index.html
COPY static/styless.css /app/static/styless.css
COPY requirements.txt /app/requirements.txt

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Comando por defecto
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5001"]
