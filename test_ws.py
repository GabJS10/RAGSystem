import asyncio
import os
import jwt
import websockets
import json
import time
from dotenv import load_dotenv

import uuid

# Load .env from current directory
load_dotenv()

SECRET = os.getenv("SUPABASE_JWT_SECRET")

def generate_token(user_id):
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + 3600,
        "aud": "authenticated",
        "role": "authenticated" # Supabase often expects this
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

async def test():
    user_id = str(uuid.uuid4())
    token = generate_token(user_id)
    # Ensure correct path. router prefix is /api/supabase
    uri = f"ws://localhost:8000/api/supabase/ws?token={token}"
    
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Send a question
            question = {
                "question": "Que es este sistema?",
                "top_k": 2,
                "conversation_id": None
            }
            print(f"Sending: {question}")
            await websocket.send(json.dumps(question))
            
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    msg_type = data.get('type')
                    content = data.get('data')
                    
                    if msg_type == 'token':
                        print(content, end="", flush=True)
                    else:
                        print(f"\n[{msg_type}]: {content}")
                    
                    if msg_type == 'done':
                        print("\nDone.")
                        break
                    if msg_type == 'error':
                        print("\nError received.")
                        break
                except websockets.exceptions.ConnectionClosed:
                    print("\nConnection closed")
                    break
    except Exception as e:
        print(f"\nFailed to connect or run: {e}")

if __name__ == "__main__":
    if not SECRET:
        print("Error: SUPABASE_JWT_SECRET not found in environment. Make sure .env exists.")
    else:
        asyncio.run(test())
