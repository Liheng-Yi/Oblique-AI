# Docker Setup for Vanessa AI

This guide shows you how to run Vanessa AI using Docker Compose, which handles all the servers in one command.

## What Docker Compose Does

Instead of managing multiple terminals, Docker Compose runs:
- ✅ **vanessa-app**: Your Flask + WebSocket server (ports 5000 & 6000)
- ✅ **ngrok-http**: ngrok tunnel for Flask HTTP (port 5000)
- ✅ **ngrok-websocket**: ngrok tunnel for WebSocket (port 6000)

Everything runs with **one command**: `docker compose up`

## Prerequisites

1. **Install Docker Desktop**
   - Windows/Mac: https://www.docker.com/products/docker-desktop
   - Linux: https://docs.docker.com/engine/install/

2. **Get ngrok auth token**
   - Sign up at https://ngrok.com
   - Go to https://dashboard.ngrok.com/get-started/your-authtoken
   - Copy your authtoken

## Quick Start

### 1. Configure Environment

Create `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Required
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
NGROK_AUTHTOKEN=your_ngrok_authtoken

# Leave these commented out for now
# BASE_URL=https://abc123.ngrok.io
# WEBSOCKET_URL=wss://xyz789.ngrok.io
```

### 2. Start All Services

```bash
docker compose up
```

You'll see output from all three containers starting up.

### 3. Get Your ngrok URLs

Open these URLs in your browser to see the ngrok tunnels:

- **Flask HTTP tunnel**: http://localhost:4540
- **WebSocket tunnel**: http://localhost:4541

On each page, you'll see a "Forwarding" URL like:
- `https://abc123.ngrok.io` (Flask HTTP)
- `https://xyz789.ngrok.io` (WebSocket)

### 4. Update Your .env File

Stop the containers (`Ctrl+C`), then edit `.env`:

```env
BASE_URL=https://abc123.ngrok.io
WEBSOCKET_URL=wss://xyz789.ngrok.io
```

**Important**: Change `https://` to `wss://` for the WEBSOCKET_URL!

### 5. Restart with New URLs

```bash
docker compose up
```

### 6. Configure Twilio

- Go to Twilio Console → Phone Numbers → Your Number
- Set "A Call Comes In" webhook to: `{BASE_URL}/voice`
- Example: `https://abc123.ngrok.io/voice`

## Making a Call

### Option 1: Using curl

```bash
curl -X POST http://localhost:5000/call \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

### Option 2: Using the test script

```bash
# If running locally (not in Docker)
cd backend
python test_call.py +1234567890
```

## Docker Commands

```bash
# Start all services
docker compose up

# Start in background (detached mode)
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs

# View logs for specific service
docker compose logs vanessa-app
docker compose logs ngrok-http

# Rebuild after code changes
docker compose up --build

# Remove everything (containers, networks, images)
docker compose down --volumes --rmi all
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Docker Compose                      │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ ngrok-http   │  │ngrok-websocket│            │
│  │   :4040      │  │    :4041      │            │
│  └──────┬───────┘  └──────┬────────┘            │
│         │                 │                      │
│         └────────┬────────┘                      │
│                  │                               │
│         ┌────────▼────────┐                      │
│         │  vanessa-app    │                      │
│         │  Flask: 5000    │                      │
│         │  WebSocket: 6000│                      │
│         └─────────────────┘                      │
└─────────────────────────────────────────────────┘
           │
           ▼
    Twilio ↔ OpenAI
```

## Troubleshooting

### "No such file or directory: .env"
Create the `.env` file: `cp .env.example .env`

### "Invalid ngrok authtoken"
- Get your token from https://dashboard.ngrok.com
- Make sure it's set in `.env` as `NGROK_AUTHTOKEN=...`

### "Address already in use" or "Ports are not available"
Another service is using the ports, or Windows has restricted them.

**Check what's using the ports:**
```bash
# Windows
netstat -ano | findstr :5000

# Mac/Linux
lsof -i :5000
```

**Windows Port Restrictions:**
If you see "access permissions" errors, Windows may have reserved the port. We've changed ngrok web UI ports to 4540/4541 to avoid common restricted ports on Windows.

### ngrok tunnel URLs keep changing
Free ngrok tunnels get new URLs each restart. Solutions:
- Keep Docker running (don't restart)
- Upgrade to ngrok paid plan for static domains
- Use a script to auto-update Twilio webhook

### "Cannot connect to Docker daemon"
Make sure Docker Desktop is running.

### Code changes not reflecting
Rebuild the image:
```bash
docker compose up --build
```

### View real-time logs
```bash
docker compose logs -f vanessa-app
```

## Development Workflow

1. **Make code changes** in `backend/app.py`
2. **Rebuild**: `docker compose up --build`
3. **Test**: Make a call
4. **Check logs**: `docker compose logs -f`

## Production Deployment

For production, consider:
- Using a proper domain instead of ngrok
- Environment-specific `.env` files
- Hosting on AWS, GCP, or Azure
- Using managed services for ngrok alternatives
- Adding health checks and monitoring

## Notes

- ngrok free tier has connection limits
- The URLs change every time ngrok restarts
- For persistent URLs, use ngrok paid plan or deploy to cloud
- Both ngrok tunnels need to stay running while making calls

