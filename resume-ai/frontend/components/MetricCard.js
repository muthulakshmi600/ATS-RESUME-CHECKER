/**
 * MetricCard Component: KPI metric summary cards for Dashboard
 * ResumeAI ATS SaaS Theme
 */

window.MetricCard = ({ title, value, subtitle, icon: Icon, badge, color = "royal" }) => {
  const colorMap = {
    royal: "bg-blue-50 text-[#2563EB] border-blue-200",
    teal: "bg-teal-50 text-[#14B8A6] border-teal-200",
    navy: "bg-slate-100 text-[#14213D] border-slate-200",
    slate: "bg-slate-100 text-[#64748B] border-slate-200",
    emerald: "bg-emerald-50 text-[#16A34A] border-emerald-200",
    amber: "bg-amber-50 text-amber-600 border-amber-200",
    indigo: "bg-blue-50 text-[#2563EB] border-blue-200",
    purple: "bg-purple-50 text-purple-600 border-purple-200"
  };

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 hover:border-slate-300 transition shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-bold text-[#64748B] uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={`p-2.5 rounded-xl border ${colorMap[color] || colorMap.royal}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-extrabold tracking-tight text-[#14213D]">{value}</span>
        {badge && (
          <span className="text-[11px] font-bold text-[#16A34A] bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-md">
            {badge}
          </span>
        )}
      </div>
      {subtitle && (
        <p className="text-xs text-[#64748B] mt-2 truncate">{subtitle}</p>
      )}
    </div>
  );
};
