"use client";

import React, { useState, useRef, useEffect } from "react";
import { MessageCircle, Send, Bot, User } from "lucide-react";
import axios from "axios";

interface Message {
  id: string;
  sender: "user" | "agent";
  content: string;
  timestamp: number;
  agent_id?: string;
}

interface ChatPanelProps {
  onLog: (message: string) => void;
}

export default function ChatPanel({ onLog }: Readonly<ChatPanelProps>) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [selectedAgent, setSelectedAgent] = useState("agent_a");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);


  const prevMessagesLength = useRef(0);

  useEffect(() => {
    // Only auto-scroll if there are new messages
    if (messages.length > prevMessagesLength.current && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
    prevMessagesLength.current = messages.length;
  }, [messages]);

  const agents = [
    { id: "agent_a", name: "Agent A (Requester)", color: "bg-blue-500" },
    { id: "agent_b", name: "Agent B (Responder)", color: "bg-green-500" },
    { id: "fake_agent_f", name: "Fake Agent F", color: "bg-red-500" },
  ];

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      content: inputMessage,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    onLog(`💬 User to ${selectedAgent}: ${inputMessage}`);

    try {
      const response = await axios.post("http://localhost:8000/chat", {
        agent_id: selectedAgent,
        message: inputMessage,
      });

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "agent",
        content: response.data.content,
        timestamp: Date.now(),
        agent_id: selectedAgent,
      };

      setMessages((prev) => [...prev, agentMessage]);
      onLog(`🤖 ${selectedAgent}: ${response.data.content}`);

      if (response.data.from_cache) {
        onLog(`💾 Response served from cache`);
      }
    } catch (error) {
      onLog(`❌ Chat error: ${error}`);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "agent",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: Date.now(),
        agent_id: selectedAgent,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setInputMessage("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getAgentColor = (agentId: string) => {
    return agents.find((a) => a.id === agentId)?.color || "bg-gray-500";
  };

  const clearChat = () => {
    setMessages([]);
    onLog("🗑️ Chat cleared");
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 flex flex-col" style={{ height: '600px' }}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-semibold">AI Agent Chat</h2>
        </div>
        <button
          onClick={clearChat}
          className="text-sm text-gray-500 cursor-pointer hover:text-gray-700 px-2 py-1 rounded"
        >
          Clear
        </button>
      </div>

      {/* Agent Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Chat with Agent:
        </label>
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {agents.map((agent) => (
            <option key={agent.id} value={agent.id}>
              {agent.name}
            </option>
          ))}
        </select>
      </div>

      {/* Messages */}
      <div ref={messagesContainerRef} className="flex-1 overflow-y-auto mb-4 space-y-3 min-h-0 pr-2 -mr-2">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <Bot className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>Start a conversation with an AI agent</p>
            <p className="text-sm">
              Try: &quot;Hello, can you verify your identity?&quot;
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === "user"
                    ? "bg-blue-600 text-white"
                    : `${getAgentColor(message.agent_id || "")} text-white`
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {message.sender === "user" ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                  <span className="text-xs opacity-75">
                    {message.sender === "user" ? "You" : message.agent_id}
                  </span>
                </div>
                <p className="text-sm">{message.content}</p>
                <p className="text-xs opacity-75 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isLoading}
          className="flex-1 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
        />
        <button
          onClick={sendMessage}
          disabled={!inputMessage.trim() || isLoading}
          className="px-4 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Send className="w-4 h-4" />
          {isLoading ? "Sending..." : "Send"}
        </button>
      </div>

      {/* Quick Actions */}
      <div className="mt-3 flex flex-wrap gap-2">
        <button
          onClick={() =>
            setInputMessage("Hello, I'm ready to verify identities.")
          }
          className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
        >
          Greeting
        </button>
        <button
          onClick={() =>
            setInputMessage("Can you prove you're a genuine AI agent?")
          }
          className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
        >
          Challenge
        </button>
        <button
          onClick={() => setInputMessage("Let's start the handshake protocol.")}
          className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
        >
          Handshake
        </button>
      </div>
    </div>
  );
}
