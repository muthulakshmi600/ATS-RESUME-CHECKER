/**
 * ApplyModal Component: Transparent Job Application & Platform Navigation Modal
 * ResumeAI ATS SaaS Theme
 * 
 * Supports 3 external application destinations:
 * 1. LinkedIn Jobs search or direct listing
 * 2. Naukri.com search or direct listing
 * 3. Official Employer Career Website
 * 
 * Clear explanations & user privacy guarantees:
 * - Directs user to the official job listing or search page.
 * - Application must be completed directly on the external platform.
 * - No application is automatically submitted by ResumeAI ATS.
 * - No private data or resume content is transmitted without explicit user action.
 * - Allows reviewing job title, company name, and destination before navigating.
 * - Opens external page with target="_blank" and rel="noopener noreferrer".
 */

window.ApplyModal = ({
  job,
  platform = 'company',
  isOpen,
  onClose,
  onApplied,
  showToast
}) => {
  if (!isOpen || !job) return null;

  const {
    ExternalLink, X, Building, MapPin, DollarSign,
    ShieldCheck, CheckCircle, AlertCircle, FileText,
    Linkedin, Naukri, Check, Info
  } = window.Icons || {};

  const SafeBuilding = Building || ExternalLink;
  const SafeLinkedin = Linkedin || ExternalLink;
  const SafeNaukri = Naukri || ExternalLink;
  const SafeInfo = Info || AlertCircle;

  const [notes, setNotes] = React.useState('');
  const [trackInDashboard, setTrackInDashboard] = React.useState(true);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  // Determine platform details & destination URL
  let targetUrl = '';
  let platformTitle = '';
  let platformBadge = '';
  let badgeColor = '';
  let iconBoxColor = '';
  let PlatformIcon = SafeBuilding;
  let proceedBtnText = '';
  let proceedBtnClass = '';
  let portalName = '';

  if (platform === 'linkedin') {
    targetUrl = job.linkedin_search_url || job.linkedin_url || (
      window.ResumeAIService?.getLinkedInSearchUrl
        ? window.ResumeAIService.getLinkedInSearchUrl(job)
        : 'https://www.linkedin.com/jobs/'
    );
    platformTitle = 'Find Role on LinkedIn Jobs';
    platformBadge = job.linkedin_is_direct ? 'Verified LinkedIn Listing' : 'LinkedIn Jobs Search Query';
    badgeColor = 'bg-[#0A66C2]/10 text-[#0A66C2] border-[#0A66C2]/20';
    iconBoxColor = 'bg-[#0A66C2]/10 text-[#0A66C2] border-[#0A66C2]/20';
    PlatformIcon = SafeLinkedin;
    portalName = 'Official LinkedIn Jobs Portal (https://www.linkedin.com/jobs/)';
    proceedBtnText = 'Proceed to LinkedIn Jobs';
    proceedBtnClass = 'bg-[#0A66C2] hover:bg-[#084e96] text-white shadow-md shadow-[#0A66C2]/20';
  } else if (platform === 'naukri') {
    targetUrl = job.naukri_search_url || job.naukri_url || (
      window.ResumeAIService?.getNaukriSearchUrl
        ? window.ResumeAIService.getNaukriSearchUrl(job)
        : 'https://www.naukri.com/'
    );
    platformTitle = 'Find Role on Naukri.com';
    platformBadge = job.naukri_is_direct ? 'Verified Naukri Listing' : 'Naukri.com Search Query';
    badgeColor = 'bg-[#1856B6]/10 text-[#1856B6] border-[#1856B6]/20';
    iconBoxColor = 'bg-[#1856B6]/10 text-[#1856B6] border-[#1856B6]/20';
    PlatformIcon = SafeNaukri;
    portalName = 'Official Naukri Portal (https://www.naukri.com/)';
    proceedBtnText = 'Proceed to Naukri.com';
    proceedBtnClass = 'bg-[#1856B6] hover:bg-[#12428c] text-white shadow-md shadow-[#1856B6]/20';
  } else {
    // Default: Company Website
    targetUrl = job.application_url || job.company_application_url || '';
    platformTitle = `Apply at ${job.company || 'Company Website'}`;
    platformBadge = 'Verified Employer Career Portal';
    badgeColor = 'bg-blue-50 text-[#2563EB] border-blue-200';
    iconBoxColor = 'bg-blue-50 text-[#2563EB] border-blue-200';
    PlatformIcon = SafeBuilding;
    portalName = job.portal_name || 'Official Company Career Portal';
    proceedBtnText = 'Proceed to Official Application Page';
    proceedBtnClass = 'bg-[#2563EB] hover:bg-[#1D4ED8] text-white shadow-md shadow-blue-500/20';
  }

  const hasValidUrl = Boolean(targetUrl && targetUrl.startsWith('http'));

  const handleProceed = async () => {
    if (!hasValidUrl) {
      if (showToast) showToast('Official application link is unavailable for this role.', 'error');
      return;
    }

    setIsSubmitting(true);

    try {
      if (trackInDashboard) {
        const statusVal = platform === 'company' ? 'Applied' : 'Saved';
        const defaultNote = `Navigated via ${platform === 'linkedin' ? 'LinkedIn Jobs' : (platform === 'naukri' ? 'Naukri.com' : 'Company Website')}`;
        await window.ResumeAIService.recordApplication({
          job_id: job.id,
          job_title: job.title || 'Software Developer',
          company: job.company || 'Direct Employer',
          application_url: targetUrl,
          status: statusVal,
          applied_date: new Date().toISOString().split('T')[0],
          notes: notes.trim() || defaultNote
        });
        if (onApplied) onApplied(job);
        if (showToast) showToast(`Added ${job.title} to your Application Tracker!`, 'success');
      }

      // Open external destination page in new tab with secure attributes
      window.open(targetUrl, '_blank', 'noopener,noreferrer');
      onClose();
    } catch (e) {
      console.error("Error proceeding to external destination:", e);
      window.open(targetUrl, '_blank', 'noopener,noreferrer');
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
      <div 
        className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-xl w-full p-6 sm:p-7 relative overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
          title="Close dialog"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3.5 mb-5">
          <div className={`w-12 h-12 rounded-2xl border flex items-center justify-center flex-shrink-0 ${iconBoxColor}`}>
            <PlatformIcon className="w-6 h-6" />
          </div>
          <div className="min-w-0 pr-8">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`text-[11px] font-extrabold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${badgeColor}`}>
                {platformBadge}
              </span>
              {job.is_verified ? (
                <span className="text-[10px] font-bold text-[#16A34A] bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" />
                  Verified Listing
                </span>
              ) : null}
            </div>
            <h3 className="text-xl font-extrabold text-[#14213D] mt-1 truncate">
              {job.title || 'Untitled Role'}
            </h3>
            <p className="text-xs font-semibold text-[#64748B] truncate">
              {job.company || 'Direct Employer'} • {job.location || 'Location Not Specified'}
            </p>
          </div>
        </div>

        {/* Review Job Specifics */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] mb-4 text-xs">
          <div>
            <span className="text-[#64748B] block text-[10px] font-bold uppercase">Role Type</span>
            <span className="font-bold text-[#1E293B]">{job.job_type || 'Full-Time'}</span>
          </div>
          <div>
            <span className="text-[#64748B] block text-[10px] font-bold uppercase">Experience Level</span>
            <span className="font-bold text-[#1E293B]">{job.experience_level || 'Fresher'}</span>
          </div>
          <div className="col-span-2 sm:col-span-1">
            <span className="text-[#64748B] block text-[10px] font-bold uppercase">Compensation</span>
            <span className="font-bold text-[#16A34A]">{job.salary || 'Competitive'}</span>
          </div>
        </div>

        {/* Destination Review Box */}
        <div className="space-y-3 mb-4">
          <div>
            <label className="text-xs font-bold text-[#14213D] block mb-1">
              External Destination URL Preview:
            </label>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2 truncate text-[#2563EB] font-mono text-[11px]">
                <ExternalLink className="w-4 h-4 flex-shrink-0 text-slate-400" />
                <span className="truncate">{targetUrl || 'Official platform link'}</span>
              </div>
              <span className="text-[10px] font-bold text-slate-600 bg-white border border-slate-200 px-2 py-0.5 rounded-md flex-shrink-0">
                New Tab
              </span>
            </div>
          </div>

          {/* Explicit Disclosure & Transparency Notice */}
          <div className="p-3.5 rounded-xl bg-emerald-50/70 border border-emerald-200 space-y-1.5 text-xs text-slate-700">
            <div className="flex items-center gap-1.5 font-bold text-[#14213D] text-[11px]">
              <ShieldCheck className="w-4 h-4 text-[#16A34A] flex-shrink-0" />
              <span>External Redirection & Privacy Guarantees</span>
            </div>
            <ul className="text-[11px] text-slate-600 space-y-1 pl-5 list-disc leading-relaxed">
              <li>
                <strong>Direct Redirection:</strong> ResumeAI ATS directs you to the official {platform === 'linkedin' ? 'LinkedIn Jobs' : (platform === 'naukri' ? 'Naukri.com' : 'employer career')} page.
              </li>
              <li>
                <strong>Manual Completion Required:</strong> You must review and complete your application directly on {platform === 'linkedin' ? 'LinkedIn' : (platform === 'naukri' ? 'Naukri' : 'the employer website')}.
              </li>
              <li>
                <strong>Zero Automatic Submissions:</strong> No application is ever submitted automatically by ResumeAI ATS.
              </li>
              <li>
                <strong>Privacy Guaranteed:</strong> ResumeAI ATS never shares your resume document, contact details, or private data with external platforms without explicit action.
              </li>
            </ul>
          </div>
        </div>

        {/* Application Tracker Integration Checkbox */}
        <div className="space-y-2 mb-5 pt-3 border-t border-slate-100">
          <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-[#1E293B]">
            <input
              type="checkbox"
              checked={trackInDashboard}
              onChange={(e) => setTrackInDashboard(e.target.checked)}
              className="w-4 h-4 rounded text-[#2563EB] focus:ring-[#2563EB] border-slate-300"
            />
            <span>Log this role in my Application Tracker dashboard</span>
          </label>

          {trackInDashboard && (
            <div>
              <input
                type="text"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add optional notes (e.g. Applied via referral, resume revision #2)..."
                className="w-full text-xs px-3.5 py-2 rounded-xl border border-slate-200 focus:outline-none focus:border-[#2563EB] bg-[#F8FAFC]"
                maxLength={150}
              />
            </div>
          )}
        </div>

        {/* Modal Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-100">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition"
          >
            Cancel
          </button>

          {hasValidUrl ? (
            <button
              type="button"
              onClick={handleProceed}
              disabled={isSubmitting}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-white font-bold text-xs transition ${proceedBtnClass}`}
            >
              <span>{isSubmitting ? 'Opening Portal...' : proceedBtnText}</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              type="button"
              disabled
              className="px-5 py-2.5 rounded-xl bg-slate-200 text-slate-400 font-bold text-xs cursor-not-allowed border border-slate-300"
            >
              Application Link Unavailable
            </button>
          )}
        </div>

      </div>
    </div>
  );
};
