#!/bin/bash

# Frontend Development Script
# Use this for local development of the frontend

echo "🚀 Starting Frontend Development Server"
echo "======================================"

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "❌ This script must be run from the frontend directory"
    echo "💡 Try: cd frontend && ./dev.sh"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting Vite development server..."
echo "📍 Frontend will be available at: http://localhost:3000"
echo "🔗 API proxy will connect to: http://localhost:8080"
echo ""
echo "💡 Make sure your backend is running on port 8080"
echo "   You can start it with: docker-compose -f ../docker-compose-vllm.yml up"
echo ""

npm run dev
