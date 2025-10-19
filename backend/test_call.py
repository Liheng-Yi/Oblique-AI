"""
Simple test script to make a call
"""

import requests
import sys

def make_call(phone_number):
    """Make a test call"""
    url = "http://localhost:5000/call"
    
    response = requests.post(url, json={
        "phone_number": phone_number
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Call initiated!")
        print(f"Call SID: {data['call_sid']}")
        print(f"Status: {data['status']}")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_call.py +1234567890")
        sys.exit(1)
    
    phone = sys.argv[1]
    make_call(phone)
