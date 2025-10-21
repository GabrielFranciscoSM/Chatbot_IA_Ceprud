#!/bin/bash
# Stop Cloudflare Tunnel

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -f tunnel.pid ]; then
    PID=$(cat tunnel.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Stopping Cloudflare Tunnel (PID: $PID)..."
        kill $PID
        rm tunnel.pid
        echo "✓ Tunnel stopped"
    else
        echo "Tunnel process not running (stale PID file)"
        rm tunnel.pid
    fi
else
    echo "No tunnel PID file found. Checking for cloudflared processes..."
    pkill -f "cloudflared tunnel"
    echo "✓ Killed any running cloudflared processes"
fi
