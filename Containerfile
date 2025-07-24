#syntax=docker/dockerfile:1.4
# 1. Use an official NVIDIA CUDA image as the base
# This image includes CUDA 12.1.1 and cuDNN 8 on Ubuntu 22.04
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set environment variables to prevent buffering and warnings
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# 2. Install Python, pip, and other system dependencies
# The NVIDIA base image does not include Python
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3.10 \
      python3-pip \
      build-essential \
      cmake \
      pkg-config && \
    # Clean up apt cache to reduce image size
    rm -rf /var/lib/apt/lists/*

# Copiar archivos necesarios
COPY requirements.txt /app/requirements.txt

# 3. Install PyTorch with CUDA support FIRST
# This command specifically installs a version of PyTorch compatible with CUDA 12.1.
# IMPORTANT: Remove 'torch', 'torchvision', and 'torchaudio' from your requirements.txt file.
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Instalar dependencias de Python
RUN pip3 install --no-cache-dir --upgrade -r /app/requirements.txt

# Comando por defecto
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]
