/**
 * HistoryPage Component: Resume Analysis History & Management
 * ResumeAI ATS SaaS Theme
 */

window.HistoryPage = ({ onNavigate, onViewAnalysis, showToast }) => {
  const {
    History, Search, Eye, Trash2, FileText, ArrowRight,
    Sparkles, AlertCircle, CheckCircle, Target
  } = window.Icons;

  const [historyList, setHistoryList] = React.useState([]);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [filterMode, setFilterMode] = React.useState('All'); // 'All' | 'JD' | 'Standalone'
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const data = await window.ResumeAIService.getHistory();
      setHistoryList(data);
    } catch (e) {
      console.warn("Failed loading history:", e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id, name, e) => {
    e.stopPropagation();
    if (!window.confirm(`Are you sure you want to delete the audit report for "${name}"?`)) {
      return;
    }
    try {
      await window.ResumeAIService.deleteAnalysis(id);
      setHistoryList(prev => prev.filter(item => String(item.id) !== String(id)));
      showToast('Analysis record deleted.', 'info');
    } catch (err) {
      showToast('Failed to delete item.', 'error');
    }
  };

  const handleDeleteAll = async () => {
    if (!historyList.length) return;
    const confirmed = window.confirm(`Are you sure you want to delete ALL (${historyList.length}) resume analysis records? This cannot be undone.`);
    if (!confirmed) return;

    setIsLoading(true);
    try {
      await window.ResumeAIService.deleteAllHistory();
      setHistoryList([]);
      showToast('All resume analysis history deleted successfully!', 'success');
    } catch (err) {
      showToast('Failed to delete all history records.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreBadge = (score) => {
    if (score >= 80) return { bg: 'bg-emerald-50 text-[#16A34A] border-emerald-200', text: 'High Quality' };
    if (score >= 60) return { bg: 'bg-amber-50 text-amber-700 border-amber-200', text: 'Fair Quality' };
    return { bg: 'bg-rose-50 text-rose-600 border-rose-200', text: 'Needs Work' };
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Recent';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return dateStr;
    }
  };

  const filteredHistory = historyList.filter(item => {
    const matchesSearch = (item.resume_name || '').toLowerCase().includes(searchTerm.toLowerCase());
    let matchesMode = true;
    if (filterMode === 'JD') matchesMode = Boolean(item.has_job_description);
    if (filterMode === 'Standalone') matchesMode = !item.has_job_description;
    return matchesSearch && matchesMode;
  });

  return (
    <div className="space-y-6 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2E8F0] pb-5">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#14213D] tracking-tight flex items-center gap-3">
            <History className="w-7 h-7 text-[#2563EB]" />
            <span>Resume Analysis History</span>
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Access previous diagnostic reports, review scores, and track your resume quality improvement.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          {historyList.length > 0 && (
            <button
              onClick={handleDeleteAll}
              disabled={isLoading}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-rose-50 hover:bg-rose-600 text-rose-600 hover:text-white border border-rose-200 font-semibold text-xs transition-all shadow-sm active:scale-95 disabled:opacity-50"
              title="Delete all scan history records"
            >
              <Trash2 className="w-4 h-4" />
              <span>Delete All ({historyList.length})</span>
            </button>
          )}

          <button
            onClick={() => onNavigate('check-resume')}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-xs transition shadow-sm active:scale-95"
          >
            <Sparkles className="w-4 h-4" />
            <span>New Resume Audit</span>
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
        
        {/* Search Input */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-[#64748B] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by resume filename..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] placeholder-slate-400 text-xs focus:outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition"
          />
        </div>

        {/* Mode Filter */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-xs text-[#64748B] font-medium whitespace-nowrap">Filter Audit Mode:</span>
          <select
            value={filterMode}
            onChange={(e) => setFilterMode(e.target.value)}
            className="w-full sm:w-auto px-3 py-2 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[#1E293B] text-xs focus:outline-none focus:border-[#2563EB] transition"
          >
            <option value="All">All Audits</option>
            <option value="JD">Target Job Description Matched</option>
            <option value="Standalone">Standalone Quality Only</option>
          </select>
        </div>

      </div>

      {/* History Table */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl overflow-hidden shadow-sm">
        {filteredHistory.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-[#1E293B]">
              <thead className="text-xs uppercase bg-[#F8FAFC] text-[#64748B] border-b border-[#E2E8F0]">
                <tr>
                  <th scope="col" className="px-6 py-4">Resume Document</th>
                  <th scope="col" className="px-6 py-4">Audit Mode</th>
                  <th scope="col" className="px-6 py-4">Quality Score</th>
                  <th scope="col" className="px-6 py-4">Scan Date</th>
                  <th scope="col" className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2E8F0]">
                {filteredHistory.map((item) => {
                  const badge = getScoreBadge(item.overall_score);
                  return (
                    <tr
                      key={item.id}
                      onClick={() => onViewAnalysis(item)}
                      className="hover:bg-slate-50 cursor-pointer transition"
                    >
                      <td className="px-6 py-4 font-semibold text-[#14213D] flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB] flex-shrink-0">
                          <FileText className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="truncate max-w-xs">{item.resume_name}</p>
                          <span className="text-[11px] text-[#64748B]">
                            {item.has_job_description ? 'JD alignment verified' : 'Standalone quality audit'}
                          </span>
                        </div>
                      </td>

                      <td className="px-6 py-4 text-xs">
                        {item.has_job_description ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-teal-50 text-[#0D9488] border border-teal-200 font-semibold">
                            <Target className="w-3 h-3" />
                            <span>JD Matched ({item.job_match_score || 0}%)</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-[#64748B] border border-slate-200 font-semibold">
                            <span>Standalone Quality</span>
                          </span>
                        )}
                      </td>

                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className="text-base font-extrabold text-[#14213D]">{item.overall_score}</span>
                          <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${badge.bg}`}>
                            {badge.text}
                          </span>
                        </div>
                      </td>

                      <td className="px-6 py-4 text-xs text-[#64748B]">
                        {formatDate(item.created_at)}
                      </td>

                      <td className="px-6 py-4 text-right">
                        <div className="inline-flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => onViewAnalysis(item)}
                            className="p-2 rounded-lg bg-blue-50 hover:bg-[#2563EB] text-[#2563EB] hover:text-white border border-blue-200 text-xs font-semibold transition shadow-sm"
                            title="View Full Report"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={(e) => handleDelete(item.id, item.resume_name, e)}
                            className="p-2 rounded-lg bg-rose-50 hover:bg-rose-600 text-rose-600 hover:text-white border border-rose-200 text-xs font-semibold transition shadow-sm"
                            title="Delete Record"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-16 px-4">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB] mb-3">
              <History className="w-7 h-7" />
            </div>
            <h4 className="text-base font-bold text-[#14213D] mb-1">No analysis records match</h4>
            <p className="text-xs text-[#64748B] max-w-sm mx-auto mb-6">
              {searchTerm || filterMode !== 'All'
                ? 'Try adjusting your search query or filter parameters.'
                : 'Upload and audit a resume to begin building your progress history.'}
            </p>
            <button
              onClick={() => onNavigate('check-resume')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold transition shadow-sm"
            >
              <span>Audit a Resume Now</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>

    </div>
  );
};
