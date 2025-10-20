# Vanessa AI - Simple Voice Agent Prototype

A voice AI prototype that connects Twilio Voice with OpenAI's Realtime API to conduct phone conversations with property owners, qualifying leads by asking if they're interested in selling their real estate.

## What This Does

Makes phone calls and has smooth, natural AI conversations for lead qualification.

1. You trigger a call via API
2. Twilio makes the call
3. OpenAI Realtime API conducts the conversation
4. AI engages in natural dialogue to qualify property selling interest

## Quick Start (Docker Only)

```bash
# 1. Create your .env file
cp .env.example .env
# Edit .env with your API keys

# 2. Start everything with one command
docker compose up

# 3. Get ngrok URL from http://localhost:4540
# 4. Update .env with that URL and restart
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

3. **Docker & Docker Compose** - to run everything in containers

## Architecture

```
Twilio ←→ Flask Server ←→ OpenAI Realtime API
      (Single Port via Docker + ngrok)
```

Super simple. Audio flows bidirectionally through your server on a single port.

## Local Development

Docker Compose handles the ngrok tunnel automatically - everything runs on one port (5000).

## Files

```
backend/
├── app.py              # Main Flask app (simple!)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── Dockerfile          # Docker container config
└── README.md           # Backend-specific docs

docker-compose.yml      # Orchestrates all services
```

## Customization

Edit the `SYSTEM_PROMPT` in `app.py` to change how Vanessa talks:

```python
SYSTEM_PROMPT = """You are Vanessa, a friendly AI assistant.

Your instructions here..."""
```

**Stack:** Python + Flask + Twilio + OpenAI Realtime API
