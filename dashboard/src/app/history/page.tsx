"use client";

import React, { useEffect, useState } from "react";
import { api } from "../../services/api";
import {
  SessionSummary,
  AggregatedAnalytics,
  StudyRecommendation
} from "../../types/monitor";
import { RecommendationsCard } from "../../components/history/RecommendationsCard";

function formatMinutes(seconds: number): string {
  const m = Math.round(seconds / 60);
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  const remM = m % 60;
  return `${h}h ${remM}m`;
}

export default function HistoryPage() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [analytics, setAnalytics] = useState<AggregatedAnalytics | null>(null);
  const [recommendations, setRecommendations] = useState<StudyRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [sessList, aggData, recs] = await Promise.allSettled([
          api.getSessions(30),
          api.getAggregatedAnalytics(),
          api.getRecommendations()
        ]);

        if (sessList.status === "fulfilled") setSessions(sessList.value);
        if (aggData.status === "fulfilled") setAnalytics(aggData.value);
        if (recs.status === "fulfilled") setRecommendations(recs.value);
      } catch (err) {
        console.error("Failed to load historical analytics:", err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-black text-white tracking-tight">
          Study History & Longitudinal Intelligence
        </h2>
        <p className="text-xs text-zinc-400 mt-1">
          Historical session logs, aggregate focus metrics, and AI behavioral recommendations.
        </p>
      </div>

      {/* Aggregate Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 bg-zinc-900/80 border border-zinc-800 rounded-xl">
          <span className="text-xs text-zinc-400 uppercase font-medium">Total Sessions</span>
          <div className="text-2xl font-bold text-white mt-1">
            {analytics?.total_sessions ?? sessions.length}
          </div>
        </div>

        <div className="p-4 bg-zinc-900/80 border border-zinc-800 rounded-xl">
          <span className="text-xs text-zinc-400 uppercase font-medium">Total Study Time</span>
          <div className="text-2xl font-bold text-indigo-400 mt-1">
            {analytics ? formatMinutes(analytics.total_study_time) : "0m"}
          </div>
        </div>

        <div className="p-4 bg-zinc-900/80 border border-zinc-800 rounded-xl">
          <span className="text-xs text-zinc-400 uppercase font-medium">Average Focus</span>
          <div className="text-2xl font-bold text-emerald-400 mt-1">
            {analytics ? `${Math.round(analytics.average_focus_score)}%` : "100%"}
          </div>
        </div>

        <div className="p-4 bg-zinc-900/80 border border-zinc-800 rounded-xl">
          <span className="text-xs text-zinc-400 uppercase font-medium">Longest Focus Streak</span>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            {analytics ? formatMinutes(analytics.longest_focus_streak) : "0m"}
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <RecommendationsCard recommendations={recommendations} />

      {/* Session History Table */}
      <div className="p-6 bg-zinc-900/80 backdrop-blur border border-zinc-800 rounded-2xl shadow-xl">
        <h3 className="text-xs uppercase tracking-widest text-zinc-400 font-semibold mb-4">
          Recorded Study Sessions
        </h3>

        {loading ? (
          <p className="text-zinc-400 text-sm py-4 text-center">Loading study history...</p>
        ) : sessions.length === 0 ? (
          <div className="text-center py-8 text-zinc-400 text-sm">
            No study sessions recorded yet. Start a session from the Live Monitor!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-zinc-800 text-zinc-400 uppercase">
                  <th className="pb-3 font-semibold">Session ID</th>
                  <th className="pb-3 font-semibold">Date & Time</th>
                  <th className="pb-3 font-semibold">Duration</th>
                  <th className="pb-3 font-semibold">Focus Score</th>
                  <th className="pb-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {sessions.map((s) => (
                  <tr key={s.id} className="hover:bg-zinc-800/30 transition">
                    <td className="py-3.5 font-bold text-white">{s.id}</td>
                    <td className="py-3.5 text-zinc-300">
                      {new Date(s.start_time).toLocaleString()}
                    </td>
                    <td className="py-3.5 text-zinc-200">
                      {formatMinutes(s.duration)}
                    </td>
                    <td className="py-3.5">
                      <span
                        className={`px-2.5 py-1 rounded font-bold ${
                          s.focus_score >= 80
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                            : s.focus_score >= 60
                            ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                            : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                        }`}
                      >
                        {Math.round(s.focus_score)}%
                      </span>
                    </td>
                    <td className="py-3.5">
                      <span className="text-zinc-400 uppercase text-[10px]">
                        {s.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
