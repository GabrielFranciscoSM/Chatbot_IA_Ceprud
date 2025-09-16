#!/bin/bash

# Chatbot Setup Script
# This script sets up the complete chatbot environment with frontend and backend

set -e

echo "🚀 Setting up Chatbot UGR - CEPRUD"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    # Detect container runtime
    if command -v podman &> /dev/null; then
        CONTAINER_CMD="podman"
        COMPOSE_CMD="podman-compose"
        print_status "Using Podman as container runtime"
    elif command -v docker &> /dev/null; then
        CONTAINER_CMD="docker"
        COMPOSE_CMD="docker-compose"
        print_status "Using Docker as container runtime"
    else
        print_error "Neither Docker nor Podman is installed. Please install one of them first."
        exit 1
    fi
    
    if ! command -v $COMPOSE_CMD &> /dev/null; then
        print_error "$COMPOSE_CMD is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. Frontend development will require Node.js."
    fi
    
    print_status "Requirements check completed."
}

# Install frontend dependencies
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    if command -v node &> /dev/null; then
        print_status "Installing frontend dependencies..."
        npm install
        print_status "Frontend dependencies installed."
    else
        print_warning "Skipping frontend dependency installation (Node.js not found)."
    fi
    
    cd ..
}

# Build and start services
start_services() {
    print_status "Starting services with Docker Compose..."
    
    # Check for port conflicts
    print_status "Checking for port conflicts..."
    
    # Check if port 3000 is in use (Grafana conflicts)
    if lsof -Pi :3000 -sTCP:LISTEN &> /dev/null; then
        print_warning "Port 3000 is in use. Checking if it's Grafana..."
        if $CONTAINER_CMD ps --format "{{.Names}}" | grep -q grafana; then
            print_warning "Stopping Grafana containers to free port 3000..."
            $CONTAINER_CMD stop $(${CONTAINER_CMD} ps --format "{{.Names}}" | grep grafana) || true
        fi
    fi
    
    # Clean up any existing containers
    print_status "Cleaning up existing containers..."
    $COMPOSE_CMD -f docker-compose-full.yml down --remove-orphans || true
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from example..."
        cp .env.example .env 2>/dev/null || echo "HF_TOKEN=your_huggingface_token_here" > .env
        print_warning "Please edit .env file and add your Hugging Face token."
    fi
    
    # Build and start services
    $COMPOSE_CMD -f docker-compose-full.yml up --build -d
    
    print_status "Services are starting..."
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    check_health() {
        local service_name=$1
        local port=$2
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -s http://localhost:$port/health &> /dev/null; then
                print_status "$service_name is ready!"
                return 0
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                print_error "$service_name failed to start properly"
                return 1
            fi
            
            print_status "Waiting for $service_name... (attempt $attempt/$max_attempts)"
            sleep 5
            ((attempt++))
        done
    }
    
    # Check backend health
    check_health "Backend" 8080
    
    # Check if frontend is accessible
    if curl -s http://localhost:3000 &> /dev/null; then
        print_status "Frontend is ready!"
    else
        print_warning "Frontend may still be starting..."
    fi
}

# Show final information
show_info() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "Services are running:"
    echo "  🌐 Frontend:  http://localhost:3000"
    echo "  🔧 Backend:   http://localhost:8080"
    echo "  🤖 LLM API:   http://localhost:8000"
    echo "  📊 Embeddings: http://localhost:8001"
    echo ""
    echo "To view logs:"
    echo "  $COMPOSE_CMD -f docker-compose-full.yml logs -f"
    echo ""
    echo "To stop services:"
    echo "  $COMPOSE_CMD -f docker-compose-full.yml down"
    echo ""
    echo "To rebuild after changes:"
    echo "  $COMPOSE_CMD -f docker-compose-full.yml up --build"
    echo ""
    print_warning "Don't forget to configure your .env file with your Hugging Face token!"
}

# Main execution
main() {
    check_requirements
    setup_frontend
    start_services
    show_info
}

# Handle script arguments
case "${1:-}" in
    "frontend-only")
        check_requirements
        print_status "Setting up frontend only..."
        setup_frontend
        ;;
    "services-only")
        check_requirements
        print_status "Starting services only..."
        start_services
        show_info
        ;;
    "stop")
        check_requirements
        print_status "Stopping all services..."
        $COMPOSE_CMD -f docker-compose-full.yml down
        ;;
    "logs")
        check_requirements
        $COMPOSE_CMD -f docker-compose-full.yml logs -f
        ;;
    "rebuild")
        check_requirements
        print_status "Rebuilding and restarting services..."
        $COMPOSE_CMD -f docker-compose-full.yml down
        $COMPOSE_CMD -f docker-compose-full.yml up --build -d
        show_info
        ;;
    *)
        main
        ;;
esac
