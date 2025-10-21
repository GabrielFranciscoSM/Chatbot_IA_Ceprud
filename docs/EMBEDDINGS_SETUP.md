# Embeddings Setup Guide

This document explains how to configure embeddings for the RAG service with support for both GPU (vLLM) and CPU (Ollama) backends.

## Overview

The RAG service now supports two embedding backends:

1. **vLLM (GPU-based)** - High performance, requires NVIDIA GPU
2. **Ollama (CPU-based)** - No GPU required, runs on CPU

## Quick Start with Ollama (CPU)

### 1. Start the services

```bash
docker-compose -f docker-compose-full.yml up -d
```

### 2. Pull the embedding model

After the Ollama container is running, pull the embedding model:

```bash
chmod +x scripts/setup_ollama_embeddings.sh
./scripts/setup_ollama_embeddings.sh
```

Or manually:

```bash
docker exec chatbot-ollama ollama pull nomic-embed-text
```

### 3. Verify it's working

The RAG service should now be using Ollama for embeddings. Check the logs:

```bash
docker logs chatbot-rag-service
```

## Configuration

The embedding backend is controlled by environment variables in `docker-compose-full.yml`:

### For Ollama (CPU - Default)

```yaml
environment:
  USE_OLLAMA: "true"
  OLLAMA_URL: http://ollama:11434
  OLLAMA_MODEL_NAME: nomic-embed-text
```

### For vLLM (GPU)

1. Uncomment the `vllm-openai-embeddings` service in `docker-compose-full.yml`
2. Update the RAG service configuration:

```yaml
environment:
  USE_OLLAMA: "false"  # or remove this line
  VLLM_EMBEDDING_URL: http://vllm-openai-embeddings:8001
  EMBEDDING_MODEL_DIR: /models/Qwen--Qwen3-Embedding-0.6B
```

3. Update dependencies:

```yaml
depends_on:
  - vllm-openai-embeddings
```

## Switching Between Backends

### Switch to Ollama (CPU)

1. Set `USE_OLLAMA: "true"` in the rag-service environment
2. Ensure `ollama` is in the `depends_on` section
3. Restart the services:

```bash
docker-compose -f docker-compose-full.yml restart rag-service
```

### Switch to vLLM (GPU)

1. Set `USE_OLLAMA: "false"` in the rag-service environment
2. Uncomment the `vllm-openai-embeddings` service
3. Update `depends_on` to include `vllm-openai-embeddings`
4. Restart the services:

```bash
docker-compose -f docker-compose-full.yml up -d vllm-openai-embeddings
docker-compose -f docker-compose-full.yml restart rag-service
```

## Available Embedding Models

### Ollama Models

You can use different Ollama embedding models by changing `OLLAMA_MODEL_NAME`:

- `nomic-embed-text` (default) - 137M parameters, good balance
- `mxbai-embed-large` - Larger model, better quality
- `all-minilm` - Smaller, faster

Pull a different model:

```bash
docker exec chatbot-ollama ollama pull mxbai-embed-large
```

### vLLM Models

Any HuggingFace model compatible with vLLM can be used. Update `EMBEDDING_MODEL_DIR` to point to your model path.

## Performance Comparison

| Backend | Hardware | Speed | Quality | Memory |
|---------|----------|-------|---------|--------|
| vLLM | GPU (NVIDIA) | Very Fast | High | ~2-4GB VRAM |
| Ollama | CPU | Moderate | Good | ~1-2GB RAM |

## Troubleshooting

### Ollama service not starting

Check if the container is running:

```bash
docker ps | grep ollama
```

View logs:

```bash
docker logs chatbot-ollama
```

### Model not found

Ensure you've pulled the model:

```bash
docker exec chatbot-ollama ollama list
```

### RAG service can't connect to Ollama

Check network connectivity:

```bash
docker exec chatbot-rag-service ping ollama
```

## Testing

You can test the embeddings endpoint directly:

```bash
# Test Ollama
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "Hello world"
}'
```

## Notes

- The first embedding request may be slow as the model loads into memory
- Ollama caches models in the `ollama_data` volume
- ChromaDB will automatically use whichever embedding function is configured
- If you switch backends, you may need to rebuild your ChromaDB collection
