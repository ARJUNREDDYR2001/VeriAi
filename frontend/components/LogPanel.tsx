"use client";

import React, { useState, useEffect } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Shield,
} from "lucide-react";
import axios from "axios";

interface EventData {
  agent_id?: string;
  agent_type?: string;
  handshake_id?: string;
  requester_id?: string;
  responder_id?: string;
  signature_valid?: boolean;
  anomaly_score?: number;
  sender_id?: string;
  receiver_id?: string;
  message_length?: number;
  response_length?: number;
}

interface LogEntry {
  timestamp: number;
  event_type: string;
  data: EventData;
  id: string;
}

interface LogPanelProps {
  readonly logs: readonly string[];
  readonly onClearLogs: () => void;
}

export default function LogPanel({ logs, onClearLogs }: LogPanelProps) {
  const [systemLogs, setSystemLogs] = useState<LogEntry[]>([]);
  const [isAutoRefresh, setIsAutoRefresh] = useState(true);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isAutoRefresh) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get("http://localhost:8000/logs");
          setSystemLogs(response.data.logs || []);
        } catch (error) {
          console.error("Failed to fetch logs:", error);
        }
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isAutoRefresh]);

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case "agent_registered":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "handshake_started":
        return <Clock className="w-4 h-4 text-blue-500" />;
      case "handshake_response":
        return <Shield className="w-4 h-4 text-purple-500" />;
      case "handshake_verified":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "fake_agent_detected":
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case "secure_message":
        return <Shield className="w-4 h-4 text-indigo-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case "agent_registered":
        return "border-l-green-500 bg-green-50";
      case "handshake_started":
        return "border-l-blue-500 bg-blue-50";
      case "handshake_response":
        return "border-l-purple-500 bg-purple-50";
      case "handshake_verified":
        return "border-l-green-500 bg-green-50";
      case "fake_agent_detected":
        return "border-l-red-500 bg-red-50";
      case "secure_message":
        return "border-l-indigo-500 bg-indigo-50";
      default:
        return "border-l-gray-500 bg-gray-50";
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  const formatEventData = (eventType: string, data: EventData) => {
    switch (eventType) {
      case "agent_registered":
        return `Agent ${data.agent_id} (${data.agent_type}) registered`;
      case "handshake_started":
        return `Handshake ${data.handshake_id?.substring(0, 8)} started: ${
          data.requester_id
        } → ${data.responder_id}`;
      case "handshake_response":
        return `Response from ${data.responder_id}: ${
          data.signature_valid ? "✅ Valid" : "❌ Invalid"
        } signature`;
      case "handshake_verified":
        return `Handshake verified! Session token issued. ML Score: ${data.anomaly_score?.toFixed(
          3
        )}`;
      case "fake_agent_detected":
        return (
          `🚨 Fake agent ${data.agent_id || "unknown"} detected and blocked! ` +
          `| Handshake ID: ${data.handshake_id?.substring(0, 8) || "N/A"}`
        );
      case "secure_message":
        return `Secure message: ${data.sender_id} → ${data.receiver_id} (${data.message_length} chars)`;
      case "chat_message":
        return `Chat: ${data.agent_id} (${data.message_length}→${data.response_length} chars)`;
      default:
        return JSON.stringify(data);
    }
  };

  const clearAllLogs = async () => {
    try {
      // Clear backend logs
      await axios.delete("http://localhost:8000/clear-logs");
      // Clear frontend logs
      setSystemLogs([]);
      onClearLogs();
    } catch (error) {
      console.error("Failed to clear logs:", error);
    }
  };

  const handleLogClick = (log: LogEntry) => {
    // You can add more detailed view or actions here
    console.log("Log details:", log);
  };

  return (
    <div
      className="bg-white rounded-lg shadow-lg p-4 flex flex-col h-[1500px] overflow-hidden"
      style={{ maxHeight: "500px" }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-green-600" />
          <h2 className="text-lg font-semibold">System Logs</h2>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1 text-sm">
            <input
              type="checkbox"
              checked={isAutoRefresh}
              onChange={(e) => setIsAutoRefresh(e.target.checked)}
              className="rounded"
              aria-label="Auto-refresh logs"
            />
            <span className="ml-1">Auto-refresh</span>
          </label>
          <button
            onClick={clearAllLogs}
            className="text-sm text-gray-500 hover:text-gray-700 px-2 py-1 rounded"
          >
            Clear
          </button>
        </div>
      </div>

      <div
        className="flex-1 overflow-y-auto space-y-2 min-h-0 pr-2 -mr-2 custom-scrollbar"
        style={{ maxHeight: "calc(100% - 60px)" }}
      >
        {/* System Events */}
        {systemLogs.map((log, index) => (
          <div
            key={`system-${log.id || index}`}
            className={`border-l-4 p-3 rounded-r mb-2 cursor-pointer hover:bg-gray-50 transition-colors ${getEventColor(
              log.event_type
            )}`}
            onClick={() => handleLogClick(log)}
          >
            <div className="flex items-start gap-2">
              {getEventIcon(log.event_type)}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900">
                    {log.event_type.replace(/_/g, " ").toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatTimestamp(log.timestamp)}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mt-1 break-words whitespace-pre-wrap overflow-wrap-anywhere">
                  {formatEventData(log.event_type, log.data)}
                </p>
              </div>
            </div>
          </div>
        ))}

        {/* UI Logs */}
        {logs.map((log, index) => {
          // Create a stable key using the log content and its index
          const logKey = `ui-${btoa(encodeURIComponent(log)).substring(
            0,
            20
          )}-${index}`;
          return (
            <div
              key={logKey}
              className="border-l-4 border-l-gray-400 bg-gray-50 p-3 rounded-r mb-2"
            >
              <div className="flex items-start gap-2">
                <Activity className="w-4 h-4 text-gray-500 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">
                      UI EVENT
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date().toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mt-1 font-mono break-words whitespace-pre-wrap overflow-wrap-anywhere">
                    {log}
                  </p>
                </div>
              </div>
            </div>
          );
        })}

        {systemLogs.length === 0 && logs.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No system events yet</p>
            <p className="text-sm">Start interacting with agents to see logs</p>
          </div>
        )}

        {/* Removed auto-scroll target */}
      </div>

      {/* Stats */}
      <div className="mt-auto pt-3 border-t border-gray-200">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-semibold text-blue-600">
              {
                systemLogs.filter((l) => l.event_type === "handshake_started")
                  .length
              }
            </div>
            <div className="text-xs text-gray-500">Handshakes</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-green-600">
              {
                systemLogs.filter((l) => l.event_type === "handshake_verified")
                  .length
              }
            </div>
            <div className="text-xs text-gray-500">Verified</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-red-600">
              {
                systemLogs.filter(
                  (l) =>
                    l.event_type === "fake_agent_detected" ||
                    (l.event_type === "handshake_response" &&
                      l.data.signature_valid === false)
                ).length
              }
            </div>
            <div className="text-xs text-gray-500">Blocked</div>
          </div>
        </div>
      </div>
    </div>
  );
}
