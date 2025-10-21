#!/bin/bash
# Complete deployment script for external testing

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     Chatbot IA CEPRUD - External Deployment Script           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if cloudflared exists
if [ ! -f "./cloudflared" ]; then
    print_error "Cloudflared not found. Downloading..."
    wget -q --show-progress -O cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x cloudflared
    print_success "Cloudflared downloaded successfully"
fi

echo ""
print_info "Step 1/4: Checking prerequisites..."

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    print_error "podman-compose not found. Please install it first."
    exit 1
fi
print_success "Podman-compose is installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please edit .env file with your configuration"
        print_info "Minimum required: HF_TOKEN"
        exit 1
    else
        print_error ".env.example not found. Cannot proceed."
        exit 1
    fi
fi
print_success ".env file exists"

echo ""
print_info "Step 2/4: Starting Docker services..."

# Stop existing services
print_info "Stopping any existing services..."
podman-compose -f docker-compose-full.yml down 2>/dev/null || true

# Start services
print_info "Starting all services (this may take a few minutes)..."
podman-compose -f docker-compose-full.yml up -d

# Wait for services to be ready
print_info "Waiting for services to initialize..."
sleep 10

# Check if services are running
print_info "Checking service health..."
SERVICES=("backend" "frontend" "rag-service" "user-service" "mongodb" "ollama")
ALL_HEALTHY=true

for service in "${SERVICES[@]}"; do
    if podman-compose -f docker-compose-full.yml ps | grep -q "chatbot-$service"; then
        print_success "$service is running"
    else
        print_error "$service failed to start"
        ALL_HEALTHY=false
    fi
done

if [ "$ALL_HEALTHY" = false ]; then
    print_error "Some services failed to start. Check logs with:"
    echo "  podman-compose -f docker-compose-full.yml logs"
    exit 1
fi

echo ""
print_info "Step 3/4: Testing service connectivity..."

# Test backend
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    print_success "Backend API is responding"
else
    print_warning "Backend API not responding yet (may still be starting up)"
fi

# Test frontend
if curl -s http://localhost:8090 > /dev/null 2>&1; then
    print_success "Frontend is responding"
else
    print_warning "Frontend not responding yet (may still be starting up)"
fi

echo ""
print_info "Step 4/4: Starting Cloudflare Tunnel..."

# Stop existing tunnel if running
if [ -f tunnel.pid ] && kill -0 $(cat tunnel.pid) 2>/dev/null; then
    print_info "Stopping existing tunnel..."
    ./scripts/stop-tunnel.sh 2>/dev/null || true
fi

# Start new tunnel
print_info "Establishing secure tunnel..."
./scripts/start-tunnel.sh

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    DEPLOYMENT COMPLETE                        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Get the tunnel URL
if [ -f cloudflare-tunnel.log ]; then
    TUNNEL_URL=$(grep -oP 'https://[^|]+\.trycloudflare\.com' cloudflare-tunnel.log | tail -1 | xargs)
    
    if [ -n "$TUNNEL_URL" ]; then
        echo -e "${GREEN}✓ Your chatbot is now accessible at:${NC}"
        echo ""
        echo -e "  ${BLUE}${TUNNEL_URL}${NC}"
        echo ""
        print_info "Share this URL with your testers!"
        echo ""
        
        # Save URL to file for easy access
        echo "$TUNNEL_URL" > current-url.txt
        print_success "URL saved to current-url.txt"
    else
        print_warning "Could not extract tunnel URL. Check cloudflare-tunnel.log"
    fi
fi

echo ""
echo "Local access URLs:"
echo "  • Frontend:     http://localhost:8090"
echo "  • Backend API:  http://localhost:8080/docs"
echo "  • MongoDB UI:   http://localhost:8081"
echo "    (user: mongoexpressuser, pass: mongoexpresspass)"
echo ""

print_info "Useful commands:"
echo "  • View logs:        podman-compose -f docker-compose-full.yml logs -f"
echo "  • Stop services:    podman-compose -f docker-compose-full.yml down"
echo "  • Stop tunnel:      ./scripts/stop-tunnel.sh"
echo "  • Restart all:      ./scripts/deploy-for-testing.sh"
echo ""

print_success "Deployment complete! Your chatbot is ready for testing."
echo ""
echo "See DEPLOYMENT_GUIDE.md for detailed instructions and troubleshooting."
