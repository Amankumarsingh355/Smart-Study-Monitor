"use client";

import React from "react";

interface FocusStreakProps {
  currentStreakSeconds: number;
  longestStreakSeconds: number;
}

function formatStreak(sec: number): string {
  const s = Math.round(sec);
  const m = Math.floor(s / 60);
  const remS = s % 60;
  if (m === 0) return `${remS}s`;
  return `${m}m ${remS}s`;
}

export const FocusStreak: React.FC<FocusStreakProps> = ({
  currentStreakSeconds,
  longestStreakSeconds
}) => {
  return (
    <div className="p-5 bg-gradient-to-br from-amber-500/10 via-zinc-900 to-zinc-900 border border-amber-500/20 rounded-2xl shadow-xl flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="h-12 w-12 rounded-xl bg-amber-500/20 flex items-center justify-center text-2xl animate-bounce">
          🔥
        </div>
        <div>
          <span className="text-xs uppercase tracking-wider text-amber-300/80 font-bold block">
            Current Focus Streak
          </span>
          <span className="text-2xl sm:text-3xl font-extrabold text-white">
            {formatStreak(currentStreakSeconds)}
          </span>
        </div>
      </div>

      <div className="text-right pl-4 border-l border-zinc-800">
        <span className="text-[11px] uppercase tracking-wider text-zinc-400 block font-medium">
          Session Best
        </span>
        <span className="text-sm font-semibold text-zinc-200">
          🏆 {formatStreak(longestStreakSeconds)}
        </span>
      </div>
    </div>
  );
};
