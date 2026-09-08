import React, { useState } from 'react';
import { committeeApi } from '../../services/api';
import { Lock, ShieldCheck, CheckCircle2, X, AlertTriangle } from 'lucide-react';

export const DecisionLockModal = ({ isOpen, onClose, caseId, currentCase, onDecisionFinalized }) => {
  const [decision, setDecision] = useState(currentCase?.status?.includes('APPROVED') ? 'APPROVED_WITH_CONDITIONS' : 'APPROVED_WITH_CONDITIONS');
  const [noticeText, setNoticeText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const payload = {
        decision: decision,
        notice_text: noticeText || undefined
      };
      const res = await committeeApi.finalizeDecision(caseId, payload);
      if (onDecisionFinalized) onDecisionFinalized(res.data);
      onClose();
    } catch (err) {
      console.error('Finalize error:', err);
      alert('Error finalizing decision.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl animate-in fade-in zoom-in duration-150">
        <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
            <Lock className="w-5 h-5" />
            <h3>Finalize Risk Committee Decision & Seal Audit</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 text-xs space-y-1">
            <div className="text-slate-400">Target Case: <strong className="text-white">{currentCase?.title}</strong></div>
            <div className="text-slate-400">Division: <span className="font-mono text-cyan-400">{currentCase?.division}</span></div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Final Governance Decision *
            </label>
            <select
              value={decision}
              onChange={(e) => setDecision(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs font-bold text-slate-100 focus:outline-none focus:border-emerald-500"
            >
              <option value="APPROVED_WITH_CONDITIONS">✅ APPROVED WITH CONDITIONS</option>
              <option value="APPROVED">✅ APPROVED (Clean / Fast-Track)</option>
              <option value="DEFERRED">⏳ DEFERRED (Pending EDD)</option>
              <option value="REJECTED">❌ REJECTED (Regulatory Blockers)</option>
            </select>
          </div>

          {(decision === 'DEFERRED' || decision === 'REJECTED') && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Rejection / Deferral Notice & Resubmission Criteria
              </label>
              <textarea
                rows={3}
                value={noticeText}
                onChange={(e) => setNoticeText(e.target.value)}
                placeholder="Explain prerequisites required before resubmission (e.g., CASP license, Travel Rule technical plan, or EDD findings)..."
                className="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
              />
            </div>
          )}

          <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-xs text-emerald-300 flex items-start gap-2">
            <ShieldCheck className="w-4 h-4 shrink-0 mt-0.5" />
            <div>
              Finalizing will permanently lock all scores, votes, and conditions into an immutable ACID audit trail.
            </div>
          </div>

          <div className="pt-3 border-t border-slate-800 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-300 hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-1.5 shadow-lg shadow-emerald-600/30"
            >
              <Lock className="w-3.5 h-3.5" />
              <span>Seal & Lock Decision</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
