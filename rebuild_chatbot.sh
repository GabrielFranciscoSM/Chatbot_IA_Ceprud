#!/bin/bash
# rebuild_chatbot.sh - Script to rebuild and redeploy the chatbot

# Exit immediately if a command exits with a non-zero status.
set -e

echo "🔨 Rebuilding the chatbot container..."

# 1. Stop the chatbot service
echo "⏹️  Stopping the current chatbot service..."
podman-compose -f docker-compose-vllm-embeddings.yml stop

# 3. Prune build cache to ensure fresh build
echo "🔄 Rebuilding the image without cache..."
sleep 5
podman-compose -f docker-compose-vllm-embeddings.yml build --no-cache --pull chatbot

# 4. Rebuild the image without using cache
# The --no-cache flag ensures all layers are rebuilt, picking up any code changes
echo "🧹 Clearing build cache..."
sleep 5
podman system prune -f --filter="label!=keep"

# 5. Start the updated service in detached mode
echo "🚀 Starting the updated service..."
podman-compose -f docker-compose-vllm-embeddings.yml up -d

echo "⏳ Waiting for services to be ready..."

# Function to check if a container is running
# check_container() {
#     local container_name=$1
#     local service_name=$2
#     local max_attempts=30
#     local attempt=1
    
#     echo "🔍 Checking $service_name container..."
#     while [ $attempt -le $max_attempts ]; do
#         if podman ps --format "table {{.Names}}" | grep -q "$container_name"; then
#             echo "✅ $service_name container is running!"
#             return 0
#         fi
#         echo "   Attempt $attempt/$max_attempts - $service_name not ready yet..."
#         sleep 10
#         attempt=$((attempt + 1))
#     done
    
#     echo "❌ $service_name failed to start within expected time"
#     return 1
# }

# Function to check if a service endpoint is responding
check_service_endpoint() {
    local url=$1
    local service_name=$2
    local max_attempts=20
    local attempt=1
    
    echo "🔍 Checking $service_name endpoint..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is responding!"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - $service_name endpoint not ready yet..."
        sleep 15
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name endpoint failed to respond within expected time"
    return 1
}

# Wait for all containers to be running
# check_container "my-vllm-service" "vLLM Main Service"
# check_container "my-embedding-service" "vLLM Embeddings Service"
# check_container "my-chatbot-app" "Chatbot Service"

# Wait for services to be responding (give them time to initialize)
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check if services are responding (optional - you can comment these out if they don't have health endpoints)
check_service_endpoint "http://localhost:8000/health" "vLLM Main Service"
check_service_endpoint "http://localhost:8001/health" "vLLM Embeddings Service" 
check_service_endpoint "http://localhost:5001/health" "Chatbot Service"

echo "🗃️ All services are ready! Now populating the RAG database..."

# Check if the chatbot container is running before trying to execute commands
if ! podman ps --format "table {{.Names}}" | grep -q "my-chatbot-app"; then
    echo "❌ Chatbot container 'my-chatbot-app' is not running!"
    echo "   Something went wrong during startup. Check logs with: podman logs my-chatbot-app"
    exit 1
fi

# Populate the database inside the container
echo "📚 Executing populate_database.py inside the chatbot container..."
if podman exec my-chatbot-app python3 app/rag/populate_database.py --reset; then
    echo "✅ Database population completed successfully!"
else
    echo "❌ Database population failed!"
    echo "   Check the container logs with: podman logs my-chatbot-app"
    echo "   You can try running it manually with:"
    echo "   podman exec my-chatbot-app python3 app/rag/populate_database.py --reset"
    exit 1
fi

echo "🎉 Chatbot redeployment and database initialization complete!"
echo "🌐 Chatbot is available at: http://0.0.0.0:5001"
echo "📊 You can also check the logs with: podman logs my-chatbot-app"