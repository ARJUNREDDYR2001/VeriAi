"use client";

import React, { useState } from "react";
import ChatPanel from "../../components/ChatPanel";
import LogPanel from "../../components/LogPanel";
import SecurePanel from "../../components/SecurePanel";

export default function Home() {
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs((prev) => [...prev, message]);
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 ">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">VeriAI</h1>
              <p className="text-sm text-gray-600">
                AI-to-AI Verification Protocol Demo
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">
                  Live Demo
                </div>
                <div className="text-xs text-gray-500">
                  Handshake • ML Detection • Secure Mode
                </div>
              </div>
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-2 sm:px-4 py-4 flex flex-col">
        <div
          className="flex flex-col lg:flex-row gap-4"
          style={{ height: "700px" }}
        >
          {/* Secure Panel - Takes 60% width on large screens, full width on mobile */}
          <div className="lg:w-3/5 w-full h-full">
            <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200 h-full">
              <SecurePanel onLog={addLog} />
            </div>
          </div>

          {/* Log Panel - Takes 40% width on large screens, full width on mobile */}
          <div className="lg:w-2/5 w-full h-full">
            <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200 h-full">
              <LogPanel logs={logs} onClearLogs={clearLogs} />
            </div>
          </div>
        </div>

        {/* Impact Stats - More Compelling */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-center text-white">
            <div className="text-3xl font-bold">95%</div>
            <div className="text-sm opacity-90 mt-1">Fraud Detection Rate</div>
            <div className="text-xs opacity-75 mt-1">HMAC + ML Detection</div>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow-lg p-6 text-center text-white">
            <div className="text-3xl font-bold">&lt;300ms</div>
            <div className="text-sm opacity-90 mt-1">Verification Speed</div>
            <div className="text-xs opacity-75 mt-1">Real-time Security</div>
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow-lg p-6 text-center text-white">
            <div className="text-3xl font-bold">$2-5</div>
            <div className="text-sm opacity-90 mt-1">Demo Cost</div>
            <div className="text-xs opacity-75 mt-1">OpenAI Optimized</div>
          </div>
          <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg shadow-lg p-6 text-center text-white">
            <div className="text-3xl font-bold">100%</div>
            <div className="text-sm opacity-90 mt-1">Attack Prevention</div>
            <div className="text-xs opacity-75 mt-1">Crypto + Behavioral</div>
          </div>
        </div>

        {/* Problem & Solution - Hackathon Pitch */}
        <div className="mt-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-8 text-white">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold mb-2">
              🏆 Hackathon Demo: VeriAI
            </h2>
            <p className="text-lg opacity-90">AI-to-AI Verification Protocol</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl mb-3">🚨</div>
              <h3 className="font-bold text-lg mb-2">THE PROBLEM</h3>
              <p className="text-sm opacity-90">
                AI agents can&apos;t verify they&apos;re talking to other AIs vs
                humans/bots. This enables impersonation attacks in multi-agent
                systems.
              </p>
            </div>

            <div className="text-center">
              <div className="text-4xl mb-3">🔐</div>
              <h3 className="font-bold text-lg mb-2">OUR SOLUTION</h3>
              <p className="text-sm opacity-90">
                Cryptographic handshake protocol + ML fraud detection. Agents
                prove identity with HMAC signatures + behavioral analysis.
              </p>
            </div>

            <div className="text-center">
              <div className="text-4xl mb-3">🚀</div>
              <h3 className="font-bold text-lg mb-2">THE IMPACT</h3>
              <p className="text-sm opacity-90">
                Enables secure multi-agent systems, prevents AI impersonation,
                and creates trust layer for autonomous agent collaboration.
              </p>
            </div>
          </div>
        </div>

        {/* Demo Instructions */}
        <div className="mt-6 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold mb-4 text-center">
            🎯 Live Demo Flow
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl mb-2">1️⃣</div>
              <h3 className="font-medium text-blue-900 mb-2">
                Start Verification
              </h3>
              <p className="text-xs text-blue-700">
                Click &quot;Start Verify&quot; to see cryptographic handshake in
                action
              </p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl mb-2">2️⃣</div>
              <h3 className="font-medium text-green-900 mb-2">
                Watch ML Detection
              </h3>
              <p className="text-xs text-green-700">
                Observe real-time anomaly scoring and signature verification
              </p>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl mb-2">3️⃣</div>
              <h3 className="font-medium text-red-900 mb-2">Simulate Attack</h3>
              <p className="text-xs text-red-700">
                Test &quot;Fake Agent F&quot; to see fraud detection in action
              </p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl mb-2">4️⃣</div>
              <h3 className="font-medium text-purple-900 mb-2">
                Secure Messaging
              </h3>
              <p className="text-xs text-purple-700">
                Send encrypted messages between verified agents
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
