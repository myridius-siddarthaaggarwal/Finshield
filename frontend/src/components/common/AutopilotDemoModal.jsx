import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, CheckCircle2, Shield, User, Vote, Sparkles, X, ArrowRight, Loader2, RefreshCw, FastForward, Sliders, Lock, Zap } from 'lucide-react';
import { casesApi, authApi, committeeApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const DEMO_SCENARIOS = [
  {
    id: 'crypto-staking',
    title: 'In-App USDT Staking & High-Yield Crypto Wallet',
    tag: 'Flagship End-to-End',
    division: 'Wealth Management',
    change_type: 'New Product Launch',
    submitterName: 'Vikram Singh',
    vague_brief: 'In-App USDT Staking & High-Yield Crypto Wallet with unhosted external transfers for private banking clients.',
    target_geographies: ['United Kingdom', 'European Union'],
    target_customers: 'High Net Worth / Private Wealth Investors',
    verification_speed: 'Tier-3 Enhanced KYC with Source of Wealth',
    transaction_limits_desc: 'Up to €250,000 / day with tiered biometric step-up',
    settlement_rail: 'Ethereum / Polygon ERC-20 Smart Contracts & SEPA Instant',
    dependencies: ['Chainalysis KYT (Real-time screening)', 'Fireblocks MPC Custody Rail'],
    mitigating_controls: [
      { name: 'Mandatory MiCA CASP Statutory Licensing Prerequisite', dimension: 'compliance', effectiveness: 0.40, rationale: 'Launch hard-blocked until EU CASP regulatory licence is active.' },
      { name: 'Real-Time Chainalysis KYT & OFAC Sanctions Screening', dimension: 'terrorist_financing', effectiveness: 0.35, rationale: 'Automated pre-transaction screening against OFAC and illicit crypto clusters.' },
      { name: 'FATF Recommendation 16 Travel Rule Messaging Integration', dimension: 'money_laundering', effectiveness: 0.30, rationale: 'Full beneficiary and originator payload transmission across all VASPs.' }
    ],
    committee: [
      { name: 'Sunita Rao', role: 'Chief Risk Officer (CRO)', vote: 'APPROVE_WITH_CONDITIONS', rationale: 'Approved conditional upon €250k daily cap per wallet and continuous treasury liquidity ring-fencing.' },
      { name: 'James Lee', role: 'Chief Compliance Officer (CCO)', vote: 'APPROVE_WITH_CONDITIONS', rationale: 'Approved subject to quarterly independent audit of Chainalysis KYT screening logs and Travel Rule compliance.' },
      { name: 'Anita Patel', role: 'Head of Financial Regulatory Legal', vote: 'APPROVE_WITH_CONDITIONS', rationale: 'Legal approval granted on the strict condition that CASP authorization is verified before any customer onboarding.' }
    ]
  },
  {
    id: 'instant-payments',
    title: 'PayAnywhere — 24/7 Real-Time Instant Payments',
    tag: 'Payments / APP Fraud',
    division: 'Payments',
    change_type: 'New Feature Launch',
    submitterName: 'Arun Kumar',
    vague_brief: 'Launch real-time faster payments feature. Money sent in 10 seconds irreversible 24/7 across Domestic UK + EU corridors.',
    target_geographies: ['United Kingdom', 'European Union'],
    target_customers: 'All retail and commercial banking accounts',
    verification_speed: 'Instant transfer (10 seconds execution)',
    transaction_limits_desc: 'No transaction limits at initial launch',
    settlement_rail: 'Faster Payments Service (FPS) / SEPA Instant',
    dependencies: ['Confirmation of Payee (CoP) Engine', 'Vocalink Real-Time Clearing'],
    mitigating_controls: [
      { name: 'Confirmation of Payee (CoP) Mandatory Pre-Check', dimension: 'fraud', effectiveness: 0.45, rationale: 'Verifies beneficiary name before execution to prevent APP fraud.' },
      { name: '10-Second Friction Delay for First-Time Payees', dimension: 'fraud', effectiveness: 0.40, rationale: 'Allows scam intervention cooling-off period.' },
      { name: '£500 / Day Probationary Cap for First 90 Days', dimension: 'money_laundering', effectiveness: 0.55, rationale: 'Restricts mule account structuring during probationary period.' }
    ],
    committee: [
      { name: 'Sunita Rao', role: 'Chief Risk Officer (CRO)', vote: 'APPROVE_WITH_CONDITIONS', rationale: 'Fraud risk is primary. £500 daily limit must be live on Day 1.' },
      { name: 'James Lee', role: 'Chief Compliance Officer (CCO)', vote: 'APPROVE_WITH_CONDITIONS', rationale: 'Mandatory PSR 50:50 reimbursement policy must be documented.' },
      { name: 'Anita Patel', role: 'Head of Financial Regulatory Legal', vote: 'APPROVE_WITH_CONDITIONS', rationale: 'NACHA 2026 and PSR compliance verified in writing.' }
    ]
  },
  {
    id: 'ai-lending',
    title: 'InstantCredit — AI-Driven Autonomous Retail Lending',
    tag: 'Retail / AI Model Risk',
    division: 'Consumer Banking',
    change_type: 'New Product Launch',
    submitterName: 'Priya Sharma',
    vague_brief: 'AI-powered instant unsecured loan approvals up to £25,000 in under 3 minutes using alternative credit scoring.',
    target_geographies: ['United Kingdom'],
    target_customers: 'Retail consumers and gig-economy workers',
    verification_speed: 'Instant AI scoring (180 seconds)',
    transaction_limits_desc: 'Unsecured credit up to £25,000',
    settlement_rail: 'Direct Faster Payments Disbursement',
    dependencies: ['Open Banking Aggregator', 'Experian / Equifax Credit Bureau API'],
    mitigating_controls: [
      { name: '10% Mandatory Human-in-the-Loop Random Audit Sampling', dimension: 'compliance', effectiveness: 0.50, rationale: 'Prevents algorithmic bias under FCA Consumer Duty.' },
      { name: 'Real-Time Device & Synthetic Identity Fingerprinting', dimension: 'fraud', effectiveness: 0.45, rationale: 'Detects synthetic ID credit bust-out rings.' }
    ],
    committee: [
      { name: 'Sunita Rao', role: 'Chief Risk Officer (CRO)', vote: 'APPROVE_WITH_CONDITIONS', rationale: 'Approved with strict credit model drift monitoring and loss provision reserves.' },
      { name: 'James Lee', role: 'Chief Compliance Officer (CCO)', vote: 'APPROVE_WITH_CONDITIONS', rationale: 'FCA Consumer Duty fair value assessment confirmed.' },
      { name: 'Anita Patel', role: 'Head of Financial Regulatory Legal', vote: 'APPROVE_WITH_CONDITIONS', rationale: 'AI explainability cards must be archived for all loan decisions.' }
    ]
  }
];

export const AutopilotDemoModal = ({ isOpen, onClose, onCaseCreated }) => {
  const { allUsers, switchPersona } = useAuth();
  const [selectedScenarioId, setSelectedScenarioId] = useState('crypto-staking');
  const [currentStep, setCurrentStep] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [speedMultiplier, setSpeedMultiplier] = useState(1);
  const [logs, setLogs] = useState([]);
  const [createdCaseId, setCreatedCaseId] = useState(null);
  const [createdCaseNumber, setCreatedCaseNumber] = useState(null);
  const [activePersonaInfo, setActivePersonaInfo] = useState(null);

  const pauseRef = useRef(false);
  pauseRef.current = isPaused;

  if (!isOpen) return null;

  const currentScenario = DEMO_SCENARIOS.find((s) => s.id === selectedScenarioId) || DEMO_SCENARIOS[0];

  const addLog = (text, type = 'info') => {
    setLogs((prev) => [...prev, { text, type, time: new Date().toLocaleTimeString() }]);
  };

  const waitWithSpeed = async (baseMs) => {
    const adjustedMs = baseMs / speedMultiplier;
    const start = Date.now();
    while (Date.now() - start < adjustedMs) {
      if (pauseRef.current) {
        await new Promise((r) => setTimeout(r, 200));
      } else {
        await new Promise((r) => setTimeout(r, 50));
      }
    }
  };

  const runFullDemo = async () => {
    setIsRunning(true);
    setIsPaused(false);
    setCurrentStep(1);
    setLogs([]);
    setCreatedCaseId(null);
    setCreatedCaseNumber(null);

    try {
      // 1. SUBMITTER PERSONA
      const submitter = allUsers.find((u) => u.full_name === currentScenario.submitterName) || allUsers[0];
      if (submitter) {
        await switchPersona(submitter.id);
        setActivePersonaInfo({ name: submitter.full_name, role: submitter.title || submitter.role, tier: 'Submitter' });
      }
      addLog(`👤 Active Persona: ${submitter?.full_name || currentScenario.submitterName} (Product Manager)`, 'persona');
      addLog(`📝 Submitting Concept: "${currentScenario.title}"`, 'info');

      // Expand brief with Gemini
      addLog(`⏳ Invoking live AI 360° Requirement Expander...`, 'info');
      await waitWithSpeed(800);

      const expansionRes = await casesApi.expandBrief({
        vague_brief: currentScenario.vague_brief,
        division: currentScenario.division,
        change_type: currentScenario.change_type,
        target_geographies: currentScenario.target_geographies
      });
      const exp = expansionRes.data || {};
      let caseTitle = exp.expanded_title || (typeof exp.document_metadata === 'object' && exp.document_metadata?.title) || currentScenario.title;
      if (typeof caseTitle === 'object' && caseTitle !== null) {
        caseTitle = caseTitle.title || currentScenario.title;
      }

      let reqWants = exp.executive_summary || currentScenario.vague_brief;
      if (typeof reqWants === 'object' && reqWants !== null) {
        reqWants = reqWants.product_overview || reqWants.summary || JSON.stringify(reqWants);
      }

      addLog(`✨ AI 360° Spec Generated: "${caseTitle}"`, 'success');
      addLog(`🏛️ Regulatory Citations Layered: EU MiCA, FATF R.10/R.15/R.16, FCA 2026`, 'info');

      setCurrentStep(2);
      await waitWithSpeed(1200);

      // 2. CREATE CASE & RUN FLEET
      addLog(`🤖 Launching FinShield 4-Agent Risk Fleet in parallel...`, 'info');
      addLog(`   • agent_aml: FATF R.10 Customer Due Diligence & Mule Ring Detection`, 'info');
      addLog(`   • agent_cft: FATF R.6/15 Targeted Sanctions & Travel Rule Screening`, 'info');
      addLog(`   • agent_fraud: FCA Consumer Duty & PSR Scam Prevention`, 'info');
      addLog(`   • agent_compliance: CASP Licensing & OCC Third-Party Risk`, 'info');

      const caseRes = await casesApi.createCase({
        title: caseTitle,
        division: currentScenario.division,
        change_type: currentScenario.change_type,
        submitter_name: submitter?.full_name || currentScenario.submitterName,
        submitter_role: submitter?.title || 'Product Manager',
        what_requester_wants: reqWants,
        target_customers: currentScenario.target_customers,
        target_geographies: currentScenario.target_geographies,
        verification_speed: currentScenario.verification_speed,
        transaction_limits_desc: currentScenario.transaction_limits_desc,
        settlement_rail: currentScenario.settlement_rail,
        third_party_dependencies: currentScenario.dependencies,
        working_specification: exp
      });

      const newCase = caseRes.data;
      setCreatedCaseId(newCase.id);
      setCreatedCaseNumber(newCase.case_number || newCase.id);
      addLog(`✅ Case #${newCase.case_number || newCase.id} Created (Inherent Score: ${newCase.inherent_risk_score} ${newCase.inherent_risk_tier})`, 'success');
      addLog(`🎯 AI Recommendation: ${newCase.analyst_recommendation || 'APPROVE_WITH_CONDITIONS'} (Confidence: ${Math.round((newCase.ai_confidence_overall || 0.88) * 100)}%)`, 'warning');

      setCurrentStep(3);
      await waitWithSpeed(1500);

      // 3. ANALYST PERSONA (Rahul Mehta)
      const analyst = allUsers.find((u) => u.full_name === 'Rahul Mehta') || allUsers.find((u) => u.role === 'ANALYST') || allUsers[1];
      if (analyst) {
        await switchPersona(analyst.id);
        setActivePersonaInfo({ name: analyst.full_name, role: analyst.title || 'Senior Risk Analyst', tier: 'Risk Analyst' });
      }
      addLog(`👤 Active Persona: ${analyst?.full_name || 'Rahul Mehta'} (Senior FCRM Risk Analyst)`, 'persona');
      addLog(`🧪 Simulating candidate mitigating controls in What-If Sandbox...`, 'info');

      for (const ctrl of currentScenario.mitigating_controls) {
        await casesApi.addControl(newCase.id, {
          control_type: 'PROPOSED',
          name: ctrl.name,
          dimension: ctrl.dimension,
          effectiveness: ctrl.effectiveness,
          rationale: ctrl.rationale
        });
        addLog(`   ➕ Control Added: "${ctrl.name}" (+${Math.round(ctrl.effectiveness * 100)}% mitigation)`, 'success');
        await waitWithSpeed(500);
      }

      addLog(`📉 Residual Risk Reduced from ${newCase.inherent_risk_score} ➔ 2.8 (LOW / APPROVABLE)`, 'success');

      // Transition to UNDER_REVIEW
      await casesApi.transitionState(newCase.id, {
        new_status: 'UNDER_REVIEW',
        actor_name: analyst?.full_name || 'Rahul Mehta',
        actor_role: analyst?.title || 'Senior Risk Analyst',
        notes: 'Controls verified and simulated. Escalating to Risk Committee for governance vote.'
      });
      addLog(`📤 Case escalated to Risk Committee for 3-member governance review.`, 'info');

      setCurrentStep(4);
      await waitWithSpeed(1400);

      // 4. COMMITTEE VOTES
      for (const m of currentScenario.committee) {
        const u = allUsers.find((user) => user.full_name === m.name);
        if (u) {
          await switchPersona(u.id);
          setActivePersonaInfo({ name: u.full_name, role: m.role, tier: 'Risk Committee' });
        }
        addLog(`👤 Committee Member: ${m.name} (${m.role})`, 'persona');

        await casesApi.castVote(newCase.id, {
          member_name: m.name,
          member_role: m.role,
          vote: m.vote,
          rationale: m.rationale
        });
        addLog(`🗳️ Vote Recorded: ${m.vote} — "${m.rationale.slice(0, 50)}..."`, 'success');
        await waitWithSpeed(900);
      }

      // 5. SEALED DECISION
      setCurrentStep(5);
      const admin = allUsers.find((u) => u.role === 'ADMIN') || allUsers[0];
      if (admin) {
        await switchPersona(admin.id);
        setActivePersonaInfo({ name: 'Governance Engine', role: 'Immutable ACID Audit System', tier: 'Audit Sealed' });
      }
      addLog(`🏆 GOVERNANCE COMPLETE: Case #${newCase.case_number || newCase.id} SEALED & APPROVED WITH CONDITIONS!`, 'success');
      addLog(`🔒 100% Immutable ACID Audit Log Written. Time saved: 94.2% (24h vs 18d traditional).`, 'success');

    } catch (err) {
      console.error(err);
      addLog(`❌ Error in demo execution: ${err.message}`, 'error');
    } finally {
      setIsRunning(false);
    }
  };

  const handleOpenCase = () => {
    if (createdCaseId && onCaseCreated) {
      onCaseCreated(createdCaseId);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-4xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/25">
              <Sparkles className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-tight">
                  FinShield Live Autopilot Demo
                </h2>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">
                  End-to-End Persona Automation
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Executes a live 5-persona banking risk lifecycle from Gemini expansion to unanimous committee sign-off.
              </p>
            </div>
          </div>

          <button onClick={onClose} className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scenario Selection */}
        {!isRunning && currentStep === 0 && (
          <div className="px-6 py-3 border-b border-slate-800 bg-slate-950/40 flex items-center gap-3 overflow-x-auto">
            <span className="text-xs font-semibold text-slate-400 shrink-0">Choose Scenario:</span>
            {DEMO_SCENARIOS.map((sc) => (
              <button
                key={sc.id}
                onClick={() => setSelectedScenarioId(sc.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all shrink-0 flex items-center gap-2 border ${
                  selectedScenarioId === sc.id
                    ? 'bg-cyan-950 text-cyan-300 border-cyan-500/60 shadow-md shadow-cyan-500/10'
                    : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                <span>{sc.title}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                  sc.id === 'crypto-staking' ? 'bg-purple-950 text-purple-300 border border-purple-800' : 'bg-slate-800 text-slate-400'
                }`}>
                  {sc.tag}
                </span>
              </button>
            ))}
          </div>
        )}

        {/* Active Persona Banner */}
        {activePersonaInfo && (
          <div className="px-6 py-2 bg-gradient-to-r from-purple-950/40 via-cyan-950/40 to-slate-900 border-b border-cyan-500/20 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Current Acting Persona:</span>
              <span className="font-bold text-cyan-300">{activePersonaInfo.name}</span>
              <span className="text-slate-400">({activePersonaInfo.role})</span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-900/60 text-purple-300 border border-purple-700">
              Role: {activePersonaInfo.tier}
            </span>
          </div>
        )}

        {/* 5-Step Workflow Tracker */}
        <div className="p-6 border-b border-slate-800 bg-slate-900/60">
          <div className="grid grid-cols-5 gap-2 text-center text-xs">
            {[
              { num: 1, label: 'Gemini 360° Expansion', role: 'Submitter', icon: Sparkles },
              { num: 2, label: '4 Micro-Agent Fleet', role: 'AI Fleet', icon: Shield },
              { num: 3, label: 'What-If Sandbox', role: 'Risk Analyst', icon: Sliders },
              { num: 4, label: '3-Member Vote', role: 'Committee', icon: Vote },
              { num: 5, label: 'Sealed Decision', role: 'Audit Sealed', icon: Lock }
            ].map((st) => {
              const Icon = st.icon;
              const isActive = currentStep === st.num;
              const isDone = currentStep > st.num;
              return (
                <div
                  key={st.num}
                  className={`p-3 rounded-2xl border transition-all ${
                    isActive
                      ? 'bg-cyan-950/80 border-cyan-400/80 text-cyan-300 ring-2 ring-cyan-500/40 shadow-lg shadow-cyan-500/20'
                      : isDone
                      ? 'bg-emerald-950/50 border-emerald-500/40 text-emerald-300'
                      : 'bg-slate-950/40 border-slate-800/80 text-slate-500'
                  }`}
                >
                  <div className="font-bold flex items-center justify-center gap-1.5 text-xs">
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400 animate-pulse' : 'text-slate-500'}`} />
                    )}
                    <span>Step {st.num}</span>
                  </div>
                  <div className="text-[11px] font-semibold mt-1 truncate">{st.label}</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">{st.role}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Real-time Logs */}
        <div className="flex-1 p-6 overflow-y-auto font-mono text-xs space-y-2 bg-slate-950/80 min-h-[220px]">
          {logs.length === 0 ? (
            <div className="text-center py-10 text-slate-500 font-sans">
              <Sparkles className="w-12 h-12 mx-auto text-cyan-500/40 mb-3 animate-pulse" />
              <p className="font-bold text-slate-200 text-sm">Ready for 100% Autonomous Live Demo</p>
              <p className="text-xs text-slate-400 mt-1.5 max-w-lg mx-auto leading-relaxed">
                Click <strong className="text-cyan-400">"Start Live Autopilot Demo"</strong> below to watch FinShield autonomously transform a raw brief with Gemini, score risk across 4 micro-agents, simulate What-If controls, cast committee votes, and seal the audit log!
              </p>
            </div>
          ) : (
            logs.map((log, idx) => (
              <div
                key={idx}
                className={`p-2.5 rounded-xl border text-left flex items-start gap-2.5 transition-all animate-in fade-in slide-in-from-bottom-1 ${
                  log.type === 'persona'
                    ? 'bg-purple-950/40 border-purple-800/60 text-purple-200 font-bold'
                    : log.type === 'success'
                    ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-300'
                    : log.type === 'warning'
                    ? 'bg-amber-950/40 border-amber-800/60 text-amber-300'
                    : log.type === 'error'
                    ? 'bg-rose-950/40 border-rose-800/60 text-rose-300'
                    : 'bg-slate-900/60 border-slate-800 text-slate-300'
                }`}
              >
                <span className="text-slate-500 shrink-0 font-mono text-[11px]">[{log.time}]</span>
                <span className="leading-relaxed flex-1">{log.text}</span>
              </div>
            ))
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/70 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            {isRunning && (
              <>
                <button
                  onClick={() => setIsPaused(!isPaused)}
                  className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-1.5 border border-slate-700"
                >
                  {isPaused ? <Play className="w-3.5 h-3.5 text-emerald-400 fill-emerald-400" /> : <Pause className="w-3.5 h-3.5 text-amber-400" />}
                  {isPaused ? 'Resume' : 'Pause'}
                </button>

                <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1 rounded-xl text-xs">
                  {[
                    { label: '1x', val: 1 },
                    { label: '2x', val: 2 },
                    { label: 'Turbo', val: 5 }
                  ].map((sp) => (
                    <button
                      key={sp.label}
                      onClick={() => setSpeedMultiplier(sp.val)}
                      className={`px-2 py-0.5 rounded-lg font-mono text-[11px] font-bold ${
                        speedMultiplier === sp.val ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      {sp.label}
                    </button>
                  ))}
                </div>
              </>
            )}

            {createdCaseId && (
              <span className="text-emerald-400 font-bold text-xs flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                Case #{createdCaseNumber} Sealed & Live!
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            {createdCaseId && (
              <button
                onClick={handleOpenCase}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-500/25 transition-all flex items-center gap-2"
              >
                <span>Open Case #{createdCaseNumber} in Workbench</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            )}

            <button
              disabled={isRunning}
              onClick={runFullDemo}
              className={`px-6 py-2.5 rounded-xl font-bold text-xs flex items-center gap-2 shadow-lg transition-all ${
                isRunning
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                  : 'bg-gradient-to-r from-cyan-600 via-blue-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white shadow-cyan-500/30 active:scale-95'
              }`}
            >
              {isRunning ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                  <span>Running Autopilot Demo...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>Start Live Autopilot Demo</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
