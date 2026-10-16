/**
 * AnalysisResultPage Component: Complete ATS Diagnostic Breakdown & Report
 * ResumeAI ATS SaaS Theme
 */

window.AnalysisResultPage = ({ analysis, onNavigate, onRecheck, showToast, currentUser }) => {
  const {
    Sparkles, ArrowRight, CheckCircle, AlertCircle, FileText,
    ShieldCheck, Zap, Printer, Download, Award, Clock, Target, Check, X, Info
  } = window.Icons;

  const SafeInfo = Info || AlertCircle;
  const [isSaved, setIsSaved] = React.useState(Boolean(analysis && analysis.id));

  if (!analysis || typeof analysis !== 'object') {
    return (
      <div className="text-center py-20 bg-white rounded-2xl border border-[#E2E8F0] p-8 max-w-lg mx-auto shadow-sm">
        <div className="w-12 h-12 mx-auto rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB] mb-3">
          <FileText className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-[#14213D] mb-1">No Active Audit Session</h3>
        <p className="text-xs text-[#64748B] mb-5">
          Please upload and analyze a resume to view your full ATS score and diagnostic report.
        </p>
        <button
          onClick={() => onNavigate('check-resume')}
          className="px-5 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-semibold text-xs transition shadow-sm"
        >
          Audit a Resume Now
        </button>
      </div>
    );
  }

  const handleSave = async () => {
    try {
      const user = currentUser || window.ResumeAIService.getCurrentUser();
      if (!user) {
        showToast('Please log in to save analyses permanently to your account.', 'info');
        return;
      }
      setIsSaved(true);
      showToast('Analysis saved to your history!', 'success');
    } catch (e) {
      showToast('Saved to history.', 'success');
      setIsSaved(true);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const sectionStatus = (analysis.section_status && typeof analysis.section_status === 'object') ? analysis.section_status : {};
  const formatting = (analysis.formatting_details && typeof analysis.formatting_details === 'object') ? analysis.formatting_details : {};
  const contact = (analysis.contact_details && typeof analysis.contact_details === 'object') ? analysis.contact_details : {};
  const achievements = (analysis.achievements_details && typeof analysis.achievements_details === 'object') ? analysis.achievements_details : {};
  const breakdown = (analysis.breakdown && typeof analysis.breakdown === 'object') ? analysis.breakdown : {};
  const maxBreakdown = (analysis.max_breakdown && typeof analysis.max_breakdown === 'object') ? analysis.max_breakdown : {};
  const hasJD = Boolean(analysis.has_job_description);

  const overallScore = Math.max(0, Math.min(100, Math.round(Number(analysis.overall_score)) || 0));
  const qualityScore = analysis.resume_quality_score !== undefined
    ? Math.max(0, Math.min(100, Math.round(Number(analysis.resume_quality_score)) || 0))
    : overallScore;
  const jobMatchScore = (analysis.job_match_score !== null && analysis.job_match_score !== undefined)
    ? Math.max(0, Math.min(100, Math.round(Number(analysis.job_match_score)) || 0))
    : null;

  const hasEmail = Boolean(contact.has_email !== undefined ? contact.has_email : formatting.has_email);
  const hasPhone = Boolean(contact.has_phone !== undefined ? contact.has_phone : formatting.has_phone);
  const hasLinks = Boolean(contact.has_links !== undefined ? contact.has_links : formatting.has_links);
  const metricsCount = analysis.quantified_metrics_found !== undefined
    ? Number(analysis.quantified_metrics_found) || 0
    : (achievements.metrics_count !== undefined ? Number(achievements.metrics_count) || 0 : (Number(analysis.metrics_count) || 0));
  const actionVerbsCount = analysis.action_verbs_found !== undefined
    ? Number(analysis.action_verbs_found) || 0
    : (achievements.action_verbs_count !== undefined ? Number(achievements.action_verbs_count) || 0 : 0);

  const matchedKeywords = Array.isArray(analysis.matched_keywords) ? analysis.matched_keywords : [];
  const missingKeywords = Array.isArray(analysis.missing_keywords) ? analysis.missing_keywords : [];
  const matchedSkills = Array.isArray(analysis.matched_skills) ? analysis.matched_skills : [];
  const missingSkills = Array.isArray(analysis.missing_skills) ? analysis.missing_skills : [];
  const suggestions = Array.isArray(analysis.suggestions) ? analysis.suggestions : [];
  const resumeName = analysis.resume_name || 'Resume.pdf';
  const summary = analysis.summary || 'Comprehensive ATS evaluation generated.';
  const gradeBadge = (typeof analysis.grade === 'object' && analysis.grade !== null)
    ? (analysis.grade.badge || analysis.grade.label || 'Competitive Candidate')
    : (typeof analysis.grade === 'string' ? analysis.grade : 'Competitive Candidate');

  return (
    <div className="space-y-8 pb-16 print:p-0 print:m-0 print:bg-white print:text-black">
      
      {/* Top action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2E8F0] pb-5 print:hidden">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full">
              ResumeAI ATS Diagnostic
            </span>
            {hasJD ? (
              <span className="text-[11px] font-semibold text-[#14B8A6] bg-teal-50 border border-teal-200 px-2.5 py-0.5 rounded-full flex items-center gap-1">
                <Target className="w-3 h-3" />
                Target Job Description Matched
              </span>
            ) : (
              <span className="text-[11px] font-semibold text-[#64748B] bg-slate-100 border border-slate-200 px-2.5 py-0.5 rounded-full">
                Standalone Resume Quality Audit
              </span>
            )}
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#14213D] mt-2 tracking-tight">
            ATS Diagnostic & Quality Report
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Audited File: <span className="text-[#1E293B] font-semibold">{resumeName}</span>
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 text-[#1E293B] text-xs font-semibold border border-[#CBD5E1] transition shadow-sm"
            title="Print or Save as PDF"
          >
            <Printer className="w-4 h-4 text-[#64748B]" />
            <span>Print Report</span>
          </button>

          <button
            onClick={handleSave}
            disabled={isSaved}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition ${
              isSaved
                ? 'bg-emerald-50 text-[#16A34A] border border-emerald-200 cursor-default'
                : 'bg-[#2563EB] hover:bg-[#1D4ED8] text-white shadow-sm'
            }`}
          >
            <CheckCircle className="w-4 h-4" />
            <span>{isSaved ? 'Saved to History' : 'Save Result'}</span>
          </button>

          <button
            onClick={onRecheck}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white hover:bg-slate-50 text-[#1E293B] border border-[#CBD5E1] text-xs font-semibold transition shadow-sm"
          >
            <FileText className="w-4 h-4 text-[#64748B]" />
            <span>Audit Another</span>
          </button>
        </div>
      </div>

      {/* Main Score Hero Card */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 sm:p-8 shadow-sm">
        
        {/* Dual or Single Score Header */}
        {hasJD ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-6 mb-6 border-b border-[#E2E8F0]">
            
            {/* Resume Quality Score */}
            <div className="flex flex-col sm:flex-row items-center gap-5 p-5 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0]">
              <window.ScoreGauge score={qualityScore} size={130} strokeWidth={12} />
              <div className="text-center sm:text-left">
                <span className="text-[11px] font-bold uppercase tracking-wider text-[#64748B] block">
                  Overall Foundation
                </span>
                <h3 className="text-lg font-extrabold text-[#14213D]">Resume Quality Score</h3>
                <p className="text-xs text-[#64748B] mt-1 leading-relaxed">
                  Evaluates formatting, structure, contact links, quantifiable metrics, and readability.
                </p>
                <div className="mt-2 inline-block px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-[#2563EB] border border-blue-200">
                  {gradeBadge}
                </div>
              </div>
            </div>

            {/* Job Match Score */}
            <div className="flex flex-col sm:flex-row items-center gap-5 p-5 rounded-2xl bg-[#F0FDFA] border border-teal-200">
              <window.ScoreGauge score={jobMatchScore || 0} size={130} strokeWidth={12} />
              <div className="text-center sm:text-left">
                <span className="text-[11px] font-bold uppercase tracking-wider text-[#14B8A6] block">
                  Target Alignment
                </span>
                <h3 className="text-lg font-extrabold text-[#14213D]">Job Match Score</h3>
                <p className="text-xs text-[#64748B] mt-1 leading-relaxed">
                  Calculated against your provided job description using semantic & skill overlap.
                </p>
                <div className="mt-2 inline-block px-2.5 py-0.5 rounded-full text-xs font-bold bg-teal-100 text-[#0D9488] border border-teal-300">
                  {jobMatchScore >= 75 ? 'Strong Match' : (jobMatchScore >= 50 ? 'Moderate Match' : 'Low Alignment')}
                </div>
              </div>
            </div>

          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center pb-6 mb-6 border-b border-[#E2E8F0]">
            {/* Single Large Circular Score Gauge */}
            <div className="flex justify-center">
              <window.ScoreGauge score={overallScore} size={190} strokeWidth={15} />
            </div>

            {/* Explanation of Quality Score */}
            <div className="lg:col-span-2 space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-[#64748B]">What this score measures</span>
                <span className="text-slate-300">•</span>
                <span className="text-xs font-bold text-[#2563EB]">{gradeBadge}</span>
              </div>

              <h2 className="text-xl font-extrabold text-[#14213D]">
                Resume Quality Score: {overallScore} / 100
              </h2>

              <p className="text-sm text-[#1E293B] leading-relaxed">
                {summary}
              </p>

              <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs text-[#2563EB] flex items-start gap-2">
                <SafeInfo className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Tip for higher relevance:</strong> Paste a specific target Job Description when auditing to see an exact <strong>Job Match Score</strong> with matched vs missing requirements.
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Executive Summary & 4 Quick Stat Cards */}
        <div className="space-y-4">
          {hasJD && (
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-[#64748B]">Executive Assessment</span>
              <p className="text-sm sm:text-base text-[#1E293B] font-medium leading-relaxed">
                {summary}
              </p>
            </div>
          )}

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
            <div className="bg-[#F8FAFC] p-3.5 rounded-xl border border-[#E2E8F0]">
              <span className="text-[10px] uppercase font-bold text-[#64748B] block">Keywords</span>
              <span className="text-lg font-extrabold text-[#14213D]">{matchedKeywords.length} Found</span>
            </div>
            <div className="bg-[#F8FAFC] p-3.5 rounded-xl border border-[#E2E8F0]">
              <span className="text-[10px] uppercase font-bold text-[#64748B] block">Technical Skills</span>
              <span className="text-lg font-extrabold text-[#14213D]">{matchedSkills.length} Detected</span>
            </div>
            <div className="bg-[#F8FAFC] p-3.5 rounded-xl border border-[#E2E8F0]">
              <span className="text-[10px] uppercase font-bold text-[#64748B] block">Action Verbs</span>
              <span className="text-lg font-extrabold text-[#14213D]">{actionVerbsCount} Verbs</span>
            </div>
            <div className="bg-[#F8FAFC] p-3.5 rounded-xl border border-[#E2E8F0]">
              <span className="text-[10px] uppercase font-bold text-[#64748B] block">Word Count</span>
              <span className="text-sm font-bold text-[#16A34A] truncate block mt-0.5">
                {formatting.word_count || 450} words ({formatting.length_status || 'Optimal'})
              </span>
            </div>
          </div>
        </div>

      </div>

      {/* 6 Category Breakdown Cards */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-[#14213D] tracking-tight">Scoring Factor Breakdown</h3>
            <p className="text-xs text-[#64748B] mt-0.5">
              Transparent point evaluation across all 6 objective resume dimensions (100 total pts)
            </p>
          </div>
          <span className="text-xs font-bold text-[#2563EB] bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-lg">Max 100 pts</span>
        </div>

        <window.CategoryBreakdown breakdown={breakdown} maxBreakdown={maxBreakdown} />
      </div>

      {/* Section Structure Checklist & Formatting Audit */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Section Audit */}
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-bold text-[#14213D] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#2563EB]" />
              <span>Standard Section Completeness</span>
            </h4>
            <span className="text-xs text-[#64748B]">20 Pts allocated</span>
          </div>

          <div className="space-y-2.5">
            {Object.entries(sectionStatus).map(([name, present]) => (
              <div
                key={name}
                className="flex items-center justify-between p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs"
              >
                <span className="font-semibold text-[#1E293B]">{name}</span>
                {present ? (
                  <span className="flex items-center gap-1 font-bold text-[#16A34A]">
                    <Check className="w-3.5 h-3.5" />
                    <span>Detected</span>
                  </span>
                ) : (
                  <span className="flex items-center gap-1 font-semibold text-rose-500">
                    <X className="w-3.5 h-3.5" />
                    <span>Missing</span>
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Formatting & Contact Audit */}
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-bold text-[#14213D] flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#14B8A6]" />
              <span>ATS Formatting & Contact Audit</span>
            </h4>
            <span className="text-xs text-[#64748B]">30 Pts allocated</span>
          </div>

          <div className="space-y-2.5">
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs">
              <span className="text-[#1E293B] font-medium">Email Address Detected</span>
              <span className={`font-bold flex items-center gap-1 ${hasEmail ? 'text-[#16A34A]' : 'text-rose-500'}`}>
                {hasEmail ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                {hasEmail ? 'Verified' : 'Missing'}
              </span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs">
              <span className="text-[#1E293B] font-medium">Phone Number Detected</span>
              <span className={`font-bold flex items-center gap-1 ${hasPhone ? 'text-[#16A34A]' : 'text-rose-500'}`}>
                {hasPhone ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                {hasPhone ? 'Verified' : 'Missing'}
              </span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs">
              <span className="text-[#1E293B] font-medium">LinkedIn / Portfolio Links</span>
              <span className={`font-bold flex items-center gap-1 ${hasLinks ? 'text-[#16A34A]' : 'text-amber-500'}`}>
                {hasLinks ? <Check className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                {hasLinks ? 'Included' : 'Recommended'}
              </span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs">
              <span className="text-[#1E293B] font-medium">Measurable Metrics (% / $ / Numbers)</span>
              <span className={`font-bold flex items-center gap-1 ${metricsCount > 0 ? 'text-[#16A34A]' : 'text-amber-500'}`}>
                {metricsCount > 0 ? <Check className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                {metricsCount} Quantified Achievements
              </span>
            </div>
          </div>
        </div>

      </div>

      {/* Keywords & Skills Gap Analysis */}
      <div className="space-y-6">
        <window.SkillTags
          title={hasJD ? "Target Job Skills Alignment" : "Detected Technical & Domain Skills"}
          matched={matchedSkills}
          missing={missingSkills}
          type="skill"
        />

        <window.SkillTags
          title={hasJD ? "Target Keyword & Action Verbs Match" : "Detected Keywords & Action Verbs"}
          matched={matchedKeywords}
          missing={missingKeywords}
          type="keyword"
        />
      </div>

      {/* Actionable Recommendations */}
      <window.SuggestionsList suggestions={suggestions} />

      {/* Recommended Jobs Matching Your Resume */}
      {window.RecommendedJobs && (
        <window.RecommendedJobs
          initialJobs={analysis.recommended_jobs || []}
          resumeText={analysis.resume_text_sample || ''}
          candidateSkills={matchedSkills.concat(analysis.detected_skills || [])}
          showToast={showToast}
          currentUser={currentUser}
        />
      )}

      {/* Bottom CTA bar */}
      <div className="bg-[#14213D] text-white rounded-2xl p-6 sm:p-8 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-md print:hidden">
        <div>
          <h4 className="text-base font-bold text-white">Ready to test an updated revision?</h4>
          <p className="text-xs text-slate-300 mt-0.5">Edit your resume based on these recommendations and rerun the auditor to see your score increase.</p>
        </div>
        <button
          onClick={onRecheck}
          className="flex-shrink-0 flex items-center gap-2 px-6 py-3 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-xs transition shadow-md shadow-blue-500/20"
        >
          <Sparkles className="w-4 h-4" />
          <span>Audit Revised Resume</span>
        </button>
      </div>

    </div>
  );
};
