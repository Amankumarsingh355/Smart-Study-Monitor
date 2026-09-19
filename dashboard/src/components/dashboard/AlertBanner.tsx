"use client";

import React from "react";
import { AlertPayload } from "../../types/monitor";

interface AlertBannerProps {
  alert: AlertPayload | null;
  onDismiss: () => void;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({ alert, onDismiss }) => {
  if (!alert) return null;

  const isCritical = alert.severity === "CRITICAL";

  return (
    <div
      className={`fixed top-4 left-1/2 transform -translate-x-1/2 z-50 w-11/12 max-w-xl p-4 rounded-xl shadow-2xl border flex items-center justify-between transition-all animate-in fade-in slide-in-from-top duration-300 ${
        isCritical
          ? "bg-rose-950/95 border-rose-500 text-rose-100 shadow-rose-950/50"
          : "bg-amber-950/95 border-amber-500 text-amber-100 shadow-amber-950/50"
      }`}
    >
      <div className="flex items-center gap-3">
        <span className="text-2xl animate-pulse">
          {isCritical ? "🚨" : "⚠️"}
        </span>
        <div>
          <h4 className="text-sm font-bold tracking-wide uppercase">
            {alert.alert_type.replace(/_/g, " ")}
          </h4>
          <p className="text-xs text-zinc-200 mt-0.5">{alert.message}</p>
        </div>
      </div>

      <button
        onClick={onDismiss}
        className="ml-4 px-2.5 py-1 text-xs font-semibold rounded-md bg-white/10 hover:bg-white/20 transition"
      >
        Dismiss
      </button>
    </div>
  );
};
