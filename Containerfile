#syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.12-slim-bookworm

# Exponer puerto Flask
EXPOSE 5001

# Variables de entorno
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1

# Directorio de trabajo
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      cmake \
      pkg-config 

# Copiar archivos necesarios
COPY requirements3.txt /app/requirements.txt

# Instalar dependencias de Python
RUN pip3 install --no-cache-dir --upgrade -r /app/requirements.txt

# Comando por defecto
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]
