/**
 * SettingsPage Component: Dedicated ATS Engine Configuration & Preferences
 * ResumeAI ATS SaaS Theme
 */

window.SettingsPage = ({ onNavigate, showToast }) => {
  const { Settings, CheckCircle, Trash2, ShieldCheck, Sparkles, ArrowRight } = window.Icons;

  const [sensitivity, setSensitivity] = React.useState('Standard');
  const [autoSave, setAutoSave] = React.useState(true);
  const [isSaving, setIsSaving] = React.useState(false);

  React.useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const s = await window.ResumeAIService.getSettings();
      if (s) {
        setSensitivity(s.scoring_sensitivity || 'Standard');
        setAutoSave(Boolean(s.auto_save));
      }
    } catch (e) {}
  };

  const handleSettingsSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await window.ResumeAIService.updateSettings({
        scoring_sensitivity: sensitivity,
        auto_save: autoSave
      });
      showToast('ATS Engine preferences saved successfully!', 'success');
    } catch (err) {
      showToast('Failed to save settings.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear your local resume history? This cannot be undone.')) {
      window.ResumeAIService.clearAllLocalHistory();
      showToast('All local resume history cleared.', 'info');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="border-b border-[#E2E8F0] pb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-[#2563EB] text-xs font-semibold uppercase tracking-wider mb-2">
            <Settings className="w-3.5 h-3.5" />
            <span>Preferences & Engine Tuning</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#14213D] tracking-tight">
            ATS Engine Settings
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Configure parser strictness, storage automation, display themes, and data retention.
          </p>
        </div>

        <button
          onClick={() => onNavigate('dashboard')}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white hover:bg-slate-50 text-[#1E293B] text-xs font-semibold border border-[#CBD5E1] transition shadow-sm"
        >
          <span>Back to Dashboard</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Main Settings Card */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 sm:p-8 space-y-8 shadow-sm">
        <form onSubmit={handleSettingsSave} className="space-y-6">
          
          {/* Scoring Sensitivity */}
          <div>
            <label className="block text-xs font-bold text-[#14213D] mb-1 uppercase tracking-wider">
              ATS Evaluation Strictness
            </label>
            <p className="text-xs text-[#64748B] mb-4">
              Select how strictly the rule-based engine evaluates keyword repetition, action verbs, and section structure.
            </p>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { id: 'Lenient', label: 'Lenient', subtitle: 'Forgiving match for entry-level and fresher applicants' },
                { id: 'Standard', label: 'Standard', subtitle: 'Balanced corporate enterprise ATS model (Recommended)' },
                { id: 'Strict', label: 'Strict', subtitle: 'Demanding filters for senior roles & top tech firms' }
              ].map(level => (
                <button
                  key={level.id}
                  type="button"
                  onClick={() => setSensitivity(level.id)}
                  className={`p-4 rounded-xl text-left border transition-all ${
                    sensitivity === level.id
                      ? 'bg-blue-50 border-[#2563EB] text-[#14213D] shadow-sm'
                      : 'bg-[#F8FAFC] border-[#E2E8F0] text-[#64748B] hover:text-[#1E293B] hover:bg-slate-50'
                  }`}
                >
                  <span className="text-xs font-bold block text-[#14213D]">{level.label}</span>
                  <span className="text-[11px] text-[#64748B] mt-1 block leading-relaxed">
                    {level.subtitle}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Toggle options */}
          <div className="space-y-4 pt-4 border-t border-[#E2E8F0]">
            <label className="flex items-center justify-between p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] cursor-pointer">
              <div>
                <span className="text-xs font-bold text-[#14213D] block">Auto-Save Analyses</span>
                <span className="text-[11px] text-[#64748B]">Save every resume scan automatically to your history records</span>
              </div>
              <input
                type="checkbox"
                checked={autoSave}
                onChange={(e) => setAutoSave(e.target.checked)}
                className="w-4 h-4 rounded text-[#2563EB] bg-white border-slate-300 focus:ring-[#2563EB]"
              />
            </label>

            <div className="flex items-center justify-between p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
              <div>
                <span className="text-xs font-bold text-[#14213D] block">Theme Mode</span>
                <span className="text-[11px] text-[#64748B]">Modern AI SaaS Light Theme (Active)</span>
              </div>
              <span className="text-xs font-bold text-[#2563EB] bg-blue-50 px-3 py-1 rounded-lg border border-blue-200">
                SaaS Light
              </span>
            </div>
          </div>

          <div className="pt-2 flex items-center justify-between">
            <button
              type="submit"
              disabled={isSaving}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-xs shadow-sm transition"
            >
              <CheckCircle className="w-4 h-4" />
              <span>{isSaving ? 'Saving Settings...' : 'Save Engine Preferences'}</span>
            </button>
          </div>
        </form>

        {/* Danger Zone: Clear History */}
        <div className="pt-6 border-t border-rose-200">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-rose-50 border border-rose-200">
            <div>
              <h4 className="text-xs font-bold text-rose-600 uppercase tracking-wider">Purge Local Scan History</h4>
              <p className="text-[11px] text-slate-600 mt-0.5">Permanently deletes all saved resume scans from your local browser database.</p>
            </div>
            <button
              type="button"
              onClick={handleClearHistory}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition shadow-sm"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear History</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
