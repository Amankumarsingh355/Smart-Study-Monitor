"use client";

import React from "react";

interface FocusScoreProps {
  score: number;
}

export const FocusScore: React.FC<FocusScoreProps> = ({ score }) => {
  const clamped = Math.max(0, Math.min(100, score));
  const radius = 64;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clamped / 100) * circumference;

  let colorClass = "text-emerald-400 stroke-emerald-400";
  let bgGlow = "shadow-emerald-500/10";
  if (clamped < 60) {
    colorClass = "text-rose-400 stroke-rose-400";
    bgGlow = "shadow-rose-500/10";
  } else if (clamped < 80) {
    colorClass = "text-amber-400 stroke-amber-400";
    bgGlow = "shadow-amber-500/10";
  }

  return (
    <div className={`flex flex-col items-center justify-center p-6 bg-zinc-900/80 backdrop-blur border border-zinc-800 rounded-2xl shadow-xl ${bgGlow}`}>
      <span className="text-xs uppercase tracking-widest text-zinc-400 font-semibold mb-4">
        Focus Score
      </span>

      <div className="relative flex items-center justify-center">
        <svg className="w-40 h-40 transform -rotate-90" viewBox="0 0 160 160">
          {/* Background Track */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            className="stroke-zinc-800"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Animated Value Arc */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            className={`${colorClass} transition-all duration-700 ease-out`}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>

        {/* Center Text */}
        <div className="absolute flex flex-col items-center">
          <span className="text-4xl font-extrabold text-white tracking-tight">
            {clamped}
          </span>
          <span className="text-xs text-zinc-400 font-medium">/ 100</span>
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2">
        <span
          className={`h-2 w-2 rounded-full ${
            clamped >= 80 ? "bg-emerald-400 animate-pulse" : clamped >= 60 ? "bg-amber-400" : "bg-rose-400"
          }`}
        />
        <span className="text-xs text-zinc-300 font-medium">
          {clamped >= 80 ? "High Focus" : clamped >= 60 ? "Moderate Attention" : "Distracted"}
        </span>
      </div>
    </div>
  );
};
