/**
 * CheckResumePage Component: The core ATS Resume Upload & Analysis Flow
 * ResumeAI ATS SaaS Theme
 */

window.CheckResumePage = ({ onNavigate, onAnalysisComplete, showToast, currentUser }) => {
  const {
    Sparkles, ArrowRight, Upload, FileText, X, AlertCircle,
    CheckCircle, ShieldCheck, Zap
  } = window.Icons;

  const [selectedFile, setSelectedFile] = React.useState(null);
  const [fileError, setFileError] = React.useState('');
  const [jobDescription, setJobDescription] = React.useState('');
  const [autoSave, setAutoSave] = React.useState(true);
  
  // Multi-step animated loading states
  const [isAnalyzing, setIsAnalyzing] = React.useState(false);
  const [loadingStepIndex, setLoadingStepIndex] = React.useState(0);

  const loadingSteps = [
    'Parsing resume structure & formatting...',
    'Analyzing contact info, metrics & impact...',
    'Evaluating sections, skills & readability...',
    jobDescription.trim() ? 'Matching against Target Job Description...' : 'Calculating Resume Quality Score...',
    'Generating actionable recommendations...',
    'Finalizing comprehensive audit report...'
  ];

  const handleFileSelect = (file, error) => {
    setSelectedFile(file);
    setFileError(error || '');
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    setFileError('');
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setFileError('Please upload a resume file (PDF or DOCX) before starting analysis.');
      return;
    }

    setFileError('');
    setIsAnalyzing(true);
    setLoadingStepIndex(0);

    // Animate through the multi-stage status messages
    const stepInterval = setInterval(() => {
      setLoadingStepIndex(prev => {
        if (prev < loadingSteps.length - 1) return prev + 1;
        return prev;
      });
    }, 500);

    try {
      const result = await window.ResumeAIService.analyzeResume(
        selectedFile,
        jobDescription.trim(),
        autoSave
      );

      clearInterval(stepInterval);
      setIsAnalyzing(false);
      showToast('Resume analysis complete!', 'success');
      onAnalysisComplete(result);

    } catch (err) {
      clearInterval(stepInterval);
      setIsAnalyzing(false);
      setFileError(err.message || 'Analysis encountered an error. Please try another file.');
      showToast(err.message || 'Analysis error occurred.', 'error');
    }
  };

  // Quick sample loader for reviewers/tutors convenience
  const loadSampleDoc = async () => {
    try {
      const resp = await fetch('/api/sample-resume?type=pdf');
      if (resp.ok) {
        const blob = await resp.blob();
        const file = new File([blob], 'sample_ai_ml_engineer.pdf', { type: 'application/pdf' });
        setSelectedFile(file);
        setFileError('');
        setJobDescription('Looking for an AI/ML Engineer experienced in Python, PyTorch, TensorFlow, Scikit-Learn, Docker, and REST APIs.');
        showToast('Sample AI/ML Engineer resume loaded!', 'success');
        return;
      }
    } catch (e) {
      console.warn("Could not fetch remote sample resume:", e);
    }
    showToast('Could not load sample file from server.', 'error');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      
      {/* Title Header */}
      <div className="text-center sm:text-left border-b border-[#E2E8F0] pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-[#2563EB] text-xs font-semibold uppercase tracking-wider mb-2">
          <Sparkles className="w-3.5 h-3.5" />
          <span>ResumeAI ATS Diagnostic Engine</span>
        </div>
        <h1 className="text-3xl font-extrabold text-[#14213D] tracking-tight">
          Audit & Optimize Your Resume
        </h1>
        <p className="text-sm text-[#64748B] mt-1">
          Evaluate resume formatting, section completeness, contact links, measurable metrics, and optional job description alignment.
        </p>

        {/* Quick sample banner */}
        <div className="mt-4 p-3.5 rounded-xl bg-slate-100 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="text-[#1E293B]">
            <span className="font-bold text-[#14213D]">Quick Demo:</span> Load a pre-populated professional sample resume & target job description to test immediately.
          </div>
          <button
            type="button"
            onClick={loadSampleDoc}
            className="flex-shrink-0 px-3.5 py-1.5 rounded-lg bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-semibold transition shadow-sm"
          >
            Load Sample Data
          </button>
        </div>
      </div>

      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 sm:p-8 space-y-8 shadow-sm">
        
        {/* STEP 1: Upload Resume */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-[#2563EB] text-white text-xs font-bold flex items-center justify-center">
              1
            </span>
            <h3 className="text-base font-bold text-[#14213D]">Upload Resume Document</h3>
            <span className="text-xs text-rose-500 font-semibold">*Required</span>
          </div>

          <window.FileUploader
            file={selectedFile}
            onFileSelect={handleFileSelect}
            onFileRemove={handleFileRemove}
            error={fileError}
          />
        </div>

        {/* STEP 2: Job Description (Optional) */}
        <div className="space-y-3 pt-6 border-t border-[#E2E8F0]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-[#2563EB] text-white text-xs font-bold flex items-center justify-center">
                2
              </span>
              <h3 className="text-base font-bold text-[#14213D]">Target Job Description</h3>
              <span className="text-xs text-[#64748B] font-medium bg-slate-100 px-2 py-0.5 rounded">(Optional)</span>
            </div>
          </div>

          <p className="text-xs text-[#64748B] leading-relaxed">
            Paste a target job posting below to calculate a separate <strong>Job Match Score</strong>, detect matched & missing keywords, and get tailored application advice. Leave empty to evaluate <strong>Resume Quality</strong> alone.
          </p>

          <textarea
            rows={5}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the target job description or requirements here (optional)..."
            className="w-full p-4 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] placeholder-slate-400 text-sm focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition resize-y font-sans"
          />
        </div>

        {/* Options & Action Button */}
        <div className="pt-6 border-t border-[#E2E8F0] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <label className="flex items-center gap-2.5 cursor-pointer text-xs text-[#64748B] select-none">
            <input
              type="checkbox"
              checked={autoSave}
              onChange={(e) => setAutoSave(e.target.checked)}
              className="w-4 h-4 rounded text-[#2563EB] bg-white border-slate-300 focus:ring-[#2563EB]"
            />
            <span>Automatically save this scan to my Resume History</span>
          </label>

          <button
            type="button"
            onClick={handleAnalyze}
            disabled={!selectedFile || isAnalyzing}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-sm shadow-md shadow-blue-600/20 transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-40 disabled:hover:scale-100"
          >
            <Sparkles className="w-4 h-4" />
            <span>Audit Resume with ResumeAI</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </button>
        </div>

      </div>

      {/* Multi-step Animated Loading Overlay */}
      {isAnalyzing && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-8 max-w-md w-full text-center shadow-2xl relative overflow-hidden">
            
            {/* Top accent bar */}
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-[#2563EB] via-[#14B8A6] to-[#14213D]" />

            <div className="relative w-16 h-16 mx-auto mb-5 flex items-center justify-center">
              <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB]">
                <Sparkles className="w-8 h-8 animate-spin-slow" />
              </div>
            </div>

            <h3 className="text-xl font-extrabold text-[#14213D] mb-2">
              Analyzing Resume...
            </h3>
            
            <p className="text-sm font-semibold text-[#2563EB] h-6 transition-all duration-300">
              {loadingSteps[loadingStepIndex]}
            </p>

            {/* Progress Bar */}
            <div className="w-full bg-slate-100 rounded-full h-2 mt-6 overflow-hidden">
              <div
                className="h-2 bg-[#2563EB] rounded-full transition-all duration-500 ease-out"
                style={{ width: `${Math.round(((loadingStepIndex + 1) / loadingSteps.length) * 100)}%` }}
              />
            </div>

            <p className="text-[11px] text-[#64748B] mt-4">
              Running deep structural heuristic & keyword matching...
            </p>

          </div>
        </div>
      )}

    </div>
  );
};
