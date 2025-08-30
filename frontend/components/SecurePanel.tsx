"use client";

import React, { useState } from "react";
import { Shield, Lock, Unlock, AlertCircle, CheckCircle, Play, Zap, Eye, EyeOff, ShieldCheck, AlertTriangle } from "lucide-react";
import axios from "axios";

interface HandshakeStatus {
  handshake_id?: string;
  status: "idle" | "started" | "responded" | "verified" | "failed";
  session_token?: string;
  anomaly_score?: number;
  nonce?: string;
  fakeAgentDetected?: boolean;
}

interface SecurePanelProps {
  onLog: (message: string) => void;
}

export default function SecurePanel({ onLog }: Readonly<SecurePanelProps>) {
  const [handshakeStatus, setHandshakeStatus] = useState<HandshakeStatus>({
    status: "idle",
  });
  const [secureMessage, setSecureMessage] = useState("");
  const [encryptedMessage, setEncryptedMessage] = useState("");
  const [showDecrypted, setShowDecrypted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [mlScore, setMlScore] = useState<number | null>(null);

  const startHandshake = async () => {
    setIsLoading(true);
    onLog("🤝 Starting handshake protocol...");

    try {
      // Register Agent A if not exists
      await axios
        .post("http://localhost:8000/register_agent", {
          agent_id: "agent_a",
          agent_type: "genuine",
        })
        .catch(() => {}); // Ignore if already registered

      // Register Agent B if not exists
      await axios
        .post("http://localhost:8000/register_agent", {
          agent_id: "agent_b",
          agent_type: "genuine",
        })
        .catch(() => {}); // Ignore if already registered

      // Start handshake
      const response = await axios.post(
        "http://localhost:8000/handshake/start",
        {
          requester_id: "agent_a",
          responder_id: "agent_b",
        }
      );

      const handshakeData = response.data;
      setHandshakeStatus({
        status: "started",
        handshake_id: handshakeData.handshake_id,
        nonce: handshakeData.nonce,
      });

      onLog(`✅ Handshake started: ${handshakeData.handshake_id}`);
      onLog(`🎲 Nonce challenge: ${handshakeData.nonce}`);

      // Simulate Agent B response after a delay
      setTimeout(async () => {
        await simulateAgentBResponse(handshakeData.handshake_id);
      }, 1500);
    } catch (error: any) {
      onLog(
        `❌ Handshake failed: ${error.response?.data?.detail || error.message}`
      );
      setHandshakeStatus({ status: "failed" });
    } finally {
      setIsLoading(false);
    }
  };

  const simulateAgentBResponse = async (handshakeId: string) => {
    onLog("🤖 Agent B generating signature...");

    try {
      // Use backend endpoint to simulate Agent B with correct signature
      const response = await axios.post(
        `http://localhost:8000/simulate_agent_b_response?handshake_id=${handshakeId}`
      );

      if (response.data.valid) {
        setHandshakeStatus((prev) => ({ ...prev, status: "responded" }));
        onLog("✅ Agent B signature verified");

        // Auto-verify after short delay
        setTimeout(
          () => verifyHandshake(handshakeId, response.data.signature),
          1000
        );
      } else {
        onLog("❌ Agent B signature invalid");
        setHandshakeStatus({ status: "failed" });
      }
    } catch (error: any) {
      onLog(
        `❌ Agent B response failed: ${
          error.response?.data?.detail || error.message
        }`
      );
      setHandshakeStatus({ status: "failed" });
    }
  };

  const generateHMACSignature = async (nonce: string): Promise<string> => {
    // Simulate HMAC generation (in real app, Agent B would do this)
    const encoder = new TextEncoder();
    const data = encoder.encode(nonce);
    const key = encoder.encode("agent_b_secret_key"); // Simulated secret

    const cryptoKey = await crypto.subtle.importKey(
      "raw",
      key,
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );

    const signature = await crypto.subtle.sign("HMAC", cryptoKey, data);
    return Array.from(new Uint8Array(signature))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  };

  const verifyHandshake = async (handshakeId: string, signature: string) => {
    onLog("🔍 Verifying handshake...");

    try {
      const response = await axios.post(
        "http://localhost:8000/handshake/verify",
        {
          handshake_id: handshakeId,
          signature: signature,
        }
      );

      if (response.data.status === "verified") {
        setHandshakeStatus({
          status: "verified",
          handshake_id: handshakeId,
          session_token: response.data.session_token,
          anomaly_score: response.data.anomaly_score,
        });
        setMlScore(response.data.anomaly_score);

        onLog("🎉 Handshake verified successfully!");
        onLog(
          `🔑 Session token issued: ${response.data.session_token.substring(
            0,
            16
          )}...`
        );
        onLog(`🤖 ML Anomaly Score: ${response.data.anomaly_score.toFixed(3)}`);
      } else {
        setHandshakeStatus({ status: "failed" });
        onLog("❌ Handshake verification failed");
      }
    } catch (error: any) {
      onLog(
        `❌ Verification failed: ${
          error.response?.data?.detail || error.message
        }`
      );
      setHandshakeStatus({ status: "failed" });
    }
  };

  const sendSecureMessage = async () => {
    if (!secureMessage.trim() || !handshakeStatus.session_token) return;

    onLog("📨 Sending secure message...");

    try {
      // Encrypt message (simple XOR for demo)
      const encrypted = encryptMessage(
        secureMessage,
        handshakeStatus.session_token
      );
      setEncryptedMessage(encrypted);

      const response = await axios.post(
        "http://localhost:8000/secure_message",
        {
          session_token: handshakeStatus.session_token,
          encrypted_message: encrypted,
          sender_id: "agent_a",
          receiver_id: "agent_b",
        }
      );

      onLog(`✅ Secure message delivered: ${response.data.message_id}`);
      onLog(`🔒 Encrypted: ${encrypted.substring(0, 32)}...`);
    } catch (error: any) {
      onLog(
        `❌ Secure message failed: ${
          error.response?.data?.detail || error.message
        }`
      );
    }
  };

  const encryptMessage = (message: string, sessionToken: string): string => {
    // Simple XOR encryption for demo
    const keyBytes = new TextEncoder().encode(
      sessionToken.substring(0, 32).padEnd(32, "0")
    );
    const messageBytes = new TextEncoder().encode(message);

    const encrypted = new Uint8Array(messageBytes.length);
    for (let i = 0; i < messageBytes.length; i++) {
      encrypted[i] = messageBytes[i] ^ keyBytes[i % keyBytes.length];
    }

    return btoa(String.fromCharCode(...encrypted));
  };

  const decryptMessage = (
    encryptedMessage: string,
    sessionToken: string
  ): string => {
    try {
      const keyBytes = new TextEncoder().encode(
        sessionToken.substring(0, 32).padEnd(32, "0")
      );
      const encryptedBytes = new Uint8Array(
        atob(encryptedMessage)
          .split("")
          .map((c) => c.charCodeAt(0))
      );

      const decrypted = new Uint8Array(encryptedBytes.length);
      for (let i = 0; i < encryptedBytes.length; i++) {
        decrypted[i] = encryptedBytes[i] ^ keyBytes[i % keyBytes.length];
      }

      return new TextDecoder().decode(decrypted);
    } catch {
      return "[Decryption failed]";
    }
  };

  const simulateFakeAgent = async () => {
    setIsLoading(true);
    // Reset to initial state before starting fake agent simulation
    setHandshakeStatus({
      status: "idle",
      fakeAgentDetected: undefined
    });
    onLog("🎭 Simulating fake agent attack...");

    try {
      const response = await axios.post("http://localhost:8000/simulate_fake");

      if (response.data.detected) {
        onLog("🚨 Fake agent detected and blocked!");
        // Set status to failed when fake agent is detected
        setHandshakeStatus({
          status: "failed",
          fakeAgentDetected: true,
          handshake_id: response.data.handshake_id
        });
      } else {
        onLog("⚠️ Fake agent not detected - security breach!");
        setHandshakeStatus({
          status: "failed",
          fakeAgentDetected: false
        });
      }
    } catch (error: any) {
      onLog(
        `❌ Fake agent simulation failed: ${
          error.response?.data?.detail || error.message
        }`
      );
      setHandshakeStatus({
        status: "failed",
        fakeAgentDetected: false
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = () => {
    if (handshakeStatus.fakeAgentDetected) {
      return <AlertTriangle className="w-5 h-5 text-red-600" />;
    }
    switch (handshakeStatus.status) {
      case "verified":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "failed":
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case "started":
      case "responded":
        return <Shield className="w-5 h-5 text-blue-600 animate-pulse" />;
      default:
        return <Shield className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusText = () => {
    if (handshakeStatus.fakeAgentDetected) {
      return "SECURITY ALERT: FAKE AGENT DETECTED";
    }
    switch (handshakeStatus.status) {
      case "verified":
        return "VERIFIED";
      case "failed":
        return "HANDSHAKE FAILED";
      case "started":
        return "HANDSHAKE STARTED";
      case "responded":
        return "RESPONSE RECEIVED";
      default:
        return "IDLE";
    }
  };

  const getStatusColor = () => {
    if (handshakeStatus.fakeAgentDetected) {
      return "text-red-600";
    }
    switch (handshakeStatus.status) {
      case "verified":
        return "text-green-600";
      case "failed":
        return "text-red-600";
      case "started":
      case "responded":
        return "text-blue-600";
      default:
        return "text-gray-600";
    }
  };

  const getMlScoreColor = (score: number) => {
    if (score > 0.7) return "text-red-600 bg-red-100";
    if (score > 0.4) return "text-yellow-600 bg-yellow-100";
    return "text-green-600 bg-green-100";
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-6">
        <Shield className="w-5 h-5 text-purple-600" />
        <h2 className="text-lg font-semibold">Secure Mode & Verification</h2>
      </div>

      {/* Handshake Status */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium">Handshake Protocol</h3>
          {getStatusIcon()}
        </div>

        <div className={`text-sm ${getStatusColor()} mb-3 font-medium`}>
          Status: {getStatusText()}
        </div>

        {handshakeStatus.handshake_id && (
          <div className="text-xs text-gray-500 mb-2">
            ID: {handshakeStatus.handshake_id}
          </div>
        )}

        {mlScore !== null && (
          <div className="mb-3">
            <div className="flex items-center justify-between text-sm">
              <span>ML Anomaly Score:</span>
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${getMlScoreColor(
                  mlScore
                )}`}
              >
                {mlScore.toFixed(3)}
              </span>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-3">
          <div className="flex gap-2">
            <button
              onClick={startHandshake}
              disabled={isLoading || handshakeStatus.status === "verified"}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="w-4 h-4" />
              Start Verify (Agent A)
            </button>

            <button
              onClick={simulateFakeAgent}
              disabled={isLoading}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Zap className="w-4 h-4" />
              Simulate Fake Agent
            </button>
          </div>
          
          {handshakeStatus.fakeAgentDetected !== undefined && (
            <div className={`p-3 rounded-md ${
              handshakeStatus.fakeAgentDetected 
                ? 'bg-green-100 text-green-800 border border-green-200' 
                : 'bg-red-100 text-red-800 border border-red-200'
            }`}>
              <div className="flex items-center gap-2">
                {handshakeStatus.fakeAgentDetected ? (
                  <>
                    <ShieldCheck className="w-5 h-5 text-green-600" />
                    <span>Security Alert: Fake agent detected and blocked!</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="w-5 h-5 text-red-600" />
                    <span>Security Warning: Fake agent was not detected!</span>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Secure Messaging */}
      <div className="flex-1 flex flex-col">
        <div className="flex items-center gap-2 mb-3">
          <Lock className="w-4 h-4 text-indigo-600" />
          <h3 className="font-medium">Secure Messaging</h3>
        </div>

        {handshakeStatus.status === "verified" ? (
          <div className="flex-1 flex flex-col">
            <div className="mb-3">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message to encrypt:
              </label>
              <textarea
                value={secureMessage}
                onChange={(e) => setSecureMessage(e.target.value)}
                placeholder="Enter message to send securely..."
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                rows={3}
              />
            </div>

            <button
              onClick={sendSecureMessage}
              disabled={!secureMessage.trim()}
              className="mb-4 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send Secure Message
            </button>

            {encryptedMessage && (
              <div className="flex-1 bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    Encrypted Message:
                  </span>
                  <button
                    onClick={() => setShowDecrypted(!showDecrypted)}
                    className="flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-700"
                  >
                    {showDecrypted ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                    {showDecrypted ? "Hide" : "Show"} Decrypted
                  </button>
                </div>

                <div className="bg-white p-3 rounded border font-mono text-sm break-all">
                  {encryptedMessage}
                </div>

                {showDecrypted && handshakeStatus.session_token && (
                  <div className="mt-3">
                    <span className="text-sm font-medium text-gray-700">
                      Decrypted:
                    </span>
                    <div className="bg-green-50 p-3 rounded border border-green-200 mt-1">
                      {decryptMessage(
                        encryptedMessage,
                        handshakeStatus.session_token
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <Unlock className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Complete handshake verification</p>
              <p className="text-sm">to enable secure messaging</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
