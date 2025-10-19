#!/bin/bash

# Helper script to get ngrok URLs from running containers

echo "🔍 Getting ngrok tunnel URLs..."
echo ""

echo "📞 Flask HTTP Tunnel (port 5000):"
curl -s http://localhost:4540/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1
echo ""

echo "🔌 WebSocket Tunnel (port 6000):"
curl -s http://localhost:4541/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1 | sed 's/https:/wss:/'
echo ""

echo "💡 Update your .env file with these URLs:"
echo "BASE_URL=<Flask HTTP URL>"
echo "WEBSOCKET_URL=<WebSocket URL with wss://>"

