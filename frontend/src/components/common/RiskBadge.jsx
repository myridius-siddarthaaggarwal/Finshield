import React from 'react';

export const RiskBadge = ({ score, tier, showScore = true }) => {
  const getStyle = (t) => {
    switch (t?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
      case 'HIGH':
        return 'bg-orange-500/15 text-orange-400 border-orange-500/30';
      case 'MEDIUM':
        return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
      case 'LOW':
        return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      default:
        return 'bg-slate-700/30 text-slate-300 border-slate-600/30';
    }
  };

  const getDotColor = (t) => {
    switch (t?.toUpperCase()) {
      case 'CRITICAL': return 'bg-rose-500';
      case 'HIGH': return 'bg-orange-500';
      case 'MEDIUM': return 'bg-amber-500';
      case 'LOW': return 'bg-emerald-500';
      default: return 'bg-slate-400';
    }
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${getStyle(tier)}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${getDotColor(tier)} animate-pulse`}></span>
      <span>{tier || 'UNKNOWN'}</span>
      {showScore && score !== undefined && score !== null && (
        <span className="font-mono opacity-85 ml-0.5">({score.toFixed(1)})</span>
      )}
    </span>
  );
};

export const OutcomeBadge = ({ outcome }) => {
  if (!outcome) return null;

  switch (outcome) {
    case 'APPROVED':
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-md text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
          ✅ APPROVED (Clean)
        </span>
      );
    case 'APPROVED_WITH_CONDITIONS':
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-md text-xs font-bold bg-teal-500/20 text-teal-300 border border-teal-500/40">
          ✅ APPROVED WITH CONDITIONS
        </span>
      );
    case 'DEFERRED':
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-md text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
          ⏳ DEFERRED (Pending EDD)
        </span>
      );
    case 'REJECTED':
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-md text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
          ❌ REJECTED (Regulatory Blockers)
        </span>
      );
    case 'COMMITTEE_PENDING':
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-md text-xs font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">
          🏛️ COMMITTEE VOTING
        </span>
      );
    case 'IN_REVIEW':
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-md text-xs font-bold bg-blue-500/20 text-blue-300 border border-blue-500/40">
          🔍 ANALYST REVIEW
        </span>
      );
    case 'REQUIRES_MANUAL_REVIEW':
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-md text-xs font-bold bg-amber-600/20 text-amber-200 border border-amber-500/50 animate-pulse">
          ⚠️ CONFIDENCE GATE TRIGGERED (Manual Review)
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
          {outcome}
        </span>
      );
  }
};
