# Quick Start with Docker - 5 Minutes Setup

## Step 1: Get Your API Keys

1. **Twilio** → https://console.twilio.com
   - Copy Account SID
   - Copy Auth Token
   - Get a phone number

2. **OpenAI** → https://platform.openai.com
   - Copy API Key

3. **ngrok** → https://dashboard.ngrok.com
   - Sign up (free)
   - Copy your Auth Token

## Step 2: Configure

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env` and paste your keys:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
NGROK_AUTHTOKEN=xxxxxxxxxxxxx
```

## Step 3: Start Everything

```bash
docker compose up
```

Wait ~30 seconds for everything to start.

## Step 4: Get ngrok URLs

Open in your browser:
- http://localhost:4540 (Flask HTTP tunnel)
- http://localhost:4541 (WebSocket tunnel)

Copy the "Forwarding" URLs you see.

**OR** use the helper script:

```bash
# Mac/Linux
bash get-ngrok-urls.sh

# Windows PowerShell
.\get-ngrok-urls.ps1
```

## Step 5: Update .env

Stop Docker (`Ctrl+C`), then edit `.env`:

```env
BASE_URL=https://abc123.ngrok.io
WEBSOCKET_URL=wss://xyz789.ngrok.io
```

⚠️ **Important**: Change `https://` to `wss://` for WEBSOCKET_URL!

Restart:

```bash
docker compose up
```

## Step 6: Configure Twilio

1. Go to https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click your phone number
3. Under "Voice Configuration"
4. Set "A CALL COMES IN" to: **Webhook**
5. Paste: `https://your-base-url.ngrok.io/voice`
6. Click Save

## Step 7: Make a Test Call! 🎉

```bash
curl -X POST http://localhost:5000/call \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1YOUR_PHONE_NUMBER"}'
```

**Replace** `+1YOUR_PHONE_NUMBER` with your actual number!

Your phone should ring, and Vanessa should say hi! 🎊

## Troubleshooting

### "Ports are not available" (Windows)
- Windows may have restricted certain ports
- The updated docker-compose.yml uses ports 4540/4541 to avoid this
- If you still have issues, try restarting Docker Desktop

### "Invalid ngrok authtoken"
- Make sure NGROK_AUTHTOKEN in .env is correct
- Get it from https://dashboard.ngrok.com

### "Call connects but no audio"
- Check WEBSOCKET_URL in .env
- Make sure it starts with `wss://` not `https://`
- Verify both ngrok tunnels are running

### "Call doesn't connect at all"
- Check Twilio webhook is set correctly
- Should be: `{BASE_URL}/voice`
- Make sure BASE_URL uses `https://`

### Still stuck?
Check the logs:

```bash
docker compose logs -f vanessa-app
```

## Next Steps

Once this works:
1. Customize Vanessa's personality in `backend/app.py` (line 33)
2. Add call recording
3. Build a dashboard
4. Add lead qualification logic

Read [DOCKER.md](DOCKER.md) for more details!

