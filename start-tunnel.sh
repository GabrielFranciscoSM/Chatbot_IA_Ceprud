#!/bin/bash
# Start Cloudflare Tunnel for HTTPS access

# Check if tunnel is already running
if [ -f tunnel.pid ] && kill -0 $(cat tunnel.pid) 2>/dev/null; then
    echo "Tunnel is already running (PID: $(cat tunnel.pid))"
    echo "Current URL:"
    grep -i "https://" cloudflare-tunnel.log | tail -1
    exit 0
fi

# Start tunnel in background
echo "Starting Cloudflare Tunnel..."
nohup ./cloudflared tunnel --url http://localhost:8090 > cloudflare-tunnel.log 2>&1 &
TUNNEL_PID=$!
echo $TUNNEL_PID > tunnel.pid

# Wait for tunnel to establish
echo "Waiting for tunnel to establish..."
sleep 5

# Extract and display URL
URL=$(grep -oP 'https://[^|]+\.trycloudflare\.com' cloudflare-tunnel.log | tail -1 | xargs)

if [ -n "$URL" ]; then
    echo "✓ Tunnel started successfully!"
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "  HTTPS URL: $URL"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    echo "Update your Moodle LTI configuration with:"
    echo "  - Tool URL: ${URL}/api/lti/launch"
    echo "  - Login URL: ${URL}/api/lti/login"
    echo "  - JWKS URL: ${URL}/api/lti/jwks"
    echo ""
    echo "PID: $TUNNEL_PID (saved to tunnel.pid)"
else
    echo "✗ Failed to get tunnel URL. Check cloudflare-tunnel.log"
    cat cloudflare-tunnel.log
fi
