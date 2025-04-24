# Usar imagen base de Python 3.12
FROM python:3.12-slim

# Variables de entorno
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1
ENV HUGGINGFACEHUB_API_TOKEN="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"

# Directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY app.py /app/app.py
COPY query_logic.py /app/query_logic.py
COPY generate_data.py /app/generate_data.py
COPY requirements.txt /app/requirements.txt
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY get_embedding_function.py /app/get_embedding_function.py

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Solución al error de 'xla_device'
RUN pip install transformers==4.36.2 tiktoken==0.6.0 --force-reinstall

# Exponer puerto Flask
EXPOSE 5000

# Comando por defecto
CMD ["python", "app.py"]
