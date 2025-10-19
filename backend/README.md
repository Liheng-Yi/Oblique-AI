# Vanessa AI - Simple Prototype

A minimal voice AI agent that connects Twilio and OpenAI Realtime API for basic phone conversations.

## What It Does

- Makes outbound phone calls via Twilio
- Streams audio to/from OpenAI Realtime API
- Has a simple conversation (says hi and chats)

That's it! No complex features, just the basics working.

## Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create `backend/.env` (copy from `env.example`):

```env
# Twilio (get from https://console.twilio.com)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# OpenAI (get from https://platform.openai.com)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# Server
PORT=5000
BASE_URL=http://localhost:5000
WEBSOCKET_URL=ws://localhost:6000
```

**Important:** `BASE_URL` is for Flask HTTP (port 5000), `WEBSOCKET_URL` is for WebSocket streaming (port 6000).

### 3. Run the Server

```bash
python app.py
```

Server starts on port 5000 (Flask) and 6000 (WebSocket).

## Make a Call

```bash
curl -X POST http://localhost:5000/call \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

## How It Works

```
1. POST /call → Twilio initiates call
2. Twilio calls /voice webhook → Returns TwiML to connect WebSocket
3. WebSocket connects Twilio ↔ OpenAI
4. Audio streams bidirectionally
5. OpenAI responds with voice
6. Conversation happens!
```

## Architecture

```
┌─────────┐       ┌─────────┐       ┌─────────┐
│ Twilio  │←─────→│ Flask   │←─────→│ OpenAI  │
│ Voice   │ Audio │WebSocket│ Audio │Realtime │
└─────────┘       └─────────┘       └─────────┘
```

## Endpoints

- `GET /health` - Health check
- `POST /call` - Initiate a call
- `GET|POST /voice` - Twilio voice webhook (TwiML)
- `POST /status` - Twilio status callback
- `WS /media/:call_sid` - WebSocket for audio streaming (port 6000)

## Testing Locally

For local testing, you'll need to expose your server to the internet so Twilio can reach your webhooks.

### Option 1: ngrok (Requires 2 tunnels!)

Since we run Flask (port 5000) and WebSocket (port 6000) on separate ports, you need **TWO ngrok tunnels**:

```bash
# Terminal 1: Tunnel for Flask HTTP
ngrok http 5000

# Terminal 2: Tunnel for WebSocket
ngrok http 6000
```

Then update your `.env`:

```env
BASE_URL=https://abc123.ngrok.io         # From terminal 1
WEBSOCKET_URL=wss://xyz789.ngrok.io      # From terminal 2
```

**Configure Twilio:**
- Go to your Twilio phone number settings
- Set "A Call Comes In" webhook to: `https://abc123.ngrok.io/voice` (your BASE_URL + /voice)

### Option 2: Deploy to cloud (Heroku, Railway, etc.)

Make sure your deployment exposes both ports or combines them into one server.

## Customizing

Edit `SYSTEM_PROMPT` in `app.py` to change Vanessa's personality or instructions:

```python
SYSTEM_PROMPT = """You are Vanessa, a friendly AI assistant. 

Your custom instructions here...
"""
```

## Troubleshooting

**"Connection refused"**
- Make sure both Flask (5000) and WebSocket (6000) servers are running
- Check both ngrok tunnels are active

**"No audio"**
- Check OpenAI API key is valid
- Check Twilio account has credit
- Check WEBSOCKET_URL is correctly set to your WebSocket ngrok tunnel
- Verify the WebSocket URL uses `wss://` (not `https://`)

**"Call doesn't connect"**
- Check Twilio credentials
- Check phone number is in E.164 format (+1234567890)
- Check webhook URLs are publicly accessible
- Verify Twilio webhook points to `{BASE_URL}/voice`

**"WebSocket fails to connect"**
- Ensure you have TWO separate ngrok tunnels running
- BASE_URL should point to port 5000 ngrok
- WEBSOCKET_URL should point to port 6000 ngrok
- Don't mix them up!

## Next Steps

Once this works, you can add:
- Call recording
- Conversation logging
- Multiple phone numbers
- Call routing
- Web dashboard

But first, just get this basic version working! 🚀

