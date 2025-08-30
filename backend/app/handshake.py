"""
Handshake Protocol Implementation
Handles cryptographic challenge-response authentication between AI agents
"""

import secrets
import hmac
import hashlib
import time
import base64
from typing import Dict, Optional
from cryptography.fernet import Fernet


class HandshakeManager:
    def __init__(self):
        self.handshakes: Dict = {}
        
    def register_agent(self, agent_id: str, agent_type: str, secret_seed: Optional[str] = None) -> Dict:
        """Register an agent with a secret seed for HMAC signing"""
        if not secret_seed:
            # Generate random secret for genuine agents
            secret_seed = secrets.token_hex(32)
        
        # Store as string for JSON serialization, convert to bytes when needed
        agent_data = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "secret_seed": secret_seed,  # Keep as string
            "registered_at": time.time()
        }
        
        return agent_data
    
    def start_handshake(self, requester_id: str, responder_id: str) -> Dict:
        """Start handshake protocol by generating nonce challenge"""
        handshake_id = secrets.token_hex(16)
        nonce = secrets.token_hex(16)
        
        handshake_data = {
            "handshake_id": handshake_id,
            "requester_id": requester_id,
            "responder_id": responder_id,
            "nonce": nonce,
            "created_at": time.time(),
            "status": "pending"
        }
        
        self.handshakes[handshake_id] = handshake_data
        return handshake_data
    
    def generate_signature(self, nonce: str, secret_seed: bytes) -> str:
        """Generate HMAC-SHA256 signature for nonce using secret seed"""
        signature = hmac.new(
            secret_seed,
            nonce.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_signature(self, nonce: str, signature: str, secret_seed: bytes) -> bool:
        """Verify HMAC signature against expected value"""
        expected_signature = self.generate_signature(nonce, secret_seed)
        return hmac.compare_digest(signature, expected_signature)
    
    def generate_session_token(self) -> str:
        """Generate session token for secure communication"""
        return secrets.token_urlsafe(32)
    
    def encrypt_message(self, message: str, session_token: str) -> str:
        """
        Encrypt message using session token (demo implementation)
        In production, use proper AES-GCM or similar
        """
        # Simple XOR encryption for demo (NOT for production)
        key_bytes = session_token.encode()[:32].ljust(32, b'0')
        message_bytes = message.encode()
        
        encrypted_bytes = bytearray()
        for i, byte in enumerate(message_bytes):
            encrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return base64.b64encode(encrypted_bytes).decode()
    
    def decrypt_message(self, encrypted_message: str, session_token: str) -> str:
        """
        Decrypt message using session token (demo implementation)
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_message.encode())
            key_bytes = session_token.encode()[:32].ljust(32, b'0')
            
            decrypted_bytes = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
            
            return decrypted_bytes.decode()
        except Exception:
            return "[Decryption failed]"
    
    def is_session_valid(self, session_token: str, sessions_db: Dict) -> bool:
        """Check if session token is valid and not expired"""
        if session_token not in sessions_db:
            return False
        
        session = sessions_db[session_token]
        return time.time() < session["expires_at"]
    
    def get_handshake_latency(self, handshake_data: Dict) -> float:
        """Calculate handshake response latency in milliseconds"""
        if "response_time" not in handshake_data:
            return 0.0
        
        return (handshake_data["response_time"] - handshake_data["created_at"]) * 1000
    
    def calculate_message_entropy(self, message: str) -> float:
        """
        Calculate approximate Shannon entropy of message
        Used for detecting bot-like vs natural language patterns
        """
        if not message:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in message.lower():
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        message_length = len(message)
        
        for count in char_counts.values():
            probability = count / message_length
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)
        
        return min(entropy, 5.0)  # Cap at 5.0 for normalization