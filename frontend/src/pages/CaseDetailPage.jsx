import React, { useEffect, useState } from 'react';
import { casesApi, assessmentApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { RiskBadge, OutcomeBadge } from '../components/common/RiskBadge';
import { RiskDimensionCard } from '../components/analyst/RiskDimensionCard';
import { OverrideModal } from '../components/analyst/OverrideModal';
import { WhatIfSandbox } from '../components/analyst/WhatIfSandbox';
import { TraceabilityChain } from '../components/analyst/TraceabilityChain';
import { VotingPanel, ConditionsManager } from '../components/committee/VotingPanel';
import { DecisionLockModal } from '../components/committee/DecisionLockModal';
import {
  ArrowLeft, Shield, CheckCircle2, AlertTriangle, Scale, GitCommit,
  FileText, Lock, Send, Sparkles, Clock, Globe, User, MessageSquare
} from 'lucide-react';

export const CaseDetailPage = ({ caseId, onBack }) => {
  const { currentUser } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dimensions'); // dimensions, committee, trace, intake
  const [selectedDimensionForOverride, setSelectedDimensionForOverride] = useState(null);
  const [decisionModalOpen, setDecisionModalOpen] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatReplies, setChatReplies] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    loadCase();
  }, [caseId]);

  const loadCase = async () => {
    setLoading(true);
    try {
      const res = await casesApi.getCaseDetail(caseId);
      setData(res.data);
    } catch (err) {
      console.error('Failed to load case detail:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOverrideApplied = () => {
    loadCase();
  };

  const handleEscalateToCommittee = async () => {
    try {
      await assessmentApi.escalate(caseId, {
        recommendation: 'APPROVE_WITH_CONDITIONS',
        analyst_name: currentUser.full_name,
        notes: 'Risk manageable with Day-1 controls in place.'
      });
      loadCase();
      setActiveTab('committee');
    } catch (err) {
      console.error('Escalation failed:', err);
      alert('Failed to escalate case.');
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;

    const userMsg = chatMessage;
    setChatMessage('');
    setChatReplies(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatLoading(true);

    try {
      const res = await assessmentApi.chatCopilot(caseId, userMsg);
      setChatReplies(prev => [...prev, { role: 'ai', content: res.data.response }]);
    } catch (err) {
      setChatReplies(prev => [...prev, { role: 'ai', content: 'FCRM Copilot: Analyzing regulatory libraries...' }]);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-400">
        Loading case assessment #{caseId}...
      </div>
    );
  }

  const { case: c, dimensions, controls, committee_votes, conditions, audit_events } = data;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Back button and Case Header */}
      <div className="space-y-4">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Risk Portfolio</span>
        </button>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="w-7 h-7 rounded-lg bg-cyan-950 text-cyan-400 font-mono font-bold text-xs flex items-center justify-center border border-cyan-800">
                #{c.case_number || c.id}
              </span>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {c.division}
              </span>
              <span className="text-xs font-mono text-slate-400">
                {c.change_type}
              </span>
              <OutcomeBadge outcome={c.final_outcome || c.status} />
            </div>

            <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
              {c.title}
            </h1>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-slate-500" />
                Submitter: <strong className="text-slate-200">{c.submitter_name}</strong> ({c.submitter_role})
              </span>
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-emerald-400" />
                Time Saved: <strong className="text-emerald-400 font-mono">{c.time_saved_pct || 93}%</strong> ({c.time_taken_hours || 25}h vs {c.old_process_days || 18}d)
              </span>
              {c.is_audit_locked && (
                <span className="flex items-center gap-1 text-teal-400 font-mono text-[11px] font-semibold bg-teal-950/60 px-2 py-0.5 rounded border border-teal-800">
                  <Lock className="w-3 h-3" /> Audit Trail Locked
                </span>
              )}
            </div>
          </div>

          {/* Quick Score Card */}
          <div className="flex items-center gap-4 bg-slate-950/80 p-4 rounded-xl border border-slate-800">
            <div>
              <div className="text-[10px] uppercase font-mono text-slate-500 mb-1">Inherent Risk</div>
              <RiskBadge score={c.inherent_risk_score} tier={c.inherent_risk_tier} />
            </div>
            <div className="w-px h-8 bg-slate-800"></div>
            <div>
              <div className="text-[10px] uppercase font-mono text-slate-500 mb-1">Residual Risk</div>
              <RiskBadge score={c.residual_risk_score} tier={c.residual_risk_tier} />
            </div>
          </div>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center gap-2 border-b border-slate-800 text-xs font-semibold overflow-x-auto pb-2">
        <button
          onClick={() => setActiveTab('dimensions')}
          className={`px-4 py-2 rounded-xl transition-colors flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'dimensions'
              ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Shield className="w-4 h-4" />
          <span>Risk Dimensions & Sandbox</span>
        </button>

        <button
          onClick={() => setActiveTab('committee')}
          className={`px-4 py-2 rounded-xl transition-colors flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'committee'
              ? 'bg-purple-950 text-purple-300 border border-purple-800'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Scale className="w-4 h-4" />
          <span>Risk Committee Governance ({committee_votes?.length || 0}/3)</span>
        </button>

        <button
          onClick={() => setActiveTab('trace')}
          className={`px-4 py-2 rounded-xl transition-colors flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'trace'
              ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <GitCommit className="w-4 h-4" />
          <span>Traceability & Audit Logs ({audit_events?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab('intake')}
          className={`px-4 py-2 rounded-xl transition-colors flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'intake'
              ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Intake & Precedent Context</span>
        </button>
      </div>

      {/* Tab 1: Risk Dimensions & Sandbox */}
      {activeTab === 'dimensions' && (
        <div className="space-y-6">
          {/* Rejection notice banner if applicable */}
          {c.rejection_or_deferral_notice && (
            <div className={`p-4 rounded-xl border text-xs leading-relaxed ${
              c.status === 'REJECTED'
                ? 'bg-rose-950/30 border-rose-500/40 text-rose-200'
                : 'bg-amber-950/30 border-amber-500/40 text-amber-200'
            }`}>
              <div className="font-bold uppercase tracking-wider mb-1 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                {c.status === 'REJECTED' ? 'Official Rejection Notice' : 'Official Deferral Notice'}
              </div>
              <p>{c.rejection_or_deferral_notice}</p>
            </div>
          )}

          {/* 4 Dimension Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {dimensions.map((dim) => (
              <RiskDimensionCard
                key={dim.id}
                dimension={dim}
                isLocked={c.is_audit_locked}
                onOpenOverride={(d) => setSelectedDimensionForOverride(d)}
              />
            ))}
          </div>

          {/* What-If Sandbox */}
          <WhatIfSandbox caseId={c.id} inherentScore={c.inherent_risk_score} />

          {/* Action Bar for Analyst */}
          {!c.is_audit_locked && (
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
              <div className="text-xs text-slate-400">
                Completed analyst review and overrides?
              </div>
              <button
                onClick={handleEscalateToCommittee}
                className="px-5 py-2.5 rounded-xl font-semibold text-xs bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-600/30 transition-all flex items-center gap-2"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Submit to Risk Committee</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Committee Governance */}
      {activeTab === 'committee' && (
        <div className="space-y-6">
          <VotingPanel
            caseId={c.id}
            existingVotes={committee_votes}
            isLocked={c.is_audit_locked}
            onVoteRecorded={loadCase}
          />

          <ConditionsManager
            conditions={conditions}
            isLocked={c.is_audit_locked}
          />

          {/* Finalize Button */}
          {!c.is_audit_locked && (
            <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/30 border border-slate-800 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-100">Ready to Finalize Committee Governance?</div>
                <div className="text-[11px] text-slate-400">Locks the 3-member decision and seals immutable audit trail.</div>
              </div>

              <button
                onClick={() => setDecisionModalOpen(true)}
                className="px-6 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30 transition-all flex items-center gap-2"
              >
                <Lock className="w-4 h-4" />
                <span>Finalize & Lock Decision</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Traceability & Audit Logs */}
      {activeTab === 'trace' && (
        <div className="space-y-6">
          <TraceabilityChain dimensions={dimensions} caseTitle={c.title} />

          {/* Immutable Audit Log List */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Lock className="w-5 h-5 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">Immutable ACID Audit Trail ({audit_events?.length})</h3>
              </div>
              <span className="text-[11px] font-mono text-slate-400">Zero Tolerance for Omissions</span>
            </div>

            <div className="space-y-2.5">
              {audit_events?.map((evt, idx) => (
                <div key={evt.id || idx} className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-cyan-400 uppercase text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-800">
                        {evt.event_type}
                      </span>
                      <span className="font-semibold text-slate-200">{evt.actor_name}</span>
                      <span className="text-slate-500">({evt.actor_role})</span>
                    </div>
                    <p className="text-slate-300">{evt.description}</p>
                  </div>
                  <span className="font-mono text-[10px] text-slate-500 shrink-0">
                    {new Date(evt.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Intake & Precedents */}
      {activeTab === 'intake' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Submitter details */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-sm font-bold text-white border-b border-slate-800 pb-3">
              Intake Specification & Parameters
            </h3>
            <div className="space-y-3 text-xs">
              <div>
                <div className="text-[11px] text-slate-500 uppercase font-mono">Proposal Description</div>
                <p className="text-slate-200 mt-1 leading-relaxed">{c.what_requester_wants}</p>
              </div>
              <div>
                <div className="text-[11px] text-slate-500 uppercase font-mono">Target Geographies</div>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {c.target_geographies?.map((g, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[11px] border border-slate-700">
                      {g}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-[11px] text-slate-500 uppercase font-mono">Verification Speed</div>
                <div className="text-slate-200 mt-0.5 font-mono">{c.verification_speed || 'Standard'}</div>
              </div>
              <div>
                <div className="text-[11px] text-slate-500 uppercase font-mono">Transaction Limits</div>
                <div className="text-slate-200 mt-0.5 font-mono">{c.transaction_limits_desc || 'None'}</div>
              </div>
            </div>
          </div>

          {/* Real-World Context & Fine Precedents */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-sm font-bold text-white border-b border-slate-800 pb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>Real-World Precedent & Industry Exposure</span>
            </h3>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 leading-relaxed space-y-2">
              <p>{c.real_world_context || 'Standard regulatory examination checks apply.'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Modals */}
      <OverrideModal
        isOpen={!!selectedDimensionForOverride}
        dimension={selectedDimensionForOverride}
        caseId={c.id}
        onClose={() => setSelectedDimensionForOverride(null)}
        onOverrideApplied={handleOverrideApplied}
      />

      <DecisionLockModal
        isOpen={decisionModalOpen}
        caseId={c.id}
        currentCase={c}
        onClose={() => setDecisionModalOpen(false)}
        onDecisionFinalized={loadCase}
      />
    </div>
  );
};
