/**
 * ScoreGauge Component: Circular animated gauge for ATS Score (0 - 100)
 * ResumeAI ATS SaaS Theme
 */

window.ScoreGauge = ({ score = 0, size = 180, strokeWidth = 14 }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const validScore = Math.max(0, Math.min(100, Number(score) || 0));
  const strokeDashoffset = circumference - (validScore / 100) * circumference;

  let strokeColor = "#16A34A";
  let badgeText = "Exceptional ATS Fit";
  let badgeClass = "bg-emerald-50 text-[#16A34A] border-emerald-200";

  if (validScore < 50) {
    strokeColor = "#DC2626";
    badgeText = "Needs Revision";
    badgeClass = "bg-rose-50 text-rose-600 border-rose-200";
  } else if (validScore < 70) {
    strokeColor = "#D97706";
    badgeText = "Moderate Quality";
    badgeClass = "bg-amber-50 text-amber-700 border-amber-200";
  } else if (validScore < 85) {
    strokeColor = "#2563EB";
    badgeText = "Competitive Quality";
    badgeClass = "bg-blue-50 text-[#2563EB] border-blue-200";
  }

  return (
    <div className="relative flex flex-col items-center justify-center p-4 rounded-2xl bg-white border border-[#E2E8F0] shadow-sm">
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="transform -rotate-90" width={size} height={size}>
          {/* Background track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#E2E8F0"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Active progress stroke */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
            fill="transparent"
          />
        </svg>

        {/* Center score readout */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-4xl font-extrabold tracking-tight text-[#14213D]">{validScore}</span>
          <span className="text-[10px] font-bold text-[#64748B] uppercase tracking-widest mt-0.5">out of 100</span>
        </div>
      </div>

      <div className="mt-2.5 flex flex-col items-center">
        <span className={`text-[11px] font-bold uppercase px-2.5 py-0.5 rounded-full border ${badgeClass}`}>
          {badgeText}
        </span>
      </div>
    </div>
  );
};
