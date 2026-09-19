"use client";

import React from "react";
import { ConnectionStatus as StatusType } from "../../hooks/useMonitorSocket";

interface ConnectionStatusProps {
  status: StatusType;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ status }) => {
  const config = {
    CONNECTED: {
      label: "CONNECTED",
      color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
      dot: "bg-emerald-400"
    },
    DISCONNECTED: {
      label: "DISCONNECTED",
      color: "text-rose-400 border-rose-500/30 bg-rose-500/10",
      dot: "bg-rose-400"
    },
    RECONNECTING: {
      label: "RECONNECTING...",
      color: "text-amber-400 border-amber-500/30 bg-amber-500/10",
      dot: "bg-amber-400 animate-ping"
    },
    CONNECTING: {
      label: "CONNECTING...",
      color: "text-zinc-400 border-zinc-700 bg-zinc-800/40",
      dot: "bg-zinc-400 animate-pulse"
    }
  }[status];

  return (
    <div className={`flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-mono font-bold tracking-wider ${config.color}`}>
      <span className={`h-2 w-2 rounded-full ${config.dot}`} />
      <span>{config.label}</span>
    </div>
  );
};
