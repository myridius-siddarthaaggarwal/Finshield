import React, { useState } from 'react';
import { committeeApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { Vote, CheckCircle2, ShieldCheck, Scale, AlertOctagon, Clock, Check } from 'lucide-react';
import { OutcomeBadge } from '../common/OutcomeBadge';

const COMMITTEE_MEMBERS = [
  { name: 'Sunita Rao', role: 'Chief Risk Officer (CRO)', division: 'Executive Risk', focusLens: 'Overall Institutional Risk Exposure & Capital Impact' },
  { name: 'James Lee', role: 'Chief Compliance Officer (CCO)', division: 'Compliance', focusLens: 'Regulatory Obligations & FCRM Supervisory Letters' },
  { name: 'Anita Patel', role: 'Head of Regulatory Legal', division: 'Legal Counsel', focusLens: 'Statutory Liability, CASP/MiCA & Consumer Duty Compliance' }
];

export const VotingPanel = ({ caseId, existingVotes = [], isLocked = false, onVoteRecorded }) => {
  const { currentUser } = useAuth();
  const [selectedMember, setSelectedMember] = useState(COMMITTEE_MEMBERS[0].name);
  const [voteChoice, setVoteChoice] = useState('APPROVE_WITH_CONDITIONS');
  const [rationale, setRationale] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCastVote = async (e) => {
    e.preventDefault();
    if (!rationale.trim()) {
      alert('Committee members must document a written rationale for their vote.');
      return;
    }

    setIsSubmitting(true);
    try {
      const memberObj = COMMITTEE_MEMBERS.find(m => m.name === selectedMember);
      const payload = {
        member_name: memberObj.name,
        member_role: memberObj.role,
        vote: voteChoice,
        rationale: rationale.trim()
      };

      const res = await committeeApi.castVote(caseId, payload);
      setRationale('');
      if (onVoteRecorded) onVoteRecorded(res.data);
    } catch (err) {
      console.error('Failed to cast vote:', err);
      alert('Error recording vote.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Vote className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Risk Committee 3-Member Governance</h3>
            <p className="text-xs text-slate-400">Zero auto-approval policy. Unanimous 3-member vote required.</p>
          </div>
        </div>

        <div className="text-right">
          <span className="text-xs font-mono text-slate-400">
            Votes Logged: <strong className="text-purple-400">{existingVotes.length} / 3</strong>
          </span>
        </div>
      </div>

      {/* 3 Member Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {COMMITTEE_MEMBERS.map((member) => {
          const vote = existingVotes.find(v => v.member_name === member.name);
          return (
            <div
              key={member.name}
              className={`p-4 rounded-xl border transition-all flex flex-col justify-between ${
                vote
                  ? 'bg-slate-950/80 border-purple-500/30 shadow-sm shadow-purple-500/10'
                  : 'bg-slate-800/40 border-slate-700/60'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-100">{member.name}</span>
                  {vote ? (
                    <OutcomeBadge outcome={vote.vote} />
                  ) : (
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-700 text-slate-400 font-mono">
                      Pending Vote
                    </span>
                  )}
                </div>

                <div className="text-[11px] font-mono text-purple-400 mb-1">{member.role}</div>
                <div className="text-[11px] text-slate-400 leading-tight mb-3">
                  <strong>Lens:</strong> {member.focusLens}
                </div>

                {vote && (
                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 italic mb-2">
                    "{vote.rationale}"
                  </div>
                )}
              </div>

              {vote && (
                <div className="text-[10px] text-slate-500 font-mono flex items-center gap-1 mt-2">
                  <Check className="w-3 h-3 text-emerald-400" />
                  <span>Voted & Signed off</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Vote Casting Form for Active Persona */}
      {!isLocked && (
        <form onSubmit={handleCastVote} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-4">
          <div className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Scale className="w-4 h-4 text-cyan-400" />
            <span>Record Committee Member Vote</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                Acting Member
              </label>
              <select
                value={selectedMember}
                onChange={(e) => setSelectedMember(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-100 focus:outline-none focus:border-purple-500"
              >
                {COMMITTEE_MEMBERS.map(m => (
                  <option key={m.name} value={m.name}>{m.name} — {m.role}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                Vote Decision
              </label>
              <select
                value={voteChoice}
                onChange={(e) => setVoteChoice(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-100 focus:outline-none focus:border-purple-500 font-bold"
              >
                <option value="APPROVE_WITH_CONDITIONS">✅ APPROVE WITH CONDITIONS</option>
                <option value="APPROVE">✅ APPROVE (Clean)</option>
                <option value="DEFER">⏳ DEFER (Pending EDD / Actions)</option>
                <option value="REJECT">❌ REJECT (Regulatory Blocker)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
              Written Governance Rationale *
            </label>
            <textarea
              rows={2}
              required
              value={rationale}
              onChange={(e) => setRationale(e.target.value)}
              placeholder="e.g. Controls proposed are necessary and sufficient if implemented before launch. KYC gap is primary concern..."
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-purple-500"
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-purple-600 hover:bg-purple-500 text-white shadow-md shadow-purple-600/30 transition-all"
            >
              Record Member Vote
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export const ConditionsManager = ({ conditions = [], isLocked = false }) => {
  if (!conditions || conditions.length === 0) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-teal-400" />
          <h3 className="text-sm font-bold text-white">Mandated Approval Conditions ({conditions.length})</h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {conditions.filter(c => c.is_met).length} / {conditions.length} Verified
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {conditions.map((cond, idx) => (
          <div
            key={cond.id || idx}
            className={`p-3 rounded-xl border text-xs flex items-start gap-2.5 ${
              cond.is_met
                ? 'bg-teal-950/20 border-teal-500/30 text-slate-200'
                : 'bg-slate-800/40 border-slate-700/60 text-slate-300'
            }`}
          >
            <div className={`mt-0.5 p-0.5 rounded ${cond.is_met ? 'bg-teal-500/20 text-teal-300' : 'bg-slate-700 text-slate-400'}`}>
              <CheckCircle2 className="w-3.5 h-3.5" />
            </div>
            <div className="space-y-0.5">
              <div className="font-medium leading-tight">{cond.condition_text}</div>
              <div className="text-[10px] font-mono text-slate-500">
                {cond.is_met ? 'Confirmed pre-launch' : 'Pending operational verification'}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
