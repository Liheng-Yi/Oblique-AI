# Vanessa AI - Simple Voice Agent Prototype

A minimal working prototype connecting Twilio Voice + OpenAI Realtime API for basic phone conversations.

## What This Does

Makes phone calls and has simple AI conversations. That's it!

1. You trigger a call via API
2. Twilio makes the call
3. OpenAI Realtime API handles the conversation
4. Basic "hi" and casual chat

## Quick Start

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Configure (create .env file)
cp .env.example .env
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

For Twilio to reach your webhooks locally, use ngrok:

```bash
ngrok http 5000

# Update .env with ngrok URL
BASE_URL=https://xxxx.ngrok-free.app
```

## Files

```
backend/
├── app.py              # Main Flask app (simple!)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # Backend-specific docs
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
