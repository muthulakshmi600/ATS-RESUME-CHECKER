/**
 * DashboardPage Component: Central analytics & recent scans dashboard
 * ResumeAI ATS SaaS Theme
 */

window.DashboardPage = ({ onNavigate, currentUser, onViewAnalysis }) => {
  const {
    Sparkles, ArrowRight, FileText, BarChart, Award, Clock,
    TrendingUp, Eye, CheckCircle, AlertCircle, Target
  } = window.Icons;

  const [stats, setStats] = React.useState({
    total_checked: 0,
    avg_score: 0,
    best_score: 0,
    last_analysis: null
  });
  const [recentAnalyses, setRecentAnalyses] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [statsData, historyData] = await Promise.all([
        window.ResumeAIService.getStats(),
        window.ResumeAIService.getHistory()
      ]);
      setStats(statsData);
      setRecentAnalyses(historyData.slice(0, 5));
    } catch (e) {
      console.warn("Failed loading dashboard data:", e);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Never';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch (e) {
      return dateStr;
    }
  };

  const getScoreBadge = (score) => {
    if (score >= 80) return { bg: 'bg-emerald-50 text-[#16A34A] border-emerald-200', text: 'High Quality' };
    if (score >= 60) return { bg: 'bg-amber-50 text-amber-700 border-amber-200', text: 'Fair Quality' };
    return { bg: 'bg-rose-50 text-rose-600 border-rose-200', text: 'Needs Work' };
  };

  const hasHistory = recentAnalyses.length > 0;
  const displayTotal = hasHistory ? stats.total_checked : "0";
  const displayAvg = hasHistory ? (stats.avg_score ? `${stats.avg_score}%` : '0%') : "—";
  const displayBest = hasHistory ? (stats.best_score ? `${stats.best_score}/100` : '0/100') : "—";
  const displayLast = hasHistory ? formatDate(stats.last_analysis) : "None yet";

  return (
    <div className="space-y-8 pb-12">
      
      {/* Top Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-[#14213D] text-white p-6 sm:p-8 shadow-sm">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-[#2563EB]/20 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/20 text-[#14B8A6] text-xs font-semibold uppercase tracking-wider mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>ResumeAI ATS Overview</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Welcome, {currentUser ? currentUser.name : 'Candidate'}!
            </h1>
            <p className="text-sm text-slate-300 mt-1 max-w-xl">
              Audit your resume structure, metrics, formatting, and match against target job descriptions with instant, deterministic scoring.
            </p>
          </div>

          <button
            onClick={() => onNavigate('check-resume')}
            className="flex-shrink-0 flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-sm shadow-md shadow-blue-600/30 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <FileText className="w-4 h-4" />
            <span>Audit a Resume</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
        <window.MetricCard
          title="Resumes Audited"
          value={displayTotal}
          subtitle="Total document scans"
          icon={FileText}
          color="royal"
        />
        <window.MetricCard
          title="Average Quality"
          value={displayAvg}
          subtitle="Mean score across resumes"
          icon={BarChart}
          color="teal"
        />
        <window.MetricCard
          title="Top Resume Score"
          value={displayBest}
          subtitle="Highest scored candidate file"
          icon={Award}
          color="navy"
        />
        <window.MetricCard
          title="Last Audit"
          value={displayLast}
          subtitle="Most recent evaluation"
          icon={Clock}
          color="slate"
        />
      </div>

      {/* Recent Analysis Section */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-lg font-bold text-[#14213D] tracking-tight">Recent Resume Audits</h3>
            <p className="text-xs text-[#64748B] mt-0.5">
              Review recent score cards or re-inspect detailed breakdown reports
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigate('history')}
              className="text-xs font-semibold text-[#2563EB] hover:text-[#1D4ED8] transition flex items-center gap-1"
            >
              <span>View All History</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {hasHistory ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-[#1E293B]">
              <thead className="text-xs uppercase bg-[#F8FAFC] text-[#64748B] border-y border-[#E2E8F0]">
                <tr>
                  <th scope="col" className="px-5 py-3.5 rounded-l-lg">Resume Document</th>
                  <th scope="col" className="px-5 py-3.5">Analysis Mode</th>
                  <th scope="col" className="px-5 py-3.5">Quality Score</th>
                  <th scope="col" className="px-5 py-3.5">Date</th>
                  <th scope="col" className="px-5 py-3.5 text-right rounded-r-lg">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2E8F0]">
                {recentAnalyses.map((item) => {
                  const badge = getScoreBadge(item.overall_score);
                  return (
                    <tr key={item.id} className="hover:bg-slate-50 transition">
                      <td className="px-5 py-4 font-semibold text-[#14213D] flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB] flex-shrink-0">
                          <FileText className="w-4 h-4" />
                        </div>
                        <span className="truncate max-w-xs">{item.resume_name}</span>
                      </td>
                      <td className="px-5 py-4 text-xs">
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
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-2">
                          <span className="text-base font-extrabold text-[#14213D]">{item.overall_score}</span>
                          <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${badge.bg}`}>
                            {badge.text}
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-4 text-xs text-[#64748B]">
                        {formatDate(item.created_at)}
                      </td>
                      <td className="px-5 py-4 text-right">
                        <button
                          onClick={() => onViewAnalysis(item)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-[#2563EB] text-[#2563EB] hover:text-white border border-blue-200 text-xs font-semibold transition"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Report</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          /* Empty / Initial State with Sample Cards */
          <div>
            <div className="text-center py-10 px-4 bg-[#F8FAFC] rounded-2xl border border-[#E2E8F0] mb-6">
              <div className="w-12 h-12 mx-auto rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB] mb-3">
                <FileText className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-[#14213D] mb-1">No resumes audited yet</h4>
              <p className="text-xs text-[#64748B] max-w-md mx-auto mb-4">
                Upload your resume in PDF or DOCX format to receive your detailed ATS score, category breakdown, and actionable recommendations.
              </p>
              <button
                onClick={() => onNavigate('check-resume')}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold transition shadow-sm"
              >
                <span>Audit Resume Now</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-between text-xs text-[#64748B]">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#2563EB]" />
                <span><strong className="text-[#14213D]">Fast Testing:</strong> Click "Audit Resume Now" and use the one-click demo button to load a sample resume!</span>
              </div>
              <button
                onClick={() => onNavigate('check-resume')}
                className="text-[#2563EB] hover:underline font-bold"
              >
                Go to Auditor →
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Job Search Banner */}
      <div className="bg-gradient-to-r from-[#14213D] to-[#1F3158] text-white rounded-2xl p-6 sm:p-7 flex flex-col sm:flex-row sm:items-center justify-between gap-5 shadow-sm">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-teal-500/20 text-[#14B8A6] text-[11px] font-bold uppercase tracking-wider">
            <Zap className="w-3.5 h-3.5" />
            <span>Job Opportunities</span>
          </div>
          <h3 className="text-lg font-bold text-white">Discover Matching Fresher & Entry-Level Roles</h3>
          <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
            Compare your resume against verified roles at Zoho, Microsoft, Cisco, Amazon, Fractal, and more. Apply directly through official portals.
          </p>
        </div>

        <button
          onClick={() => onNavigate('jobs')}
          className="flex-shrink-0 flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-xs transition shadow-md shadow-blue-500/20"
        >
          <span>Explore Job Matches</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

    </div>
  );
};
