"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { StudyState, AlertPayload, MonitorUpdate } from "../types/monitor";

export type ConnectionStatus = "CONNECTED" | "DISCONNECTED" | "RECONNECTING" | "CONNECTING";

export interface TimelineEvent {
  id: string;
  timestamp: string;
  timeLabel: string;
  type: string;
  state?: string;
  message?: string;
  color: string;
}

export interface MonitorSocketState {
  status: ConnectionStatus;
  sessionId: string | null;
  state: StudyState;
  confidence: number;
  focusScore: number;
  focusedTime: number;
  distractedTime: number;
  phoneTime: number;
  drowsyTime: number;
  readingTime: number;
  duration: number;
  currentStreak: number;
  longestStreak: number;
  distractionCount: number;
  recentEvents: TimelineEvent[];
  activeAlert: AlertPayload | null;
  dismissAlert: () => void;
}

const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL || "ws://127.0.0.1:8000/ws/monitor";

export function useMonitorSocket(): MonitorSocketState {
  const [status, setStatus] = useState<ConnectionStatus>("CONNECTING");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [state, setState] = useState<StudyState>("FOCUSED");
  const [confidence, setConfidence] = useState<number>(0.95);
  const [focusScore, setFocusScore] = useState<number>(100);
  const [focusedTime, setFocusedTime] = useState<number>(0);
  const [distractedTime, setDistractedTime] = useState<number>(0);
  const [phoneTime, setPhoneTime] = useState<number>(0);
  const [drowsyTime, setDrowsyTime] = useState<number>(0);
  const [readingTime, setReadingTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [currentStreak, setCurrentStreak] = useState<number>(0);
  const [longestStreak, setLongestStreak] = useState<number>(0);
  const [distractionCount, setDistractionCount] = useState<number>(0);
  const [recentEvents, setRecentEvents] = useState<TimelineEvent[]>([]);
  const [activeAlert, setActiveAlert] = useState<AlertPayload | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const backoffRef = useRef<number>(1000);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const alertTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const dismissAlert = useCallback(() => {
    setActiveAlert(null);
  }, []);

  const addTimelineEvent = useCallback((event: TimelineEvent) => {
    setRecentEvents((prev) => [event, ...prev.slice(0, 19)]);
  }, []);

  const connect = useCallback(() => {
    try {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        return;
      }

      setStatus((prev) => (prev === "DISCONNECTED" ? "RECONNECTING" : "CONNECTING"));
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus("CONNECTED");
        backoffRef.current = 1000;

        // Start heartbeat ping
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "ping" }));
          }
        }, 15000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const timeLabel = new Date().toLocaleTimeString();

          switch (data.type) {
            case "CONNECTED":
              break;

            case "MONITOR_UPDATE":
              if (data.session_id) setSessionId(data.session_id);
              if (data.state) setState(data.state.toUpperCase() as StudyState);
              if (data.confidence !== undefined) setConfidence(data.confidence);
              if (data.focus_score !== undefined) setFocusScore(Math.round(data.focus_score));
              if (data.focused_time !== undefined) setFocusedTime(data.focused_time);
              if (data.distracted_time !== undefined) setDistractedTime(data.distracted_time);
              if (data.phone_time !== undefined) setPhoneTime(data.phone_time);
              if (data.drowsy_time !== undefined) setDrowsyTime(data.drowsy_time);
              if (data.reading_time !== undefined) setReadingTime(data.reading_time);
              if (data.duration !== undefined) setDuration(data.duration);
              if (data.current_streak !== undefined) setCurrentStreak(data.current_streak);
              if (data.longest_streak !== undefined) setLongestStreak(data.longest_streak);
              if (data.distraction_count !== undefined) setDistractionCount(data.distraction_count);
              break;

            case "BEHAVIOR_CHANGE":
              const newState = (data.current || "").toUpperCase() as StudyState;
              setState(newState);
              if (data.focus_score !== undefined) setFocusScore(Math.round(data.focus_score));
              if (data.confidence !== undefined) setConfidence(data.confidence);

              const isNeg = ["PHONE_USAGE", "DROWSY", "POOR_POSTURE", "LOOKING_AWAY"].includes(newState);
              addTimelineEvent({
                id: Math.random().toString(36).substring(2, 9),
                timestamp: new Date().toISOString(),
                timeLabel,
                type: "BEHAVIOR_CHANGE",
                state: newState,
                message: `State changed to ${newState}`,
                color: isNeg ? "text-rose-400 border-rose-500/40" : "text-emerald-400 border-emerald-500/40"
              });
              break;

            case "ALERT":
              setActiveAlert(data as AlertPayload);
              if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
              alertTimeoutRef.current = setTimeout(() => {
                setActiveAlert(null);
              }, 6000);

              addTimelineEvent({
                id: Math.random().toString(36).substring(2, 9),
                timestamp: new Date().toISOString(),
                timeLabel,
                type: "ALERT",
                message: data.message || "Alert triggered",
                color: "text-amber-400 border-amber-500/40"
              });
              break;

            case "SESSION_STARTED":
              setSessionId(data.session_id);
              setDuration(0);
              addTimelineEvent({
                id: Math.random().toString(36).substring(2, 9),
                timestamp: new Date().toISOString(),
                timeLabel,
                type: "SESSION",
                message: `Study session started (${data.session_id})`,
                color: "text-blue-400 border-blue-500/40"
              });
              break;

            case "SESSION_ENDED":
              addTimelineEvent({
                id: Math.random().toString(36).substring(2, 9),
                timestamp: new Date().toISOString(),
                timeLabel,
                type: "SESSION",
                message: `Session ended. Focus: ${Math.round(data.focus_score || 0)}%`,
                color: "text-purple-400 border-purple-500/40"
              });
              break;

            default:
              break;
          }
        } catch (err) {
          console.error("Error parsing WebSocket payload:", err);
        }
      };

      ws.onclose = () => {
        setStatus("DISCONNECTED");
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);

        // Schedule auto-reconnect with exponential backoff
        const delay = Math.min(backoffRef.current, 10000);
        backoffRef.current = Math.min(backoffRef.current * 1.5, 10000);
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch (e) {
      console.error("WebSocket connection error:", e);
      setStatus("DISCONNECTED");
    }
  }, [addTimelineEvent]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
      if (alertTimeoutRef.current) clearTimeout(alertTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    status,
    sessionId,
    state,
    confidence,
    focusScore,
    focusedTime,
    distractedTime,
    phoneTime,
    drowsyTime,
    readingTime,
    duration,
    currentStreak,
    longestStreak,
    distractionCount,
    recentEvents,
    activeAlert,
    dismissAlert
  };
}
