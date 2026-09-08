import React, { useState } from 'react';
import { casesApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { FileUp, ShieldAlert, CheckCircle2, ArrowRight, Loader2, Sparkles, Building2, Globe2, AlertCircle } from 'lucide-react';

export const IntakeForm = ({ onCaseCreated }) => {
  const { currentUser } = useAuth();
  const [formData, setFormData] = useState({
    title: '',
    division: 'Consumer Banking',
    change_type: 'New Product Launch',
    what_requester_wants: '',
    target_geographies: 'United Kingdom',
    target_customers: 'Retail consumers',
    verification_speed: 'Instant (60 seconds digital)',
    transaction_limits_desc: 'Standard limits'
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeStep, setActiveStep] = useState(0); // 0: Idle, 1: Auto-Screening, 2: AI Parsing, 3: Risk Scoring, 4: Done
  const [screeningPreview, setScreeningPreview] = useState(null);

  const handleGeoChange = (e) => {
    const val = e.target.value;
    setFormData(prev => ({ ...prev, target_geographies: val }));

    // Instant local screening preview
    const valLower = val.toLowerCase();
    if (valLower.includes('nigeria') || valLower.includes('uae') || valLower.includes('southeast asia')) {
      setScreeningPreview({
        tier: 'HIGH',
        message: 'FATF Increased Monitoring Corridor detected. Enhanced Due Diligence (EDD) will be required.',
        color: 'text-amber-400 border-amber-500/40 bg-amber-950/20'
      });
    } else if (valLower.includes('iran') || valLower.includes('korea') || valLower.includes('dprk')) {
      setScreeningPreview({
        tier: 'CRITICAL_SANCTIONED',
        message: 'Sanctioned Jurisdiction detected. Automatic block under OFAC / FATF Black List.',
        color: 'text-rose-400 border-rose-500/40 bg-rose-950/20'
      });
    } else {
      setScreeningPreview({
        tier: 'LOW',
        message: 'Standard / Domestic jurisdiction. Low geographic risk multiplier (1.0x).',
        color: 'text-emerald-400 border-emerald-500/40 bg-emerald-950/20'
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setActiveStep(1); // Auto screening

    try {
      setTimeout(() => setActiveStep(2), 500); // AI doc parsing
      setTimeout(() => setActiveStep(3), 1000); // AI risk scoring

      const geoList = formData.target_geographies.split(',').map(s => s.trim()).filter(Boolean);
      
      const payload = {
        title: formData.title,
        division: formData.division,
        change_type: formData.change_type,
        submitter_name: currentUser.full_name,
        submitter_role: currentUser.title,
        what_requester_wants: formData.what_requester_wants,
        target_geographies: geoList,
        target_customers: formData.target_customers,
        verification_speed: formData.verification_speed,
        transaction_limits_desc: formData.transaction_limits_desc
      };

      const res = await casesApi.createCase(payload);
      
      setTimeout(() => {
        setIsSubmitting(false);
        if (onCaseCreated) onCaseCreated(res.data);
      }, 1500);

    } catch (err) {
      console.error('Submission failed:', err);
      setIsSubmitting(false);
      alert('Failed to submit case. Please check that the backend is running.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl">
        <div className="border-b border-slate-800 pb-5 mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <FileUp className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight">
                Submit New Business Change / Product Intake
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Evaluates proposals against FATF, FCA, NACHA, OCC, and FinCEN compliance frameworks.
              </p>
            </div>
          </div>
        </div>

        {isSubmitting ? (
          <div className="py-12 flex flex-col items-center justify-center space-y-6 text-center">
            <div className="relative">
              <div className="w-16 h-16 rounded-full border-4 border-cyan-500/20 border-t-cyan-400 animate-spin flex items-center justify-center"></div>
              <Sparkles className="w-6 h-6 text-cyan-400 absolute inset-0 m-auto animate-pulse" />
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-bold text-white">FinShield Orchestrator Processing...</h3>
              <div className="space-y-1 text-xs font-mono text-slate-400">
                <div className={`flex items-center justify-center gap-2 ${activeStep >= 1 ? 'text-cyan-400' : 'text-slate-600'}`}>
                  <CheckCircle2 className="w-3.5 h-3.5" /> 1. Deterministic Sanctions & FATF Geography Screening
                </div>
                <div className={`flex items-center justify-center gap-2 ${activeStep >= 2 ? 'text-cyan-400' : 'text-slate-600'}`}>
                  <CheckCircle2 className="w-3.5 h-3.5" /> 2. AI Document Parsing & Extraction (Claude Sonnet v1.2.0)
                </div>
                <div className={`flex items-center justify-center gap-2 ${activeStep >= 3 ? 'text-cyan-400' : 'text-slate-600'}`}>
                  <CheckCircle2 className="w-3.5 h-3.5" /> 3. Multi-Dimension Risk Scoring & Traceability Logging
                </div>
              </div>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Title */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Proposal Title / Initiative Name *
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g., QuickAccount — Instant Digital Account Opening"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>

            {/* Division and Change Type */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Banking Division *
                </label>
                <select
                  value={formData.division}
                  onChange={(e) => setFormData({ ...formData, division: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:border-cyan-500"
                >
                  <option value="Consumer Banking">Consumer Banking</option>
                  <option value="Payments">Payments</option>
                  <option value="Commercial Banking">Commercial Banking</option>
                  <option value="Wealth Management">Wealth Management</option>
                  <option value="FCRM / Compliance">FCRM / Compliance (Internal)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Change Type *
                </label>
                <select
                  value={formData.change_type}
                  onChange={(e) => setFormData({ ...formData, change_type: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:border-cyan-500"
                >
                  <option value="New Product Launch">New Product Launch</option>
                  <option value="New Feature Launch">New Feature Launch</option>
                  <option value="New Vendor Onboarding">New Vendor Onboarding</option>
                  <option value="Process Change — INTERNAL">Process Change — INTERNAL (e.g. AI Triage)</option>
                </select>
              </div>
            </div>

            {/* What Requester Wants */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Detailed Proposal Description & Features *
              </label>
              <textarea
                rows={4}
                required
                value={formData.what_requester_wants}
                onChange={(e) => setFormData({ ...formData, what_requester_wants: e.target.value })}
                placeholder="Describe product mechanics, settlement speed, customer eligibility, limits, and operational workflow..."
                className="w-full px-4 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>

            {/* Geographies with Real-Time Screening Feedback */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Target Geographies (Comma-separated) *
                </label>
                <span className="text-[11px] text-slate-400">Validated against FATF & OFAC lists</span>
              </div>
              <input
                type="text"
                required
                value={formData.target_geographies}
                onChange={handleGeoChange}
                placeholder="e.g. United Kingdom, European Union, Nigeria, United Arab Emirates"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500"
              />
              
              {screeningPreview && (
                <div className={`mt-2 p-3 rounded-lg border text-xs flex items-start gap-2 ${screeningPreview.color}`}>
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold uppercase tracking-wider">Screening Preview: </span>
                    {screeningPreview.message}
                  </div>
                </div>
              )}
            </div>

            {/* Operational Parameters */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Verification & Onboarding Speed
                </label>
                <input
                  type="text"
                  value={formData.verification_speed}
                  onChange={(e) => setFormData({ ...formData, verification_speed: e.target.value })}
                  placeholder="e.g., 60-second digital, standard branch, EDD"
                  className="w-full px-4 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Transaction & Volume Limits
                </label>
                <input
                  type="text"
                  value={formData.transaction_limits_desc}
                  onChange={(e) => setFormData({ ...formData, transaction_limits_desc: e.target.value })}
                  placeholder="e.g., No limits at launch, £500/day limit"
                  className="w-full px-4 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="pt-4 border-t border-slate-800 flex justify-end">
              <button
                type="submit"
                className="px-6 py-3 rounded-xl font-semibold text-sm bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/25 flex items-center gap-2 transition-all hover:scale-[1.02]"
              >
                <span>Run FinShield Assessment</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
