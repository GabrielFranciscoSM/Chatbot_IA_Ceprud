#syntax=docker/dockerfile:1.4

# 1. Use an official NVIDIA CUDA image as the base
FROM docker.io/nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /chatbot

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
RUN pip3 install --no-cache-dir -r requirements.txt 

# 5.1. Verify wikipedia package is installed
#RUN python3 -c "import wikipedia; print('Wikipedia package installed successfully')" 


# 6. Copy the application code
# Note: This should be one of the last steps to ensure code changes invalidate the cache
COPY ./app ./app

# 7. Set environment variables for Python path
#ENV PYTHONPATH=/chatbot/app

# 8. Set proper permissions (if needed)
#RUN chmod -R 755 /app

# Default command to run the application
#CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5001"]