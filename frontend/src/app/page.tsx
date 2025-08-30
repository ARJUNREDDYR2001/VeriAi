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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
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
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-0">
          {/* Chat Panel */}
          <div className="lg:col-span-1">
            <ChatPanel onLog={addLog} />
          </div>

          {/* Secure Panel */}
          <div className="lg:col-span-1">
            <SecurePanel onLog={addLog} />
          </div>

          {/* Log Panel */}
          <div className="lg:col-span-1 flex flex-col h-[600px]">
            <LogPanel logs={logs} onClearLogs={clearLogs} />
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">🤝</div>
            <div className="text-sm text-gray-600 mt-1">Handshake Protocol</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-green-600">🔒</div>
            <div className="text-sm text-gray-600 mt-1">Secure Messaging</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">🤖</div>
            <div className="text-sm text-gray-600 mt-1">
              ML Anomaly Detection
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-red-600">🚨</div>
            <div className="text-sm text-gray-600 mt-1">Fraud Prevention</div>
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold mb-4">🚀 Demo Instructions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">
                1. Start Verification
              </h3>
              <p className="text-sm text-gray-600 mb-3">
                Click &quot;Start Verify (Agent A)&quot; to initiate the handshake
                protocol between Agent A and Agent B.
              </p>

              <h3 className="font-medium text-gray-900 mb-2">
                2. Watch the Process
              </h3>
              <p className="text-sm text-gray-600 mb-3">
                Observe the cryptographic challenge-response in the logs panel.
                See ML anomaly scores in real-time.
              </p>
            </div>
            <div>
              <h3 className="font-medium text-gray-900 mb-2">
                3. Test Security
              </h3>
              <p className="text-sm text-gray-600 mb-3">
                Click &quot; Simulate Fake Agent F &quot; to see how the system detects and
                blocks fraudulent agents.
              </p>

              <h3 className="font-medium text-gray-900 mb-2">
                4. Secure Communication
              </h3>
              <p className="text-sm text-gray-600">
                After successful verification, send encrypted messages between
                verified agents.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
