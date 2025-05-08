# Usar imagen con soporte CUDA y python
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# Exponer puerto Flask
EXPOSE 5001

# Variables de entorno
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1

# Directorio de trabajo
WORKDIR /app

# Instalar Python 3.12 y pip
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip

# Instalar dependencias del sistema para sentencepiece
RUN apt-get update && apt-get install -y \
    pkg-config \
    cmake \
    build-essential\
    libgl1

# Copiar archivos necesarios
COPY app.py /app/app.py
COPY query_logic.py /app/query_logic.py
COPY get_embedding_function.py /app/get_embedding_function.py 
COPY populate_database.py /app/populate_database.py
COPY templates/index.html /app/templates/index.html
COPY static/styles.css /app/static/styles.css
COPY requirements.txt /app/requirements.txt

# Instalar PyTorch con soporte CUDA 12.4
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Comando por defecto
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]
