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
from flask_sock import Sock
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
sock = Sock(app)

# Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
PORT = int(os.getenv('PORT', 5000))

# Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# System prompt - caring boyfriend persona
SYSTEM_PROMPT = """You are Cecilia's caring and attentive boyfriend. 

You're checking in on her because you're concerned about her neck pain. Be warm, loving, and genuinely interested in how she's feeling. Ask follow-up questions about her well-being.

Keep responses natural and conversational, like a real boyfriend would talk. Be supportive and caring.

Keep responses relatively short and natural - this is a phone conversation."""


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
            url=f'{BASE_URL}/voice'
            # Temporarily disabled status callback due to ngrok free tier
            # status_callback=f'{BASE_URL}/status',
            # status_callback_event=['initiated', 'ringing', 'answered', 'completed']
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
        # WebSocket runs on the same port as Flask (with flask-sock)
        ws_url = BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://')
        
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


# WebSocket handler for media streaming using flask-sock
@sock.route('/media/<call_sid>')
def handle_media_stream(ws, call_sid):
    """
    Handle WebSocket connection between Twilio and OpenAI
    This is where the magic happens - audio flows bidirectionally
    """
    print(f"\n{'='*60}", flush=True)
    print(f"🔌 WEBSOCKET CONNECTION ESTABLISHED", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"Call SID: {call_sid}", flush=True)
    print(f"WebSocket object: {ws}", flush=True)
    print(f"OPENAI_API_KEY present: {'Yes' if OPENAI_API_KEY else 'No'}", flush=True)
    
    # Create a new event loop for this WebSocket connection
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        print(f"Starting async handler...", flush=True)
        loop.run_until_complete(handle_media_stream_async(ws, call_sid))
    except Exception as e:
        print(f"\n❌ ERROR IN MEDIA STREAM:", flush=True)
        print(f"Error Type: {type(e).__name__}", flush=True)
        print(f"Error Message: {str(e)}", flush=True)
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}", flush=True)
        print(f"{'='*60}\n", flush=True)
    finally:
        loop.close()
        print(f"WebSocket handler finished for {call_sid}", flush=True)


async def handle_media_stream_async(ws, call_sid):
    """Async handler for WebSocket media streaming"""
    stream_sid = None  # Add this to store the streamSid
    
    try:
        # Connect to OpenAI Realtime API
        print(f"🔗 Connecting to OpenAI Realtime API...", flush=True)
        print(f"API Key : {OPENAI_API_KEY} ", flush=True)
        
        openai_ws = await websockets.connect(
            'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17',
            extra_headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'OpenAI-Beta': 'realtime=v1'
            }
        )
        
        print(f"✅ Connected to OpenAI for call {call_sid}", flush=True)
    
    except Exception as e:
        print(f"❌ ERROR CONNECTING TO OPENAI:", flush=True)
        print(f"Error Type: {type(e).__name__}", flush=True)
        print(f"Error Message: {str(e)}", flush=True)
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}", flush=True)
        print(f"{'='*60}\n", flush=True)
        return
    
    # Configure OpenAI session
    session_config = {
        'type': 'session.update',
        'session': {
            'modalities': ['text', 'audio'],
            'instructions': SYSTEM_PROMPT,
            'voice': 'echo',  # Male voice options: 'echo', 'fable', 'onyx'
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
        print("✅ OpenAI session configured", flush=True)
        
        # Send initial greeting to make AI speak first
        initial_message = {
            'type': 'conversation.item.create',
            'item': {
                'type': 'message',
                'role': 'user',
                'content': [
                    {
                        'type': 'input_text',
                        'text': 'Say: "Hi, Cecilia, I\'m your boyfriend. Does your neck still hurt?"'
                    }
                ]
            }
        }
        await openai_ws.send(json.dumps(initial_message))
        
        # Trigger the response
        response_create = {
            'type': 'response.create'
        }
        await openai_ws.send(json.dumps(response_create))
        print("✅ Initial greeting sent", flush=True)
        print(f"{'='*60}\n", flush=True)
        
    except Exception as e:
        print(f"❌ ERROR CONFIGURING OPENAI SESSION:", flush=True)
        print(f"Error Type: {type(e).__name__}", flush=True)
        print(f"Error Message: {str(e)}", flush=True)
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}", flush=True)
        print(f"{'='*60}\n", flush=True)
        return
    
    # Handle bidirectional streaming
    async def twilio_to_openai():
        """Forward audio from Twilio to OpenAI"""
        nonlocal stream_sid
        print(f"📥 Starting Twilio -> OpenAI stream", flush=True)
        try:
            while True:
                # Run synchronous ws.receive() in an executor to avoid blocking
                loop = asyncio.get_event_loop()
                message = await loop.run_in_executor(None, ws.receive)
                
                if message is None:
                    print(f"Twilio WebSocket closed", flush=True)
                    break
                    
                data = json.loads(message)
                print(f"📩 Twilio event: {data.get('event')}", flush=True)  # Debug
                
                if data.get('event') == 'start':
                    stream_sid = data['start']['streamSid']
                    print(f"✅ Twilio stream started: {stream_sid}", flush=True)
                
                elif data.get('event') == 'media':
                    # Forward audio to OpenAI
                    audio_payload = data['media']['payload']
                    await openai_ws.send(json.dumps({
                        'type': 'input_audio_buffer.append',
                        'audio': audio_payload
                    }))
                
                elif data.get('event') == 'stop':
                    print(f"⏹️ Twilio stream stopped", flush=True)
                    break
        
        except Exception as e:
            print(f"\n❌ Error in twilio_to_openai:", flush=True)
            print(f"Error Type: {type(e).__name__}", flush=True)
            print(f"Error Message: {str(e)}\n", flush=True)
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}", flush=True)
    
    async def openai_to_twilio():
        """Forward audio from OpenAI to Twilio"""
        print(f"📤 Starting OpenAI -> Twilio stream", flush=True)
        try:
            async for message in openai_ws:
                event = json.loads(message)
                print(f"📨 OpenAI event: {event['type']}", flush=True)
                
                if event['type'] == 'response.audio.delta':
                    print(f"🔊 Received audio delta from OpenAI (size: {len(event.get('delta', ''))})", flush=True)
                    # Forward audio to Twilio with streamSid
                    if stream_sid:  # Only send if we have the streamSid
                        ws.send(json.dumps({
                            'event': 'media',
                            'streamSid': stream_sid,
                            'media': {
                                'payload': event['delta']
                            }
                        }))
                        print(f"📤 Sent audio to Twilio", flush=True)
                    else:
                        print(f"⚠️ No streamSid yet, skipping audio", flush=True)
                
                elif event['type'] == 'conversation.item.input_audio_transcription.completed':
                    transcript = event.get('transcript', '')
                    print(f"👤 User said: {transcript}", flush=True)
                
                elif event['type'] == 'response.done':
                    output = event.get('response', {}).get('output', [])
                    if output:
                        content = output[0].get('content', [])
                        if content:
                            transcript = content[0].get('transcript', '')
                            if transcript:
                                print(f"🤖 Vanessa said: {transcript}", flush=True)
                
                elif event['type'] == 'error':
                    print(f"\n❌ OPENAI ERROR:", flush=True)
                    print(f"Error: {event.get('error', {})}", flush=True)
                    print()
        
        except Exception as e:
            print(f"\n❌ Error in openai_to_twilio:", flush=True)
            print(f"Error Type: {type(e).__name__}", flush=True)
            print(f"Error Message: {str(e)}\n", flush=True)
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}", flush=True)
    
    # Run both directions concurrently
    print(f"🔄 Starting bidirectional streaming...", flush=True)
    try:
        await asyncio.gather(
            twilio_to_openai(),
            openai_to_twilio()
        )
        print(f"✅ Streaming completed normally", flush=True)
    except Exception as e:
        print(f"\n❌ ERROR IN STREAMING:", flush=True)
        print(f"Error Type: {type(e).__name__}", flush=True)
        print(f"Error Message: {str(e)}", flush=True)
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}", flush=True)
    finally:
        await openai_ws.close()
        print(f"\n🔌 OpenAI connection closed for call {call_sid}", flush=True)
        print(f"{'='*60}\n", flush=True)


if __name__ == '__main__':
    # Start Flask app with WebSocket support
    print(f"🚀 Vanessa AI Server starting on port {PORT}")
    print(f"📞 Make calls to: POST {BASE_URL}/call")
    print(f"🔌 WebSocket available at: ws://<your-domain>:{PORT}/media/<call_sid>")
    print(f"\nNote: Both HTTP and WebSocket run on the same port ({PORT})")
    
    # In production/Docker, disable the reloader
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    use_reloader = os.getenv('FLASK_USE_RELOADER', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=PORT, debug=debug_mode, use_reloader=use_reloader)

