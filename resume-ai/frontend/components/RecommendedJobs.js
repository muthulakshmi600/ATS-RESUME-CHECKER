/**
 * RecommendedJobs Component: Intelligent Job Matching section for AnalysisResultPage
 * ResumeAI ATS SaaS Theme
 */

window.RecommendedJobs = ({
  initialJobs = [],
  resumeText = "",
  candidateSkills = [],
  showToast,
  currentUser
}) => {
  const {
    Briefcase, Search, Filter, Sliders, ShieldCheck,
    CheckCircle, AlertCircle, Bookmark, ExternalLink, Zap
  } = window.Icons;

  const [jobs, setJobs] = React.useState(Array.isArray(initialJobs) ? initialJobs : []);
  const [threshold, setThreshold] = React.useState(75);
  const [onlyGoodMatches, setOnlyGoodMatches] = React.useState(false);
  const [savedJobIds, setSavedJobIds] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(false);

  // Filters
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedJobType, setSelectedJobType] = React.useState('');
  const [selectedRemote, setSelectedRemote] = React.useState('');
  const [selectedLocation, setSelectedLocation] = React.useState('');

  // Selected job and platform for ApplyModal
  const [selectedApply, setSelectedApply] = React.useState(null); // { job, platform }

  // Load saved jobs on mount
  React.useEffect(() => {
    async function loadSaved() {
      try {
        const saved = await window.ResumeAIService.getSavedJobs();
        if (Array.isArray(saved)) {
          setSavedJobIds(saved.map(j => j.id));
        }
      } catch (e) {}
    }
    loadSaved();
  }, []);

  // Sync if initialJobs changes
  React.useEffect(() => {
    if (Array.isArray(initialJobs) && initialJobs.length > 0) {
      setJobs(initialJobs);
    } else if (resumeText) {
      // Re-fetch matches if initialJobs was empty
      handleFilterChange();
    }
  }, [initialJobs]);

  const handleFilterChange = async () => {
    setIsLoading(true);
    try {
      const filters = {};
      if (searchTerm.trim()) filters.search = searchTerm.trim();
      if (selectedJobType) filters.job_type = selectedJobType;
      if (selectedRemote) filters.remote = selectedRemote;
      if (selectedLocation) filters.location = selectedLocation;

      const res = await window.ResumeAIService.matchJobs(
        resumeText,
        candidateSkills,
        threshold,
        filters
      );
      if (res && Array.isArray(res.jobs)) {
        setJobs(res.jobs);
      }
    } catch (e) {
      console.warn("Failed to match jobs dynamically:", e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveToggle = async (job) => {
    const isSaved = savedJobIds.includes(job.id);
    try {
      if (isSaved) {
        await window.ResumeAIService.unsaveJob(job.id);
        setSavedJobIds(prev => prev.filter(id => id !== job.id));
        if (showToast) showToast('Job removed from bookmarks.', 'info');
      } else {
        await window.ResumeAIService.saveJob(job.id);
        setSavedJobIds(prev => [...prev, job.id]);
        if (showToast) showToast('Job saved to your bookmarks!', 'success');
      }
    } catch (e) {
      if (showToast) showToast('Bookmark updated.', 'success');
    }
  };

  const handleResetFilters = () => {
    setSearchTerm('');
    setSelectedJobType('');
    setSelectedRemote('');
    setSelectedLocation('');
    setOnlyGoodMatches(false);
    setThreshold(75);
    if (Array.isArray(initialJobs) && initialJobs.length > 0) {
      setJobs(initialJobs);
    }
  };

  // Filter jobs by threshold and search on the client for instant responsiveness
  const filteredJobs = jobs.filter(job => {
    const matchPct = Number(job.job_match_percentage) || 0;
    if (onlyGoodMatches && matchPct < threshold) return false;

    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      const matchText = (job.title + ' ' + job.company + ' ' + (job.description || '')).toLowerCase();
      if (!matchText.includes(q)) return false;
    }

    if (selectedJobType && (job.job_type || '').toLowerCase() !== selectedJobType.toLowerCase()) {
      return false;
    }

    if (selectedRemote === 'remote' && job.is_remote !== 1) return false;
    if (selectedRemote === 'hybrid' && job.is_remote !== 2) return false;
    if (selectedRemote === 'onsite' && job.is_remote !== 0) return false;

    if (selectedLocation && !(job.location || '').toLowerCase().includes(selectedLocation.toLowerCase())) {
      return false;
    }

    return true;
  });

  const goodMatchesCount = jobs.filter(j => (Number(j.job_match_percentage) || 0) >= threshold).length;

  return (
    <div className="space-y-6 pt-6 border-t border-[#E2E8F0]">
      
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-[#14B8A6] uppercase tracking-wider bg-teal-50 border border-teal-200 px-2.5 py-0.5 rounded-full flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 text-[#14B8A6]" />
              Intelligent Role Matching
            </span>
            <span className="text-xs font-bold text-[#64748B] bg-slate-100 border border-slate-200 px-2.5 py-0.5 rounded-full">
              {jobs.length} Verified Roles
            </span>
          </div>
          <h2 className="text-2xl font-extrabold text-[#14213D] mt-2 tracking-tight flex items-center gap-2">
            <span>Find Matching Jobs (LinkedIn, Naukri & Direct Careers)</span>
          </h2>
          <p className="text-xs text-[#64748B] mt-1 max-w-2xl leading-relaxed">
            Calculated by comparing your extracted technical skills, tools, and background against verified job requirements.
            Explore verified company postings or discover open vacancies on LinkedIn and Naukri.
          </p>

        </div>

        {/* Good match count counter badge */}
        <div className="flex items-center gap-3">
          <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-3 px-4 text-center sm:text-right">
            <span className="text-xs font-extrabold text-[#16A34A] block">
              {goodMatchesCount} High Match Roles
            </span>
            <span className="text-[10px] text-[#64748B]">Meeting {threshold}%+ threshold</span>
          </div>
        </div>
      </div>

      {/* Threshold & Filters Control Panel */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm space-y-4">
        
        {/* Top Filter Controls: Threshold Selector & Only Good Match Switch */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          
          {/* Match Threshold Control */}
          <div className="flex flex-wrap items-center gap-3 text-xs">
            <span className="font-bold text-[#14213D] flex items-center gap-1.5">
              <Sliders className="w-4 h-4 text-[#2563EB]" />
              Match Threshold:
            </span>
            <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl">
              {[50, 65, 75, 85].map((val) => (
                <button
                  key={val}
                  onClick={() => setThreshold(val)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                    threshold === val
                      ? 'bg-[#2563EB] text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {val}%
                </button>
              ))}
            </div>
            <span className="text-[11px] text-[#64748B] hidden sm:inline">
              (Initial baseline: 75%)
            </span>
          </div>

          {/* Toggle: Only Show Good Matches */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setOnlyGoodMatches(!onlyGoodMatches)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold border transition flex items-center gap-1.5 ${
                onlyGoodMatches
                  ? 'bg-emerald-50 text-[#16A34A] border-emerald-300'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>{onlyGoodMatches ? 'Showing Only Good Matches (>= ' + threshold + '%)' : 'Show All Match Tiers'}</span>
            </button>
          </div>

        </div>

        {/* Search & Attributes Filter Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          
          {/* Keyword Search */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search title, company, or skills..."
              className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#F8FAFC] focus:bg-white focus:outline-none focus:border-[#2563EB] transition text-xs"
            />
          </div>

          {/* Job Type Dropdown */}
          <div>
            <select
              value={selectedJobType}
              onChange={(e) => setSelectedJobType(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#F8FAFC] focus:bg-white focus:outline-none focus:border-[#2563EB] transition text-xs font-medium text-slate-700"
            >
              <option value="">All Job Types</option>
              <option value="Full-Time">Full-Time</option>
              <option value="Internship">Internship</option>
              <option value="Contract">Contract</option>
            </select>
          </div>

          {/* Remote / On-Site Dropdown */}
          <div>
            <select
              value={selectedRemote}
              onChange={(e) => setSelectedRemote(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#F8FAFC] focus:bg-white focus:outline-none focus:border-[#2563EB] transition text-xs font-medium text-slate-700"
            >
              <option value="">Workplace (All)</option>
              <option value="remote">Remote Only</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">On-Site</option>
            </select>
          </div>

          {/* Location Filter */}
          <div>
            <input
              type="text"
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              placeholder="Filter by location (e.g. Bangalore)..."
              className="w-full px-3 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#F8FAFC] focus:bg-white focus:outline-none focus:border-[#2563EB] transition text-xs"
            />
          </div>

        </div>

      </div>

      {/* Recommended Jobs List */}
      <div className="space-y-4">
        {filteredJobs.map((job) => (
          <window.JobCard
            key={job.id}
            job={job}
            threshold={threshold}
            isSaved={savedJobIds.includes(job.id)}
            onSaveToggle={handleSaveToggle}
            onApplyClick={(j, platform) => setSelectedApply({ job: j, platform: platform || 'company' })}
            showMatchDetails={true}
          />
        ))}

        {/* Empty State */}
        {filteredJobs.length === 0 && (
          <div className="text-center py-12 bg-white rounded-2xl border border-[#E2E8F0] p-8 shadow-sm">
            <div className="w-12 h-12 mx-auto rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-3">
              <Briefcase className="w-6 h-6" />
            </div>
            <h4 className="text-base font-bold text-[#14213D] mb-1">No Matching Jobs Found</h4>
            <p className="text-xs text-[#64748B] max-w-md mx-auto mb-4">
              {onlyGoodMatches
                ? `No current jobs meet your ${threshold}% match threshold with the current search filters. Lower your threshold or expand search parameters.`
                : "No verified jobs match your active filters. Try clearing your search query."}
            </p>
            <button
              onClick={handleResetFilters}
              className="px-4 py-2 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-semibold text-xs transition shadow-sm"
            >
              Reset Filters
            </button>
          </div>
        )}
      </div>

      {/* Legal & Algorithmic Disclaimer */}
      <div className="p-3.5 rounded-xl bg-slate-100 border border-slate-200 text-xs text-[#64748B] flex items-start gap-2.5">
        <ShieldCheck className="w-4 h-4 text-[#2563EB] flex-shrink-0 mt-0.5" />
        <span className="leading-relaxed">
          <strong>Transparency Disclaimer:</strong> Job Match Percentage is calculated algorithmically by comparing extracted skills and terminology from your resume against employer requirements. A high match score indicates strong keyword alignment and does not constitute a guarantee of interview selection or employment.
        </span>
      </div>

      {/* Apply Modal with Platform Support */}
      {selectedApply && (
        <window.ApplyModal
          job={selectedApply.job}
          platform={selectedApply.platform || 'company'}
          isOpen={Boolean(selectedApply)}
          onClose={() => setSelectedApply(null)}
          onApplied={() => {
            if (showToast) showToast('Application logged in tracker!', 'success');
          }}
          showToast={showToast}
        />
      )}

    </div>
  );
};

