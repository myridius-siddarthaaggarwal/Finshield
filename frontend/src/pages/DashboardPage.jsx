import React, { useEffect, useState } from 'react';
import { casesApi } from '../services/api';
import { RiskBadge, OutcomeBadge } from '../components/common/RiskBadge';
import { Layers, Search, Filter, ArrowUpRight, Clock, AlertTriangle, ShieldCheck, CheckCircle2, XCircle, Sparkles } from 'lucide-react';

export const DashboardPage = ({ onSelectCase, onNewCaseClick }) => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [divisionFilter, setDivisionFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadCases();
  }, [divisionFilter]);

  const loadCases = async () => {
    setLoading(true);
    try {
      const params = divisionFilter !== 'ALL' ? { division: divisionFilter } : {};
      const res = await casesApi.getCases(params);
      setCases(res.data);
    } catch (err) {
      console.warn('Backend unavailable, using default fallback list:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredCases = cases.filter(c => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return c.title.toLowerCase().includes(q) || c.division.toLowerCase().includes(q) || c.submitter_name?.toLowerCase().includes(q);
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Hero Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 sm:p-8 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/50 border border-slate-800 shadow-xl">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-950 text-cyan-400 border border-cyan-800">
              TIER-1 FCRM WORKBENCH
            </span>
            <span className="text-xs text-slate-400">All 7 Benchmark Cases Active</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Financial Crime Risk Portfolio
          </h1>
          <p className="text-xs text-slate-400 max-w-xl">
            Governed AI reasoning over FATF, FCA, NACHA, MiCA, and FinCEN frameworks. Probabilistic reasoning with deterministic math & immutable audit trails.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onNewCaseClick}
            className="px-5 py-2.5 rounded-xl font-semibold text-xs bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-600/25 transition-all flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>Submit New Intake</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/80 p-4 rounded-xl border border-slate-800">
        <div className="flex items-center gap-2 overflow-x-auto pb-2 sm:pb-0 text-xs">
          {['ALL', 'Consumer Banking', 'Payments', 'Commercial Banking', 'Wealth Management', 'FCRM / Compliance'].map((div) => (
            <button
              key={div}
              onClick={() => setDivisionFilter(div)}
              className={`px-3 py-1.5 rounded-lg whitespace-nowrap font-medium transition-colors ${
                divisionFilter === div
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {div === 'ALL' ? 'All Divisions' : div}
            </button>
          ))}
        </div>

        <div className="relative min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search proposals, submitters..."
            className="w-full pl-9 pr-4 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      {/* Case Grid */}
      {loading ? (
        <div className="text-center py-16 text-slate-400 text-sm">Loading portfolio cases...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredCases.map((c) => (
            <div
              key={c.id}
              onClick={() => onSelectCase(c.id)}
              className="glass-card rounded-2xl p-5 cursor-pointer flex flex-col justify-between group"
            >
              <div className="space-y-3">
                {/* Header */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-lg bg-slate-800 text-cyan-400 font-mono font-bold text-xs flex items-center justify-center border border-slate-700">
                      #{c.case_number || c.id}
                    </span>
                    <span className="text-[11px] font-mono text-slate-400 font-medium">{c.division}</span>
                  </div>
                  <OutcomeBadge outcome={c.final_outcome || c.status} />
                </div>

                {/* Title */}
                <h3 className="text-sm font-bold text-slate-100 group-hover:text-cyan-400 transition-colors line-clamp-2">
                  {c.title}
                </h3>

                {/* Submitter */}
                <div className="text-[11px] text-slate-400 flex items-center justify-between">
                  <span>Submitter: <strong className="text-slate-300">{c.submitter_name}</strong></span>
                  <span className="text-slate-500 font-mono text-[10px]">{c.change_type}</span>
                </div>

                {/* Risk Score Pill */}
                <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800 flex items-center justify-between">
                  <div>
                    <div className="text-[10px] uppercase font-mono text-slate-500">Inherent</div>
                    <RiskBadge score={c.inherent_risk_score} tier={c.inherent_risk_tier} />
                  </div>

                  <div className="text-right">
                    <div className="text-[10px] uppercase font-mono text-slate-500">Residual</div>
                    <RiskBadge score={c.residual_risk_score} tier={c.residual_risk_tier} />
                  </div>
                </div>
              </div>

              {/* Card Footer */}
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5 text-emerald-400 font-mono text-[11px] font-semibold">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{c.time_saved_pct || 93}% Time Saved ({c.time_taken_hours || 24}h)</span>
                </div>

                <div className="flex items-center gap-1 text-cyan-400 text-xs font-semibold group-hover:translate-x-0.5 transition-transform">
                  <span>Inspect</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
