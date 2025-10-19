# PowerShell Debug Script for Vanessa AI

Write-Host "`n🔍 VANESSA AI - COMPLETE SYSTEM DEBUG" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "1️⃣  Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri http://localhost:5000/health
    Write-Host "✅ Health check passed" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: ngrok URLs
Write-Host "2️⃣  Checking ngrok tunnels..." -ForegroundColor Yellow
Write-Host "Flask HTTP tunnel (port 5000):" -ForegroundColor Gray
try {
    $flaskTunnels = Invoke-RestMethod -Uri http://localhost:4540/api/tunnels
    $flaskUrl = $flaskTunnels.tunnels | Where-Object { $_.public_url -like "https://*" } | Select-Object -First 1 -ExpandProperty public_url
    if ($flaskUrl) {
        Write-Host "✅ Flask URL: $flaskUrl" -ForegroundColor Green
    } else {
        Write-Host "❌ Cannot get Flask ngrok URL" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Cannot connect to Flask ngrok: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "WebSocket tunnel (port 6000):" -ForegroundColor Gray
try {
    $wsTunnels = Invoke-RestMethod -Uri http://localhost:4541/api/tunnels
    $wsUrl = $wsTunnels.tunnels | Where-Object { $_.public_url -like "https://*" } | Select-Object -First 1 -ExpandProperty public_url
    if ($wsUrl) {
        $wsWss = $wsUrl -replace "https://", "wss://"
        Write-Host "✅ WebSocket URL: $wsWss" -ForegroundColor Green
    } else {
        Write-Host "❌ Cannot get WebSocket ngrok URL" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Cannot connect to WebSocket ngrok: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Environment Check
Write-Host "3️⃣  Checking .env configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
    
    $envContent = Get-Content .env -Raw
    
    if ($envContent -match "TWILIO_ACCOUNT_SID=AC") {
        Write-Host "✅ TWILIO_ACCOUNT_SID configured" -ForegroundColor Green
    } else {
        Write-Host "❌ TWILIO_ACCOUNT_SID missing or invalid" -ForegroundColor Red
    }
    
    if ($envContent -match "TWILIO_AUTH_TOKEN=\w{20,}") {
        Write-Host "✅ TWILIO_AUTH_TOKEN configured" -ForegroundColor Green
    } else {
        Write-Host "❌ TWILIO_AUTH_TOKEN missing" -ForegroundColor Red
    }
    
    if ($envContent -match "TWILIO_PHONE_NUMBER=\+") {
        Write-Host "✅ TWILIO_PHONE_NUMBER configured" -ForegroundColor Green
    } else {
        Write-Host "❌ TWILIO_PHONE_NUMBER missing" -ForegroundColor Red
    }
    
    if ($envContent -match "OPENAI_API_KEY=sk-") {
        Write-Host "✅ OPENAI_API_KEY configured" -ForegroundColor Green
    } else {
        Write-Host "❌ OPENAI_API_KEY missing" -ForegroundColor Red
    }
    
    # Check BASE_URL
    if ($envContent -match "BASE_URL=(.+)") {
        $baseUrl = $matches[1].Trim()
        if ($baseUrl -and $baseUrl -ne "http://localhost:5000") {
            Write-Host "✅ BASE_URL set to: $baseUrl" -ForegroundColor Green
        } else {
            Write-Host "⚠️  BASE_URL not set or using localhost" -ForegroundColor Yellow
            Write-Host "   Current: $baseUrl" -ForegroundColor Gray
            if ($flaskUrl) {
                Write-Host "   Should be: $flaskUrl" -ForegroundColor Gray
            }
        }
    }
    
    # Check WEBSOCKET_URL
    if ($envContent -match "WEBSOCKET_URL=(.+)") {
        $websocketUrl = $matches[1].Trim()
        if ($websocketUrl -like "wss://*") {
            Write-Host "✅ WEBSOCKET_URL set to: $websocketUrl" -ForegroundColor Green
        } else {
            Write-Host "⚠️  WEBSOCKET_URL not set correctly" -ForegroundColor Yellow
            Write-Host "   Current: $websocketUrl" -ForegroundColor Gray
            if ($wsWss) {
                Write-Host "   Should be: $wsWss" -ForegroundColor Gray
            }
        }
    }
    
} else {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
}
Write-Host ""

# Test 4: Docker logs check
Write-Host "4️⃣  Checking for recent errors in Docker logs..." -ForegroundColor Yellow
$logs = docker compose logs vanessa-app --tail=100 2>&1 | Select-String -Pattern "error|exception|failed" -CaseSensitive:$false | Select-Object -Last 5
if ($logs) {
    Write-Host "⚠️  Recent errors found:" -ForegroundColor Yellow
    $logs | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
} else {
    Write-Host "✅ No recent errors in logs" -ForegroundColor Green
}
Write-Host ""

# Summary and Next Steps
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""

if ($flaskUrl -and $wsWss) {
    Write-Host "1. Update your .env file with these URLs:" -ForegroundColor White
    Write-Host "   BASE_URL=$flaskUrl" -ForegroundColor Gray
    Write-Host "   WEBSOCKET_URL=$wsWss" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Restart the app container:" -ForegroundColor White
    Write-Host "   docker compose restart vanessa-app" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Configure Twilio webhook:" -ForegroundColor White
    Write-Host "   Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming" -ForegroundColor Gray
    Write-Host "   Set webhook to: $flaskUrl/voice" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Make a test call:" -ForegroundColor White
    Write-Host "   curl -X POST http://localhost:5000/call ``" -ForegroundColor Gray
    Write-Host "     -H 'Content-Type: application/json' ``" -ForegroundColor Gray
    Write-Host "     -d '{`"phone_number`": `"+1YOUR_NUMBER`"}'" -ForegroundColor Gray
}

Write-Host ""
Write-Host "5. Watch live logs:" -ForegroundColor White
Write-Host "   docker compose logs -f vanessa-app" -ForegroundColor Gray

