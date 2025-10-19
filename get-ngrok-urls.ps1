# Helper script to get ngrok URLs from running containers (Windows PowerShell)

Write-Host "🔍 Getting ngrok tunnel URLs..." -ForegroundColor Cyan
Write-Host ""

Write-Host "📞 Flask HTTP Tunnel (port 5000):" -ForegroundColor Green
$httpUrl = (Invoke-RestMethod -Uri http://localhost:4540/api/tunnels).tunnels | Where-Object { $_.public_url -like "https://*" } | Select-Object -First 1 -ExpandProperty public_url
Write-Host $httpUrl
Write-Host ""

Write-Host "🔌 WebSocket Tunnel (port 6000):" -ForegroundColor Green
$wsUrl = (Invoke-RestMethod -Uri http://localhost:4541/api/tunnels).tunnels | Where-Object { $_.public_url -like "https://*" } | Select-Object -First 1 -ExpandProperty public_url
$wsUrl = $wsUrl -replace "https://", "wss://"
Write-Host $wsUrl
Write-Host ""

Write-Host "💡 Update your .env file with these URLs:" -ForegroundColor Yellow
Write-Host "BASE_URL=$httpUrl"
Write-Host "WEBSOCKET_URL=$wsUrl"

