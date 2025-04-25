# Usar imagen base de Python 3.12
FROM python:3.12-slim

# Exponer puerto Flask
EXPOSE 5001

# Variables de entorno
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1

# Directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Comando por defecto
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5001"]
