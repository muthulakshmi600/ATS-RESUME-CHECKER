/**
 * JobCard Component: High-impact job recommendation & match card
 * ResumeAI ATS SaaS Theme
 */

window.JobCard = ({
  job,
  threshold = 75,
  isSaved = false,
  onSaveToggle,
  onApplyClick,
  showMatchDetails = true
}) => {
  const {
    Building, MapPin, DollarSign, Bookmark, ExternalLink,
    CheckCircle, ShieldCheck, Zap, AlertCircle, Check,
    Linkedin, Naukri
  } = window.Icons || {};

  const SafeBuilding = Building || ExternalLink;
  const SafeLinkedin = Linkedin || ExternalLink;
  const SafeNaukri = Naukri || ExternalLink;

  const matchPct = Math.max(0, Math.min(100, Math.round(Number(job.job_match_percentage) || 0)));
  const isGoodMatch = matchPct >= threshold;
  const hasUrl = Boolean(job.application_url && job.application_url.startsWith('http'));

  const matchedSkills = Array.isArray(job.matched_skills) ? job.matched_skills : [];
  const missingSkills = Array.isArray(job.missing_skills) ? job.missing_skills : [];
  const requiredSkills = Array.isArray(job.required_skills) ? job.required_skills : [];

  // Match badge styling
  let badgeColor = "bg-rose-50 text-rose-600 border-rose-200";
  let gaugeStroke = "#DC2626";
  if (matchPct >= 75) {
    badgeColor = "bg-emerald-50 text-[#16A34A] border-emerald-200";
    gaugeStroke = "#16A34A";
  } else if (matchPct >= 50) {
    badgeColor = "bg-blue-50 text-[#2563EB] border-blue-200";
    gaugeStroke = "#2563EB";
  } else if (matchPct >= 35) {
    badgeColor = "bg-amber-50 text-amber-700 border-amber-200";
    gaugeStroke = "#D97706";
  }

  const remoteLabel = job.is_remote === 1 ? 'Remote' : (job.is_remote === 2 ? 'Hybrid' : 'On-Site');
  const remoteColor = job.is_remote === 1 ? 'bg-purple-50 text-purple-700 border-purple-200' : (job.is_remote === 2 ? 'bg-teal-50 text-[#14B8A6] border-teal-200' : 'bg-slate-100 text-slate-600 border-slate-200');

  return (
    <div className={`bg-white border rounded-2xl p-5 sm:p-6 transition shadow-sm hover:shadow-md ${
      isGoodMatch ? 'border-emerald-200 ring-1 ring-emerald-500/10' : 'border-[#E2E8F0] hover:border-slate-300'
    }`}>
      
      {/* Top Header: Title, Company, Match Gauge & Save */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        
        {/* Left: Role info */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            {isGoodMatch && (
              <span className="inline-flex items-center gap-1 text-[11px] font-extrabold uppercase px-2.5 py-0.5 rounded-full bg-emerald-100 text-[#16A34A] border border-emerald-300">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Good Match ({threshold}%+ Threshold)</span>
              </span>
            )}
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${remoteColor}`}>
              {remoteLabel}
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
              {job.job_type || 'Full-Time'}
            </span>
          </div>

          <h3 className="text-lg font-extrabold text-[#14213D] tracking-tight">
            {job.title}
          </h3>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1 text-xs text-[#64748B]">
            <span className="font-semibold text-[#1E293B] flex items-center gap-1">
              <Building className="w-3.5 h-3.5 text-slate-400" />
              {job.company}
            </span>
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              {job.location}
            </span>
            {job.salary && (
              <span className="font-bold text-[#16A34A] flex items-center gap-0.5">
                <DollarSign className="w-3.5 h-3.5" />
                {job.salary}
              </span>
            )}
          </div>
        </div>

        {/* Right: Job Match Score & Bookmark */}
        <div className="flex items-center sm:items-end sm:flex-col justify-between sm:justify-start gap-3">
          {showMatchDetails && (
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#64748B] block">
                  Job Match
                </span>
                <span className="text-xs font-semibold text-[#1E293B]">
                  {matchPct >= 75 ? 'Strong Fit' : (matchPct >= 50 ? 'Moderate Fit' : 'Low Match')}
                </span>
              </div>
              <div className={`px-3 py-1.5 rounded-xl border flex items-center gap-1.5 font-extrabold text-base ${badgeColor}`}>
                <Zap className="w-4 h-4 flex-shrink-0" />
                <span>{matchPct}%</span>
              </div>
            </div>
          )}

          <button
            onClick={() => onSaveToggle && onSaveToggle(job)}
            className={`p-2 rounded-xl border transition ${
              isSaved
                ? 'bg-rose-50 text-rose-600 border-rose-200'
                : 'bg-white text-slate-400 hover:text-slate-700 hover:bg-slate-50 border-slate-200'
            }`}
            title={isSaved ? "Remove from saved jobs" : "Save job"}
          >
            <Bookmark className="w-4 h-4" filled={isSaved} />
          </button>
        </div>

      </div>

      {/* Match Explanation Box */}
      {showMatchDetails && job.match_explanation && (
        <div className="mt-4 p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs">
          <div className="flex items-start gap-2 text-[#1E293B]">
            <Zap className="w-3.5 h-3.5 text-amber-500 flex-shrink-0 mt-0.5" />
            <span className="leading-relaxed font-medium">
              <strong className="text-[#14213D]">Why this matches:</strong> {job.match_explanation}
            </span>
          </div>
        </div>
      )}

      {/* Skills Comparison */}
      <div className="mt-4 space-y-2.5 text-xs">
        {matchedSkills.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-bold text-[#16A34A] mr-1 flex items-center gap-1">
              <Check className="w-3 h-3" /> Matched ({matchedSkills.length}):
            </span>
            {matchedSkills.map((sk, idx) => (
              <span
                key={`m-${idx}`}
                className="px-2.5 py-0.5 rounded-lg text-[11px] font-semibold bg-emerald-50 text-[#16A34A] border border-emerald-200"
              >
                {sk}
              </span>
            ))}
          </div>
        )}

        {missingSkills.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-bold text-rose-500 mr-1 flex items-center gap-1">
              <span className="font-bold">+</span> Missing ({missingSkills.length}):
            </span>
            {missingSkills.slice(0, 5).map((sk, idx) => (
              <span
                key={`miss-${idx}`}
                className="px-2.5 py-0.5 rounded-lg text-[11px] font-semibold bg-rose-50/70 text-rose-600 border border-rose-200"
              >
                {sk}
              </span>
            ))}
            {missingSkills.length > 5 && (
              <span className="text-[10px] text-[#64748B]">+{missingSkills.length - 5} more</span>
            )}
          </div>
        )}

        {/* If no resume comparison active, show required skills */}
        {!showMatchDetails && requiredSkills.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-bold text-[#64748B] mr-1">Required Skills:</span>
            {requiredSkills.map((sk, idx) => (
              <span
                key={`req-${idx}`}
                className="px-2 py-0.5 rounded-lg text-[11px] font-semibold bg-slate-100 text-[#1E293B] border border-slate-200"
              >
                {sk}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Card Footer: Portal info & 3-Button Navigation Action Group */}
      <div className="mt-5 pt-4 border-t border-[#E2E8F0] flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        <div className="text-[11px] text-[#64748B]">
          Official Portal: <span className="font-semibold text-[#1E293B]">{job.portal_name || 'Verified Career Portal'}</span>
          {job.posted_date && <span className="text-slate-400"> • Posted {job.posted_date}</span>}
        </div>

        {/* 3 Application & Search Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          {/* 1. LinkedIn */}
          <button
            type="button"
            onClick={() => onApplyClick && onApplyClick(job, 'linkedin')}
            className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-[#0A66C2] hover:bg-[#084e96] text-white font-bold text-xs transition shadow-sm active:scale-95"
            title="Search or apply for this role on LinkedIn Jobs"
          >
            <SafeLinkedin className="w-3.5 h-3.5 fill-current" />
            <span>Find on LinkedIn</span>
          </button>

          {/* 2. Naukri */}
          <button
            type="button"
            onClick={() => onApplyClick && onApplyClick(job, 'naukri')}
            className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-[#1856B6] hover:bg-[#12428c] text-white font-bold text-xs transition shadow-sm active:scale-95"
            title="Search or apply for this role on Naukri.com"
          >
            <SafeNaukri className="w-3.5 h-3.5" />
            <span>Find on Naukri</span>
          </button>

          {/* 3. Company Website */}
          {hasUrl ? (
            <button
              type="button"
              onClick={() => onApplyClick && onApplyClick(job, 'company')}
              className="inline-flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-xs transition shadow-sm active:scale-95"
              title="Apply directly on the employer's official career website"
            >
              <SafeBuilding className="w-3.5 h-3.5" />
              <span>Apply on Company Website</span>
              <ExternalLink className="w-3 h-3 text-blue-200" />
            </button>
          ) : (
            <button
              type="button"
              disabled
              className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-slate-100 text-slate-400 text-xs font-semibold cursor-not-allowed border border-slate-200"
              title="Official company application link is currently unavailable"
            >
              <SafeBuilding className="w-3.5 h-3.5 text-slate-300" />
              <span>Application link unavailable</span>
            </button>
          )}
        </div>
      </div>

    </div>
  );
};
