#!/usr/bin/env python3
"""
Agent A (Requester) - Initiates handshake protocol and verifies other agents
"""

import requests
import time
import json
import sys
from typing import Dict, Optional


class AgentA:
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.agent_id = "agent_a"
        self.session_token: Optional[str] = None
    
    def register_self(self) -> bool:
        """Register this agent with the backend"""
        try:
            response = requests.post(f"{self.backend_url}/register_agent", json={
                "agent_id": self.agent_id,
                "agent_type": "genuine"
            })
            
            if response.status_code == 200:
                print(f"✅ Agent A registered successfully")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def start_handshake(self, responder_id: str) -> Optional[Dict]:
        """Start handshake protocol with another agent"""
        try:
            print(f"\n🤝 Starting handshake with {responder_id}...")
            
            response = requests.post(f"{self.backend_url}/handshake/start", json={
                "requester_id": self.agent_id,
                "responder_id": responder_id
            })
            
            if response.status_code == 200:
                handshake_data = response.json()
                print(f"📝 Handshake started: {handshake_data['handshake_id']}")
                print(f"🎲 Nonce challenge: {handshake_data['nonce']}")
                return handshake_data
            else:
                print(f"❌ Handshake start failed: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Handshake error: {e}")
            return None
    
    def verify_handshake(self, handshake_id: str, signature: str) -> Optional[Dict]:
        """Verify handshake signature and get session token"""
        try:
            print(f"\n🔍 Verifying handshake {handshake_id}...")
            
            response = requests.post(f"{self.backend_url}/handshake/verify", json={
                "handshake_id": handshake_id,
                "signature": signature
            })
            
            if response.status_code == 200:
                result = response.json()
                if result["status"] == "verified":
                    self.session_token = result["session_token"]
                    print(f"✅ Handshake verified successfully!")
                    print(f"🔑 Session token: {self.session_token[:16]}...")
                    print(f"🤖 ML Anomaly score: {result['anomaly_score']}")
                    return result
                else:
                    print(f"❌ Verification failed")
                    return None
            else:
                print(f"❌ Verification error: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return None
    
    def send_secure_message(self, receiver_id: str, message: str) -> bool:
        """Send encrypted message using session token"""
        if not self.session_token:
            print("❌ No valid session token. Complete handshake first.")
            return False
        
        try:
            # Encrypt message (simple XOR for demo)
            encrypted_message = self._encrypt_message(message)
            
            print(f"\n📨 Sending secure message to {receiver_id}...")
            print(f"📝 Original: {message}")
            print(f"🔒 Encrypted: {encrypted_message[:32]}...")
            
            response = requests.post(f"{self.backend_url}/secure_message", json={
                "session_token": self.session_token,
                "encrypted_message": encrypted_message,
                "sender_id": self.agent_id,
                "receiver_id": receiver_id
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Message delivered: {result['message_id']}")
                return True
            else:
                print(f"❌ Message failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Message error: {e}")
            return False
    
    def _encrypt_message(self, message: str) -> str:
        """Simple XOR encryption for demo"""
        import base64
        
        key_bytes = self.session_token.encode()[:32].ljust(32, b'0')
        message_bytes = message.encode()
        
        encrypted_bytes = bytearray()
        for i, byte in enumerate(message_bytes):
            encrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return base64.b64encode(encrypted_bytes).decode()
    
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
    
    def get_ml_check(self, handshake_id: str) -> Optional[Dict]:
        """Get ML anomaly check for handshake"""
        try:
            response = requests.post(f"{self.backend_url}/ml_check", 
                                   params={"handshake_id": handshake_id})
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"ML check failed: {response.text}")
                return None
        except Exception as e:
            print(f"ML check error: {e}")
            return None


def main():
    """Demo script for Agent A"""
    print("🤖 Agent A (Requester) - AI Verification Protocol Demo")
    print("=" * 50)
    
    agent_a = AgentA()
    
    # Register self
    if not agent_a.register_self():
        sys.exit(1)
    
    # Wait for user input or run automated demo
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Automated demo
        print("\n🚀 Running automated demo...")
        
        # Start handshake with Agent B
        handshake = agent_a.start_handshake("agent_b")
        if handshake:
            # Wait for Agent B to respond (in real scenario)
            print("⏳ Waiting for Agent B to respond...")
            time.sleep(2)
            
            # For demo, we'll simulate the verification
            # In real scenario, Agent B would have responded with signature
            print("🔍 Attempting verification...")
            
            # Get ML check
            ml_result = agent_a.get_ml_check(handshake["handshake_id"])
            if ml_result:
                print(f"🤖 ML Analysis: Score {ml_result['anomaly_score']}")
        
        # Demo chat
        chat_response = agent_a.chat_with_agent("Hello, I'm Agent A. Ready to verify identities.")
        if chat_response:
            print(f"\n💬 Agent A says: {chat_response}")
    
    else:
        # Interactive mode
        print("\n📋 Available commands:")
        print("1. handshake <agent_id> - Start handshake with agent")
        print("2. verify <handshake_id> <signature> - Verify handshake")
        print("3. message <agent_id> <message> - Send secure message")
        print("4. chat <message> - Chat with AI")
        print("5. quit - Exit")
        
        while True:
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue
                
                if command[0] == "quit":
                    break
                elif command[0] == "handshake" and len(command) > 1:
                    agent_a.start_handshake(command[1])
                elif command[0] == "verify" and len(command) > 2:
                    agent_a.verify_handshake(command[1], command[2])
                elif command[0] == "message" and len(command) > 2:
                    message = " ".join(command[2:])
                    agent_a.send_secure_message(command[1], message)
                elif command[0] == "chat" and len(command) > 1:
                    message = " ".join(command[1:])
                    response = agent_a.chat_with_agent(message)
                    print(f"🤖 Response: {response}")
                else:
                    print("❌ Invalid command")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("\n👋 Agent A shutting down...")


if __name__ == "__main__":
    main()