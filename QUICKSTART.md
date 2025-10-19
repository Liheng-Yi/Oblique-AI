# Quick Start - Get Vanessa Working in 5 Minutes

## 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 2. Get API Keys

### Twilio
1. Go to https://console.twilio.com
2. Sign up (free trial gives you credit)
3. Get a phone number with Voice capability
4. Copy your Account SID and Auth Token

### OpenAI
1. Go to https://platform.openai.com
2. Sign up and add payment method
3. Get API key from https://platform.openai.com/api-keys
4. Make sure you have Realtime API access

## 3. Configure Environment

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your real credentials:
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
PORT=5000
BASE_URL=http://localhost:5000
```

## 4. For Local Testing - Use ngrok

Twilio needs to reach your webhooks. Use ngrok:

```bash
# Install ngrok from https://ngrok.com
ngrok http 5000
```

Copy the ngrok URL (e.g., `https://xxxx-xx-xxx.ngrok-free.app`) and update `.env`:
```env
BASE_URL=https://xxxx-xx-xxx.ngrok-free.app
```

**Important:** Also update your ngrok URL for the WebSocket (port 6000):
```bash
# In another terminal
ngrok http 6000
```

## 5. Run the Server

```bash
python app.py
```

You should see:
```
🚀 Vanessa AI Server starting on port 5000
📞 Make calls to: POST http://localhost:5000/call
WebSocket server started on port 6000
```

## 6. Make a Test Call

### Using curl:
```bash
curl -X POST http://localhost:5000/call \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

### Using the test script:
```bash
python test_call.py +1234567890
```

## 7. Answer the Call!

Pick up your phone and talk to Vanessa! She'll say hi and have a basic conversation with you.

## Troubleshooting

### "No module named flask"
```bash
pip install -r requirements.txt
```

### "Connection refused" or webhooks failing
- Make sure ngrok is running
- Update BASE_URL in .env with ngrok URL
- Restart the server after changing .env

### "Call connects but no audio"
- Check OpenAI API key is valid
- Check you have Realtime API access
- Check WebSocket is accessible (port 6000 via ngrok)

### "Twilio error"
- Verify Account SID and Auth Token
- Check phone number format: +1234567890 (include country code)
- Check Twilio account has credit (trial gives free credit)

## What's Happening?

```
1. POST /call → Server asks Twilio to call the number
2. Twilio calls your phone
3. When answered, Twilio hits /voice webhook
4. /voice returns TwiML telling Twilio to connect to WebSocket
5. WebSocket bridges audio: Twilio ←→ OpenAI
6. OpenAI processes audio and responds with voice
7. Conversation happens in real-time!
```

## Next Steps

Once it works:
1. Customize `SYSTEM_PROMPT` in `app.py`
2. Add your own conversation logic
3. Build features on top (recording, logging, etc.)

**But first - just get it working!** 🎉

