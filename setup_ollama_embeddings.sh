#!/bin/bash
# Script to pull the embedding model in Ollama container

echo "Pulling nomic-embed-text model in Ollama container..."
podman exec chatbot-ollama ollama pull nomic-embed-text

echo "Model pulled successfully!"
echo "You can now use Ollama for CPU-based embeddings."
