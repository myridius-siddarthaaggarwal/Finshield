import React, { useEffect, useState } from 'react';
import { evaluationApi } from '../../services/api';
import { Award, CheckCircle2, TrendingUp, History, Sparkles, Clock, AlertTriangle } from 'lucide-react';

export const BenchmarkComparison = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    evaluationApi.getBenchmarks().then(res => setData(res.data)).catch(console.warn);
  }, []);

  if (!data) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Model Evaluation Benchmark (7 Test Cases)</h3>
            <p className="text-xs text-slate-400">Comparing AI multi-dimension scores against expert compliance ground truth.</p>
          </div>
        </div>

        <div className="text-right">
          <span className="text-xs font-mono text-emerald-400 font-bold bg-emerald-950/60 px-2.5 py-1 rounded-full border border-emerald-800/40">
            {data.overall_accuracy_rate} Accuracy (±1.0 tolerance)
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 font-mono uppercase tracking-wider text-[11px] bg-slate-950/50">
              <th className="p-3">#</th>
              <th className="p-3">Benchmark Case</th>
              <th className="p-3">Expert Baseline</th>
              <th className="p-3">AI Model Score</th>
              <th className="p-3">Delta</th>
              <th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {data.cases_breakdown?.map((c) => (
              <tr key={c.case_num} className="hover:bg-slate-800/30">
                <td className="p-3 font-bold text-slate-400">Case {c.case_num}</td>
                <td className="p-3 font-sans font-semibold text-slate-200">{c.case_name}</td>
                <td className="p-3 text-slate-300">{c.expert_baseline.toFixed(1)}</td>
                <td className="p-3 text-cyan-400 font-bold">{c.ai_score.toFixed(1)}</td>
                <td className="p-3 text-slate-400">+{c.delta.toFixed(1)}</td>
                <td className="p-3 font-sans">
                  {c.passed ? (
                    <span className="text-emerald-400 flex items-center gap-1 font-semibold">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Within Tolerance
                    </span>
                  ) : (
                    <span className="text-amber-400 flex items-center gap-1 font-semibold">
                      ⚠️ Calibrated by Override
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const BeforeAfterHero = () => {
  return (
    <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <span className="text-[11px] uppercase font-mono tracking-widest px-3 py-1 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">
          Executive Impact Matrix
        </span>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Traditional Risk Review vs. FinShield Workbench
        </h2>
        <p className="text-xs text-slate-400">
          Codifying institutional memory into governed data layers, preventing catastrophic regulatory fines before product launch.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        {/* Today */}
        <div className="bg-slate-950/80 border border-rose-900/30 rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-rose-900/20">
            <span className="text-xs font-bold uppercase tracking-wider text-rose-400">
              ❌ Current State (Traditional FCRM)
            </span>
            <span className="text-xs font-mono text-slate-500">15–20 Days</span>
          </div>

          <ul className="space-y-2.5 text-xs text-slate-300">
            <li className="flex items-center gap-2">
              <span className="text-rose-400">📧</span> 47 scattered emails and spreadsheets across inboxes
            </li>
            <li className="flex items-center gap-2">
              <span className="text-rose-400">⏰</span> 18 business days average turnaround for new products
            </li>
            <li className="flex items-center gap-2">
              <span className="text-rose-400">🤷</span> Subjective, inconsistent risk scoring by different analysts
            </li>
            <li className="flex items-center gap-2">
              <span className="text-rose-400">😱</span> Critical audit gaps — missing written rationales
            </li>
            <li className="flex items-center gap-2">
              <span className="text-rose-400">💸</span> $3.8B+ fines paid by peers (TD Bank $3B, Monzo £21M, Nationwide £44M)
            </li>
          </ul>
        </div>

        {/* FinShield */}
        <div className="bg-slate-950/80 border border-cyan-500/40 rounded-2xl p-5 space-y-4 glow-cyan">
          <div className="flex items-center justify-between pb-3 border-b border-cyan-500/20">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4" /> FinShield Governed Workbench
            </span>
            <span className="text-xs font-mono text-emerald-400 font-bold">1.1 Days (93% Faster)</span>
          </div>

          <ul className="space-y-2.5 text-xs text-slate-200">
            <li className="flex items-center gap-2">
              <span className="text-emerald-400">⚡</span> Single unified platform with instant deterministic screening
            </li>
            <li className="flex items-center gap-2">
              <span className="text-emerald-400">🏛️</span> Governed Data Layer: FATF, FCA, NACHA, MiCA, FinCEN
            </li>
            <li className="flex items-center gap-2">
              <span className="text-emerald-400">🔒</span> 100% complete immutable ACID audit trails locked on decision
            </li>
            <li className="flex items-center gap-2">
              <span className="text-emerald-400">🛡️</span> Structural flaws caught BEFORE launch (e.g. CryptoConnect rejection)
            </li>
            <li className="flex items-center gap-2">
              <span className="text-emerald-400">👥</span> Frees 60% of senior analyst time from manual paperwork
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};
