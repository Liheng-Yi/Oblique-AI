"""
Vanessa AI - Minimal Voice Agent
Simple Flask app connecting Twilio + OpenAI Realtime API
"""

import os
import asyncio
import websockets
import json
import base64
from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect
from dotenv import load_dotenv
from threading import Thread

load_dotenv()

app = Flask(__name__)

# Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL', 'ws://localhost:6000')
PORT = int(os.getenv('PORT', 5000))

# Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Simple system prompt - just say hi and have a basic conversation
SYSTEM_PROMPT = """You are Vanessa, a friendly AI assistant. 

Keep the conversation simple and natural. Say hi, introduce yourself briefly, and have a casual conversation. Be warm and friendly.

Example opening: "Hi! This is Vanessa. How are you doing today?"

Keep responses short and conversational."""


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Vanessa AI - Simple Prototype'
    })


@app.route('/call', methods=['POST'])
def initiate_call():
    """Initiate an outbound call"""
    data = request.json
    phone_number = data.get('phone_number')
    
    print(f"\n{'='*60}")
    print(f"📞 INITIATING CALL")
    print(f"{'='*60}")
    print(f"To: {phone_number}")
    print(f"From: {TWILIO_PHONE_NUMBER}")
    print(f"Webhook URL: {BASE_URL}/voice")
    
    if not phone_number:
        error_msg = 'phone_number is required'
        print(f"❌ ERROR: {error_msg}\n")
        return jsonify({'error': error_msg}), 400
    
    try:
        # Make the call via Twilio
        call = twilio_client.calls.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            url=f'{BASE_URL}/voice',
            status_callback=f'{BASE_URL}/status',
            status_callback_event=['initiated', 'ringing', 'answered', 'completed']
        )
        
        print(f"✅ Call initiated successfully!")
        print(f"Call SID: {call.sid}")
        print(f"Status: {call.status}")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'call_sid': call.sid,
            'status': call.status
        })
    
    except Exception as e:
        print(f"❌ ERROR INITIATING CALL:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"{'='*60}\n")
        return jsonify({'error': str(e)}), 500


@app.route('/voice', methods=['GET', 'POST'])
def voice():
    """Twilio voice webhook - connects call to WebSocket"""
    call_sid = request.form.get('CallSid', 'unknown')
    call_from = request.form.get('From', 'unknown')
    call_to = request.form.get('To', 'unknown')
    
    print(f"\n{'='*60}")
    print(f"📱 VOICE WEBHOOK TRIGGERED")
    print(f"{'='*60}")
    print(f"Call SID: {call_sid}")
    print(f"From: {call_from}")
    print(f"To: {call_to}")
    
    try:
        response = VoiceResponse()
        
        # Connect to WebSocket for audio streaming
        # Use the separate WEBSOCKET_URL (port 6000) not the BASE_URL (port 5000)
        ws_url = WEBSOCKET_URL.replace('http://', 'ws://').replace('https://', 'wss://')
        
        print(f"WebSocket URL: {ws_url}/media/{call_sid}")
        
        connect = Connect()
        connect.stream(url=f'{ws_url}/media/{call_sid}')
        
        response.append(connect)
        
        twiml = str(response)
        print(f"✅ TwiML Response Generated:")
        print(twiml)
        print(f"{'='*60}\n")
        
        return twiml, 200, {'Content-Type': 'text/xml'}
    
    except Exception as e:
        print(f"❌ ERROR IN VOICE WEBHOOK:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"{'='*60}\n")
        raise


@app.route('/status', methods=['POST'])
def status():
    """Twilio status callback"""
    call_sid = request.form.get('CallSid')
    call_status = request.form.get('CallStatus')
    error_code = request.form.get('ErrorCode')
    error_message = request.form.get('ErrorMessage')
    
    print(f"\n{'='*60}")
    print(f"📊 CALL STATUS UPDATE")
    print(f"{'='*60}")
    print(f"Call SID: {call_sid}")
    print(f"Status: {call_status}")
    
    if error_code:
        print(f"❌ ERROR CODE: {error_code}")
        print(f"❌ ERROR MESSAGE: {error_message}")
    
    print(f"{'='*60}\n")
    
    return '', 200


# WebSocket handler for media streaming
async def handle_media_stream(websocket, path):
    """
    Handle WebSocket connection between Twilio and OpenAI
    This is where the magic happens - audio flows bidirectionally
    """
    call_sid = path.split('/')[-1] if '/' in path else 'unknown'
    
    print(f"\n{'='*60}")
    print(f"🔌 WEBSOCKET CONNECTION ESTABLISHED")
    print(f"{'='*60}")
    print(f"Path: {path}")
    print(f"Call SID: {call_sid}")
    
    try:
        # Connect to OpenAI Realtime API
        print(f"🔗 Connecting to OpenAI Realtime API...")
        openai_ws = await websockets.connect(
            'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
            extra_headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'OpenAI-Beta': 'realtime=v1'
            }
        )
        
        print(f"✅ Connected to OpenAI for call {call_sid}")
    
    except Exception as e:
        print(f"❌ ERROR CONNECTING TO OPENAI:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"{'='*60}\n")
        return
    
    # Configure OpenAI session
    session_config = {
        'type': 'session.update',
        'session': {
            'modalities': ['text', 'audio'],
            'instructions': SYSTEM_PROMPT,
            'voice': 'alloy',
            'input_audio_format': 'g711_ulaw',
            'output_audio_format': 'g711_ulaw',
            'input_audio_transcription': {
                'model': 'whisper-1'
            },
            'turn_detection': {
                'type': 'server_vad',
                'threshold': 0.5,
                'prefix_padding_ms': 300,
                'silence_duration_ms': 500
            },
            'temperature': 0.8
        }
    }
    
    try:
        await openai_ws.send(json.dumps(session_config))
        print("✅ OpenAI session configured")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"❌ ERROR CONFIGURING OPENAI SESSION:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"{'='*60}\n")
        return
    
    # Handle bidirectional streaming
    async def twilio_to_openai():
        """Forward audio from Twilio to OpenAI"""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data.get('event') == 'start':
                    print(f"Twilio stream started: {data.get('streamSid')}")
                
                elif data.get('event') == 'media':
                    # Forward audio to OpenAI
                    audio_payload = data['media']['payload']
                    await openai_ws.send(json.dumps({
                        'type': 'input_audio_buffer.append',
                        'audio': audio_payload
                    }))
                
                elif data.get('event') == 'stop':
                    print("Twilio stream stopped")
                    break
        
        except Exception as e:
            print(f"\n❌ Error in twilio_to_openai:")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}\n")
    
    async def openai_to_twilio():
        """Forward audio from OpenAI to Twilio"""
        try:
            async for message in openai_ws:
                event = json.loads(message)
                
                if event['type'] == 'response.audio.delta':
                    # Forward audio to Twilio
                    await websocket.send(json.dumps({
                        'event': 'media',
                        'media': {
                            'payload': event['delta']
                        }
                    }))
                
                elif event['type'] == 'conversation.item.input_audio_transcription.completed':
                    transcript = event.get('transcript', '')
                    print(f"👤 User said: {transcript}")
                
                elif event['type'] == 'response.done':
                    output = event.get('response', {}).get('output', [])
                    if output:
                        content = output[0].get('content', [])
                        if content:
                            transcript = content[0].get('transcript', '')
                            if transcript:
                                print(f"🤖 Vanessa said: {transcript}")
                
                elif event['type'] == 'error':
                    print(f"\n❌ OPENAI ERROR:")
                    print(f"Error: {event.get('error', {})}")
                    print()
        
        except Exception as e:
            print(f"\n❌ Error in openai_to_twilio:")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}\n")
    
    # Run both directions concurrently
    try:
        await asyncio.gather(
            twilio_to_openai(),
            openai_to_twilio()
        )
    except Exception as e:
        print(f"\n❌ ERROR IN MEDIA STREAM:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"{'='*60}\n")
    finally:
        await openai_ws.close()
        print(f"\n🔌 OpenAI connection closed for call {call_sid}")
        print(f"{'='*60}\n")


def run_websocket_server():
    """Run WebSocket server in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    start_server = websockets.serve(handle_media_stream, '0.0.0.0', 6000)
    
    print("WebSocket server started on port 6000")
    loop.run_until_complete(start_server)
    loop.run_forever()


if __name__ == '__main__':
    # Start WebSocket server in background
    ws_thread = Thread(target=run_websocket_server, daemon=True)
    ws_thread.start()
    
    # Start Flask app
    print(f"🚀 Vanessa AI Server starting on port {PORT}")
    print(f"📞 Make calls to: POST {BASE_URL}/call")
    
    # In production/Docker, disable the reloader to prevent WebSocket port conflicts
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    use_reloader = os.getenv('FLASK_USE_RELOADER', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=PORT, debug=debug_mode, use_reloader=use_reloader)

