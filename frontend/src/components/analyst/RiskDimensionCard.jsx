import React from 'react';
import { RiskBadge } from '../common/RiskBadge';
import { Edit3, BookOpen, AlertCircle, Sparkles, CheckCircle } from 'lucide-react';

export const RiskDimensionCard = ({ dimension, onOpenOverride, isLocked = false }) => {
  const isOverridden = dimension.analyst_override_score !== null && dimension.analyst_override_score !== undefined;

  const getTier = (s) => {
    if (s <= 3.0) return 'LOW';
    if (s <= 6.0) return 'MEDIUM';
    if (s <= 8.0) return 'HIGH';
    return 'CRITICAL';
  };

  const tier = getTier(dimension.final_score);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all shadow-lg flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <div className="flex items-center gap-2">
              <h4 className="font-bold text-sm text-slate-100">{dimension.dimension_name}</h4>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                Weight: {intPercent(dimension.weight)}%
              </span>
            </div>
            <div className="flex items-center gap-1.5 mt-1 text-xs text-cyan-400">
              <BookOpen className="w-3.5 h-3.5" />
              <span className="font-mono text-[11px] font-medium">{dimension.framework_citation}</span>
            </div>
          </div>

          <div className="text-right">
            <RiskBadge score={dimension.final_score} tier={tier} />
            {isOverridden && (
              <div className="text-[10px] text-amber-400 font-mono mt-1 font-semibold">
                Overridden (AI: {dimension.ai_score.toFixed(1)})
              </div>
            )}
          </div>
        </div>

        {/* Confidence score */}
        <div className="mb-3 flex items-center justify-between text-xs bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>AI Reasoning Confidence:</span>
          </div>
          <span className="font-mono font-bold text-cyan-300">
            {intPercent(dimension.confidence)}%
          </span>
        </div>

        {/* Reasoning */}
        <p className="text-xs text-slate-300 leading-relaxed mb-4">
          {dimension.reasoning}
        </p>

        {/* Traceability factors */}
        {dimension.traceability_factors && dimension.traceability_factors.length > 0 && (
          <div className="space-y-1 mb-4">
            <div className="text-[10px] uppercase font-mono text-slate-500 font-bold tracking-wider">
              Traceability Factors
            </div>
            <div className="flex flex-wrap gap-1.5">
              {dimension.traceability_factors.map((factor, idx) => (
                <span
                  key={idx}
                  className={`text-[11px] px-2 py-0.5 rounded font-mono ${
                    factor.includes('-')
                      ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/40'
                      : 'bg-rose-950/40 text-rose-300 border border-rose-800/30'
                  }`}
                >
                  {factor}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer / Override Button */}
      <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
        <span className="text-[11px] text-slate-400 font-mono">
          Final: <strong className="text-white">{dimension.final_score.toFixed(1)} / 10.0</strong>
        </span>

        {!isLocked && (
          <button
            onClick={() => onOpenOverride(dimension)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 transition-colors"
          >
            <Edit3 className="w-3 h-3 text-cyan-400" />
            <span>{isOverridden ? 'Edit Override' : 'Override Score'}</span>
          </button>
        )}
      </div>
    </div>
  );
};

const intPercent = (val) => {
  if (val <= 1.0) return Math.round(val * 100);
  return Math.round(val);
};
