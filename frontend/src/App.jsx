import React, { useState, useEffect } from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { Navbar } from './components/common/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { CaseDetailPage } from './pages/CaseDetailPage';
import { NewCasePage } from './pages/NewCasePage';
import { EvaluationHubPage } from './pages/EvaluationHubPage';

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard', 'case-detail', 'new-case', 'evaluation'
  const [selectedCaseId, setSelectedCaseId] = useState(1); // Default to Case 1 (QuickAccount)
  const [demoModalOpen, setDemoModalOpen] = useState(false);

  useEffect(() => {
    // Parse URL search parameters for live demo triggers or direct case links
    const params = new URLSearchParams(window.location.search);
    const caseIdParam = params.get('caseId') || params.get('case_id') || params.get('case');
    const demoParam = params.get('demo') || params.get('autopilot');
    const tabParam = params.get('tab');

    if (caseIdParam) {
      const parsedId = parseInt(caseIdParam, 10);
      if (!isNaN(parsedId)) {
        setSelectedCaseId(parsedId);
        setActiveTab('case-detail');
      }
    } else if (tabParam) {
      setActiveTab(tabParam);
    }

    if (demoParam === 'true' || demoParam === '1' || demoParam === 'live') {
      setDemoModalOpen(true);
    }
  }, []);

  const handleSelectCase = (caseId) => {
    setSelectedCaseId(caseId);
    setActiveTab('case-detail');
  };

  const handleCaseCreated = (newCase) => {
    const id = typeof newCase === 'object' ? newCase.id : newCase;
    setSelectedCaseId(id);
    setActiveTab('case-detail');
  };

  return (
    <AuthProvider>
      <div className="min-h-screen bg-[#080d1a] text-slate-100 flex flex-col font-sans">
        <Navbar 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          onSelectCase={handleSelectCase}
          demoModalOpen={demoModalOpen}
          setDemoModalOpen={setDemoModalOpen}
        />

        <main className="flex-1 pb-16">
          {activeTab === 'dashboard' && (
            <DashboardPage
              onSelectCase={handleSelectCase}
              onNewCaseClick={() => setActiveTab('new-case')}
            />
          )}

          {activeTab === 'case-detail' && (
            <CaseDetailPage
              caseId={selectedCaseId}
              onBack={() => setActiveTab('dashboard')}
            />
          )}

          {activeTab === 'new-case' && (
            <NewCasePage
              onCaseCreated={handleCaseCreated}
              onBack={() => setActiveTab('dashboard')}
            />
          )}

          {activeTab === 'evaluation' && (
            <EvaluationHubPage />
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-900 bg-[#060a14] py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-400">FinShield FCRM Workbench</span>
              <span>— Tier-1 Financial Crime Risk Platform</span>
            </div>
            <div className="font-mono text-[11px] text-slate-600">
              Governed Reference Layer: FATF / FCA / PSR / OCC / FinCEN 2026
            </div>
          </div>
        </footer>
      </div>
    </AuthProvider>
  );
}

export default App;
