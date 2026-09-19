"use client";

import React from "react";
import { StudyRecommendation } from "../../types/monitor";

interface RecommendationsCardProps {
  recommendations: StudyRecommendation[];
}

export const RecommendationsCard: React.FC<RecommendationsCardProps> = ({
  recommendations
}) => {
  const categoryIcons: Record<string, string> = {
    FATIGUE: "⚡",
    POSTURE: "🪑",
    DISTRACTION: "📵",
    FOCUS: "🎯",
    ROUTINE: "💡"
  };

  return (
    <div className="p-6 bg-zinc-900/80 backdrop-blur border border-zinc-800 rounded-2xl shadow-xl">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xl">🤖</span>
        <h3 className="text-base font-bold text-white tracking-wide">
          Adaptive AI Study Insights
        </h3>
      </div>

      <div className="space-y-4">
        {recommendations.length === 0 ? (
          <p className="text-zinc-400 text-sm">
            Evaluating historical study patterns...
          </p>
        ) : (
          recommendations.map((rec) => (
            <div
              key={rec.id}
              className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/50 hover:border-zinc-700 transition"
            >
              <div className="flex items-center gap-2 mb-1">
                <span>{categoryIcons[rec.category] || "💡"}</span>
                <span className="text-xs uppercase font-bold tracking-wider text-indigo-400">
                  {rec.category}
                </span>
                <span className="text-xs text-zinc-400 ml-auto">
                  {Math.round(rec.confidence * 100)}% confidence
                </span>
              </div>

              <h4 className="text-sm font-semibold text-zinc-100 mt-1">
                {rec.title}
              </h4>
              <p className="text-xs text-zinc-300 mt-1 leading-relaxed">
                {rec.insight}
              </p>

              <div className="mt-3 pt-2 border-t border-zinc-800/80 flex items-start gap-2 text-xs text-emerald-400 font-medium">
                <span className="font-bold">Recommendation:</span>
                <span>{rec.action}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
