#syntax=docker/dockerfile:1.4

# 1. Use an official NVIDIA CUDA image as the base
FROM docker.io/nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# 2. Install Python and system dependencies
# The NVIDIA base image does not include Python
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3.10 \
      python3-pip \
      build-essential \
      cmake \
      pkg-config && \
    # Clean up apt cache to reduce image size
    rm -rf /var/lib/apt/lists/*

# 3. Copy requirements and constraints files
# We copy these first to leverage Docker's layer caching.
COPY requirements.txt ./

# 4. Install PyTorch with CUDA support FIRST
# This command specifically installs a version of PyTorch compatible with CUDA 12.1.
# IMPORTANT: Make sure 'torch', 'torchvision', and 'torchaudio' are NOT in your requirements.txt file.
# RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 5. Install your application's Python dependencies
# The --constraint flag is the key. It forces pip to use the versions specified
# in constraints.txt, preventing it from reinstalling torch.
RUN pip3 install --no-cache-dir -r requirements.txt 

# 6. Copy the application code
#COPY app/ /app/

# Default command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]