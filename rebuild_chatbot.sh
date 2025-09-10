#!/bin/bash
# rebuild_chatbot.sh - Script to rebuild and redeploy the chatbot

# Exit immediately if a command exits with a non-zero status.
set -e

echo "🔨 Rebuilding the chatbot container..."

# 1. Stop the chatbot service
echo "⏹️  Stopping the current chatbot service..."
podman-compose -f docker-compose-vllm.yml stop

# 3. Prune build cache to ensure fresh build
echo "🔄 Rebuilding the image without cache..."
sleep 5
podman-compose -f docker-compose-vllm.yml build --no-cache --pull chatbot

# 4. Rebuild the image without using cache
# The --no-cache flag ensures all layers are rebuilt, picking up any code changes
echo "🧹 Clearing build cache..."
sleep 5
podman system prune -f --filter="label!=keep"

# 5. Start the updated service in detached mode
echo "🚀 Starting the updated service..."
podman-compose -f docker-compose-vllm.yml up -d

echo "✅ Chatbot redeployment complete."