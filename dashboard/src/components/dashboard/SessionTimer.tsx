"use client";

import React from "react";

interface SessionTimerProps {
  durationSeconds: number;
  sessionId: string | null;
}

export const SessionTimer: React.FC<SessionTimerProps> = ({
  durationSeconds,
  sessionId
}) => {
  const totalSec = Math.floor(durationSeconds);
  const hours = Math.floor(totalSec / 3600);
  const minutes = Math.floor((totalSec % 3600) / 60);
  const seconds = totalSec % 60;

  const formatted = [
    hours.toString().padStart(2, "0"),
    minutes.toString().padStart(2, "0"),
    seconds.toString().padStart(2, "0")
  ].join(":");

  return (
    <div className="flex flex-col p-6 bg-zinc-900/80 backdrop-blur border border-zinc-800 rounded-2xl shadow-xl justify-between">
      <div>
        <span className="text-xs uppercase tracking-widest text-zinc-400 font-semibold mb-4 block">
          Study Session Timer
        </span>

        <div className="text-4xl sm:text-5xl font-mono font-black text-white tracking-wider my-2">
          {formatted}
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-zinc-800/80 flex items-center justify-between text-xs text-zinc-400">
        <span>Session ID:</span>
        <span className="font-mono text-zinc-300 bg-zinc-800/80 px-2 py-0.5 rounded">
          {sessionId ? sessionId.slice(0, 18) : "IDLE"}
        </span>
      </div>
    </div>
  );
};
