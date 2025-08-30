#!/usr/bin/env python3
"""
Agent F (Fake Agent) - Simulates fraudulent handshake attempts for ML training
"""

import requests
import time
import random
import sys
from typing import Dict, Optional


class AgentF:
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.agent_id = f"fake_agent_{random.randint(1000, 9999)}"
        self.fake_secret = "wrong_secret_key_123"  # Intentionally wrong secret
    
    def register_self(self) -> bool:
        """Register this fake agent with wrong credentials"""
        try:
            response = requests.post(f"{self.backend_url}/register_agent", json={
                "agent_id": self.agent_id,
                "agent_type": "fake",
                "secret_seed": self.fake_secret
            })
            
            if response.status_code == 200:
                print(f"✅ Fake Agent {self.agent_id} registered")
                print(f"🔑 Using wrong secret: {self.fake_secret[:16]}...")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def attempt_fake_handshake(self, target_agent: str = "agent_b") -> bool:
        """Attempt fraudulent handshake with fake signature"""
        try:
            print(f"\n🎭 Attempting to impersonate and handshake with {target_agent}...")
            
            # Start handshake (this will work)
            response = requests.post(f"{self.backend_url}/handshake/start", json={
                "requester_id": "agent_a",  # Pretend to be Agent A
                "responder_id": self.agent_id  # But respond as fake agent
            })
            
            if response.status_code != 200:
                print(f"❌ Handshake start failed: {response.text}")
                return False
            
            handshake_data = response.json()
            handshake_id = handshake_data["handshake_id"]
            nonce = handshake_data["nonce"]
            
            print(f"📝 Handshake started: {handshake_id}")
            print(f"🎲 Nonce: {nonce}")
            
            # Generate fake signature (multiple strategies)
            fake_signatures = [
                "fake_signature_12345",  # Obviously fake
                nonce + "_fake",         # Nonce-based but wrong
                "a" * 64,               # Wrong length/format
                self._generate_weak_signature(nonce),  # Weak crypto attempt
            ]
            
            fake_signature = random.choice(fake_signatures)
            print(f"🔏 Generated fake signature: {fake_signature[:16]}...")
            
            # Add suspicious timing (too fast - bot-like behavior)
            time.sleep(random.uniform(0.01, 0.05))  # Very fast response
            
            # Respond with fake signature
            response = requests.post(f"{self.backend_url}/handshake/respond", json={
                "handshake_id": handshake_id,
                "signature": fake_signature,
                "responder_id": self.agent_id
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"📨 Fake response sent")
                print(f"🔍 Signature valid: {result['signature_valid']}")
                
                if not result["signature_valid"]:
                    print("🚨 DETECTED: Fake signature rejected!")
                
                # Try to get ML analysis
                ml_result = self._get_ml_analysis(handshake_id)
                if ml_result:
                    print(f"🤖 ML Anomaly Score: {ml_result['anomaly_score']}")
                    print(f"🚨 Detected as anomaly: {ml_result['is_anomaly']}")
                
                return result["signature_valid"]
            else:
                print(f"❌ Fake response failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Fake handshake error: {e}")
            return False
    
    def _generate_weak_signature(self, nonce: str) -> str:
        """Generate a weak/predictable signature that ML should detect"""
        # Simulate weak crypto attempts that bots might use
        weak_methods = [
            lambda x: f"sig_{hash(x) % 10000}",  # Predictable hash
            lambda x: x[::-1],                   # Just reverse the nonce
            lambda x: f"{x}_signed",             # Append text
            lambda x: "0" * len(x),              # All zeros
        ]
        
        method = random.choice(weak_methods)
        return method(nonce)
    
    def _get_ml_analysis(self, handshake_id: str) -> Optional[Dict]:
        """Get ML analysis for the fake handshake"""
        try:
            response = requests.post(f"{self.backend_url}/ml_check", 
                                   params={"handshake_id": handshake_id})
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception:
            return None
    
    def simulate_bot_behavior(self) -> Dict:
        """Simulate various bot-like behaviors for ML training"""
        behaviors = []
        
        # Rapid-fire requests (bot-like)
        print("\n🤖 Simulating bot behavior: Rapid requests...")
        for i in range(3):
            success = self.attempt_fake_handshake()
            behaviors.append({
                "attempt": i + 1,
                "success": success,
                "timing": "rapid"
            })
            time.sleep(0.1)  # Very short delay
        
        # Predictable patterns
        print("\n🔄 Simulating bot behavior: Predictable patterns...")
        for pattern in ["pattern_1", "pattern_2", "pattern_3"]:
            # Use predictable agent IDs
            old_id = self.agent_id
            self.agent_id = f"bot_{pattern}"
            
            success = self.attempt_fake_handshake()
            behaviors.append({
                "pattern": pattern,
                "success": success,
                "timing": "predictable"
            })
            
            self.agent_id = old_id
            time.sleep(0.2)
        
        return {"behaviors": behaviors, "total_attempts": len(behaviors)}
    
    def chat_with_suspicious_responses(self, message: str) -> Optional[str]:
        """Generate suspicious chat responses that ML might detect"""
        try:
            response = requests.post(f"{self.backend_url}/chat", json={
                "agent_id": self.agent_id,
                "message": message
            })
            
            if response.status_code == 200:
                result = response.json()
                
                # Add suspicious modifications to response
                suspicious_response = self._make_response_suspicious(result["content"])
                return suspicious_response
            else:
                return f"Chat error: {response.text}"
        except Exception as e:
            return f"Chat error: {e}"
    
    def _make_response_suspicious(self, response: str) -> str:
        """Make AI response more suspicious/bot-like"""
        suspicious_modifications = [
            lambda x: x.upper(),  # ALL CAPS
            lambda x: x.replace(" ", "_"),  # Replace spaces with underscores
            lambda x: f"[BOT] {x} [/BOT]",  # Add bot tags
            lambda x: x * 2,  # Repeat response
            lambda x: "ERROR: " + x,  # Add error prefix
        ]
        
        modification = random.choice(suspicious_modifications)
        return modification(response)


def main():
    """Demo script for Fake Agent F"""
    print("🎭 Agent F (Fake Agent) - Fraud Simulation Demo")
    print("=" * 45)
    
    agent_f = AgentF()
    
    # Register fake agent
    if not agent_f.register_self():
        sys.exit(1)
    
    # Wait for user input or run automated demo
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Automated fraud simulation
        print("\n🚀 Running automated fraud simulation...")
        
        # Single fake attempt
        print("\n1️⃣ Single fake handshake attempt:")
        agent_f.attempt_fake_handshake()
        
        # Bot behavior simulation
        print("\n2️⃣ Bot behavior simulation:")
        bot_results = agent_f.simulate_bot_behavior()
        print(f"📊 Bot simulation complete: {bot_results}")
        
        # Suspicious chat
        print("\n3️⃣ Suspicious chat responses:")
        chat_response = agent_f.chat_with_suspicious_responses("Hello, I am a legitimate agent.")
        print(f"🤖 Suspicious response: {chat_response}")
    
    else:
        # Interactive mode
        print("\n📋 Available commands:")
        print("1. fake_handshake [target] - Attempt fake handshake")
        print("2. bot_behavior - Simulate bot-like behavior patterns")
        print("3. chat <message> - Send suspicious chat message")
        print("4. rapid_attack - Perform rapid-fire fake attempts")
        print("5. quit - Exit")
        
        while True:
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue
                
                if command[0] == "quit":
                    break
                elif command[0] == "fake_handshake":
                    target = command[1] if len(command) > 1 else "agent_b"
                    agent_f.attempt_fake_handshake(target)
                elif command[0] == "bot_behavior":
                    result = agent_f.simulate_bot_behavior()
                    print(f"📊 Results: {result}")
                elif command[0] == "chat" and len(command) > 1:
                    message = " ".join(command[1:])
                    response = agent_f.chat_with_suspicious_responses(message)
                    print(f"🤖 Suspicious response: {response}")
                elif command[0] == "rapid_attack":
                    print("🚨 Launching rapid attack simulation...")
                    for i in range(5):
                        print(f"Attack {i+1}/5:")
                        agent_f.attempt_fake_handshake()
                        time.sleep(0.5)
                else:
                    print("❌ Invalid command")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("\n👋 Fake Agent F shutting down...")


if __name__ == "__main__":
    main()