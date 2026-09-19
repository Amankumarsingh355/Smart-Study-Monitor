/**
 * TypeScript Data Contracts for Smart Study Monitor Dashboard.
 * Maps 1:1 with FastAPI REST and WebSocket payloads.
 */

export type StudyState =
  | "FOCUSED"
  | "READING"
  | "LOOKING_AWAY"
  | "PHONE_USAGE"
  | "DROWSY"
  | "POOR_POSTURE"
  | "AWAY_FROM_DESK"
  | "FACE_BLOCKED"
  | "NO_FACE"
  | "DISTRACTED"
  | "UNKNOWN";

export interface MonitorUpdate {
  type: "MONITOR_UPDATE";
  timestamp: string;
  session_id: string;
  state: StudyState;
  confidence: number;
  focus_score: number;
  focused_time: number;
  distracted_time: number;
  phone_time: number;
  drowsy_time: number;
  reading_time: number;
  duration?: number;
  current_streak?: number;
  longest_streak?: number;
  distraction_count?: number;
}

export interface BehaviorChangePayload {
  type: "BEHAVIOR_CHANGE";
  session_id: string;
  previous: string;
  current: string;
  confidence: number;
  focus_score: number;
}

export interface AlertPayload {
  type: "ALERT";
  alert_type: string;
  severity: "INFO" | "WARNING" | "CRITICAL";
  message: string;
  timestamp: number | string;
}

export interface SessionLifecyclePayload {
  type: "SESSION_STARTED" | "SESSION_ENDED";
  session_id: string;
  timestamp?: string;
  duration?: number;
  focus_score?: number;
}

export interface SessionSummary {
  id: string;
  start_time: string;
  end_time?: string | null;
  duration: number;
  focus_score: number;
  focused_time: number;
  distracted_time: number;
  phone_time: number;
  drowsy_time: number;
  reading_time: number;
  no_face_time: number;
  posture_issue_time: number;
  longest_streak: number;
  distraction_count: number;
  status: string;
  created_at: string;
}

export interface SessionAnalytics {
  session_id: string;
  duration: number;
  focus_score: number;
  focused_time: number;
  reading_time: number;
  distracted_time: number;
  phone_time: number;
  drowsy_time: number;
  no_face_time: number;
  posture_issue_time: number;
  distraction_count: number;
  longest_streak: number;
  events_count: number;
  events_breakdown: Record<string, number>;
}

export interface AggregatedAnalytics {
  total_sessions: number;
  total_study_time: number;
  average_focus_score: number;
  total_distractions: number;
  total_phone_time: number;
  total_reading_time: number;
  longest_focus_streak: number;
}

export interface StudyRecommendation {
  id: string;
  category: "FOCUS" | "POSTURE" | "FATIGUE" | "DISTRACTION" | "ROUTINE";
  title: string;
  insight: string;
  action: string;
  confidence: number;
  evidence: Record<string, any>;
}
