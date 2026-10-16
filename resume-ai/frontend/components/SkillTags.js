/**
 * SkillTags Component: Matched vs Missing skills and keywords tags
 * ResumeAI ATS SaaS Theme
 */

window.SkillTags = ({ matched = [], missing = [], title = "Skills", type = "skill" }) => {
  const { Check, AlertCircle } = window.Icons;
  const [filter, setFilter] = React.useState('all'); // all | matched | missing

  const safeMatched = Array.isArray(matched) ? matched : [];
  const safeMissing = Array.isArray(missing) ? missing : [];

  const displayMatched = filter === 'all' || filter === 'matched';
  const displayMissing = filter === 'all' || filter === 'missing';

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h4 className="text-sm font-bold text-[#14213D]">{title}</h4>
          <p className="text-xs text-[#64748B] mt-0.5">
            {safeMatched.length} detected in resume • {safeMissing.length} recommended to emphasize
          </p>
        </div>

        {/* Filter toggle */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs">
          <button
            onClick={() => setFilter('all')}
            className={`px-2.5 py-1 rounded-lg transition ${
              filter === 'all' ? 'bg-[#2563EB] text-white font-bold shadow-sm' : 'text-[#64748B] hover:text-[#1E293B]'
            }`}
          >
            All ({safeMatched.length + safeMissing.length})
          </button>
          <button
            onClick={() => setFilter('matched')}
            className={`px-2.5 py-1 rounded-lg transition ${
              filter === 'matched' ? 'bg-[#16A34A] text-white font-bold shadow-sm' : 'text-[#64748B] hover:text-[#1E293B]'
            }`}
          >
            Matched ({safeMatched.length})
          </button>
          <button
            onClick={() => setFilter('missing')}
            className={`px-2.5 py-1 rounded-lg transition ${
              filter === 'missing' ? 'bg-rose-600 text-white font-bold shadow-sm' : 'text-[#64748B] hover:text-[#1E293B]'
            }`}
          >
            Missing ({safeMissing.length})
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {displayMatched && safeMatched.map((item, idx) => (
          <span
            key={`m-${idx}`}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-50 text-[#16A34A] border border-emerald-200"
          >
            <Check className="w-3.5 h-3.5 text-[#16A34A]" />
            <span>{item}</span>
          </span>
        ))}

        {displayMissing && safeMissing.map((item, idx) => (
          <span
            key={`miss-${idx}`}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-rose-50 text-rose-600 border border-rose-200"
          >
            <span className="text-rose-500 font-bold">+</span>
            <span>{item}</span>
          </span>
        ))}

        {safeMatched.length === 0 && safeMissing.length === 0 && (
          <p className="text-xs text-[#64748B] italic py-2">No specific items detected.</p>
        )}
      </div>
    </div>
  );
};
