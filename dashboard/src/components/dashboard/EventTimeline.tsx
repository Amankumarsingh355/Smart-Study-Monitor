"use client";

import React from "react";
import { TimelineEvent } from "../../hooks/useMonitorSocket";

interface EventTimelineProps {
  events: TimelineEvent[];
}

export const EventTimeline: React.FC<EventTimelineProps> = ({ events }) => {
  return (
    <div className="p-6 bg-zinc-900/80 backdrop-blur border border-zinc-800 rounded-2xl shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs uppercase tracking-widest text-zinc-400 font-semibold">
          Live Activity Stream
        </span>
        <span className="text-xs text-zinc-400 font-medium">
          {events.length} event{events.length === 1 ? "" : "s"}
        </span>
      </div>

      <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
        {events.length === 0 ? (
          <div className="text-center py-8 text-zinc-400 text-sm">
            No live transitions recorded yet. Signals streaming...
          </div>
        ) : (
          events.map((ev) => (
            <div
              key={ev.id}
              className={`flex items-center justify-between p-3 rounded-lg border bg-zinc-950/40 text-xs font-mono transition-all duration-300 ${ev.color}`}
            >
              <div className="flex items-center gap-3">
                <span className="text-zinc-400">{ev.timeLabel}</span>
                <span className="font-semibold">{ev.message || ev.state}</span>
              </div>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
                {ev.type}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
