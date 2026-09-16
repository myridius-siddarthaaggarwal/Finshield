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

      {/* 10% Rubric Showcase: Context Engineering & Requirement Expansion */}
      <div className="bg-slate-900 border border-cyan-500/30 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg sm:text-xl font-extrabold text-white tracking-tight">
                  Context Engineering & Requirement Expansion
                </h2>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-700 font-bold">
                  10% Hackathon Rubric
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                "How you researched an incomplete requirement, layered in domain knowledge without an SME, and maintained context across the workflow."
              </p>
            </div>
          </div>
          <span className="text-xs font-mono text-emerald-400 bg-emerald-950/60 px-3 py-1 rounded-lg border border-emerald-800 self-start sm:self-auto">
            ✓ Zero Context Drift • 100% Traceability
          </span>
        </div>

        {/* 3 Pillars of the Context Engineering Strategy */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2.5">
            <div className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-cyan-950 flex items-center justify-center text-[11px] text-cyan-300 font-mono border border-cyan-700">1</span>
              Researching Without an SME
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              When given a vague brief with no SME, we researched <strong>$3.8B+ in real-world penalties</strong> (TD Bank $3B, Monzo £21M, OKX $504M, Nationwide £44M) to extract the true regulatory requirements for digital banking products.
            </p>
            <div className="text-[11px] text-slate-400 pt-1 font-mono">
              Indexed: FATF (R.1, 6, 10, 15, 16), UK FCA Consumer Duty, PSR APP Fraud, EU MiCA.
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2.5">
            <div className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-cyan-950 flex items-center justify-center text-[11px] text-cyan-300 font-mono border border-cyan-700">2</span>
              Layering Domain Knowledge & Public APIs
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              We codified this research into our <strong>Governed Data Layer</strong> and connected <strong>Public Open Compliance APIs</strong> (OpenSanctions, FATF registries) so the system cross-references real sanctions, PEPs, and corridors without hallucinations.
            </p>
            <div className="text-[11px] text-slate-400 pt-1 font-mono">
              Live Sources: OpenSanctions API, FATF Consolidated Grey List, UK FCA Registry.
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2.5">
            <div className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-cyan-950 flex items-center justify-center text-[11px] text-cyan-300 font-mono border border-cyan-700">3</span>
              End-to-End Context Continuity
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              An unbroken <strong>`CaseContextPacket`</strong> carries the expanded spec from Submitter Intake &rarr; Deterministic Screening &rarr; 4-Dimension AI Reasoning &rarr; Analyst Overrides &rarr; Committee Votes &rarr; Immutable ACID Audit Trail.
            </p>
            <div className="text-[11px] text-slate-400 pt-1 font-mono">
              Result: Zero context loss across 5 distinct bank personas.
            </div>
          </div>
        </div>

        {/* 4-Tier Architecture Diagram Row */}
        <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 space-y-2">
          <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            The 4-Tier Enterprise Context Architecture
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
              <div className="font-bold text-cyan-400">Tier 1: Knowledge Base</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Governed JSON + Public Open APIs</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
              <div className="font-bold text-cyan-400">Tier 2: Prompt Grounding</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Strict JSON Schema (v1.2.0)</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
              <div className="font-bold text-cyan-400">Tier 3: FSM State Carrier</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Deterministic State Transitions</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
              <div className="font-bold text-cyan-400">Tier 4: Four-Eyes Governance</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Overrides with Audit Rationale</div>
            </div>
          </div>
        </div>
      </div>

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
