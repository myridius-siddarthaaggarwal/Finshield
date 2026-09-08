import React from 'react';
import { IntakeForm } from '../components/submitter/IntakeForm';
import { ArrowLeft } from 'lucide-react';

export const NewCasePage = ({ onCaseCreated, onBack }) => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Risk Portfolio</span>
      </button>

      <IntakeForm onCaseCreated={onCaseCreated} />
    </div>
  );
};
