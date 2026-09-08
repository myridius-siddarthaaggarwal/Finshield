import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Shield, Coins, Sparkles, User, ChevronDown, CheckCircle2, AlertTriangle, Layers, BarChart3, PlusCircle } from 'lucide-react';
import { TokenCostModal } from './TokenCostModal';

export const Navbar = ({ activeTab, setActiveTab }) => {
  const { currentUser, allUsers, switchPersona } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [tokenModalOpen, setTokenModalOpen] = useState(false);

  const getRoleBadge = (role) => {
    switch (role) {
      case 'SUBMITTER':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'ANALYST':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'COMMITTEE_MEMBER':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      case 'ADMIN':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      default:
        return 'bg-slate-700 text-slate-300';
    }
  };

  return (
    <>
      <header className="sticky top-0 z-40 bg-[#0c1222]/90 backdrop-blur-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Brand */}
          <div className="flex items-center gap-6">
            <button 
              onClick={() => setActiveTab('dashboard')} 
              className="flex items-center gap-3 group text-left focus:outline-none"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
                    FinShield
                  </span>
                  <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                    FCRM v2.6
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 tracking-wide font-medium">
                  Financial Crime Risk Assessment Workbench
                </div>
              </div>
            </button>

            {/* Navigation tabs */}
            <nav className="hidden md:flex items-center gap-1 text-sm font-medium ml-4">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 ${
                  activeTab === 'dashboard'
                    ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Layers className="w-4 h-4" />
                Case Portfolio (7 Cases)
              </button>

              <button
                onClick={() => setActiveTab('new-case')}
                className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 ${
                  activeTab === 'new-case'
                    ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <PlusCircle className="w-4 h-4" />
                New Intake
              </button>

              <button
                onClick={() => setActiveTab('evaluation')}
                className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 ${
                  activeTab === 'evaluation'
                    ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                Evaluation & Judgement Hub
              </button>
            </nav>
          </div>

          {/* Right Controls */}
          <div className="flex items-center gap-3">
            {/* Live Token Counter Badge */}
            <button
              onClick={() => setTokenModalOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-cyan-500/30 text-xs font-mono text-cyan-300 hover:bg-slate-800 transition-all shadow-sm group"
              title="Click to view live Token Telemetry & Cost Optimization"
            >
              <Coins className="w-3.5 h-3.5 text-cyan-400 group-hover:rotate-12 transition-transform" />
              <span>4,184 tokens</span>
              <span className="text-[10px] px-1 py-0.2 bg-emerald-950 text-emerald-400 rounded border border-emerald-800">
                −44%
              </span>
            </button>

            {/* Persona Switcher Dropdown */}
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 hover:border-slate-600 transition-colors text-left"
              >
                <div className="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 text-xs font-bold">
                  {currentUser?.full_name?.charAt(0) || 'U'}
                </div>
                <div className="hidden sm:block">
                  <div className="text-xs font-semibold text-slate-200 leading-tight">
                    {currentUser?.full_name}
                  </div>
                  <div className="text-[10px] text-slate-400 leading-none">
                    {currentUser?.title || currentUser?.role}
                  </div>
                </div>
                <span className={`text-[9px] uppercase px-1.5 py-0.5 rounded border ${getRoleBadge(currentUser?.role)}`}>
                  {currentUser?.role === 'COMMITTEE_MEMBER' ? 'COMMITTEE' : currentUser?.role}
                </span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl py-2 z-50 animate-in fade-in zoom-in duration-100">
                  <div className="px-3 py-2 border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Switch Active Persona (Demo Mode)
                  </div>
                  <div className="max-h-72 overflow-y-auto divide-y divide-slate-800/50">
                    {allUsers.map((user) => (
                      <button
                        key={user.id}
                        onClick={() => {
                          switchPersona(user.id);
                          setDropdownOpen(false);
                        }}
                        className={`w-full text-left px-3 py-2.5 hover:bg-slate-800/70 transition-colors flex items-center justify-between ${
                          currentUser?.id === user.id ? 'bg-cyan-950/40 border-l-2 border-cyan-500' : ''
                        }`}
                      >
                        <div>
                          <div className="text-xs font-semibold text-slate-200">{user.full_name}</div>
                          <div className="text-[11px] text-slate-400">{user.title}</div>
                        </div>
                        <span className={`text-[9px] uppercase px-1.5 py-0.5 rounded border ${getRoleBadge(user.role)}`}>
                          {user.role === 'COMMITTEE_MEMBER' ? 'VOTING' : user.role}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <TokenCostModal isOpen={tokenModalOpen} onClose={() => setTokenModalOpen(false)} />
    </>
  );
};
