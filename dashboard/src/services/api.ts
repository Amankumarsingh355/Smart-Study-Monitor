/**
 * API Service for Smart Study Monitor.
 * Encapsulates all REST HTTP communication with the FastAPI backend.
 */

import {
  SessionSummary,
  SessionAnalytics,
  AggregatedAnalytics,
  StudyRecommendation
} from "../types/monitor";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {})
      }
    });

    if (!res.ok) {
      throw new Error(`API error ${res.status}: ${res.statusText} at ${endpoint}`);
    }

    return (await res.json()) as T;
  } catch (error) {
    console.error(`Fetch failed for ${url}:`, error);
    throw error;
  }
}

export const api = {
  // Session Endpoints
  async getSessions(limit = 20, offset = 0): Promise<SessionSummary[]> {
    return fetchJson<SessionSummary[]>(`/sessions?limit=${limit}&offset=${offset}`);
  },

  async getSession(sessionId: string): Promise<SessionSummary> {
    return fetchJson<SessionSummary>(`/sessions/${sessionId}`);
  },

  async getCurrentSession(): Promise<any> {
    return fetchJson<any>(`/sessions/current`);
  },

  async startSession(sessionId?: string): Promise<SessionSummary> {
    return fetchJson<SessionSummary>(`/sessions/start`, {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId })
    });
  },

  async endSession(sessionId?: string): Promise<SessionSummary> {
    return fetchJson<SessionSummary>(`/sessions/end`, {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId })
    });
  },

  // Analytics Endpoints
  async getSessionAnalytics(sessionId: string): Promise<SessionAnalytics> {
    return fetchJson<SessionAnalytics>(`/analytics/session/${sessionId}`);
  },

  async getAggregatedAnalytics(): Promise<AggregatedAnalytics> {
    return fetchJson<AggregatedAnalytics>(`/analytics/summary`);
  },

  async getRecommendations(): Promise<StudyRecommendation[]> {
    return fetchJson<StudyRecommendation[]>(`/analytics/recommendations`);
  }
};
