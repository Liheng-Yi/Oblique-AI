# Vanessa AI - Simple Voice Agent Prototype

A minimal working prototype connecting Twilio Voice + OpenAI Realtime API for basic phone conversations.

## What This Does

Makes phone calls and has simple AI conversations. That's it!

1. You trigger a call via API
2. Twilio makes the call
3. OpenAI Realtime API handles the conversation
4. Basic "hi" and casual chat

## Quick Start

### Option 1: Docker (Recommended - No Multiple Terminals!)

```bash
# 1. Create your .env file
cp .env.example .env
# Edit .env with your API keys

# 2. Start everything with one command
docker compose up

# 3. Get ngrok URLs from http://localhost:4540 and http://localhost:4541
# 4. Update .env with those URLs and restart
```

📖 **[Full Docker Guide →](DOCKER.md)**

### Option 2: Manual Setup

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Configure (create .env file)
cp backend/env.example backend/.env
# Edit .env with your API keys

# Run
python app.py
```

## Make a Test Call

```bash
curl -X POST http://localhost:5000/call \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

## What You Need

1. **Twilio Account** (https://console.twilio.com)
   - Account SID
   - Auth Token  
   - Phone Number with Voice capability

2. **OpenAI API Key** (https://platform.openai.com)
   - Needs Realtime API access

3. **Python 3.9+**

## Architecture

```
Twilio ←→ Flask/WebSocket ←→ OpenAI Realtime API
        (Your Server)
```

Super simple. Audio flows bidirectionally through your server.

## Local Development

### With Docker (Easy!)
Docker Compose handles both ngrok tunnels automatically. See [DOCKER.md](DOCKER.md)

### Manual ngrok Setup
You need TWO ngrok tunnels (one for Flask port 5000, one for WebSocket port 6000):

```bash
# Terminal 1: Flask HTTP
ngrok http 5000

# Terminal 2: WebSocket
ngrok http 6000

# Update .env with both URLs
BASE_URL=https://abc123.ngrok.io
WEBSOCKET_URL=wss://xyz789.ngrok.io
```

## Files

```
backend/
├── app.py              # Main Flask app (simple!)
├── requirements.txt    # Python dependencies
├── env.example         # Environment variables template
├── Dockerfile          # Docker container config
└── README.md           # Backend-specific docs

docker-compose.yml      # Orchestrates all services
DOCKER.md              # Docker setup guide
```

## Customization

Edit the `SYSTEM_PROMPT` in `app.py` to change how Vanessa talks:

```python
SYSTEM_PROMPT = """You are Vanessa, a friendly AI assistant.

Your instructions here..."""
```

## Troubleshooting

- **Can't make calls?** Check Twilio credentials and phone number format
- **No audio?** Check OpenAI API key and WebSocket connection
- **Webhooks failing?** Make sure BASE_URL is publicly accessible (use ngrok)

## What's Next?

Once this basic version works, you can add:
- Lead qualification logic
- Call recording
- Database/logging
- Dashboard UI
- Multiple concurrent calls

But start simple! Get this working first. 🚀

---

**Stack:** Python + Flask + Twilio + OpenAI Realtime API
