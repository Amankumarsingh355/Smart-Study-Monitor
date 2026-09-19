"use client";

import React from "react";

interface MetricsGridProps {
  focusedTime: number;
  distractedTime: number;
  phoneTime: number;
  drowsyTime: number;
  readingTime: number;
}

function formatDuration(sec: number): string {
  const s = Math.round(sec);
  const m = Math.floor(s / 60);
  const remS = s % 60;
  if (m === 0) return `${remS}s`;
  return `${m}m ${remS}s`;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({
  focusedTime,
  distractedTime,
  phoneTime,
  drowsyTime,
  readingTime
}) => {
  const cards = [
    {
      title: "Focused Time",
      value: formatDuration(focusedTime),
      color: "text-emerald-400",
      border: "border-emerald-500/20",
      bg: "bg-emerald-500/5",
      icon: "🎯"
    },
    {
      title: "Distracted Time",
      value: formatDuration(distractedTime),
      color: "text-amber-400",
      border: "border-amber-500/20",
      bg: "bg-amber-500/5",
      icon: "⚠️"
    },
    {
      title: "Phone Usage",
      value: formatDuration(phoneTime),
      color: "text-rose-400",
      border: "border-rose-500/20",
      bg: "bg-rose-500/5",
      icon: "📱"
    },
    {
      title: "Drowsy Time",
      value: formatDuration(drowsyTime),
      color: "text-purple-400",
      border: "border-purple-500/20",
      bg: "bg-purple-500/5",
      icon: "💤"
    },
    {
      title: "Reading Time",
      value: formatDuration(readingTime),
      color: "text-blue-400",
      border: "border-blue-500/20",
      bg: "bg-blue-500/5",
      icon: "📖"
    }
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
      {cards.map((card) => (
        <div
          key={card.title}
          className={`p-4 rounded-xl border ${card.border} ${card.bg} bg-zinc-900/60 backdrop-blur flex flex-col justify-between`}
        >
          <div className="flex items-center justify-between text-xs text-zinc-400 font-medium mb-2">
            <span>{card.title}</span>
            <span>{card.icon}</span>
          </div>
          <div className={`text-2xl font-bold ${card.color} tracking-tight`}>
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
};
