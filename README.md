# VeriAI - AI-to-AI Verification Protocol

We are building an AI-to-AI verification protocol that enables autonomous agents to confirm they are interacting with trusted AI's, not humans or malicious bots, by shifting from plain conversation into a secure "secret mode" of communication. This creates a new trust layer for multi-agent systems, fraud prevention, and secure AI collaboration.

## 🚀 Quick Demo (4 minutes)

1. **Agent Handshake Protocol**: Watch Agent A verify Agent B's identity using cryptographic signatures
2. **Secure Mode**: See encrypted AI-to-AI communication after successful verification
3. **ML Anomaly Detection**: Real-time fraud detection catching fake agents
4. **Live Attack Simulation**: Demonstrate how Fake Agent F gets detected and blocked

## 🏗️ Architecture

- **Frontend**: Next.js + Tailwind UI with real-time verification dashboard
- **Backend**: FastAPI with handshake protocol, ML detection, and secure messaging
- **Agents**: Python scripts simulating AI agents with OpenAI integration
- **Security**: HMAC signatures, session tokens, AES encryption
- **ML**: IsolationForest anomaly detection trained on agent behavior patterns

## 🛠️ Setup & Run

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Add your OpenAI API key to .env
OPENAI_API_KEY=your_key_here
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Train ML model (generates synthetic data)
python ../scripts/train_ml.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Test Agents (Optional)

```bash
cd agents
python agent_b.py  # Register Agent B
python agent_a.py  # Start handshake with Agent B
python agent_f.py  # Simulate fake agent attack
```

### 5. Docker (Alternative)

```bash
docker-compose up --build
```

## 🎯 Demo Flow

1. **Open UI**: http://localhost:3000
2. **Start Verification**: Click "Start Verify (Agent A)"
3. **Watch Handshake**: See cryptographic challenge-response in logs
4. **Enter Secure Mode**: Send encrypted messages between verified agents
5. **Simulate Attack**: Click "Simulate Fake Agent" to see ML detection in action
6. **View ML Scores**: Real-time anomaly detection with visual indicators

## 💰 Cost Optimization (Under $25)

- Uses `gpt-4o-mini` (cheapest OpenAI model: ~$0.0001/1K tokens)
- Caches responses to avoid repeated API calls
- Short prompts and responses for demo efficiency
- Estimated cost: ~$2-5 for full demo session

## 🔒 Security Features

- **HMAC-SHA256** signatures for agent authentication
- **AES-CTR** encryption for secure messaging (demo implementation)
- **Session tokens** with expiration (60-300 seconds)
- **ML anomaly detection** with real-time scoring
- **Rate limiting** and request validation

## 🧠 ML Detection Features

- **Signature verification** success/failure patterns
- **Response latency** analysis for bot detection
- **Message entropy** calculation for natural language validation
- **Behavioral patterns** learned from normal vs fraudulent interactions

## 📊 Technical Highlights

- **Real-time WebSocket** updates for live verification status
- **Cryptographic nonce** generation and validation
- **In-memory session** management for demo simplicity
- **CORS-enabled** API for frontend integration
- **Docker containerization** for easy deployment

## 🚨 Production Notes

- Current HMAC implementation is for demo - upgrade to mTLS/PKI for production
- In-memory storage should be replaced with Redis/database
- Add rate limiting, input validation, and proper error handling
- Implement proper key management and rotation

## 🎪 Hackathon Pitch

**Problem**: AI agents can't verify they're talking to other AIs vs humans/bots
**Solution**: Cryptographic handshake protocol + ML fraud detection  
**Impact**: Enables secure multi-agent systems, prevents AI impersonation
**Demo**: Live verification protocol with real-time attack detection
