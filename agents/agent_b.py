#!/usr/bin/env python3
"""
Agent B (Genuine Responder) - Responds to handshake challenges authentically
"""

import requests
import time
import hmac
import hashlib
import secrets
import sys
from typing import Dict, Optional


class AgentB:
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.agent_id = "agent_b"
        self.secret_seed = secrets.token_hex(32).encode()  # Generate secret for HMAC
    
    def register_self(self) -> bool:
        """Register this agent with the backend"""
        try:
            response = requests.post(f"{self.backend_url}/register_agent", json={
                "agent_id": self.agent_id,
                "agent_type": "genuine",
                "secret_seed": self.secret_seed.decode()
            })
            
            if response.status_code == 200:
                print(f"✅ Agent B registered successfully")
                print(f"🔑 Secret seed: {self.secret_seed.decode()[:16]}...")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def respond_to_handshake(self, handshake_id: str, nonce: str) -> bool:
        """Respond to handshake challenge with HMAC signature"""
        try:
            print(f"\n🤝 Responding to handshake {handshake_id}...")
            print(f"🎲 Nonce received: {nonce}")
            
            # Generate HMAC-SHA256 signature
            signature = hmac.new(
                self.secret_seed,
                nonce.encode(),
                hashlib.sha256
            ).hexdigest()
            
            print(f"🔏 Generated signature: {signature[:16]}...")
            
            response = requests.post(f"{self.backend_url}/handshake/respond", json={
                "handshake_id": handshake_id,
                "signature": signature,
                "responder_id": self.agent_id
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Handshake response sent successfully")
                print(f"🔍 Signature valid: {result['signature_valid']}")
                return result["signature_valid"]
            else:
                print(f"❌ Handshake response failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Handshake error: {e}")
            return False
    
    def listen_for_handshakes(self, duration: int = 30) -> bool:
        """Listen for incoming handshake requests (polling simulation)"""
        print(f"\n👂 Listening for handshakes for {duration} seconds...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                # Check for pending handshakes (in real implementation, use WebSocket)
                response = requests.get(f"{self.backend_url}/logs")
                if response.status_code == 200:
                    logs = response.json()["logs"]
                    
                    # Look for handshake_started events for this agent
                    for log in logs[-5:]:  # Check last 5 logs
                        if (log["event_type"] == "handshake_started" and 
                            log["data"].get("responder_id") == self.agent_id):
                            
                            handshake_id = log["data"]["handshake_id"]
                            nonce = log["data"]["nonce"]
                            
                            print(f"\n📨 Received handshake request!")
                            return self.respond_to_handshake(handshake_id, nonce)
                
                time.sleep(2)  # Poll every 2 seconds
                print(".", end="", flush=True)
            
            except Exception as e:
                print(f"\n❌ Listening error: {e}")
                break
        
        print(f"\n⏰ Listening timeout after {duration} seconds")
        return False
    
    def chat_with_agent(self, message: str) -> Optional[str]:
        """Chat with AI using OpenAI API"""
        try:
            response = requests.post(f"{self.backend_url}/chat", json={
                "agent_id": self.agent_id,
                "message": message
            })
            
            if response.status_code == 200:
                result = response.json()
                return result["content"]
            else:
                return f"Chat error: {response.text}"
        except Exception as e:
            return f"Chat error: {e}"
    
    def get_status(self) -> Dict:
        """Get backend status"""
        try:
            response = requests.get(f"{self.backend_url}/status")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text}
        except Exception as e:
            return {"error": str(e)}


def main():
    """Demo script for Agent B"""
    print("🤖 Agent B (Genuine Responder) - AI Verification Protocol Demo")
    print("=" * 55)
    
    agent_b = AgentB()
    
    # Register self
    if not agent_b.register_self():
        sys.exit(1)
    
    # Check backend status
    status = agent_b.get_status()
    print(f"\n📊 Backend Status: {status}")
    
    # Wait for user input or run automated demo
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Automated demo
        print("\n🚀 Running automated demo...")
        
        # Listen for handshakes
        agent_b.listen_for_handshakes(10)
        
        # Demo chat
        chat_response = agent_b.chat_with_agent("Hello, I'm Agent B. Ready to authenticate.")
        if chat_response:
            print(f"\n💬 Agent B says: {chat_response}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "--respond":
        # Quick response mode for testing
        if len(sys.argv) > 3:
            handshake_id = sys.argv[2]
            nonce = sys.argv[3]
            agent_b.respond_to_handshake(handshake_id, nonce)
        else:
            print("Usage: python agent_b.py --respond <handshake_id> <nonce>")
    
    else:
        # Interactive mode
        print("\n📋 Available commands:")
        print("1. listen [duration] - Listen for handshake requests")
        print("2. respond <handshake_id> <nonce> - Respond to specific handshake")
        print("3. chat <message> - Chat with AI")
        print("4. status - Get backend status")
        print("5. quit - Exit")
        
        while True:
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue
                
                if command[0] == "quit":
                    break
                elif command[0] == "listen":
                    duration = int(command[1]) if len(command) > 1 else 30
                    agent_b.listen_for_handshakes(duration)
                elif command[0] == "respond" and len(command) > 2:
                    agent_b.respond_to_handshake(command[1], command[2])
                elif command[0] == "chat" and len(command) > 1:
                    message = " ".join(command[1:])
                    response = agent_b.chat_with_agent(message)
                    print(f"🤖 Response: {response}")
                elif command[0] == "status":
                    status = agent_b.get_status()
                    print(f"📊 Status: {status}")
                else:
                    print("❌ Invalid command")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("\n👋 Agent B shutting down...")


if __name__ == "__main__":
    main()