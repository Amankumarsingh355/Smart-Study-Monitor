"use client";

import React from "react";
import { StudyState } from "../../types/monitor";

interface CurrentStateProps {
  state: StudyState | string;
  confidence: number;
}

export const CurrentState: React.FC<CurrentStateProps> = ({ state, confidence }) => {
  const normState = (state || "UNKNOWN").toUpperCase();

  const stateConfig: Record<string, { label: string; badge: string; dot: string; desc: string }> = {
    FOCUSED: {
      label: "FOCUSED",
      badge: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
      dot: "bg-emerald-400 shadow-emerald-500/50",
      desc: "Deep study & screen attention"
    },
    READING: {
      label: "READING",
      badge: "bg-blue-500/10 text-blue-400 border-blue-500/30",
      dot: "bg-blue-400 shadow-blue-500/50",
      desc: "Active textbook or notes study"
    },
    LOOKING_AWAY: {
      label: "LOOKING AWAY",
      badge: "bg-amber-500/10 text-amber-400 border-amber-500/30",
      dot: "bg-amber-400 shadow-amber-500/50",
      desc: "Head turned away from desk"
    },
    PHONE_USAGE: {
      label: "PHONE USAGE",
      badge: "bg-rose-500/10 text-rose-400 border-rose-500/30 animate-pulse",
      dot: "bg-rose-400 shadow-rose-500/50",
      desc: "Smartphone detected in hands"
    },
    DROWSY: {
      label: "DROWSY",
      badge: "bg-purple-500/10 text-purple-400 border-purple-500/30 animate-pulse",
      dot: "bg-purple-400 shadow-purple-500/50",
      desc: "Prolonged eye closure / micro-sleep"
    },
    POOR_POSTURE: {
      label: "POOR POSTURE",
      badge: "bg-orange-500/10 text-orange-400 border-orange-500/30",
      dot: "bg-orange-400 shadow-orange-500/50",
      desc: "Severe slouching or neck tilt"
    },
    AWAY_FROM_DESK: {
      label: "AWAY FROM DESK",
      badge: "bg-zinc-500/10 text-zinc-400 border-zinc-500/30",
      dot: "bg-zinc-400",
      desc: "User absent from workspace"
    },
    NO_FACE: {
      label: "NO FACE",
      badge: "bg-zinc-500/10 text-zinc-400 border-zinc-500/30",
      dot: "bg-zinc-400",
      desc: "Face not detected by camera"
    },
    UNKNOWN: {
      label: "INITIALIZING",
      badge: "bg-zinc-500/10 text-zinc-400 border-zinc-500/30",
      dot: "bg-zinc-400",
      desc: "Evaluating behavioral stream..."
    }
  };

  const confPercent = Math.round(confidence <= 1.0 ? confidence * 100 : confidence);
  const cfg = stateConfig[normState] || stateConfig.UNKNOWN;

  return (
    <div className="flex flex-col p-6 bg-zinc-900/80 backdrop-blur border border-zinc-800 rounded-2xl shadow-xl justify-between">
      <div>
        <span className="text-xs uppercase tracking-widest text-zinc-400 font-semibold mb-4 block">
          Current Activity
        </span>

        <div className="flex items-center gap-3 mt-2">
          <span className={`h-3.5 w-3.5 rounded-full ${cfg.dot} shadow-lg animate-ping absolute`} />
          <span className={`h-3.5 w-3.5 rounded-full ${cfg.dot}`} />
          <span className={`px-3 py-1 rounded-full text-base font-bold tracking-wide border ${cfg.badge}`}>
            {cfg.label}
          </span>
        </div>

        <p className="text-xs text-zinc-400 mt-3 font-normal">
          {cfg.desc}
        </p>
      </div>

      <div className="mt-6 pt-4 border-t border-zinc-800/80">
        <div className="flex justify-between items-center text-xs mb-1.5">
          <span className="text-zinc-400 font-medium">Confidence</span>
          <span className="text-white font-bold">{confPercent}%</span>
        </div>
        <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
          <div
            className="bg-indigo-500 h-full rounded-full transition-all duration-500"
            style={{ width: `${confPercent}%` }}
          />
        </div>
      </div>
    </div>
  );
};
