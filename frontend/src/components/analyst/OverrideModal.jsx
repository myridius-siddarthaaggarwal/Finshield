import React, { useState } from 'react';
import { assessmentApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { X, ShieldAlert, CheckCircle2, ArrowRight } from 'lucide-react';

export const OverrideModal = ({ isOpen, onClose, dimension, caseId, onOverrideApplied }) => {
  const { currentUser } = useAuth();
  const [newScore, setNewScore] = useState(dimension?.final_score || 7.0);
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen || !dimension) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reason.trim()) {
      alert('A written regulatory reason is mandatory for compliance audit trails.');
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        dimension_key: dimension.dimension_key,
        new_score: parseFloat(newScore),
        reason: reason.trim(),
        analyst_name: currentUser.full_name
      };

      const res = await assessmentApi.overrideDimension(caseId, payload);
      if (onOverrideApplied) onOverrideApplied(res.data);
      onClose();
    } catch (err) {
      console.error('Failed to apply override:', err);
      alert('Error applying override.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-lg overflow-hidden shadow-2xl animate-in fade-in zoom-in duration-150">
        <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
            <ShieldAlert className="w-5 h-5" />
            <h3>Analyst Judgement Override</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div className="bg-slate-800/60 border border-slate-700 p-3 rounded-lg text-xs space-y-1">
            <div className="text-slate-400">Target Dimension: <strong className="text-white">{dimension.dimension_name}</strong></div>
            <div className="text-slate-400">Current AI Score: <span className="font-mono text-cyan-400">{dimension.ai_score.toFixed(1)} / 10.0</span></div>
            <div className="text-slate-400">Regulatory Framework: <span className="font-mono text-slate-300">{dimension.framework_citation}</span></div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                New Calibrated Score (1.0 — 10.0)
              </label>
              <span className="font-mono font-bold text-cyan-400 text-sm">{parseFloat(newScore).toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="1.0"
              max="10.0"
              step="0.1"
              value={newScore}
              onChange={(e) => setNewScore(e.target.value)}
              className="w-full accent-cyan-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
              <span>1.0 (Low Risk)</span>
              <span>5.0 (Medium)</span>
              <span>8.0 (High)</span>
              <span>10.0 (Critical)</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Mandatory Regulatory Rationale / Business Context *
            </label>
            <textarea
              rows={3}
              required
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g., Confirmed product team will deploy device fingerprinting from Day 1 to suppress synthetic identity fraud..."
              className="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:border-cyan-500"
            />
            <p className="text-[11px] text-slate-400 mt-1">
              This reason is permanently committed into the immutable audit trail for regulatory examination.
            </p>
          </div>

          <div className="pt-3 border-t border-slate-800 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-2 rounded-lg text-xs font-medium text-slate-300 hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white flex items-center gap-1.5 shadow-md shadow-cyan-600/30"
            >
              <span>Commit Override</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
