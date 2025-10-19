#!/bin/bash

echo "🔍 VANESSA AI - COMPLETE SYSTEM DEBUG"
echo "======================================"
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Endpoint..."
response=$(curl -s -w "\n%{http_code}" http://localhost:5000/health)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✅ Health check passed"
    echo "Response: $body"
else
    echo "❌ Health check failed (HTTP $http_code)"
fi
echo ""

# Test 2: ngrok URLs
echo "2️⃣  Checking ngrok tunnels..."
echo "Flask HTTP tunnel (port 5000):"
flask_url=$(curl -s http://localhost:4540/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)
if [ -z "$flask_url" ]; then
    echo "❌ Cannot get Flask ngrok URL"
else
    echo "✅ Flask URL: $flask_url"
fi

echo ""
echo "WebSocket tunnel (port 6000):"
ws_url=$(curl -s http://localhost:4541/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)
if [ -z "$ws_url" ]; then
    echo "❌ Cannot get WebSocket ngrok URL"
else
    ws_https="$ws_url"
    ws_wss="${ws_https/https:/wss:}"
    echo "✅ WebSocket URL: $ws_wss"
fi
echo ""

# Test 3: Environment Check
echo "3️⃣  Checking .env configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    
    # Check for required variables (without showing sensitive values)
    if grep -q "TWILIO_ACCOUNT_SID=AC" .env; then
        echo "✅ TWILIO_ACCOUNT_SID configured"
    else
        echo "❌ TWILIO_ACCOUNT_SID missing or invalid"
    fi
    
    if grep -q "TWILIO_AUTH_TOKEN=" .env && [ $(grep "TWILIO_AUTH_TOKEN=" .env | cut -d'=' -f2 | wc -c) -gt 10 ]; then
        echo "✅ TWILIO_AUTH_TOKEN configured"
    else
        echo "❌ TWILIO_AUTH_TOKEN missing"
    fi
    
    if grep -q "TWILIO_PHONE_NUMBER=+" .env; then
        echo "✅ TWILIO_PHONE_NUMBER configured"
    else
        echo "❌ TWILIO_PHONE_NUMBER missing"
    fi
    
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        echo "✅ OPENAI_API_KEY configured"
    else
        echo "❌ OPENAI_API_KEY missing"
    fi
    
    # Check BASE_URL
    base_url=$(grep "^BASE_URL=" .env | cut -d'=' -f2)
    if [ -n "$base_url" ] && [ "$base_url" != "http://localhost:5000" ]; then
        echo "✅ BASE_URL set to: $base_url"
    else
        echo "⚠️  BASE_URL not set or using localhost (should be ngrok URL)"
        echo "   Current: $base_url"
        echo "   Should be: $flask_url"
    fi
    
    # Check WEBSOCKET_URL
    websocket_url=$(grep "^WEBSOCKET_URL=" .env | cut -d'=' -f2)
    if [ -n "$websocket_url" ] && [[ "$websocket_url" == wss://* ]]; then
        echo "✅ WEBSOCKET_URL set to: $websocket_url"
    else
        echo "⚠️  WEBSOCKET_URL not set correctly"
        echo "   Current: $websocket_url"
        echo "   Should be: $ws_wss"
    fi
    
else
    echo "❌ .env file not found!"
fi
echo ""

# Test 4: Docker logs check
echo "4️⃣  Checking for recent errors in Docker logs..."
errors=$(docker compose logs vanessa-app --tail=100 | grep -i "error\|exception\|failed" | tail -5)
if [ -z "$errors" ]; then
    echo "✅ No recent errors in logs"
else
    echo "⚠️  Recent errors found:"
    echo "$errors"
fi
echo ""

# Summary and Next Steps
echo "======================================"
echo "📋 NEXT STEPS:"
echo ""

if [ -n "$flask_url" ] && [ -n "$ws_wss" ]; then
    echo "1. Update your .env file with these URLs:"
    echo "   BASE_URL=$flask_url"
    echo "   WEBSOCKET_URL=$ws_wss"
    echo ""
    echo "2. Restart the app container:"
    echo "   docker compose restart vanessa-app"
    echo ""
    echo "3. Configure Twilio webhook:"
    echo "   Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming"
    echo "   Set webhook to: $flask_url/voice"
    echo ""
    echo "4. Make a test call:"
    echo "   curl -X POST http://localhost:5000/call \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"phone_number\": \"+1YOUR_NUMBER\"}'"
fi

echo ""
echo "5. Watch live logs:"
echo "   docker compose logs -f vanessa-app"

