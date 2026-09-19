"use client";

import React from "react";
import { useMonitorSocket } from "../hooks/useMonitorSocket";
import { FocusScore } from "../components/dashboard/FocusScore";
import { CurrentState } from "../components/dashboard/CurrentState";
import { SessionTimer } from "../components/dashboard/SessionTimer";
import { MetricsGrid } from "../components/dashboard/MetricsGrid";
import { FocusStreak } from "../components/dashboard/FocusStreak";
import { EventTimeline } from "../components/dashboard/EventTimeline";
import { AlertBanner } from "../components/dashboard/AlertBanner";
import { ConnectionStatus } from "../components/dashboard/ConnectionStatus";

export default function DashboardPage() {
  const {
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
    recentEvents,
    activeAlert,
    dismissAlert
  } = useMonitorSocket();

  return (
    <div className="space-y-8">
      {/* Real-time Alert Banner Popup */}
      <AlertBanner alert={activeAlert} onDismiss={dismissAlert} />

      {/* Top Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-zinc-900">
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight">
            Live Study Monitor
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Real-time multi-modal posture, gaze, and focus tracking stream.
          </p>
        </div>

        <ConnectionStatus status={status} />
      </div>

      {/* Main Status & Score Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <CurrentState state={state} confidence={confidence} />
        <FocusScore score={focusScore} />
        <SessionTimer durationSeconds={duration} sessionId={sessionId} />
      </div>

      {/* Focus Streak Highlight */}
      <FocusStreak
        currentStreakSeconds={currentStreak}
        longestStreakSeconds={longestStreak}
      />

      {/* Telemetry Breakdown Grid */}
      <div>
        <h3 className="text-xs uppercase tracking-widest text-zinc-400 font-semibold mb-3">
          Session Duration Breakdown
        </h3>
        <MetricsGrid
          focusedTime={focusedTime}
          distractedTime={distractedTime}
          phoneTime={phoneTime}
          drowsyTime={drowsyTime}
          readingTime={readingTime}
        />
      </div>

      {/* Live Event Timeline */}
      <EventTimeline events={recentEvents} />
    </div>
  );
}
