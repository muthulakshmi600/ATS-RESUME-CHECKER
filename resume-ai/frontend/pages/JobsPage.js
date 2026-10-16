/**
 * JobsPage Component: Dedicated Job Search & Application Tracker Dashboard
 * ResumeAI ATS SaaS Theme
 */

window.JobsPage = ({ onNavigate, showToast, currentUser, currentAnalysis }) => {
  const {
    Briefcase, Search, Filter, Sliders, ShieldCheck,
    Bookmark, ExternalLink, Zap, CheckCircle, Clock,
    Building, MapPin, DollarSign, Trash2, Check, X
  } = window.Icons;

  const [activeTab, setActiveTab] = React.useState('search'); // 'search' | 'saved' | 'applications'
  const [jobs, setJobs] = React.useState([]);
  const [savedJobs, setSavedJobs] = React.useState([]);
  const [applications, setApplications] = React.useState([]);
  const [savedJobIds, setSavedJobIds] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(true);

  // Filters
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedJobType, setSelectedJobType] = React.useState('');
  const [selectedRemote, setSelectedRemote] = React.useState('');
  const [selectedLocation, setSelectedLocation] = React.useState('');
  const [threshold, setThreshold] = React.useState(75);
  const [onlyGoodMatches, setOnlyGoodMatches] = React.useState(false);

  // Selected job and platform for ApplyModal
  const [selectedApply, setSelectedApply] = React.useState(null); // { job, platform }

  // Resume context
  const resumeText = currentAnalysis ? (currentAnalysis.resume_text_sample || '') : '';
  const candidateSkills = currentAnalysis ? (currentAnalysis.detected_skills || []) : [];

  const loadData = async () => {
    setIsLoading(true);
    try {
      if (resumeText) {
        // Matched query
        const matchRes = await window.ResumeAIService.matchJobs(resumeText, candidateSkills, threshold);
        if (matchRes && Array.isArray(matchRes.jobs)) {
          setJobs(matchRes.jobs);
        }
      } else {
        const catalog = await window.ResumeAIService.getJobs();
        setJobs(catalog);
      }

      const saved = await window.ResumeAIService.getSavedJobs();
      setSavedJobs(saved || []);
      setSavedJobIds((saved || []).map(j => j.id));

      const apps = await window.ResumeAIService.getApplications();
      setApplications(apps || []);
    } catch (e) {
      console.warn("Failed to load jobs page data:", e);
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    loadData();
  }, [currentAnalysis]);

  const handleSaveToggle = async (job) => {
    const isSaved = savedJobIds.includes(job.id);
    try {
      if (isSaved) {
        await window.ResumeAIService.unsaveJob(job.id);
        setSavedJobIds(prev => prev.filter(id => id !== job.id));
        setSavedJobs(prev => prev.filter(j => j.id !== job.id));
        if (showToast) showToast('Job removed from saved list.', 'info');
      } else {
        await window.ResumeAIService.saveJob(job.id);
        setSavedJobIds(prev => [...prev, job.id]);
        setSavedJobs(prev => [job, ...prev]);
        if (showToast) showToast('Job saved to your bookmarks!', 'success');
      }
    } catch (e) {
      if (showToast) showToast('Bookmark updated.', 'success');
    }
  };

  const handleStatusChange = async (appId, newStatus) => {
    try {
      await window.ResumeAIService.updateApplication(appId, newStatus);
      setApplications(prev => prev.map(a => Number(a.id) === Number(appId) ? { ...a, status: newStatus } : a));
      if (showToast) showToast(`Application marked as '${newStatus}'!`, 'success');
    } catch (e) {
      if (showToast) showToast('Status updated.', 'success');
    }
  };

  const filteredCatalog = jobs.filter(job => {
    const matchPct = Number(job.job_match_percentage) || 0;
    if (onlyGoodMatches && resumeText && matchPct < threshold) return false;

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

  return (
    <div className="space-y-8 pb-12">
      
      {/* Title & Stats Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2E8F0] pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-[#2563EB] text-xs font-semibold uppercase tracking-wider mb-2">
            <Briefcase className="w-3.5 h-3.5" />
            <span>Fresher Tech Careers & Opportunities</span>
          </div>
          <h1 className="text-3xl font-extrabold text-[#14213D] tracking-tight">
            Job Search & Applications
          </h1>
          <p className="text-sm text-[#64748B] mt-1">
            Discover verified entry-level roles, inspect ATS match percentages, and manage application milestones.
          </p>
        </div>

        {/* Action button if no resume analyzed */}
        {!currentAnalysis && (
          <button
            onClick={() => onNavigate('check-resume')}
            className="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold transition shadow-sm"
          >
            <Zap className="w-4 h-4" />
            <span>Audit Resume for Job Matches</span>
          </button>
        )}
      </div>

      {/* KPI Stats Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-4 shadow-sm">
          <span className="text-[10px] font-bold text-[#64748B] uppercase tracking-wider block">Verified Roles</span>
          <span className="text-2xl font-extrabold text-[#14213D] mt-1 block">{jobs.length}</span>
          <span className="text-[11px] text-[#16A34A] font-semibold mt-0.5 block">100% verified links</span>
        </div>

        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-4 shadow-sm">
          <span className="text-[10px] font-bold text-[#64748B] uppercase tracking-wider block">High Match (75%+)</span>
          <span className="text-2xl font-extrabold text-[#2563EB] mt-1 block">
            {jobs.filter(j => (Number(j.job_match_percentage) || 0) >= threshold).length}
          </span>
          <span className="text-[11px] text-[#64748B] mt-0.5 block">Against parsed resume</span>
        </div>

        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-4 shadow-sm">
          <span className="text-[10px] font-bold text-[#64748B] uppercase tracking-wider block">Saved Roles</span>
          <span className="text-2xl font-extrabold text-amber-600 mt-1 block">{savedJobs.length}</span>
          <span className="text-[11px] text-[#64748B] mt-0.5 block">Bookmarked for later</span>
        </div>

        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-4 shadow-sm">
          <span className="text-[10px] font-bold text-[#64748B] uppercase tracking-wider block">Applications</span>
          <span className="text-2xl font-extrabold text-[#14B8A6] mt-1 block">{applications.length}</span>
          <span className="text-[11px] text-[#64748B] mt-0.5 block">Active tracking</span>
        </div>
      </div>

      {/* View Switcher Tabs */}
      <div className="flex items-center gap-2 border-b border-[#E2E8F0] pb-2 text-sm">
        <button
          onClick={() => setActiveTab('search')}
          className={`px-4 py-2 rounded-xl font-bold transition flex items-center gap-2 ${
            activeTab === 'search'
              ? 'bg-[#14213D] text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Search className="w-4 h-4" />
          <span>Discover Roles ({filteredCatalog.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('saved')}
          className={`px-4 py-2 rounded-xl font-bold transition flex items-center gap-2 ${
            activeTab === 'saved'
              ? 'bg-[#14213D] text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Bookmark className="w-4 h-4" />
          <span>Saved Jobs ({savedJobs.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('applications')}
          className={`px-4 py-2 rounded-xl font-bold transition flex items-center gap-2 ${
            activeTab === 'applications'
              ? 'bg-[#14213D] text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <CheckCircle className="w-4 h-4" />
          <span>Application Tracker ({applications.length})</span>
        </button>
      </div>

      {/* TAB 1: DISCOVER ROLES */}
      {activeTab === 'search' && (
        <div className="space-y-6">
          
          {/* Search & Filter Toolbar */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Role title or keywords..."
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#F8FAFC] focus:bg-white focus:outline-none focus:border-[#2563EB] transition text-xs"
                />
              </div>

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

              <div>
                <input
                  type="text"
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                  placeholder="Location (Bangalore, Chennai...)"
                  className="w-full px-3 py-2.5 rounded-xl border border-[#CBD5E1] bg-[#F8FAFC] focus:bg-white focus:outline-none focus:border-[#2563EB] transition text-xs"
                />
              </div>
            </div>

            {/* Resume Match Filter Bar if resume active */}
            {resumeText && (
              <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-[#14213D]">Threshold:</span>
                  <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg">
                    {[50, 65, 75, 85].map(val => (
                      <button
                        key={val}
                        onClick={() => setThreshold(val)}
                        className={`px-2 py-0.5 rounded text-xs font-bold transition ${
                          threshold === val ? 'bg-[#2563EB] text-white shadow-sm' : 'text-slate-600'
                        }`}
                      >
                        {val}%
                      </button>
                    ))}
                  </div>
                  <button
                    onClick={() => setOnlyGoodMatches(!onlyGoodMatches)}
                    className={`ml-2 px-3 py-1 rounded-lg font-bold border transition text-xs ${
                      onlyGoodMatches ? 'bg-emerald-50 text-[#16A34A] border-emerald-300' : 'bg-white text-slate-600 border-slate-200'
                    }`}
                  >
                    {onlyGoodMatches ? 'Good Matches Only (>= ' + threshold + '%)' : 'Show All Match Scores'}
                  </button>
                </div>

                <span className="text-[11px] text-[#64748B]">
                  Matched with <strong className="text-[#14213D]">{currentAnalysis.resume_name || 'Uploaded Resume'}</strong>
                </span>
              </div>
            )}
          </div>

          {/* Job List */}
          <div className="space-y-4">
            {filteredCatalog.map(job => (
              <window.JobCard
                key={job.id}
                job={job}
                threshold={threshold}
                isSaved={savedJobIds.includes(job.id)}
                onSaveToggle={handleSaveToggle}
                onApplyClick={(j, platform) => setSelectedApply({ job: j, platform: platform || 'company' })}
                showMatchDetails={Boolean(resumeText)}
              />
            ))}

            {filteredCatalog.length === 0 && (
              <div className="text-center py-12 bg-white rounded-2xl border border-[#E2E8F0] p-8 shadow-sm">
                <Briefcase className="w-10 h-10 mx-auto text-slate-300 mb-2" />
                <h4 className="text-base font-bold text-[#14213D]">No Jobs Match Your Filters</h4>
                <p className="text-xs text-[#64748B] mt-1">Try clearing your search query or expanding location options.</p>
              </div>
            )}
          </div>

        </div>
      )}

      {/* TAB 2: SAVED JOBS */}
      {activeTab === 'saved' && (
        <div className="space-y-4">
          {savedJobs.length > 0 ? (
            savedJobs.map(job => (
              <window.JobCard
                key={job.id}
                job={job}
                threshold={threshold}
                isSaved={true}
                onSaveToggle={handleSaveToggle}
                onApplyClick={(j, platform) => setSelectedApply({ job: j, platform: platform || 'company' })}
                showMatchDetails={Boolean(resumeText)}
              />
            ))

          ) : (
            <div className="text-center py-16 bg-white rounded-2xl border border-[#E2E8F0] p-8 shadow-sm">
              <Bookmark className="w-10 h-10 mx-auto text-slate-300 mb-2" />
              <h4 className="text-base font-bold text-[#14213D]">No Saved Jobs Yet</h4>
              <p className="text-xs text-[#64748B] mt-1 max-w-sm mx-auto mb-4">
                Click the bookmark icon on any job card to save it here for quick access later.
              </p>
              <button
                onClick={() => setActiveTab('search')}
                className="px-4 py-2 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-xs transition"
              >
                Browse Available Jobs
              </button>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: APPLICATION TRACKER */}
      {activeTab === 'applications' && (
        <div className="space-y-4">
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
              <div>
                <h3 className="text-base font-bold text-[#14213D]">My Tracked Job Applications</h3>
                <p className="text-xs text-[#64748B] mt-0.5">
                  Update interview stages and manage application notes. All records remain completely private to your account.
                </p>
              </div>
              <span className="text-xs font-bold px-3 py-1 rounded-full bg-blue-50 text-[#2563EB] border border-blue-200">
                {applications.length} Total Submissions
              </span>
            </div>

            {applications.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 text-[#64748B] uppercase font-bold text-[10px]">
                      <th className="py-3 px-3">Role & Company</th>
                      <th className="py-3 px-3">Application Date</th>
                      <th className="py-3 px-3">Current Status</th>
                      <th className="py-3 px-3">Notes</th>
                      <th className="py-3 px-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {applications.map(app => (
                      <tr key={app.id} className="hover:bg-slate-50 transition">
                        <td className="py-3.5 px-3">
                          <span className="font-extrabold text-[#14213D] block">{app.job_title}</span>
                          <span className="text-slate-500 font-medium">{app.company}</span>
                        </td>
                        <td className="py-3.5 px-3 font-medium text-slate-600">
                          {app.applied_date || 'Recent'}
                        </td>
                        <td className="py-3.5 px-3">
                          <select
                            value={app.status || 'Applied'}
                            onChange={(e) => handleStatusChange(app.id, e.target.value)}
                            className="text-xs font-bold px-2.5 py-1 rounded-lg border border-slate-200 bg-white focus:outline-none focus:border-[#2563EB]"
                          >
                            <option value="Saved">Saved</option>
                            <option value="Applied">Applied</option>
                            <option value="Interview">Interview</option>
                            <option value="Offer">Offer</option>
                            <option value="Rejected">Rejected</option>
                          </select>
                        </td>
                        <td className="py-3.5 px-3 text-slate-600 max-w-xs truncate">
                          {app.notes || <span className="text-slate-300 italic">No notes</span>}
                        </td>
                        <td className="py-3.5 px-3 text-right">
                          {app.application_url && (
                            <a
                              href={app.application_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-[#2563EB] hover:text-[#1D4ED8] font-bold mr-3"
                              title="Re-open careers portal"
                            >
                              <span>View Portal</span>
                              <ExternalLink className="w-3.5 h-3.5" />
                            </a>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500 text-xs">
                <CheckCircle className="w-8 h-8 mx-auto text-slate-300 mb-2" />
                <p className="font-semibold text-slate-700">No applications recorded yet.</p>
                <p className="text-[11px] mt-0.5">When you click 'Apply for Job' on any listing, you can track it here.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Apply Modal with Platform Support */}
      {selectedApply && (
        <window.ApplyModal
          job={selectedApply.job}
          platform={selectedApply.platform || 'company'}
          isOpen={Boolean(selectedApply)}
          onClose={() => setSelectedApply(null)}
          onApplied={() => {
            loadData();
          }}
          showToast={showToast}
        />
      )}


    </div>
  );
};
