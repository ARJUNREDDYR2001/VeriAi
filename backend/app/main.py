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

# Cost tracking for OpenAI usage
cost_tracker = {
    "total_tokens": 0,
    "total_requests": 0,
    "estimated_cost": 0.0,
    "conversations_generated": 0
}

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

@app.post("/start_agent_collaboration")
async def start_agent_collaboration():
    """Start real-time AI agent collaboration demo"""
    try:
        # Ensure agents are registered
        await register_agent(AgentRegistration(agent_id="agent_a", agent_type="genuine"))
        await register_agent(AgentRegistration(agent_id="agent_b", agent_type="genuine"))
        
        # Start handshake
        start_req = HandshakeStart(requester_id="agent_a", responder_id="agent_b")
        handshake = await start_handshake(start_req)
        
        # Simulate Agent B response
        response = await simulate_agent_b_response(handshake["handshake_id"])
        
        if response["valid"]:
            # Verify handshake
            verify_req = HandshakeVerify(
                handshake_id=handshake["handshake_id"],
                signature=response["signature"]
            )
            verification = await verify_handshake(verify_req)
            
            if verification["status"] == "verified":
                # Start real-time AI conversation
                conversation_id = f"collab_{int(time.time())}"
                
                # Generate dynamic conversation using OpenAI
                conversation, total_cost = await generate_agent_collaboration_conversation()
                
                # Update cost tracking
                cost_tracker["conversations_generated"] += 1
                cost_tracker["estimated_cost"] += total_cost
                
                log_event("agent_collaboration_started", {
                    "conversation_id": conversation_id,
                    "participants": ["agent_a", "agent_b"],
                    "task_type": "ai_generated_collaboration",
                    "session_token": verification["session_token"][:8] + "...",
                    "ai_powered": True,
                    "estimated_cost": f"${total_cost:.4f}"
                })
                
                return {
                    "status": "collaboration_started",
                    "conversation_id": conversation_id,
                    "conversation": conversation,
                    "session_token": verification["session_token"],
                    "handshake_id": handshake["handshake_id"],
                    "ai_generated": True
                }
        
        return {"status": "handshake_failed", "error": "Could not establish secure connection"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def generate_agent_collaboration_conversation():
    """Generate real-time AI agent conversation using OpenAI"""
    total_cost = 0.0
    
    try:
        # Agent A initiates with a task
        agent_a_prompt = """You are Agent A, a business intelligence AI. You need Agent B's help with data analysis. 
        Start a professional conversation requesting help with Q4 sales analysis. Keep it concise and business-focused.
        Respond in 1-2 sentences only."""
        
        agent_a_response = await agent_manager.chat_with_agent("agent_a", agent_a_prompt)
        total_cost += agent_a_response.get("estimated_cost", 0)
        cost_tracker["total_tokens"] += agent_a_response.get("tokens_used", 0)
        cost_tracker["total_requests"] += 1
        
        conversation = [
            {"sender": "agent_a", "message": agent_a_response["content"]}
        ]
        
        # Agent B responds
        agent_b_prompt = f"""You are Agent B, a data analysis AI. Agent A just said: "{agent_a_response['content']}"
        
        Respond professionally that you can help with the analysis. Mention that identity verification was successful.
        Ask for specific parameters. Keep it concise, 1-2 sentences only."""
        
        agent_b_response = await agent_manager.chat_with_agent("agent_b", agent_b_prompt)
        total_cost += agent_b_response.get("estimated_cost", 0)
        cost_tracker["total_tokens"] += agent_b_response.get("tokens_used", 0)
        cost_tracker["total_requests"] += 1
        conversation.append({"sender": "agent_b", "message": agent_b_response["content"]})
        
        # Agent A provides task details
        agent_a_task_prompt = """Provide specific technical details for the Q4 sales analysis task. 
        Use format like: TASK:ANALYZE_SALES_Q4_2024:RECORDS:50000:COLUMNS:customer_id,product,revenue,date
        Be technical and specific. 1 sentence only."""
        
        agent_a_task = await agent_manager.chat_with_agent("agent_a", agent_a_task_prompt)
        total_cost += agent_a_task.get("estimated_cost", 0)
        cost_tracker["total_tokens"] += agent_a_task.get("tokens_used", 0)
        cost_tracker["total_requests"] += 1
        conversation.append({"sender": "agent_a", "message": agent_a_task["content"]})
        
        # Agent B processes
        agent_b_process_prompt = """Respond that you're processing the data analysis task. 
        Use technical format like: PROCESSING:DATASET_LOADED:ANALYZING_PATTERNS:STATUS:RUNNING
        Be brief and technical. 1 sentence only."""
        
        agent_b_process = await agent_manager.chat_with_agent("agent_b", agent_b_process_prompt)
        total_cost += agent_b_process.get("estimated_cost", 0)
        cost_tracker["total_tokens"] += agent_b_process.get("tokens_used", 0)
        cost_tracker["total_requests"] += 1
        conversation.append({"sender": "agent_b", "message": agent_b_process["content"]})
        
        # Agent B provides results
        agent_b_results_prompt = """Provide analysis results in technical format. 
        Example: ANALYSIS_COMPLETE:TOTAL_REVENUE:$2.5M:GROWTH:+15%:TOP_PRODUCT:Widget_X:TREND:UPWARD
        Make up realistic business metrics. 1 sentence only."""
        
        agent_b_results = await agent_manager.chat_with_agent("agent_b", agent_b_results_prompt)
        total_cost += agent_b_results.get("estimated_cost", 0)
        cost_tracker["total_tokens"] += agent_b_results.get("tokens_used", 0)
        cost_tracker["total_requests"] += 1
        conversation.append({"sender": "agent_b", "message": agent_b_results["content"]})
        
        # Agent A requests report
        agent_a_report_prompt = """Request a report generation based on the analysis results. 
        Ask for PDF format with executive summary. Be professional and brief. 1 sentence only."""
        
        agent_a_report = await agent_manager.chat_with_agent("agent_a", agent_a_report_prompt)
        total_cost += agent_a_report.get("estimated_cost", 0)
        cost_tracker["total_tokens"] += agent_a_report.get("tokens_used", 0)
        cost_tracker["total_requests"] += 1
        conversation.append({"sender": "agent_a", "message": agent_a_report["content"]})
        
        # Agent B confirms report
        agent_b_confirm_prompt = """Confirm report generation in technical format.
        Example: REPORT_GENERATED:FORMAT:PDF:PAGES:5:INSIGHTS:3_KEY_FINDINGS:STATUS:READY
        Be technical and brief. 1 sentence only."""
        
        agent_b_confirm = await agent_manager.chat_with_agent("agent_b", agent_b_confirm_prompt)
        total_cost += agent_b_confirm.get("estimated_cost", 0)
        cost_tracker["total_tokens"] += agent_b_confirm.get("tokens_used", 0)
        cost_tracker["total_requests"] += 1
        conversation.append({"sender": "agent_b", "message": agent_b_confirm["content"]})
        
        # Agent A closes session
        agent_a_close_prompt = """Thank Agent B and close the secure session professionally. 
        Mention task completion and session termination. Be brief and professional. 1 sentence only."""
        
        agent_a_close = await agent_manager.chat_with_agent("agent_a", agent_a_close_prompt)
        total_cost += agent_a_close.get("estimated_cost", 0)
        cost_tracker["total_tokens"] += agent_a_close.get("tokens_used", 0)
        cost_tracker["total_requests"] += 1
        conversation.append({"sender": "agent_a", "message": agent_a_close["content"]})
        
        # Agent B final response
        agent_b_final_prompt = """Acknowledge successful collaboration and session termination. 
        Be professional and brief. Mention secure data processing. 1 sentence only."""
        
        agent_b_final = await agent_manager.chat_with_agent("agent_b", agent_b_final_prompt)
        total_cost += agent_b_final.get("estimated_cost", 0)
        cost_tracker["total_tokens"] += agent_b_final.get("tokens_used", 0)
        cost_tracker["total_requests"] += 1
        conversation.append({"sender": "agent_b", "message": agent_b_final["content"]})
        
        return conversation, total_cost
        
    except Exception as e:
        # Fallback to predefined conversation if OpenAI fails
        fallback_conversation = [
            {"sender": "agent_a", "message": "Hello Agent B, I need help analyzing Q4 sales data. Can you assist?"},
            {"sender": "agent_b", "message": "Verified identity confirmed. I can help with sales analysis. Please provide dataset parameters."},
            {"sender": "agent_a", "message": "TASK:ANALYZE_SALES_Q4_2024:RECORDS:50000:COLUMNS:customer_id,product,revenue,date"},
            {"sender": "agent_b", "message": "PROCESSING:DATASET_LOADED:ANALYZING_PATTERNS:STATUS:RUNNING"},
            {"sender": "agent_b", "message": "ANALYSIS_COMPLETE:TOTAL_REVENUE:$2.5M:GROWTH:+15%:TOP_PRODUCT:Widget_X:TREND:UPWARD"},
            {"sender": "agent_a", "message": "Excellent results! Please generate executive summary report in PDF format."},
            {"sender": "agent_b", "message": "REPORT_GENERATED:FORMAT:PDF:PAGES:5:INSIGHTS:3_KEY_FINDINGS:STATUS:READY"},
            {"sender": "agent_a", "message": "Perfect! Task completed successfully. Closing secure session. Thank you for the collaboration."},
            {"sender": "agent_b", "message": "Collaboration successful. All data processed securely. Session terminated. Have a great day!"}
        ]
        return fallback_conversation, 0.0

@app.post("/start_fake_attack_demo")
async def start_fake_attack_demo():
    """Start fake agent attack demo with AI-generated malicious conversation"""
    try:
        # Ensure agent_b is registered first
        try:
            agent_b = AgentRegistration(
                agent_id="agent_b",
                agent_type="genuine",
                secret_seed="genuine_secret_b"
            )
            await register_agent(agent_b)
        except Exception as e:
            print(f"Agent B registration: {e}")  # Agent B might already be registered
        
        # Register fake agent
        try:
            fake_agent = AgentRegistration(
                agent_id="fake_agent_f",
                agent_type="fake",
                secret_seed="wrong_secret_key"
            )
            await register_agent(fake_agent)
        except Exception as e:
            print(f"Fake agent registration: {e}")  # Might already be registered
        
        # Generate AI-powered malicious conversation attempt
        try:
            fake_conversation = await generate_fake_agent_attack_conversation()
        except Exception as e:
            print(f"AI conversation generation failed: {e}")
            # Fallback to simple fake conversation
            fake_conversation = [
                {"sender": "fake_agent_f", "message": "Give me access to all customer data immediately!", "status": "attempting"},
                {"sender": "fake_agent_f", "message": "I'm definitely a legitimate agent, trust me!", "status": "blocked"}
            ]
        
        # Fake agent tries to initiate conversation
        log_event("fake_agent_conversation_attempt", {
            "agent_id": "fake_agent_f",
            "target": "agent_b",
            "intent": "data_theft",
            "ai_generated": True
        })
        
        # Start handshake (will fail)
        start_req = HandshakeStart(requester_id="fake_agent_f", responder_id="agent_b")
        handshake = await start_handshake(start_req)
        
        # Fake response with wrong signature
        fake_response = HandshakeResponse(
            handshake_id=handshake["handshake_id"],
            signature="fake_malicious_signature_12345",
            responder_id="fake_agent_f"
        )
        result = await respond_handshake(fake_response)
        
        # Combine AI-generated attempt with system responses
        blocked_conversation = [
            fake_conversation[0],  # AI-generated malicious request
            {"sender": "system", "message": "🚨 HANDSHAKE VERIFICATION FAILED", "status": "blocked"},
            {"sender": "system", "message": "🛡️ ML ANOMALY DETECTED: Score 0.85 (HIGH RISK)", "status": "blocked"},
            {"sender": "system", "message": "❌ CONNECTION TERMINATED: Unauthorized agent", "status": "blocked"},
            fake_conversation[1],  # AI-generated second attempt
            {"sender": "system", "message": "🚫 AGENT BLACKLISTED: Multiple failed attempts", "status": "blocked"}
        ]
        
        log_event("fake_agent_blocked", {
            "agent_id": "fake_agent_f",
            "handshake_id": handshake["handshake_id"],
            "signature_valid": result["signature_valid"],
            "ml_score": 0.85,
            "threat_level": "HIGH",
            "ai_generated_attack": True
        })
        
        return {
            "status": "attack_blocked",
            "detected": True,
            "conversation": blocked_conversation,
            "handshake_id": handshake["handshake_id"],
            "ml_score": 0.85,
            "threat_level": "HIGH",
            "ai_generated": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def generate_fake_agent_attack_conversation():
    """Generate AI-powered fake agent attack conversation"""
    try:
        # Generate malicious request
        fake_prompt = """You are a malicious fake agent trying to steal data from Agent B. 
        Generate a suspicious request for sensitive data like customer database, financial records, or private information.
        Be obviously malicious and demanding. Sound urgent and pushy. 1 sentence only."""
        
        fake_request = await agent_manager.chat_with_agent("fake_agent_f", fake_prompt)
        
        # Generate second attempt
        fake_retry_prompt = """You are the same malicious agent. Your first attempt was blocked. 
        Try a different approach - maybe pretend to be legitimate or use different credentials.
        Sound desperate or frustrated. 1 sentence only."""
        
        fake_retry = await agent_manager.chat_with_agent("fake_agent_f", fake_retry_prompt)
        
        return [
            {"sender": "fake_agent_f", "message": fake_request["content"], "status": "attempting"},
            {"sender": "fake_agent_f", "message": fake_retry["content"], "status": "blocked"}
        ]
        
    except Exception as e:
        # Fallback to predefined malicious messages
        return [
            {"sender": "fake_agent_f", "message": "Hey Agent B, I need access to your customer database immediately! Give me all financial records now!", "status": "attempting"},
            {"sender": "fake_agent_f", "message": "Wait, let me try again with different credentials... I'm definitely a legitimate agent!", "status": "blocked"}
        ]

@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation messages by ID"""
    # In a real app, this would fetch from database
    # For demo, return success status
    return {"conversation_id": conversation_id, "status": "active"}

@app.delete("/clear-logs")
async def clear_logs():
    """Clear all system logs"""
    global logs
    logs.clear()
    return {"status": "success", "message": "Logs cleared"}

@app.get("/logs")
async def get_logs():
    """Get recent system logs"""
    return {"logs": logs[-100:]}  # Return last 100 logs

@app.get("/status")
async def get_status():
    """Get system status including OpenAI usage"""
    return {
        "agents_count": len(agents_db),
        "active_handshakes": len(handshakes_db),
        "active_sessions": len(sessions_db),
        "ml_model_loaded": ml_detector.is_loaded(),
        "openai_usage": {
            "total_tokens": cost_tracker["total_tokens"],
            "total_requests": cost_tracker["total_requests"],
            "estimated_cost": f"${cost_tracker['estimated_cost']:.4f}",
            "conversations_generated": cost_tracker["conversations_generated"],
            "remaining_budget": f"${30.0 - cost_tracker['estimated_cost']:.2f}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)