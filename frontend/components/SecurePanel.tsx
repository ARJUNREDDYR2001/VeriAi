"use client";

import React, { useState, useEffect } from "react";
import {
  Shield,
  Lock,
  Unlock,
  AlertCircle,
  CheckCircle,
  Play,
  Zap,
  Eye,
  ShieldCheck,
  AlertTriangle,
  MessageCircle,
} from "lucide-react";
import axios from "axios";

interface HandshakeStatus {
  status:
    | "idle"
    | "started"
    | "responded"
    | "verified"
    | "failed"
    | "collaborating";
  handshake_id?: string;
  session_token?: string;
  fakeAgentDetected?: boolean;
}

interface ConversationMessage {
  sender: string;
  message: string;
  status?: string;
}

interface Collaboration {
  status: string;
  conversation_id: string;
  conversation: ConversationMessage[];
  session_token: string;
  handshake_id: string;
  ai_generated: boolean;
}

interface CostInfo {
  total_tokens: number;
  total_requests: number;
  estimated_cost: string;
  conversations_generated: number;
  remaining_budget: string;
}

interface LogEntry {
  timestamp: number;
  message: string;
}

interface ChatMessage {
  sender: string;
  message: string;
}

interface SecurePanelProps {
  onLog: (message: string) => void;
}

export default function SecurePanel({ onLog }: SecurePanelProps) {
  const [handshakeStatus, setHandshakeStatus] = useState<HandshakeStatus>({
    status: "idle",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [mlScore, setMlScore] = useState<number | null>(null);
  const [secureMessage, setSecureMessage] = useState("");
  const [encryptedMessage, setEncryptedMessage] = useState("");
  const [showDecrypted, setShowDecrypted] = useState(false);
  const [collaboration, setCollaboration] = useState<Collaboration | null>(
    null
  );
  const [conversationMessages, setConversationMessages] = useState<
    ConversationMessage[]
  >([]);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [isPlayingConversation, setIsPlayingConversation] = useState(false);
  const [costInfo, setCostInfo] = useState<CostInfo | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);

  // Add log function to add logs to the panel
  const addLogEntry = (message: string) => {
    const logEntry: LogEntry = {
      timestamp: Date.now(),
      message: message,
    };
    setLogs((prev) => [...prev, logEntry]);
    onLog(message); // Also call the parent onLog
  };

  // Fetch cost info periodically
  useEffect(() => {
    const fetchCostInfo = async () => {
      try {
        const response = await axios.get("http://localhost:8000/status");
        setCostInfo(response.data.openai_usage);
      } catch (error) {
        console.error("Failed to fetch cost info:", error);
      }
    };

    fetchCostInfo();
    const interval = setInterval(fetchCostInfo, 5000);
    return () => clearInterval(interval);
  }, []);

  const startAgentCollaboration = async () => {
    setIsLoading(true);
    setHandshakeStatus({ status: "idle" });
    setCollaboration(null);
    setConversationMessages([]);
    setCurrentMessageIndex(0);
    addLogEntry("🤖 Starting Agent A → Agent B collaboration...");

    try {
      const response = await axios.post(
        "http://localhost:8000/start_agent_collaboration"
      );

      if (response.data.status === "collaboration_started") {
        setCollaboration(response.data);
        setHandshakeStatus({
          status: "collaborating",
          handshake_id: response.data.handshake_id,
          session_token: response.data.session_token,
        });

        addLogEntry(
          "✅ Handshake successful! Starting secure collaboration..."
        );

        // Start playing the conversation
        playConversation(response.data.conversation);
      } else {
        addLogEntry("❌ Collaboration failed to start");
        setHandshakeStatus({ status: "failed" });
      }
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      addLogEntry(`❌ Collaboration error: ${errorMessage}`);
      setHandshakeStatus({ status: "failed" });
    } finally {
      setIsLoading(false);
    }
  };

  const startFakeAgentAttack = async () => {
    setIsLoading(true);
    setHandshakeStatus({ status: "idle" });
    setCollaboration(null);
    setConversationMessages([]);
    setCurrentMessageIndex(0);
    addLogEntry("🚨 Fake Agent F attempting to infiltrate...");

    try {
      const response = await axios.post(
        "http://localhost:8000/start_fake_attack_demo"
      );

      if (response.data.detected) {
        setHandshakeStatus({
          status: "failed",
          fakeAgentDetected: true,
          handshake_id: response.data.handshake_id,
        });

        setMlScore(response.data.ml_score);
        addLogEntry("🛡️ Fake agent detected and blocked!");

        // Play the blocked conversation
        playConversation(response.data.conversation);
      } else {
        setHandshakeStatus({
          status: "verified",
          fakeAgentDetected: false,
        });
        addLogEntry("⚠️ Warning: Fake agent was not detected!");
      }
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      addLogEntry(`❌ Attack simulation error: ${errorMessage}`);
      setHandshakeStatus({ status: "failed" });
    } finally {
      setIsLoading(false);
    }
  };

  const playConversation = (conversation: ConversationMessage[]) => {
    setIsPlayingConversation(true);
    setConversationMessages([]);

    const playNextMessage = (index: number) => {
      if (index >= conversation.length) {
        setIsPlayingConversation(false);
        return;
      }

      const message = conversation[index];
      setConversationMessages((prev) => [...prev, message]);

      // Log the message
      const statusIcon =
        message.status === "blocked"
          ? "🚫"
          : message.sender === "system"
          ? "🤖"
          : "💬";
      addLogEntry(`${statusIcon} ${message.sender}: ${message.message}`);

      // Continue to next message after delay
      setTimeout(() => playNextMessage(index + 1), 1500);
    };

    playNextMessage(0);
  };

  const sendChatMessage = async () => {
    if (!chatMessage.trim()) return;

    const userMessage = { sender: "user", message: chatMessage };
    setChatHistory((prev) => [...prev, userMessage]);
    setChatMessage("");

    try {
      const response = await axios.post("http://localhost:8000/chat", {
        agent_id: "agent_a",
        message: chatMessage,
      });

      const agentMessage = {
        sender: "agent_a",
        message: response.data.content,
      };
      setChatHistory((prev) => [...prev, agentMessage]);
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      const errorResponse = {
        sender: "system",
        message: `Error: ${errorMessage}`,
      };
      setChatHistory((prev) => [...prev, errorResponse]);
    }
  };

  const getStatusIcon = () => {
    if (handshakeStatus.fakeAgentDetected) {
      return <AlertTriangle className="w-5 h-5 text-red-600" />;
    }
    switch (handshakeStatus.status) {
      case "verified":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "collaborating":
        return (
          <MessageCircle className="w-5 h-5 text-purple-600 animate-pulse" />
        );
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
        return "VERIFIED & SECURE";
      case "collaborating":
        return "AGENTS COLLABORATING";
      case "failed":
        return "VERIFICATION FAILED";
      case "started":
        return "HANDSHAKE IN PROGRESS";
      case "responded":
        return "SIGNATURE RECEIVED";
      default:
        return "READY FOR VERIFICATION";
    }
  };

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="text-center p-4 bg-white border-b">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent mb-1">
          VeriAI Security Protocol
        </h1>
        <p className="text-gray-600 text-sm">
          AI-to-AI Identity Verification & Secure Communication
        </p>
      </div>

      {/* Status Bar */}
      <div className="bg-gradient-to-r from-blue-50 to-green-50 p-3 border-b border-blue-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="font-semibold text-sm">{getStatusText()}</span>
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-600">
            <span>
              ID: {handshakeStatus.handshake_id?.slice(0, 8) || "None"}
            </span>
            <span>
              Session: {handshakeStatus.session_token?.slice(0, 6) || "None"}...
            </span>
          </div>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Handshake Protocol Section */}
        <div className="bg-white rounded-lg shadow-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold">Handshake Protocol</h3>
          </div>

          {/* Demo Buttons */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
            <button
              onClick={startAgentCollaboration}
              disabled={isLoading || isPlayingConversation}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-lg hover:from-blue-700 hover:to-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Processing...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  🤖 Agent A ↔ Agent B
                </>
              )}
            </button>

            <button
              onClick={startFakeAgentAttack}
              disabled={isLoading || isPlayingConversation}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-lg hover:from-red-700 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Processing...
                </>
              ) : (
                <>
                  <AlertTriangle className="w-4 h-4" />
                  🚨 Fake Agent Attack
                </>
              )}
            </button>
          </div>

          {/* Compact Security Steps */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            <div className="flex items-center gap-2 p-2 bg-blue-50 rounded-lg">
              <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xs">1</span>
              </div>
              <div>
                <div className="font-medium text-sm">Challenge Generation</div>
                <div className="text-xs text-gray-600">Cryptographic nonce</div>
              </div>
            </div>

            <div className="flex items-center gap-2 p-2 bg-green-50 rounded-lg">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xs">2</span>
              </div>
              <div>
                <div className="font-medium text-sm">HMAC Signature</div>
                <div className="text-xs text-gray-600">SHA256 verification</div>
              </div>
            </div>

            <div className="flex items-center gap-2 p-2 bg-purple-50 rounded-lg">
              <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xs">3</span>
              </div>
              <div>
                <div className="font-medium text-sm">ML Verification</div>
                <div className="text-xs text-gray-600">Anomaly detection</div>
              </div>
            </div>

            <div className="flex items-center gap-2 p-2 bg-emerald-50 rounded-lg">
              <div className="w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center">
                <CheckCircle className="w-3 h-3 text-white" />
              </div>
              <div>
                <div className="font-medium text-sm">Secure Session</div>
                <div className="text-xs text-gray-600">
                  Encrypted communication
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Agent Collaboration Section */}
        {collaboration && (
          <div className="bg-white rounded-lg shadow-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-4">
              <MessageCircle className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-semibold">
                Agent Collaboration (
                {collaboration.ai_generated ? "AI-Generated" : "Simulated"})
              </h3>
              <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                Live Conversation
              </span>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto border rounded-lg p-3 bg-gray-50">
              {conversationMessages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.sender === "agent_a"
                      ? "justify-start"
                      : "justify-end"
                  }`}
                >
                  <div
                    className={`max-w-[75%] px-4 py-3 rounded-lg break-words ${
                      message.sender === "agent_a"
                        ? "bg-blue-100 text-blue-900"
                        : message.sender === "agent_b"
                        ? "bg-green-100 text-green-900"
                        : message.status === "blocked"
                        ? "bg-red-100 text-red-900 border border-red-300"
                        : "bg-gray-100 text-gray-900"
                    }`}
                  >
                    <div className="font-semibold text-xs mb-1">
                      {message.sender === "agent_a"
                        ? "🤖 Agent A"
                        : message.sender === "agent_b"
                        ? "🤖 Agent B"
                        : message.sender === "fake_agent_f"
                        ? "🚨 Fake Agent F"
                        : "🛡️ System"}
                    </div>
                    <div className="text-sm whitespace-pre-wrap overflow-wrap-anywhere">
                      {message.message}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {isPlayingConversation && (
              <div className="mt-4 flex items-center justify-center gap-2 text-purple-600">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-purple-600 border-t-transparent"></div>
                <span className="text-sm">Agents are communicating...</span>
              </div>
            )}
          </div>
        )}

        {/* OpenAI Cost Tracker */}
        {costInfo && (
          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg shadow-lg p-4 border border-green-200">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-green-600 font-semibold text-lg">
                💰 OpenAI Usage Tracker
              </span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="bg-white p-3 rounded-lg">
                <span className="text-gray-600 block">Conversations:</span>
                <span className="font-bold text-lg text-blue-600">
                  {costInfo.conversations_generated}
                </span>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <span className="text-gray-600 block">Tokens:</span>
                <span className="font-bold text-lg text-purple-600">
                  {costInfo.total_tokens}
                </span>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <span className="text-gray-600 block">Cost:</span>
                <span className="font-bold text-lg text-green-600">
                  {costInfo.estimated_cost}
                </span>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <span className="text-gray-600 block">Remaining:</span>
                <span className="font-bold text-lg text-blue-600">
                  {costInfo.remaining_budget}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
