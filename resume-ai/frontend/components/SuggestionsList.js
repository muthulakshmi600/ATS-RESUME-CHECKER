/**
 * SuggestionsList Component: Prioritized actionable resume recommendations
 * ResumeAI ATS SaaS Theme
 */

window.SuggestionsList = ({ suggestions = [] }) => {
  const { AlertCircle, Zap, ShieldCheck } = window.Icons;
  const safeSuggestions = Array.isArray(suggestions) ? suggestions : [];

  const priorityStyles = {
    High: "bg-rose-50 text-rose-600 border-rose-200",
    Medium: "bg-amber-50 text-amber-700 border-amber-200",
    Low: "bg-blue-50 text-[#2563EB] border-blue-200"
  };

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-base font-bold text-[#14213D] flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            <span>Actionable ATS Improvements</span>
          </h3>
          <p className="text-xs text-[#64748B] mt-0.5">
            Prioritized recommendations to boost your match rate and clear applicant filters
          </p>
        </div>
        <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-blue-50 text-[#2563EB] border border-blue-200">
          {safeSuggestions.length} Recommendations
        </span>
      </div>

      <div className="space-y-3.5">
        {safeSuggestions.map((sug, idx) => (
          <div
            key={idx}
            className="flex items-start gap-3.5 p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] hover:border-slate-300 transition"
          >
            <div className="mt-0.5 flex-shrink-0">
              <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${priorityStyles[sug.priority] || priorityStyles.Medium}`}>
                {sug.priority || 'Medium'} Priority
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold text-[#14213D]">
                  {sug.category || 'General'}
                </span>
              </div>
              <p className="text-sm text-[#1E293B] leading-relaxed">
                {sug.text || sug.suggestion || ''}
              </p>
            </div>
          </div>
        ))}

        {safeSuggestions.length === 0 && (
          <div className="text-center py-6 text-[#64748B] text-sm">
            <ShieldCheck className="w-8 h-8 mx-auto text-[#16A34A] mb-2" />
            <p>Your resume satisfies all primary ATS guidelines! No critical flaws detected.</p>
          </div>
        )}
      </div>
    </div>
  );
};
