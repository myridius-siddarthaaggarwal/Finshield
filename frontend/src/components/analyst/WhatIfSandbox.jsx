import React, { useState } from 'react';
import { assessmentApi } from '../../services/api';
import { Sliders, Sparkles, TrendingDown, CheckCircle2, Plus, RefreshCw } from 'lucide-react';
import { RiskBadge } from '../common/RiskBadge';

const PRESET_CONTROLS = [
  { id: 'CTRL-KYC-RISK', name: 'Risk-Based Enhanced KYC for Flagged Profiles', effectiveness: 0.65, category: 'CDD' },
  { id: 'CTRL-TXN-LIMITS', name: '£500/day Transaction Limit for 90 Days', effectiveness: 0.55, category: 'Preventative' },
  { id: 'CTRL-TXN-MONITORING', name: 'Real-Time Transaction Monitoring Rules', effectiveness: 0.60, category: 'Detective' },
  { id: 'CTRL-DEV-FINGERPRINT', name: 'Device & Network Fingerprinting', effectiveness: 0.50, category: 'Fraud' },
  { id: 'CTRL-COP', name: 'Confirmation of Payee (CoP) Service', effectiveness: 0.45, category: 'Payments' },
  { id: 'CTRL-AI-SAMPLING', name: '10% Human Sampling for AI Decisions', effectiveness: 0.70, category: 'AI Governance' }
];

export const WhatIfSandbox = ({ caseId, inherentScore = 8.4 }) => {
  const [selectedControls, setSelectedControls] = useState([]);
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const toggleControl = (ctrl) => {
    let next;
    if (selectedControls.some(c => c.id === ctrl.id)) {
      next = selectedControls.filter(c => c.id !== ctrl.id);
    } else {
      next = [...selectedControls, ctrl];
    }
    setSelectedControls(next);
    runSimulation(next);
  };

  const runSimulation = async (controls) => {
    setLoading(true);
    try {
      const res = await assessmentApi.simulateWhatIf(caseId, {
        additional_controls: controls.map(c => ({ name: c.name, effectiveness: c.effectiveness }))
      });
      setSimulationResult(res.data);
    } catch (err) {
      console.warn('Simulating locally:', err);
      // Local math calculation fallback
      let mult = 1.0;
      controls.forEach(c => { mult *= (1.0 - c.effectiveness); });
      const reduction = 1.0 - mult;
      const simRes = Math.max(Number((inherentScore * (1.0 - (reduction * 0.75))).toFixed(2)), 1.0);
      const tier = simRes <= 3.0 ? 'LOW' : simRes <= 6.0 ? 'MEDIUM' : simRes <= 8.0 ? 'HIGH' : 'CRITICAL';
      const delta = Number((inherentScore - simRes).toFixed(2));
      const pct = Number(((delta / inherentScore) * 100).toFixed(1));

      setSimulationResult({
        baseline_residual: inherentScore,
        baseline_tier: inherentScore <= 8.0 ? 'HIGH' : 'CRITICAL',
        simulated_residual: simRes,
        simulated_tier: tier,
        risk_delta: delta,
        percentage_reduction: pct,
        is_approvable_tier: tier === 'LOW' || tier === 'MEDIUM',
        summary: `Adding ${controls.length} controls reduces residual risk to ${simRes} (${tier}), a ${pct}% reduction.`
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">What-If Control Simulation Sandbox</h3>
            <p className="text-xs text-slate-400">Test how candidate controls reduce residual risk before committee review.</p>
          </div>
        </div>

        {simulationResult && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Simulated Outcome:</span>
            <RiskBadge score={simulationResult.simulated_residual} tier={simulationResult.simulated_tier} />
          </div>
        )}
      </div>

      {/* Control Checkboxes */}
      <div className="space-y-2">
        <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
          Select Candidate Controls from Library ({selectedControls.length} active)
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {PRESET_CONTROLS.map((ctrl) => {
            const isSelected = selectedControls.some(c => c.id === ctrl.id);
            return (
              <button
                key={ctrl.id}
                type="button"
                onClick={() => toggleControl(ctrl)}
                className={`p-3 rounded-xl text-left border transition-all flex items-start justify-between gap-2 ${
                  isSelected
                    ? 'bg-cyan-950/40 border-cyan-500/60 shadow-sm shadow-cyan-500/20'
                    : 'bg-slate-800/50 border-slate-700/60 hover:border-slate-600'
                }`}
              >
                <div>
                  <div className="text-xs font-semibold text-slate-200">{ctrl.name}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">Category: {ctrl.category}</div>
                </div>
                <span className={`text-[11px] font-mono px-1.5 py-0.5 rounded font-bold ${
                  isSelected ? 'bg-cyan-500/20 text-cyan-300' : 'bg-slate-700 text-slate-300'
                }`}>
                  +{Math.round(ctrl.effectiveness * 100)}%
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Simulation Result Box */}
      {simulationResult && (
        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-300">
              <TrendingDown className="w-4 h-4 text-emerald-400" />
              <span>Residual Risk Reduction:</span>
            </div>
            <div className="font-mono text-emerald-400 font-bold">
              −{simulationResult.risk_delta} pts ({simulationResult.percentage_reduction}% drop)
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800/80">
            <div>
              <div className="text-[11px] text-slate-400">Baseline Inherent</div>
              <div className="text-sm font-mono font-bold text-slate-300">{simulationResult.baseline_residual} ({simulationResult.baseline_tier})</div>
            </div>
            <div>
              <div className="text-[11px] text-slate-400">Simulated Residual</div>
              <div className="text-sm font-mono font-bold text-cyan-400">{simulationResult.simulated_residual} ({simulationResult.simulated_tier})</div>
            </div>
          </div>

          <p className="text-xs text-slate-400 italic pt-1 border-t border-slate-800/80">
            💡 {simulationResult.summary}
          </p>
        </div>
      )}
    </div>
  );
};
