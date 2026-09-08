import React from 'react';
import { BeforeAfterHero, BenchmarkComparison } from '../components/evaluation/BenchmarkComparison';
import { JudgementMatrixTable, TokenEfficiencyPanel } from '../components/evaluation/JudgementMatrixTable';
import { Cpu, Award, Zap, ShieldAlert, Sparkles, BookOpen } from 'lucide-react';

export const EvaluationHubPage = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Before vs After Hero */}
      <BeforeAfterHero />

      {/* Engineering Judgement Decision Matrix */}
      <JudgementMatrixTable />

      {/* Model Benchmark Accuracy Table */}
      <BenchmarkComparison />

      {/* Token Telemetry and Cost Optimization */}
      <TokenEfficiencyPanel />

      {/* Presentation Script Highlights */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center gap-2 text-cyan-400 font-bold text-sm border-b border-slate-800 pb-3">
          <BookOpen className="w-5 h-5" />
          <h3>Why FinShield Nails the Engineering Judgement Criteria</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-300 leading-relaxed">
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
            <h4 className="font-bold text-white flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              1. The Confidence Threshold Gate (&lt; 70%)
            </h4>
            <p className="text-slate-400">
              When AI confidence drops below 70%, FinShield suppresses the score to prevent human anchoring bias. The analyst performs an independent fresh evaluation without being influenced by uncertain AI output.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
            <h4 className="font-bold text-white flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              2. Case 7 — The Meta Moment
            </h4>
            <p className="text-slate-400">
              The internal FCRM team uses the Risk Workbench to assess a change to its OWN alert triage process. The system assessed itself — and chose governed automation with mandatory human sampling rather than blind auto-approval.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
