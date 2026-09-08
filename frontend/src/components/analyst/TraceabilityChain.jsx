import React from 'react';
import { GitCommit, ArrowDown, Shield, CheckCircle2, UserCheck, Sparkles } from 'lucide-react';

export const TraceabilityChain = ({ dimensions = [], caseTitle }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <GitCommit className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Deterministic Traceability Chain</h3>
            <p className="text-xs text-slate-400">Every score component is traceable to specific facts, regulations, and analyst decisions.</p>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {dimensions.map((dim) => {
          const isOverridden = dim.analyst_override_score !== null && dim.analyst_override_score !== undefined;
          
          return (
            <div key={dim.id || dim.dimension_key} className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-200 uppercase tracking-wider">{dim.dimension_name}</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                  {dim.framework_citation}
                </span>
              </div>

              {/* Step Flow */}
              <div className="space-y-2 text-xs">
                {/* Inputs */}
                {dim.traceability_factors && dim.traceability_factors.map((factor, idx) => (
                  <div key={idx} className="flex items-center gap-2 pl-2 border-l-2 border-slate-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                    <span className="text-slate-300 font-mono">{factor}</span>
                  </div>
                ))}

                {/* AI Inherent Score Node */}
                <div className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800 mt-2">
                  <div className="flex items-center gap-2 text-cyan-400">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>AI Reasoning Score:</span>
                  </div>
                  <span className="font-mono font-bold text-cyan-300">{dim.ai_score.toFixed(1)} / 10.0</span>
                </div>

                {/* Override Node if applicable */}
                {isOverridden && (
                  <div className="flex items-center justify-between p-2 rounded bg-amber-950/30 border border-amber-500/40 text-amber-300">
                    <div className="flex items-center gap-2">
                      <UserCheck className="w-3.5 h-3.5" />
                      <span>Analyst Calibrated Override:</span>
                    </div>
                    <span className="font-mono font-bold">{dim.analyst_override_score.toFixed(1)} / 10.0</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
