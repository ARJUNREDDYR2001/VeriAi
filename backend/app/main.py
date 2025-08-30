"""
VeriAI Backend - FastAPI server for AI-to-AI verification protocol
Handles handshake protocol, ML anomaly detection, and secure messaging
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List
import os
import time
import json
from dotenv import load_dotenv

from .handshake import HandshakeManager
from .ml_detector import MLDetector
from .agents import AgentManager

# Load environment variables
load_dotenv()

app = FastAPI(title="VeriAI Backend", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
handshake_manager = HandshakeManager()
ml_detector = MLDetector()
agent_manager = AgentManager()

# Pydantic models
class AgentRegistration(BaseModel):
    agent_id: str
    agent_type: str  # "genuine" or "fake"
    secret_seed: Optional[str] = None

class HandshakeStart(BaseModel):
    requester_id: str
    responder_id: str

class HandshakeResponse(BaseModel):
    handshake_id: str
    signature: str
    responder_id: str

class HandshakeVerify(BaseModel):
    handshake_id: str
    signature: str

class SecureMessage(BaseModel):
    session_token: str
    encrypted_message: str
    sender_id: str
    receiver_id: str

class ChatMessage(BaseModel):
    agent_id: str
    message: str
    conversation_id: Optional[str] = None

# In-memory storage (for demo purposes)
agents_db: Dict = {}
handshakes_db: Dict = {}
sessions_db: Dict = {}
logs: List[Dict] = []

def log_event(event_type: str, data: Dict):
    """Log events for frontend display"""
    log_entry = {
        "timestamp": time.time(),
        "event_type": event_type,
        "data": data
    }
    logs.append(log_entry)
    # Keep only last 100 logs
    if len(logs) > 100:
        logs.pop(0)

@app.get("/")
async def root():
    return {"message": "VeriAI Backend API", "status": "running"}

@app.post("/register_agent")
async def register_agent(registration: AgentRegistration):
    """Register an agent with the system"""
    try:
        agent_data = handshake_manager.register_agent(
            registration.agent_id,
            registration.agent_type,
            registration.secret_seed
        )
        agents_db[registration.agent_id] = agent_data
        
        log_event("agent_registered", {
            "agent_id": registration.agent_id,
            "agent_type": registration.agent_type
        })
        
        return {"status": "success", "agent_id": registration.agent_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/handshake/start")
async def start_handshake(request: HandshakeStart):
    """Start handshake protocol between two agents"""
    try:
        if request.responder_id not in agents_db:
            raise HTTPException(status_code=404, detail="Responder agent not found")
        
        handshake_data = handshake_manager.start_handshake(
            request.requester_id,
            request.responder_id
        )
        handshakes_db[handshake_data["handshake_id"]] = handshake_data
        
        log_event("handshake_started", {
            "handshake_id": handshake_data["handshake_id"],
            "requester_id": request.requester_id,
            "responder_id": request.responder_id,
            "nonce": handshake_data["nonce"]
        })
        
        return handshake_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/handshake/respond")
async def respond_handshake(response: HandshakeResponse):
    """Respond to handshake with signature"""
    try:
        if response.handshake_id not in handshakes_db:
            raise HTTPException(status_code=404, detail="Handshake not found")
        
        handshake = handshakes_db[response.handshake_id]
        agent = agents_db.get(response.responder_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Verify signature
        secret_seed = agent["secret_seed"]
        if isinstance(secret_seed, str):
            secret_seed = secret_seed.encode()
        
        is_valid = handshake_manager.verify_signature(
            handshake["nonce"],
            response.signature,
            secret_seed
        )
        
        handshake["signature"] = response.signature
        handshake["signature_valid"] = is_valid
        handshake["response_time"] = time.time()
        
        log_event("handshake_response", {
            "handshake_id": response.handshake_id,
            "responder_id": response.responder_id,
            "signature_valid": is_valid
        })
        
        return {"status": "received", "signature_valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/handshake/verify")
async def verify_handshake(verify: HandshakeVerify):
    """Verify handshake and issue session token"""
    try:
        if verify.handshake_id not in handshakes_db:
            raise HTTPException(status_code=404, detail="Handshake not found")
        
        handshake = handshakes_db[verify.handshake_id]
        
        if not handshake.get("signature_valid", False):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Generate session token
        session_token = handshake_manager.generate_session_token()
        session_data = {
            "token": session_token,
            "handshake_id": verify.handshake_id,
            "requester_id": handshake["requester_id"],
            "responder_id": handshake["responder_id"],
            "created_at": time.time(),
            "expires_at": time.time() + int(os.getenv("SESSION_TIMEOUT", 300))
        }
        sessions_db[session_token] = session_data
        
        # Calculate ML anomaly score
        ml_features = ml_detector.extract_features(handshake)
        anomaly_score = ml_detector.predict_anomaly(ml_features)
        
        log_event("handshake_verified", {
            "handshake_id": verify.handshake_id,
            "session_token": session_token[:8] + "...",
            "anomaly_score": anomaly_score
        })
        
        return {
            "status": "verified",
            "session_token": session_token,
            "anomaly_score": anomaly_score,
            "expires_at": session_data["expires_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/secure_message")
async def send_secure_message(message: SecureMessage):
    """Send encrypted message using session token"""
    try:
        if message.session_token not in sessions_db:
            raise HTTPException(status_code=401, detail="Invalid session token")
        
        session = sessions_db[message.session_token]
        if time.time() > session["expires_at"]:
            raise HTTPException(status_code=401, detail="Session expired")
        
        # Decrypt message for logging (in real app, keep encrypted)
        decrypted = handshake_manager.decrypt_message(
            message.encrypted_message,
            message.session_token
        )
        
        log_event("secure_message", {
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "message_length": len(decrypted),
            "encrypted": True
        })
        
        return {"status": "delivered", "message_id": f"msg_{int(time.time())}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chat")
async def chat_with_agent(message: ChatMessage):
    """Chat with AI agent using OpenAI"""
    try:
        response = await agent_manager.chat_with_agent(
            message.agent_id,
            message.message,
            message.conversation_id
        )
        
        log_event("chat_message", {
            "agent_id": message.agent_id,
            "message_length": len(message.message),
            "response_length": len(response["content"])
        })
        
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ml_check")
async def ml_anomaly_check(handshake_id: str):
    """Check ML anomaly score for handshake"""
    try:
        if handshake_id not in handshakes_db:
            raise HTTPException(status_code=404, detail="Handshake not found")
        
        handshake = handshakes_db[handshake_id]
        features = ml_detector.extract_features(handshake)
        anomaly_score = ml_detector.predict_anomaly(features)
        
        return {
            "handshake_id": handshake_id,
            "anomaly_score": anomaly_score,
            "is_anomaly": anomaly_score > float(os.getenv("ANOMALY_THRESHOLD", 0.5)),
            "features": features
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/simulate_agent_b_response")
async def simulate_agent_b_response(handshake_id: str):
    """Simulate Agent B responding to handshake with correct signature"""
    try:
        if handshake_id not in handshakes_db:
            raise HTTPException(status_code=404, detail="Handshake not found")
        
        handshake = handshakes_db[handshake_id]
        agent_b = agents_db.get("agent_b")
        
        if not agent_b:
            raise HTTPException(status_code=404, detail="Agent B not registered")
        
        # Generate correct signature using Agent B's secret
        secret_seed = agent_b["secret_seed"]
        if isinstance(secret_seed, str):
            secret_seed = secret_seed.encode()
            
        signature = handshake_manager.generate_signature(handshake["nonce"], secret_seed)
        
        # Submit the response
        response_data = HandshakeResponse(
            handshake_id=handshake_id,
            signature=signature,
            responder_id="agent_b"
        )
        
        result = await respond_handshake(response_data)
        return {"signature": signature, "valid": result["signature_valid"]}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/simulate_fake")
async def simulate_fake_agent():
    """Simulate fake agent attack for demo"""
    try:
        # Register fake agent
        fake_agent = AgentRegistration(
            agent_id="fake_agent_f",
            agent_type="fake",
            secret_seed="wrong_secret"
        )
        await register_agent(fake_agent)
        
        # Start handshake with wrong credentials
        start_req = HandshakeStart(
            requester_id="agent_a",
            responder_id="fake_agent_f"
        )
        handshake = await start_handshake(start_req)
        
        # Respond with wrong signature
        fake_response = HandshakeResponse(
            handshake_id=handshake["handshake_id"],
            signature="fake_signature_12345",
            responder_id="fake_agent_f"
        )
        result = await respond_handshake(fake_response)
        
        log_event("fake_agent_detected", {
            "agent_id": "fake_agent_f",
            "handshake_id": handshake["handshake_id"],
            "signature_valid": result["signature_valid"]
        })
        
        return {"status": "fake_agent_simulated", "detected": not result["signature_valid"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/logs")
async def get_logs():
    """Get recent system logs"""
    return {"logs": logs[-50:]}  # Return last 50 logs

@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "agents_count": len(agents_db),
        "active_handshakes": len(handshakes_db),
        "active_sessions": len(sessions_db),
        "ml_model_loaded": ml_detector.is_loaded()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)